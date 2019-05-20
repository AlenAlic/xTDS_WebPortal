"""merchandise_overhaul

Revision ID: 09f03a08fa5a
Revises: 90693a2af39e
Create Date: 2019-05-19 23:26:48.721964

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '09f03a08fa5a'
down_revision = '90693a2af39e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('merchandise_item',
    sa.Column('merchandise_item_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=False),
    sa.Column('shirt', sa.Boolean(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('merchandise_item_id')
    )
    op.create_table('merchandise_item_variant',
    sa.Column('merchandise_item_variant_id', sa.Integer(), nullable=False),
    sa.Column('merchandise_item_id', sa.Integer(), nullable=True),
    sa.Column('variant', sa.String(length=128), nullable=False),
    sa.ForeignKeyConstraint(['merchandise_item_id'], ['merchandise_item.merchandise_item_id'], ),
    sa.PrimaryKeyConstraint('merchandise_item_variant_id')
    )
    op.create_table('merchandise_purchase',
    sa.Column('merchandise_purchased_id', sa.Integer(), nullable=False),
    sa.Column('merchandise_info_id', sa.Integer(), nullable=True),
    sa.Column('merchandise_item_variant_id', sa.Integer(), nullable=True),
    sa.Column('paid', sa.Boolean(), nullable=False),
    sa.Column('received', sa.Boolean(), nullable=False),
    sa.Column('ordered', sa.Boolean(), nullable=False),
    sa.Column('cancelled', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['merchandise_info_id'], ['merchandise_info.contestant_id'], ),
    sa.ForeignKeyConstraint(['merchandise_item_variant_id'], ['merchandise_item_variant.merchandise_item_variant_id'], ),
    sa.PrimaryKeyConstraint('merchandise_purchased_id')
    )
    op.drop_index('ix_merchandise_info_bag_paid', table_name='merchandise_info')
    op.drop_index('ix_merchandise_info_merchandise_received', table_name='merchandise_info')
    op.drop_index('ix_merchandise_info_mug_paid', table_name='merchandise_info')
    op.drop_index('ix_merchandise_info_t_shirt_paid', table_name='merchandise_info')
    op.drop_column('merchandise_info', 'merchandise_received')
    op.drop_column('merchandise_info', 't_shirt')
    op.drop_column('merchandise_info', 'bag')
    op.drop_column('merchandise_info', 'mug')
    op.drop_column('merchandise_info', 'mug_paid')
    op.drop_column('merchandise_info', 'bag_paid')
    op.drop_column('merchandise_info', 't_shirt_paid')
    op.drop_column('system_configuration', 'bag_price')
    op.drop_column('system_configuration', 'bag_sold')
    op.drop_column('system_configuration', 't_shirt_price')
    op.drop_column('system_configuration', 'mug_price')
    op.drop_column('system_configuration', 't_shirt_sold')
    op.drop_column('system_configuration', 'mug_sold')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('system_configuration', sa.Column('mug_sold', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.add_column('system_configuration', sa.Column('t_shirt_sold', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.add_column('system_configuration', sa.Column('mug_price', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.add_column('system_configuration', sa.Column('t_shirt_price', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.add_column('system_configuration', sa.Column('bag_sold', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.add_column('system_configuration', sa.Column('bag_price', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.add_column('merchandise_info', sa.Column('t_shirt_paid', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.add_column('merchandise_info', sa.Column('bag_paid', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.add_column('merchandise_info', sa.Column('mug_paid', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.add_column('merchandise_info', sa.Column('mug', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.add_column('merchandise_info', sa.Column('bag', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.add_column('merchandise_info', sa.Column('t_shirt', mysql.VARCHAR(collation='utf8_bin', length=128), nullable=False))
    op.add_column('merchandise_info', sa.Column('merchandise_received', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.create_index('ix_merchandise_info_t_shirt_paid', 'merchandise_info', ['t_shirt_paid'], unique=False)
    op.create_index('ix_merchandise_info_mug_paid', 'merchandise_info', ['mug_paid'], unique=False)
    op.create_index('ix_merchandise_info_merchandise_received', 'merchandise_info', ['merchandise_received'], unique=False)
    op.create_index('ix_merchandise_info_bag_paid', 'merchandise_info', ['bag_paid'], unique=False)
    op.drop_table('merchandise_purchase')
    op.drop_table('merchandise_item_variant')
    op.drop_table('merchandise_item')
    # ### end Alembic commands ###
