"""news

Revision ID: 5db5366a3f7e
Revises: 7e9d03e77598
Create Date: 2019-10-12 22:14:55.567712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5db5366a3f7e'
down_revision = '7e9d03e77598'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('news',
    sa.Column('news_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(length=256), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('news_id')
    )
    op.create_index(op.f('ix_news_timestamp'), 'news', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_news_timestamp'), table_name='news')
    op.drop_table('news')
    # ### end Alembic commands ###
