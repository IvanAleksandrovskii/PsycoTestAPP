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
async def process_test_choice(callback_query: types.CallbackQuery, state: FSMContext):
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
        logger.exception(f"Error in process_test_choice: {e}")
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

    test_progress = f"Question {current_question_index + 1}/{len(test.questions)}\n\n"
    await message.edit_text(test_progress + current_question.question_text, reply_markup=keyboard)
    await state.set_state(PsycoTestState.answering_questions)


@router.callback_query(PsycoTestState.answering_questions)
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
    if test.test_type == "correct_answer":
        score += 1 if answer_option.is_correct else 0
    elif test.test_type == "score_answers":
        score += answer_option.score_value or 0

    answers = data['answers']
    answers.append(answer_option.answer.answer_text)

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
        f"Your answers:\n" + "\n".join(f"{i+1}. {answer}" for i, answer in enumerate(answers)) + "\n\n"
        f"Your score: {score}\n\n"
        f"Interpretation:\n{result.text}"
    )

    await message.edit_text(result_text)
    logger.info(f"User {message.from_user.id} completed test {test.id} with score {score}")
    await state.clear()
