"""edit tests table

Revision ID: d48e381859f0
Revises: c675d188c784
Create Date: 2024-10-03 01:44:53.073694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd48e381859f0'
down_revision: Union[str, None] = 'c675d188c784'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Шаг 1: Добавляем столбец allow_back как NULL и устанавливаем значение по умолчанию
    op.add_column('psyco_tests', sa.Column('allow_back', sa.Boolean(), nullable=True))
    op.execute("UPDATE psyco_tests SET allow_back = TRUE")
    
    # Шаг 2: Изменяем столбец на NOT NULL
    op.alter_column('psyco_tests', 'allow_back', nullable=False)
    
    op.drop_column('psyco_tests', 'test_type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('psyco_tests', sa.Column('test_type', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('psyco_tests', 'allow_back')
    # ### end Alembic commands ###
