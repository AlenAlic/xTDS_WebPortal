"""ntds_2019_overhaul

Revision ID: c06fd73d0f7a
Revises: d5592bf71272
Create Date: 2018-11-17 02:30:42.369860

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c06fd73d0f7a'
down_revision = 'd5592bf71272'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('attended_previous_tournament_contestant',
    sa.Column('contestant_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=128), nullable=False),
    sa.Column('prefixes', sa.String(length=128), nullable=True),
    sa.Column('last_name', sa.String(length=128), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('tournaments', sa.String(length=8192), nullable=False),
    sa.PrimaryKeyConstraint('contestant_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('not_selected_contestant',
    sa.Column('contestant_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=128), nullable=False),
    sa.Column('prefixes', sa.String(length=128), nullable=True),
    sa.Column('last_name', sa.String(length=128), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('tournament', sa.String(length=16), nullable=False),
    sa.PrimaryKeyConstraint('contestant_id')
    )
    op.create_table('raffle_configuration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('maximum_number_of_dancers', sa.Integer(), nullable=False),
    sa.Column('selection_buffer', sa.Integer(), nullable=False),
    sa.Column('beginners_guaranteed_entry_cutoff', sa.Boolean(), nullable=False),
    sa.Column('beginners_guaranteed_cutoff', sa.Integer(), nullable=False),
    sa.Column('beginners_guaranteed_per_team', sa.Boolean(), nullable=False),
    sa.Column('beginners_minimum_entry_per_team', sa.Integer(), nullable=False),
    sa.Column('beginners_increased_chance', sa.Boolean(), nullable=False),
    sa.Column('first_time_guaranteed_entry', sa.Boolean(), nullable=False),
    sa.Column('first_time_increased_chance', sa.Boolean(), nullable=False),
    sa.Column('guaranteed_team_size', sa.Boolean(), nullable=False),
    sa.Column('minimum_team_size', sa.Integer(), nullable=False),
    sa.Column('lions_guaranteed_per_team', sa.Boolean(), nullable=False),
    sa.Column('closed_lion', sa.Boolean(), nullable=False),
    sa.Column('open_class_lion', sa.Boolean(), nullable=False),
    sa.Column('lions_minimum_entry_per_team', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('super_volunteer',
    sa.Column('volunteer_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=128), nullable=False),
    sa.Column('prefixes', sa.String(length=128), nullable=True),
    sa.Column('last_name', sa.String(length=128), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('Diet/Allergies', sa.String(length=512), nullable=True),
    sa.Column('sleeping_arrangements', sa.Boolean(), nullable=False),
    sa.Column('remark', sa.String(length=512), nullable=True),
    sa.Column('first_aid', sa.String(length=16), nullable=False),
    sa.Column('emergency_response_officer', sa.String(length=16), nullable=False),
    sa.Column('jury_ballroom', sa.String(length=16), nullable=False),
    sa.Column('jury_latin', sa.String(length=16), nullable=False),
    sa.Column('level_ballroom', sa.String(length=16), nullable=False),
    sa.Column('level_latin', sa.String(length=16), nullable=False),
    sa.Column('license_jury_ballroom', sa.String(length=16), nullable=False),
    sa.Column('license_jury_latin', sa.String(length=16), nullable=False),
    sa.Column('jury_salsa', sa.String(length=16), nullable=False),
    sa.Column('jury_polka', sa.String(length=16), nullable=False),
    sa.PrimaryKeyConstraint('volunteer_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('system_configuration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('website_accessible', sa.Boolean(), nullable=False),
    sa.Column('system_configuration_accessible', sa.Boolean(), nullable=False),
    sa.Column('tournament', sa.String(length=4), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('city', sa.String(length=128), nullable=False),
    sa.Column('tournament_starting_date', sa.Integer(), nullable=False),
    sa.Column('number_of_teamcaptains', sa.Integer(), nullable=False),
    sa.Column('beginners_level', sa.Boolean(), nullable=False),
    sa.Column('champions_level', sa.Boolean(), nullable=False),
    sa.Column('closed_level', sa.Boolean(), nullable=False),
    sa.Column('breitensport_obliged_blind_date', sa.Boolean(), nullable=False),
    sa.Column('salsa_competition', sa.Boolean(), nullable=False),
    sa.Column('polka_competition', sa.Boolean(), nullable=False),
    sa.Column('student_price', sa.Integer(), nullable=False),
    sa.Column('non_student_price', sa.Integer(), nullable=False),
    sa.Column('phd_student_category', sa.Boolean(), nullable=False),
    sa.Column('phd_student_price', sa.Integer(), nullable=False),
    sa.Column('first_time_ask', sa.Boolean(), nullable=False),
    sa.Column('ask_diet_allergies', sa.Boolean(), nullable=False),
    sa.Column('ask_volunteer', sa.Boolean(), nullable=False),
    sa.Column('ask_first_aid', sa.Boolean(), nullable=False),
    sa.Column('ask_emergency_response_officer', sa.Boolean(), nullable=False),
    sa.Column('ask_adjudicator_highest_achieved_level', sa.Boolean(), nullable=False),
    sa.Column('ask_adjudicator_certification', sa.Boolean(), nullable=False),
    sa.Column('t_shirt_sold', sa.Boolean(), nullable=False),
    sa.Column('t_shirt_price', sa.Integer(), nullable=False),
    sa.Column('mug_sold', sa.Boolean(), nullable=False),
    sa.Column('mug_price', sa.Integer(), nullable=False),
    sa.Column('bag_sold', sa.Boolean(), nullable=False),
    sa.Column('bag_price', sa.Integer(), nullable=False),
    sa.Column('merchandise_link', sa.String(length=1028), nullable=True),
    sa.Column('merchandise_closing_date', sa.Integer(), nullable=False),
    sa.Column('finances_full_refund', sa.Boolean(), nullable=False),
    sa.Column('finances_partial_refund', sa.Boolean(), nullable=False),
    sa.Column('finances_partial_refund_percentage', sa.Integer(), nullable=False),
    sa.Column('finances_refund_date', sa.Integer(), nullable=False),
    sa.Column('main_page_link', sa.String(length=1028), nullable=True),
    sa.Column('terms_and_conditions_link', sa.String(length=1028), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment_info',
    sa.Column('contestant_id', sa.Integer(), nullable=False),
    sa.Column('entry_paid', sa.Boolean(), nullable=False),
    sa.Column('full_refund', sa.Boolean(), nullable=False),
    sa.Column('partial_refund', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['contestant_id'], ['contestants.contestant_id'], ),
    sa.PrimaryKeyConstraint('contestant_id')
    )
    op.create_index(op.f('ix_payment_info_entry_paid'), 'payment_info', ['entry_paid'], unique=False)
    op.create_index(op.f('ix_payment_info_full_refund'), 'payment_info', ['full_refund'], unique=False)
    op.create_index(op.f('ix_payment_info_partial_refund'), 'payment_info', ['partial_refund'], unique=False)
    op.drop_table('merchandise')
    op.drop_table('team_finances')
    op.drop_column('additional_info', 't_shirt')
    op.add_column('merchandise_info', sa.Column('bag', sa.Boolean(), nullable=False))
    op.add_column('merchandise_info', sa.Column('bag_paid', sa.Boolean(), nullable=False))
    op.add_column('merchandise_info', sa.Column('merchandise_received', sa.Boolean(), nullable=False))
    op.add_column('merchandise_info', sa.Column('mug', sa.Boolean(), nullable=False))
    op.add_column('merchandise_info', sa.Column('mug_paid', sa.Boolean(), nullable=False))
    op.add_column('merchandise_info', sa.Column('t_shirt', sa.String(length=128), nullable=False))
    op.add_column('merchandise_info', sa.Column('t_shirt_paid', sa.Boolean(), nullable=False))
    op.create_index(op.f('ix_merchandise_info_bag_paid'), 'merchandise_info', ['bag_paid'], unique=False)
    op.create_index(op.f('ix_merchandise_info_merchandise_received'), 'merchandise_info', ['merchandise_received'], unique=False)
    op.create_index(op.f('ix_merchandise_info_mug_paid'), 'merchandise_info', ['mug_paid'], unique=False)
    op.create_index(op.f('ix_merchandise_info_t_shirt_paid'), 'merchandise_info', ['t_shirt_paid'], unique=False)
    op.drop_column('merchandise_info', 'quantity')
    op.drop_column('merchandise_info', 'product_id')
    op.add_column('status_info', sa.Column('feedback_about_information', sa.String(length=512), nullable=True))
    op.add_column('status_info', sa.Column('received_starting_number', sa.Boolean(), nullable=False))
    op.drop_index('ix_status_info_paid', table_name='status_info')
    op.drop_column('status_info', 'paid')
    op.add_column('teams', sa.Column('amount_paid', sa.Integer(), nullable=False))
    op.add_column('tournament_state', sa.Column('organizer_account_set', sa.Boolean(), nullable=False))
    op.add_column('tournament_state', sa.Column('raffle_system_configured', sa.Boolean(), nullable=False))
    op.add_column('tournament_state', sa.Column('registration_open', sa.Boolean(), nullable=False))
    op.add_column('tournament_state', sa.Column('registration_period_started', sa.Boolean(), nullable=False))
    op.add_column('tournament_state', sa.Column('system_configured', sa.Boolean(), nullable=False))
    op.add_column('tournament_state', sa.Column('website_accessible_to_teamcaptains', sa.Boolean(), nullable=False))
    op.drop_column('tournament_state', 'tournament_config')
    op.drop_column('tournament_state', 'raffle_config')
    op.add_column('users', sa.Column('activate', sa.Boolean(), nullable=False))
    op.add_column('users', sa.Column('contestant_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('volunteer_id', sa.Integer(), nullable=True))
    op.drop_index('ix_users_password_hash', table_name='users')
    op.create_foreign_key(None, 'users', 'super_volunteer', ['volunteer_id'], ['volunteer_id'])
    op.create_foreign_key(None, 'users', 'contestants', ['contestant_id'], ['contestant_id'])
    op.add_column('volunteer_info', sa.Column('emergency_response_officer', sa.String(length=16), nullable=False))
    # ### end Alembic commands ###
    op.alter_column('contestant_info', 'student', existing_type=sa.Boolean, type_=sa.String(length=128))


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('volunteer_info', 'emergency_response_officer')
    op.drop_constraint('users_ibfk_2', 'users', type_='foreignkey')
    op.drop_constraint('users_ibfk_3', 'users', type_='foreignkey')
    op.create_index('ix_users_password_hash', 'users', ['password_hash'], unique=False)
    op.drop_column('users', 'volunteer_id')
    op.drop_column('users', 'contestant_id')
    op.drop_column('users', 'activate')
    op.add_column('tournament_state', sa.Column('raffle_config', mysql.VARCHAR(length=2048), nullable=False))
    op.add_column('tournament_state', sa.Column('tournament_config', mysql.VARCHAR(length=2048), nullable=False))
    op.drop_column('tournament_state', 'website_accessible_to_teamcaptains')
    op.drop_column('tournament_state', 'system_configured')
    op.drop_column('tournament_state', 'registration_period_started')
    op.drop_column('tournament_state', 'registration_open')
    op.drop_column('tournament_state', 'raffle_system_configured')
    op.drop_column('tournament_state', 'organizer_account_set')
    op.drop_column('teams', 'amount_paid')
    op.add_column('status_info', sa.Column('paid', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.create_index('ix_status_info_paid', 'status_info', ['paid'], unique=False)
    op.drop_column('status_info', 'received_starting_number')
    op.drop_column('status_info', 'feedback_about_information')
    op.add_column('merchandise_info', sa.Column('product_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.add_column('merchandise_info', sa.Column('quantity', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_merchandise_info_t_shirt_paid'), table_name='merchandise_info')
    op.drop_index(op.f('ix_merchandise_info_mug_paid'), table_name='merchandise_info')
    op.drop_index(op.f('ix_merchandise_info_merchandise_received'), table_name='merchandise_info')
    op.drop_index(op.f('ix_merchandise_info_bag_paid'), table_name='merchandise_info')
    op.drop_column('merchandise_info', 't_shirt_paid')
    op.drop_column('merchandise_info', 't_shirt')
    op.drop_column('merchandise_info', 'mug_paid')
    op.drop_column('merchandise_info', 'mug')
    op.drop_column('merchandise_info', 'merchandise_received')
    op.drop_column('merchandise_info', 'bag_paid')
    op.drop_column('merchandise_info', 'bag')
    op.add_column('additional_info', sa.Column('t_shirt', mysql.VARCHAR(length=128), nullable=False))
    op.create_table('team_finances',
    sa.Column('team_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('paid', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['teams.team_id'], name='team_finances_ibfk_1'),
    sa.PrimaryKeyConstraint('team_id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('merchandise',
    sa.Column('merchandise_id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('product_name', mysql.VARCHAR(length=128), nullable=False),
    sa.Column('product_description', mysql.VARCHAR(length=256), nullable=False),
    sa.Column('price', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('merchandise_id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.drop_index(op.f('ix_payment_info_partial_refund'), table_name='payment_info')
    op.drop_index(op.f('ix_payment_info_full_refund'), table_name='payment_info')
    op.drop_index(op.f('ix_payment_info_entry_paid'), table_name='payment_info')
    op.drop_table('payment_info')
    op.drop_table('system_configuration')
    op.drop_table('super_volunteer')
    op.drop_table('raffle_configuration')
    op.drop_table('not_selected_contestant')
    op.drop_table('attended_previous_tournament_contestant')
    # ### end Alembic commands ###
    op.alter_column('contestant_info', 'student', existing_type=sa.String(length=128), type_=sa.Boolean)
