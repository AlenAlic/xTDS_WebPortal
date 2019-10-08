"""publish_heat_list_round

Revision ID: 7e9d03e77598
Revises: 882c12950184
Create Date: 2019-10-08 18:14:17.043638

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e9d03e77598'
down_revision = '882c12950184'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('round', sa.Column('heat_list_published', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('round', 'heat_list_published')
    # ### end Alembic commands ###