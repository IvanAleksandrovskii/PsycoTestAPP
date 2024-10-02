# services/anxiety_test_creator.py

import asyncio
import csv
from pathlib import Path
import sys

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


questions_file = Path(__file__).parent.parent / "psyco_tests_data" / "anxiety.csv"
interpretations_file = Path(__file__).parent.parent / "psyco_tests_data" / "anxiety_interpretation.csv"


async def create_anxiety_test(session: AsyncSession):
    # Read test name and description from the first row of questions file
    with questions_file.open(encoding='utf-8') as f:
        reader = csv.reader(f)
        test_info = next(reader)
        print(f"Test info: {test_info}")
        test_name = test_info[0]
        test_description = test_info[1]
        
        # Read the actual headers
        headers = next(reader)
        print(f"CSV headers: {headers}")

    # Check if the test already exists
    existing_test = await session.execute(
        select(PsycoTest).where(PsycoTest.name == test_name)
    )
    if existing_test.scalar_one_or_none():
        print(f"Тест '{test_name}' уже существует.")
        return

    # Create new test
    new_test = PsycoTest(
        name=test_name,
        description=test_description,
        test_type="score_answers"
    )
    session.add(new_test)

    # Create a dictionary to store unique answers
    unique_answers = {}

    # Read anxiety questions
    with questions_file.open(encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the first row (test name and description)
        headers = next(reader)  # Get the actual headers
        for row in reader:
            print(f"Processing row: {row}")
            question_text = row[0]  # Вопрос находится в первом столбце
            question = PsycoQuestion(
                question_text=question_text,
                test=new_test
            )
            session.add(question)

            # Add answers with scores
            for score in range(4):
                answer_text = row[score + 1]  # Ответы начинаются со второго столбца
                if answer_text not in unique_answers:
                    unique_answers[answer_text] = await get_or_create_answer(session, answer_text)
                
                answer = unique_answers[answer_text]
                question_answer = PsycoQuestionAnswer(
                    question=question,
                    answer=answer,
                    score_value=score
                )
                session.add(question_answer)

    # Read anxiety interpretation
    # Read anxiety interpretation
    with interpretations_file.open(encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Read the header row
        print(f"Interpretation CSV headers: {headers}")
        
        for row in reader:
            print(f"Processing interpretation row: {row}")
            try:
                interpretation = row[0].strip()
                score_range = row[1].strip().split()
                if score_range[0] == 'до':
                    min_score = 0
                    max_score = int(score_range[1])
                elif score_range[0] == 'от':
                    min_score = int(score_range[1])
                    max_score = int(score_range[3])
                else:
                    raise ValueError(f"Неожиданный формат диапазона баллов: {row[1]}")
            except (IndexError, ValueError) as e:
                print(f"Ошибка при обработке строки интерпретации: {e}")
                continue

            result = PsycoResult(
                test=new_test,
                min_score=min_score,
                max_score=max_score,
                text=interpretation
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


async def run_anxiety_test_creator():
    async for session in db_helper.session_getter():
        try:
            await create_anxiety_test(session)
        except Exception as e:
            logger.exception(f"Error in run_anxiety_test_creator: {e}")
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(run_anxiety_test_creator())
