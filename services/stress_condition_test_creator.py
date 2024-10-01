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
from core.models.psyco_test_with_correct_answer import (
    PycoTestWithCorrectAnswer,
    PsycoQuestionWithCorrectAnswer,
    PsycoAnswerWithCorrectMarker,
    PsycoResultWithFromToGroup
)


questions_file = Path(__file__).parent.parent / "psyco_tests_data" / "stress_condition.csv"
interpretations_file = Path(__file__).parent.parent / "psyco_tests_data" / "stress_condition_interpretation.csv"


async def create_stress_condition_test(session: AsyncSession):
    # Check if the test already exists
    test_name = "Стресс-тест"
    existing_test = await session.execute(
        select(PycoTestWithCorrectAnswer).where(PycoTestWithCorrectAnswer.name == test_name)
    )
    if existing_test.scalar_one_or_none():
        print(f"Тест '{test_name}' уже существует.")
        return

    # Create new test
    new_test = PycoTestWithCorrectAnswer(
        name=test_name,
        description="Экспресс диагностика состояния стресса"
    )
    session.add(new_test)

    # Read stress condition questions
    with questions_file.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        next(reader)  # Skip the second row (headers)
        for row in reader:
            question = PsycoQuestionWithCorrectAnswer(
                question_text=row['экспресс диагностика состояния стресса'],
                test=new_test
            )
            logger.info(f"Created question: {question}")
            session.add(question)

            # Add answers
            answer_no = PsycoAnswerWithCorrectMarker(
                answer_text="Нет",
                is_correct=False,  # Always incorrect
                question=question
            )
            answer_yes = PsycoAnswerWithCorrectMarker(
                answer_text="Да",
                is_correct=True,  # Always correct
                question=question
            )
            session.add_all([answer_no, answer_yes])

    # Read stress condition interpretation
    with interpretations_file.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            score = int(row['баллы'].split()[0])
            result = PsycoResultWithFromToGroup(
                test=new_test,
                min_score=score,
                max_score=score,
                text=row['интерпретация']
            )
            session.add(result)

    await session.commit()
    print(f"Тест '{test_name}' успешно создан.")


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
