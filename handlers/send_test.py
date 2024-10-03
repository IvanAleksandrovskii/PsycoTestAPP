# handlers/send_test.py

from aiogram import F, types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from core import logger  # settings
from core.models import db_helper
from sqlalchemy import select
from core.models import TGUser, PsycoTest, SentTest


router = Router()

class SendTestStates(StatesGroup):
    WAITING_FOR_USERNAME = State()
    WAITING_FOR_TEST = State()
    CONFIRMING = State()

@router.message(Command("send_test"))
async def cmd_send_test(message: types.Message, state: FSMContext):
    await state.set_state(SendTestStates.WAITING_FOR_USERNAME)
    await message.reply("Введите имя пользователя, которому хотите отправить тест:")

@router.message(SendTestStates.WAITING_FOR_USERNAME)
async def process_username(message: types.Message, state: FSMContext):
    username = message.text.lstrip('@')
    async with db_helper.session_factory() as session:
        result = await session.execute(select(TGUser).where(TGUser.username == username))
        user = result.scalar_one_or_none()
    
    if not user:
        await message.reply("Пользователь не найден. Тест будет добавлен в лист ожидания и отправлен, когда пользователь активирует бота.")
        await state.update_data(receiver_username=username, receiver_id=None)
    else:
        await state.update_data(receiver_username=username, receiver_id=user.chat_id)
    
    # Получение списка доступных тестов
    async with db_helper.session_factory() as session:
        result = await session.execute(select(PsycoTest).where(PsycoTest.is_active == True))
        tests = result.scalars().all()
    
    # Создаем список кнопок
    keyboard = []
    for test in tests:
        keyboard.append([types.InlineKeyboardButton(text=test.name, callback_data=f"select_test:{test.id}")])
    
    # Создаем InlineKeyboardMarkup с правильной структурой
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await state.set_state(SendTestStates.WAITING_FOR_TEST)
    await message.reply("Выберите тест для отправки:", reply_markup=reply_markup)

@router.callback_query(SendTestStates.WAITING_FOR_TEST, F.data.startswith("select_test:"))
async def process_test_selection(callback_query: types.CallbackQuery, state: FSMContext):
    test_id = callback_query.data.split(':')[1]
    await state.update_data(test_id=test_id)
    
    data = await state.get_data()
    async with db_helper.session_factory() as session:
        test = await session.get(PsycoTest, test_id)
    
    await state.set_state(SendTestStates.CONFIRMING)
    await callback_query.message.edit_text(
        f"Вы уверены, что хотите отправить тест '{test.name}' пользователю {data['receiver_username']}?",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Да", callback_data="confirm_send"),
                types.InlineKeyboardButton(text="Нет", callback_data="cancel_send")
            ]
        ])
    )


@router.callback_query(SendTestStates.CONFIRMING, F.data.in_(["confirm_send", "cancel_send"]))
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'confirm_send':
        data = await state.get_data()
        async with db_helper.session_factory() as session:
            sent_test = SentTest(
                sender_id=callback_query.from_user.id,
                receiver_id=data.get('receiver_id'),
                receiver_username=data['receiver_username'],
                test_id=data['test_id'],
                is_delivered=bool(data.get('receiver_id'))
            )
            session.add(sent_test)
            await session.commit()
        
        if data.get('receiver_id'):
            await callback_query.message.edit_text("Тест успешно отправлен!")
            # Уведомление получателю
            receiver_id = str(data['receiver_id'])  # Преобразуем UUID в строку
            try:
                await callback_query.bot.send_message(receiver_id, f"Вам отправлен новый тест. Используйте /start, чтобы увидеть доступные тесты.")
            except Exception as e:
                logger.error(f"Error sending message to receiver: {e}")
                await callback_query.message.edit_text("Тест отправлен, но не удалось уведомить получателя.")
        else:
            await callback_query.message.edit_text("Тест добавлен в лист ожидания и будет отправлен, когда пользователь активирует бота.")
    else:
        await callback_query.message.edit_text("Отправка теста отменена.")
    
    await state.clear()
