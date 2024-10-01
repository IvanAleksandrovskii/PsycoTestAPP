# handlers/movie_quiz.py

import random
# import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.models import db_helper
from core.models.movie_quiz import MovieQuiz, MovieQuizQuestion, MovieQuizAnswer
from core import logger


router = Router()


class QuizState(StatesGroup):
    choosing_quiz = State()
    answering_questions = State()


@router.message(Command("start_quiz"))
async def start_quiz(message: types.Message, state: FSMContext):
    async for session in db_helper.session_getter():
        try: 
            quizzes = await session.execute(select(MovieQuiz))
            quizzes = quizzes.scalars().all()
        except Exception as e:
            logger.exception(f"Error in get_all_quizzes: {e}")
            await message.answer("An error occurred while fetching quizzes. Please try again later.")
            return
        finally:
            await session.close()

    if not quizzes:
        await message.answer("No quizzes available at the moment.")
        return

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=quiz.title, callback_data=f"quiz:{quiz.id}")]
            for quiz in quizzes
        ]
    )

    await message.answer("Choose a quiz:", reply_markup=keyboard)
    await state.set_state(QuizState.choosing_quiz)

@router.callback_query(QuizState.choosing_quiz)
async def process_quiz_choice(callback_query: types.CallbackQuery, state: FSMContext):
    quiz_id = callback_query.data.split(':')[1]
    
    async def fetch_quiz():
        async for session in db_helper.session_getter():
            try:
                stmt = select(MovieQuiz).options(
                    selectinload(MovieQuiz.questions).selectinload(MovieQuizQuestion.answers)
                ).where(MovieQuiz.id == quiz_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.exception(f"Error in get_quiz_by_id: {e}")
                return None
            finally:
                await session.close()

    try:
        quiz = await fetch_quiz()

        if not quiz:
            await callback_query.answer("Quiz not found.")
            return

        questions = quiz.questions
        if not questions:
            await callback_query.message.answer("This quiz has no questions.")
            await state.clear()
            return

        questions_list = list(questions)  # Convert to list to allow shuffling
        random.shuffle(questions_list)
        
        await state.update_data(quiz_id=quiz_id, questions=questions_list, current_question=0, correct_answers=0)
        await send_next_question(callback_query.message, state)
        await callback_query.answer()

    except Exception as e:
        logger.exception(f"Error in process_quiz_choice: {e}")
        await callback_query.message.answer("An error occurred while starting the quiz. Please try again later.")
        await state.clear()

async def send_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data['questions']
    current_question = data['current_question']

    if current_question >= len(questions):
        await end_quiz(message, state)
        return

    question = questions[current_question]
    answers = question.answers
    random.shuffle(answers)

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=answer.answer_text, callback_data=f"answer:{answer.id}")]
            for answer in answers
        ]
    )

    await message.answer(question.question_text, reply_markup=keyboard)
    await state.set_state(QuizState.answering_questions)

@router.callback_query(QuizState.answering_questions)
async def process_answer(callback_query: types.CallbackQuery, state: FSMContext):
    answer_id = callback_query.data.split(':')[1]
    
    data = await state.get_data()
    questions = data['questions']
    current_question = data['current_question']
    question = questions[current_question]
    
    answer = next((a for a in question.answers if str(a.id) == answer_id), None)
    
    if not answer:
        await callback_query.answer("Answer not found.")
        return

    if answer.is_correct:
        data['correct_answers'] += 1
    
    await callback_query.message.edit_text(
        f"Your answer: {answer.answer_text}\n"
        f"Correct answer: {next(a.answer_text for a in question.answers if a.is_correct)}\n"
        f"{'Correct!' if answer.is_correct else 'Incorrect.'}"
    )

    if question.interesting_fact:
        await callback_query.message.answer(f"Interesting fact: {question.interesting_fact}")

    data['current_question'] += 1
    await state.update_data(data)
    
    await send_next_question(callback_query.message, state)
    await callback_query.answer()

async def end_quiz(message: types.Message, state: FSMContext):
    data = await state.get_data()
    correct_answers = data['correct_answers']
    total_questions = len(data['questions'])

    await message.answer(
        f"Quiz completed!\n"
        f"You answered {correct_answers} out of {total_questions} questions correctly."
    )

    logger.info(f"User {message.from_user.id} completed quiz {data['quiz_id']} with score {correct_answers}/{total_questions}")

    await state.clear()
