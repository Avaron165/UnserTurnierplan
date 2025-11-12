"""create tournaments

Revision ID: 003_create_tournaments
Revises: 001_initial_migration
Create Date: 2025-11-12

Sprint 3: Tournament Management
- Creates tournaments table
- Creates tournament_participants table
- Creates all necessary enums
- Creates indexes for performance
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'  # Follows Sprint 2 migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Enums with checkfirst=True to avoid duplicates
    tournament_type_enum = postgresql.ENUM(
        'knockout', 'round_robin', 'group_stage', 'swiss', 'custom',
        name='tournament_type_enum',
        create_type=False
    )
    tournament_type_enum.create(op.get_bind(), checkfirst=True)

    tournament_status_enum = postgresql.ENUM(
        'draft', 'published', 'registration_open', 'active', 'completed', 'cancelled',
        name='tournament_status_enum',
        create_type=False
    )
    tournament_status_enum.create(op.get_bind(), checkfirst=True)

    sport_type_enum = postgresql.ENUM(
        'football', 'basketball', 'volleyball', 'handball', 'hockey',
        'tennis', 'table_tennis', 'badminton', 'esports', 'other',
        name='sport_type_enum',
        create_type=False
    )
    sport_type_enum.create(op.get_bind(), checkfirst=True)

    participant_type_enum = postgresql.ENUM(
        'team', 'individual',
        name='participant_type_enum',
        create_type=False
    )
    participant_type_enum.create(op.get_bind(), checkfirst=True)

    participant_status_enum = postgresql.ENUM(
        'pending', 'confirmed', 'cancelled', 'waitlist',
        name='participant_status_enum',
        create_type=False
    )
    participant_status_enum.create(op.get_bind(), checkfirst=True)

    payment_status_enum = postgresql.ENUM(
        'not_required', 'pending', 'paid', 'refunded',
        name='payment_status_enum',
        create_type=False
    )
    payment_status_enum.create(op.get_bind(), checkfirst=True)

    # Create tournaments table
    op.create_table(
        'tournaments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),

        # Foreign Keys
        sa.Column('club_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Basic Information
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('banner_url', sa.String(length=500), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),

        # Tournament Classification
        sa.Column('sport_type', sport_type_enum, nullable=False, server_default='football'),
        sa.Column('tournament_type', tournament_type_enum, nullable=False, server_default='knockout'),

        # Status Management
        sa.Column('status', tournament_status_enum, nullable=False, server_default='draft'),

        # Dates & Times
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('registration_start', sa.DateTime(), nullable=True),
        sa.Column('registration_end', sa.DateTime(), nullable=True),

        # Location
        sa.Column('location', sa.String(length=300), nullable=True),
        sa.Column('venue_name', sa.String(length=200), nullable=True),
        sa.Column('address', sa.String(length=300), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=False, server_default='DE'),

        # Participant Settings
        sa.Column('participant_type', participant_type_enum, nullable=False, server_default='team'),
        sa.Column('min_participants', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('max_participants', sa.Integer(), nullable=False),
        sa.Column('current_participants', sa.Integer(), nullable=False, server_default='0'),

        # Tournament Details
        sa.Column('rules', sa.Text(), nullable=True),
        sa.Column('prize_info', sa.Text(), nullable=True),
        sa.Column('entry_fee', sa.Numeric(precision=10, scale=2), nullable=True),

        # Visibility & Access
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),

        # Contact Information
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('slug'),
    )

    # Create indexes for tournaments
    op.create_index('idx_tournament_club_status', 'tournaments', ['club_id', 'status'])
    op.create_index('idx_tournament_sport_status', 'tournaments', ['sport_type', 'status'])
    op.create_index('idx_tournament_dates', 'tournaments', ['start_date', 'end_date'])
    op.create_index('idx_tournament_registration', 'tournaments', ['registration_start', 'registration_end'])
    op.create_index('idx_tournament_slug', 'tournaments', ['slug'])
    op.create_index('idx_tournament_department', 'tournaments', ['department'])
    op.create_index('idx_tournament_created_by', 'tournaments', ['created_by'])

    # Create tournament_participants table
    op.create_table(
        'tournament_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),

        # Foreign Keys
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('participant_club_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('participant_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('registered_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Participant Information
        sa.Column('participant_name', sa.String(length=200), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=True),

        # Contact Information
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),

        # Registration Details
        sa.Column('registration_date', sa.DateTime(), nullable=False),

        # Status Management
        sa.Column('status', participant_status_enum, nullable=False, server_default='pending'),

        # Payment Management
        sa.Column('payment_status', payment_status_enum, nullable=False, server_default='not_required'),
        sa.Column('payment_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
        sa.Column('payment_reference', sa.String(length=100), nullable=True),

        # Tournament Seeding
        sa.Column('seed', sa.Integer(), nullable=True),

        # Additional Information
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('player_list', sa.Text(), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_club_id'], ['clubs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['registered_by'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('tournament_id', 'participant_club_id', name='uq_tournament_club_participant'),
        sa.UniqueConstraint('tournament_id', 'participant_user_id', name='uq_tournament_user_participant'),
    )

    # Create indexes for tournament_participants
    op.create_index('idx_participant_tournament', 'tournament_participants', ['tournament_id'])
    op.create_index('idx_participant_tournament_status', 'tournament_participants', ['tournament_id', 'status'])
    op.create_index('idx_participant_seed', 'tournament_participants', ['tournament_id', 'seed'])
    op.create_index('idx_participant_club', 'tournament_participants', ['participant_club_id'])
    op.create_index('idx_participant_user', 'tournament_participants', ['participant_user_id'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_participant_user', table_name='tournament_participants')
    op.drop_index('idx_participant_club', table_name='tournament_participants')
    op.drop_index('idx_participant_seed', table_name='tournament_participants')
    op.drop_index('idx_participant_tournament_status', table_name='tournament_participants')
    op.drop_index('idx_participant_tournament', table_name='tournament_participants')

    op.drop_index('idx_tournament_created_by', table_name='tournaments')
    op.drop_index('idx_tournament_department', table_name='tournaments')
    op.drop_index('idx_tournament_slug', table_name='tournaments')
    op.drop_index('idx_tournament_registration', table_name='tournaments')
    op.drop_index('idx_tournament_dates', table_name='tournaments')
    op.drop_index('idx_tournament_sport_status', table_name='tournaments')
    op.drop_index('idx_tournament_club_status', table_name='tournaments')

    # Drop tables
    op.drop_table('tournament_participants')
    op.drop_table('tournaments')

    # Drop enums
    sa.Enum(name='payment_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='participant_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='participant_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='sport_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='tournament_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='tournament_type_enum').drop(op.get_bind(), checkfirst=True)