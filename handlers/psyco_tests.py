# handlers/psyco_tests.py

import json
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.models import db_helper
from core.models.psyco_test import PsycoTest, PsycoQuestion, PsycoQuestionAnswer, PsycoResult
from core import logger

router = Router()


class PsycoTestState(StatesGroup):
    choosing_test = State()
    confirming_test = State()
    answering_questions = State()


@router.message(Command("start_psyco_test"))
async def start_psyco_test(message: types.Message, state: FSMContext):
    async for session in db_helper.session_getter():
        try:
            tests = await session.execute(select(PsycoTest).where(PsycoTest.is_active == True))
            tests = tests.scalars().all()
        except Exception as e:
            logger.exception(f"Error in get_all_psyco_tests: {e}")
            await message.answer("An error occurred while fetching tests. Please try again later.")
            return
        finally:
            await session.close()

    if not tests:
        await message.answer("No psychological tests available at the moment.")
        return

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=test.name, callback_data=f"psyco_test:{test.id}")]
            for test in tests
        ]
    )
    
    await message.answer("Please choose a psychological test:", reply_markup=keyboard)
    await state.set_state(PsycoTestState.choosing_test)


@router.callback_query(PsycoTestState.choosing_test)
async def confirm_test_choice(callback_query: types.CallbackQuery, state: FSMContext):
    test_id = callback_query.data.split(':')[1]
    
    async def fetch_test():
        async for session in db_helper.session_getter():
            try:
                stmt = select(PsycoTest).where(PsycoTest.id == test_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.exception(f"Error in get_psyco_test_by_id: {e}")
                return None
            finally:
                await session.close()

    test = await fetch_test()

    if not test:
        await callback_query.answer("Test not found.")
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Start Test", callback_data=f"start_test:{test_id}")],
        [types.InlineKeyboardButton(text="Back to Test Selection", callback_data="back_to_selection")]
    ])

    await callback_query.message.edit_text(
        f"You've selected: {test.name}\n\n"
        f"Description: {test.description}\n\n"
        "Are you ready to start the test?",
        reply_markup=keyboard
    )
    await state.set_state(PsycoTestState.confirming_test)
    await callback_query.answer()


@router.callback_query(PsycoTestState.confirming_test, lambda c: c.data == "back_to_selection")
async def back_to_test_selection(callback_query: types.CallbackQuery, state: FSMContext):
    await start_psyco_test(callback_query.message, state)
    await callback_query.answer()


@router.callback_query(PsycoTestState.confirming_test, lambda c: c.data.startswith("start_test:"))
async def start_confirmed_test(callback_query: types.CallbackQuery, state: FSMContext):
    test_id = callback_query.data.split(':')[1]
    
    async def fetch_test():
        async for session in db_helper.session_getter():
            try:
                stmt = select(PsycoTest).options(
                    selectinload(PsycoTest.questions).selectinload(PsycoQuestion.answer_options).selectinload(PsycoQuestionAnswer.answer),
                    selectinload(PsycoTest.results)
                ).where(PsycoTest.id == test_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.exception(f"Error in get_psyco_test_by_id: {e}")
                return None
            finally:
                await session.close()

    try:
        test = await fetch_test()

        if not test:
            await callback_query.answer("Test not found.")
            return

        questions = test.questions
        if not questions:
            await callback_query.message.answer("This test has no questions.")
            await state.clear()
            return

        await state.update_data(test=test, current_question_index=0, score=0, answers=[])
        await send_next_question(callback_query.message, state)
        await callback_query.answer()

    except Exception as e:
        logger.exception(f"Error in start_confirmed_test: {e}")
        await callback_query.message.answer("An error occurred while starting the test. Please try again later.")
        await state.clear()


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

    test_progress = f"Question {current_question_index + 1}/{len(test.questions)}\n\n"
    await message.edit_text(test_progress + current_question.question_text, reply_markup=keyboard)
    await state.set_state(PsycoTestState.answering_questions)


@router.callback_query(PsycoTestState.answering_questions, lambda c: c.data == "back_question")
async def go_back_question(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_question_index = data['current_question_index']
    
    if current_question_index > 0:
        data['current_question_index'] -= 1
        data['score'] -= data['answers'].pop().score_value
        await state.set_data(data)
        await send_next_question(callback_query.message, state)
    
    await callback_query.answer()


@router.callback_query(PsycoTestState.answering_questions, lambda c: c.data.startswith("answer:"))
async def process_answer(callback_query: types.CallbackQuery, state: FSMContext):
    answer_id = callback_query.data.split(':')[1]
    
    data = await state.get_data()
    test = data['test']
    current_question_index = data['current_question_index']
    current_question = test.questions[current_question_index]
    
    answer_option = next((a for a in current_question.answer_options if str(a.id) == answer_id), None)
    
    if not answer_option:
        await callback_query.answer("Answer not found.")
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

    result = next((r for r in test.results if r.min_score <= score <= r.max_score), None)
    
    if not result:
        await message.answer("Unable to interpret your results. Please contact the administrator.")
        await state.clear()
        return

    result_text = (
        f"Test completed!\n\n"
        f"Your answers:\n" + "\n".join(f"{i+1}. {answer.answer.answer_text}" for i, answer in enumerate(answers)) + "\n\n"
        f"Your score: {score}\n\n"
        f"Interpretation:\n{result.text}"
    )

    await message.edit_text(result_text)
    logger.info(f"User {message.from_user.id} completed test {test.id} with score {score}")
    await state.clear()
