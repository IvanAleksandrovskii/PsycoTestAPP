"""del table

Revision ID: 706552ef2759
Revises: a8a656bc16fb
Create Date: 2024-10-03 16:26:19.094829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '706552ef2759'
down_revision: Union[str, None] = 'a8a656bc16fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sent_tests')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sent_tests',
    sa.Column('sender_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('test_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('receiver_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('receiver_username', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('is_completed', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('is_delivered', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('delivered_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('completed_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['receiver_id'], ['tg_users.id'], name='fk_sent_tests_receiver_id_tg_users'),
    sa.ForeignKeyConstraint(['sender_id'], ['tg_users.id'], name='fk_sent_tests_sender_id_tg_users'),
    sa.ForeignKeyConstraint(['test_id'], ['psyco_tests.id'], name='fk_sent_tests_test_id_psyco_tests'),
    sa.PrimaryKeyConstraint('id', name='pk_sent_tests')
    )
    # ### end Alembic commands ###
