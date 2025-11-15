"""create matches

Revision ID: 004
Revises: 003
Create Date: 2025-11-15

Sprint 4: Match Scheduling & Brackets
- Creates matches table
- Creates match_participants junction table  
- Creates tournament_standings table
- Adds format_rules to tournaments
- Adds group_assignment to tournament_participants
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create match_status enum
    match_status_enum = postgresql.ENUM(
        'scheduled', 'in_progress', 'completed', 'cancelled', 'postponed', 'walkover',
        name='match_status_enum',
        create_type=False
    )
    match_status_enum.create(op.get_bind(), checkfirst=True)
    
    # ==================== CREATE MATCHES TABLE ====================
    
    op.create_table(
        'matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Foreign Keys
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Match Organization
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('match_number', sa.Integer(), nullable=False),
        sa.Column('round_name', sa.String(100)),
        sa.Column('group_name', sa.String(50)),
        sa.Column('phase', sa.String(50)),  # "group_stage", "knockout", "qualifying", "final"
        
        # Scheduling
        sa.Column('scheduled_start', sa.DateTime()),
        sa.Column('scheduled_end', sa.DateTime()),
        sa.Column('actual_start', sa.DateTime()),
        sa.Column('actual_end', sa.DateTime()),
        
        # Location
        sa.Column('venue_name', sa.String(200)),
        sa.Column('court_field_number', sa.String(50)),
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, server_default='scheduled'),
        
        # Match Configuration
        sa.Column('match_format', sa.String(50)),
        sa.Column('duration_minutes', sa.Integer()),
        
        # Results
        sa.Column('is_finished', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('winner_participant_id', postgresql.UUID(as_uuid=True)),
        
        # Flexible Scoring (JSONB)
        sa.Column('score_data', postgresql.JSONB()),
        
        # Metadata
        sa.Column('notes', sa.Text()),
        sa.Column('is_bye', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('requires_referee', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('referee_user_id', postgresql.UUID(as_uuid=True)),
        
        # Bracket Dependencies
        sa.Column('dependent_on_match_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('feeds_into_match_id', postgresql.UUID(as_uuid=True)),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['winner_participant_id'], ['tournament_participants.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['referee_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['feeds_into_match_id'], ['matches.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('tournament_id', 'round_number', 'match_number', name='uq_match_tournament_round')
    )
    
    # Create indexes for matches
    op.create_index('idx_match_tournament', 'matches', ['tournament_id'])
    op.create_index('idx_match_tournament_round', 'matches', ['tournament_id', 'round_number'])
    op.create_index('idx_match_tournament_status', 'matches', ['tournament_id', 'status'])
    op.create_index('idx_match_schedule', 'matches', ['scheduled_start', 'scheduled_end'])
    op.create_index('idx_match_venue', 'matches', ['tournament_id', 'venue_name', 'court_field_number'])
    
    # ==================== CREATE MATCH_PARTICIPANTS TABLE ====================
    
    op.create_table(
        'match_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Foreign Keys
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Position in Match
        sa.Column('slot_number', sa.Integer(), nullable=False),
        sa.Column('team_side', sa.String(20)),  # "home", "away", NULL
        
        # Individual Results
        sa.Column('final_position', sa.Integer()),  # 1st, 2nd, 3rd (for races)
        sa.Column('score_value', sa.Numeric(10, 3)),
        sa.Column('result_time', postgresql.INTERVAL()),
        sa.Column('is_winner', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_disqualified', sa.Boolean(), nullable=False, server_default='false'),
        
        # Detailed scoring (JSONB)
        sa.Column('detailed_score', postgresql.JSONB()),
        sa.Column('notes', sa.Text()),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['tournament_participants.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('match_id', 'participant_id', name='uq_match_participant')
    )
    
    # Create indexes for match_participants
    op.create_index('idx_match_participants_match', 'match_participants', ['match_id'])
    op.create_index('idx_match_participants_participant', 'match_participants', ['participant_id'])
    
    # ==================== CREATE TOURNAMENT_STANDINGS TABLE ====================
    
    op.create_table(
        'tournament_standings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Foreign Keys
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Group (for group stage tournaments)
        sa.Column('group_name', sa.String(50)),
        
        # Match Statistics
        sa.Column('matches_played', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('matches_won', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('matches_drawn', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('matches_lost', sa.Integer(), nullable=False, server_default='0'),
        
        # Scoring
        sa.Column('points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('score_for', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('score_against', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('score_difference', sa.Numeric(10, 2), nullable=False, server_default='0'),
        
        # Rankings
        sa.Column('current_rank', sa.Integer()),
        sa.Column('previous_rank', sa.Integer()),
        
        # Additional stats (JSONB)
        sa.Column('additional_stats', postgresql.JSONB()),
        sa.Column('recent_form', sa.String(20)),  # "WWDLL"
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['tournament_participants.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('tournament_id', 'participant_id', 'group_name', name='uq_tournament_standings')
    )
    
    # Create indexes for tournament_standings
    op.create_index('idx_standings_tournament', 'tournament_standings', ['tournament_id'])
    op.create_index('idx_standings_tournament_group', 'tournament_standings', ['tournament_id', 'group_name'])
    op.create_index('idx_standings_rank', 'tournament_standings', ['tournament_id', 'current_rank'])
    
    # ==================== UPDATE EXISTING TABLES ====================
    
    # Add format_rules to tournaments
    op.add_column('tournaments', sa.Column('format_rules', postgresql.JSONB(), nullable=True))
    
    # Add group_assignment to tournament_participants
    op.add_column('tournament_participants', sa.Column('group_assignment', sa.String(50), nullable=True))
    op.create_index('idx_participant_group', 'tournament_participants', ['tournament_id', 'group_assignment'])


def downgrade() -> None:
    # Drop indexes and columns from updated tables
    op.drop_index('idx_participant_group', table_name='tournament_participants')
    op.drop_column('tournament_participants', 'group_assignment')
    op.drop_column('tournaments', 'format_rules')
    
    # Drop tournament_standings table and indexes
    op.drop_index('idx_standings_rank', table_name='tournament_standings')
    op.drop_index('idx_standings_tournament_group', table_name='tournament_standings')
    op.drop_index('idx_standings_tournament', table_name='tournament_standings')
    op.drop_table('tournament_standings')
    
    # Drop match_participants table and indexes
    op.drop_index('idx_match_participants_participant', table_name='match_participants')
    op.drop_index('idx_match_participants_match', table_name='match_participants')
    op.drop_table('match_participants')
    
    # Drop matches table and indexes
    op.drop_index('idx_match_venue', table_name='matches')
    op.drop_index('idx_match_schedule', table_name='matches')
    op.drop_index('idx_match_tournament_status', table_name='matches')
    op.drop_index('idx_match_tournament_round', table_name='matches')
    op.drop_index('idx_match_tournament', table_name='matches')
    op.drop_table('matches')
    
    # Drop enums
    sa.Enum(name='match_status_enum').drop(op.get_bind(), checkfirst=True)
