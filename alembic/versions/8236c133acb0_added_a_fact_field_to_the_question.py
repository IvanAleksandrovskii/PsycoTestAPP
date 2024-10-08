"""added a fact field to the question

Revision ID: 8236c133acb0
Revises: 85dfbd6179b7
Create Date: 2024-10-01 14:48:54.145724

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8236c133acb0'
down_revision: Union[str, None] = '85dfbd6179b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie_quiz_questions', sa.Column('interesting_fact', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movie_quiz_questions', 'interesting_fact')
    # ### end Alembic commands ###
