# handlers/on_start.py

from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from core.models.psyco_test import PsycoQuestion, PsycoQuestionAnswer, PsycoTest
from core.models.send_test import SentTest
from services import UserService
from core import settings, logger
from core.models import db_helper


router = Router()


async def notify_test_owner(bot, sent_test_id: int, receiver_username: str):
    async with db_helper.session_factory() as session:
        sent_test = await session.get(SentTest, sent_test_id)
        if sent_test:
            test = await session.get(PsycoTest, sent_test.test_id)
            await bot.send_message(
                sent_test.sender_id,
                f"Пользователь @{receiver_username} начал проходить отправленный вами тест '{test.name}'."
            )


class PsycoTestState(StatesGroup):
    choosing_test = State()
    confirming_test = State()
    answering_questions = State()


async def get_unfinished_tests_keyboard(chat_id: int, username: str):
    async with db_helper.session_factory() as session:
        waiting_tests = await session.execute(
            select(SentTest).where(
                SentTest.receiver_username == username,
                SentTest.is_delivered == False
            )
        )
        waiting_tests = waiting_tests.scalars().all()
        
        for test in waiting_tests:
            test.receiver_id = chat_id
            test.is_delivered = True
            test.delivered_at = func.now()
        
        unfinished_tests = await session.execute(
            select(SentTest).where(
                SentTest.receiver_id == chat_id,
                SentTest.is_completed == False
            ).options(selectinload(SentTest.test))
        )
        unfinished_tests = unfinished_tests.scalars().all()
        
        await session.commit()

    if unfinished_tests:
        logger.info(f"User {username} has {len(unfinished_tests)} unfinished tests")
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=f"Пройти тест: {sent_test.test.name}", callback_data=f"start_sent_test:{sent_test.id}")]
            for sent_test in unfinished_tests
        ])
        return keyboard, f"У вас есть {len(unfinished_tests)} непройденных тестов. Хотите пройти их сейчас?"
    else:
        logger.info(f"User {username} has no unfinished tests")
        return None, "У вас нет непройденных тестов. Вы можете посмотреть доступные тесты, используя команду /start_psyco_test"


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    username = message.from_user.username

    logger.info(f"Start command received from user {username} (chat_id: {chat_id})")

    user_service = UserService()

    user = await user_service.get_user(chat_id)
    if not user:
        user = await user_service.create_user(chat_id, username)
        logger.info(f"Created new user: {chat_id}, username: {username}")
    elif user.username != username:
        await user_service.update_username(chat_id, username)
        logger.info(f"Updated username for user {chat_id} to {username}")

    keyboard, reply_text = await get_unfinished_tests_keyboard(chat_id, username)

    welcome_message = settings.bot.welcome_message
    if welcome_message and '{username}' in welcome_message:
        formatted_message = welcome_message.format(username=username or "пользователь")
    else:
        formatted_message = welcome_message

    if keyboard:
        await message.reply(f"{formatted_message}\n\n{reply_text}", reply_markup=keyboard)
    else:
        await message.reply(f"{formatted_message}\n\n{reply_text}")


@router.callback_query(F.data.startswith("start_sent_test:"))
async def start_sent_test(callback_query: types.CallbackQuery, state: FSMContext):
    sent_test_id = callback_query.data.split(':')[1]
    logger.info(f"User {callback_query.from_user.username} starting sent test {sent_test_id}")
    async with db_helper.session_factory() as session:
        sent_test = await session.get(SentTest, sent_test_id)
        if sent_test and not sent_test.is_completed:
            test = await session.get(PsycoTest, sent_test.test_id, options=[
                selectinload(PsycoTest.questions).selectinload(PsycoQuestion.answer_options).selectinload(PsycoQuestionAnswer.answer),
                selectinload(PsycoTest.results)
            ])
            if not test:
                await callback_query.message.edit_text("Тест не найден.")
                return
            
            await state.update_data(test=test, current_question_index=0, score=0, answers=[], current_sent_test_id=sent_test_id)
            
            description_text = f"Вы выбрали тест: {test.name}\n\n{test.description}\n\nВы готовы начать?"
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Начать тест", callback_data=f"confirm_start_test:{test.id}")]
            ])
            
            if test.picture:
                image_url = f"{settings.media.base_url}/{test.picture}"
                await callback_query.message.answer_photo(photo=image_url, caption=description_text, reply_markup=keyboard)
            else:
                await callback_query.message.edit_text(text=description_text, reply_markup=keyboard)
            
            await state.set_state(PsycoTestState.confirming_test)
            
            # Notify test owner
            await notify_test_owner(callback_query.bot, sent_test_id, callback_query.from_user.username)
        else:
            await callback_query.message.edit_text("Этот тест уже пройден или недоступен.")
            logger.warning(f"Test {sent_test_id} is already completed or unavailable")


