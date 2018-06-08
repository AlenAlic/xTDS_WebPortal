"""tournament_state_fix

Revision ID: 9615133f847a
Revises: 9eae7b74051a
Create Date: 2018-06-08 07:15:29.068129

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9615133f847a'
down_revision = '9eae7b74051a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tournament_state', 'main_raffle_result_visible',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    op.alter_column('tournament_state', 'numbers_rearranged',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    op.alter_column('tournament_state', 'raffle_completed_message_sent',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    op.alter_column('users', 'send_new_messages_email',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'send_new_messages_email',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    op.alter_column('tournament_state', 'raffle_completed_message_sent',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    op.alter_column('tournament_state', 'numbers_rearranged',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    op.alter_column('tournament_state', 'main_raffle_result_visible',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    # ### end Alembic commands ###