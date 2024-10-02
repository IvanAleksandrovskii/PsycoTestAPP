# services/stress_condition_test_creator.py

import asyncio
import csv
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

sys.path.append(str(Path(__file__).parent.parent))

from core import logger
from core.models import db_helper
from core.models import (
    PsycoTest,
    PsycoQuestion,
    PsycoAnswer,
    PsycoQuestionAnswer,
    PsycoResult
)

questions_file = Path(__file__).parent.parent / "psyco_tests_data" / "stress_condition.csv"
interpretations_file = Path(__file__).parent.parent / "psyco_tests_data" / "stress_condition_interpretation.csv"

async def create_stress_condition_test(session: AsyncSession):
    # Check if the test already exists
    test_name = "Стресс - Экспресс Тест"
    existing_test = await session.execute(
        select(PsycoTest).where(PsycoTest.name == test_name)
    )
    if existing_test.scalar_one_or_none():
        print(f"Тест '{test_name}' уже существует.")
        return

    # Create new test
    new_test = PsycoTest(
        name=test_name,
        description="Экспресс диагностика состояния стресса",
        allow_back=True
    )
    session.add(new_test)

    # Create or get "Да" and "Нет" answers
    answer_no = await get_or_create_answer(session, "Нет")
    answer_yes = await get_or_create_answer(session, "Да")

    # Read stress condition questions
    with questions_file.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        next(reader)  # Skip the second row (headers)
        for row in reader:
            question = PsycoQuestion(
                question_text=row['экспресс диагностика состояния стресса'],
                test=new_test
            )
            session.add(question)

            # Add answer options
            answer_option_no = PsycoQuestionAnswer(
                question=question,
                answer=answer_no,
                score_value=0
            )
            answer_option_yes = PsycoQuestionAnswer(
                question=question,
                answer=answer_yes,
                score_value=1
            )
            session.add_all([answer_option_no, answer_option_yes])

    # Read stress condition interpretation
    with interpretations_file.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            score = int(row['баллы'].split()[0])
            result = PsycoResult(
                test=new_test,
                min_score=score,
                max_score=score,
                text=row['интерпретация']
            )
            session.add(result)

    await session.commit()
    print(f"Тест '{test_name}' успешно создан.")

async def get_or_create_answer(session: AsyncSession, answer_text: str) -> PsycoAnswer:
    existing_answer = await session.execute(
        select(PsycoAnswer).where(PsycoAnswer.answer_text == answer_text)
    )
    answer = existing_answer.scalar_one_or_none()
    if not answer:
        answer = PsycoAnswer(answer_text=answer_text)
        session.add(answer)
    return answer

# Run stress condition test creator
async def run_stress_condition_test_creator():
    async for session in db_helper.session_getter():
        try:
            await create_stress_condition_test(session)
        except Exception as e:
            logger.exception(f"Error in run_stress_condition_test_creator: {e}")
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(run_stress_condition_test_creator())