@router.callback_query(PsycoTestState.confirming_test, F.data.startswith("confirm_start_test:"))
async def confirm_start_test(callback_query: types.CallbackQuery, state: FSMContext):
    await send_next_question(callback_query.message, state)
    await callback_query.answer()

async def send_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test = data['test']
    current_question_index = data['current_question_index']

    if current_question_index >= len(test.questions):
        await end_test(message, state)
        return

    current_question = test.questions[current_question_index]
    answer_options = current_question.answer_options

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=option.answer.answer_text, callback_data=f"answer:{option.id}")]
            for option in answer_options
        ]
    )

    if test.allow_back and current_question_index > 0:
        keyboard.inline_keyboard.append([types.InlineKeyboardButton(text="⬅️ Back", callback_data="back_question")])

    test_progress = f"Вопрос {current_question_index + 1}/{len(test.questions)}\n\n"
    question_text = test_progress + current_question.question_text

    try:
        if test.picture:
            image_url = f"{settings.media.base_url}/{test.picture}"
            await message.edit_media(
                media=types.InputMediaPhoto(media=image_url, caption=question_text),
                reply_markup=keyboard
            )
        else:
            await message.edit_text(text=question_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error sending question: {e}")
        if test.picture:
            image_url = f"{settings.media.base_url}/{test.picture}"
            await message.answer_photo(photo=image_url, caption=question_text, reply_markup=keyboard)
        else:
            await message.answer(text=question_text, reply_markup=keyboard)

    await state.set_state(PsycoTestState.answering_questions)


@router.callback_query(PsycoTestState.answering_questions, F.data == "back_question")
async def go_back_question(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_question_index = data['current_question_index']
    
    if current_question_index > 0:
        data['current_question_index'] -= 1
        data['score'] -= data['answers'].pop().score_value
        await state.set_data(data)
        await send_next_question(callback_query.message, state)
    
    await callback_query.answer()


@router.callback_query(PsycoTestState.answering_questions, F.data.startswith("answer:"))
async def process_answer(callback_query: types.CallbackQuery, state: FSMContext):
    answer_id = callback_query.data.split(':')[1]
    
    data = await state.get_data()
    test = data['test']
    current_question_index = data['current_question_index']
    current_question = test.questions[current_question_index]
    
    answer_option = next((a for a in current_question.answer_options if str(a.id) == answer_id), None)
    
    if not answer_option:
        await callback_query.answer("Ответ не найден.")
        return

    score = data['score']
    score += answer_option.score_value

    answers = data['answers']
    answers.append(answer_option)

    await state.update_data(score=score, answers=answers, current_question_index=current_question_index + 1)
    
    await send_next_question(callback_query.message, state)
    await callback_query.answer()


async def end_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test = data['test']
    score = data['score']
    answers = data['answers']
    current_sent_test_id = data.get('current_sent_test_id')

    result = next((r for r in test.results if r.min_score <= score <= r.max_score), None)
    
    if not result:
        await message.edit_text("Невозможно интерпретировать ваши результаты. Пожалуйста, свяжитесь с администратором.")
        await state.clear()
        return

    result_text = (
        f"Тест завершен!\n\n"
        f"Ваши ответы:\n" + "\n".join(f"{i+1}. {answer.answer.answer_text}" for i, answer in enumerate(answers)) + "\n\n"
        f"Ваш результат: {score}\n\n"
        f"Интерпретация:\n{result.text}"
    )

    try:
        if test.picture:
            image_url = f"{settings.media.base_url}/{test.picture}"
            await message.edit_media(
                media=types.InputMediaPhoto(media=image_url, caption=result_text)
            )
        else:
            await message.edit_text(result_text)
    except Exception as e:
        logger.error(f"Error sending result: {e}")
        if test.picture:
            image_url = f"{settings.media.base_url}/{test.picture}"
            await message.answer_photo(photo=image_url, caption=result_text)
        else:
            await message.answer(result_text)

    # Обновление статуса отправленного теста
    if current_sent_test_id:
        async with db_helper.session_factory() as session:
            sent_test = await session.get(SentTest, current_sent_test_id)
            if sent_test:
                sent_test.is_completed = True
                sent_test.completed_at = func.now()
                await session.commit()
                
                # Уведомление отправителю о завершении теста
                await message.bot.send_message(sent_test.sender_id, f"Пользователь @{message.from_user.username} завершил отправленный вами тест '{test.name}' с результатом {score} и интерпретацией: {result.text}.")

    logger.info(f"User {message.from_user.id} completed test {test.id} with score {score}")
    await state.clear()

    # Проверяем, есть ли еще незавершенные тесты
    keyboard, reply_text = await get_unfinished_tests_keyboard(message.chat.id, message.from_user.username)
    if keyboard:
        await message.answer(reply_text, reply_markup=keyboard)
    else:
        await message.answer("Спасибо, вы прошли все отправленные вам тесты! Можете посмотреть доступные тесты, используя команду /start_psyco_test")
