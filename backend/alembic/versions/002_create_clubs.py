"""Create clubs and club_members tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums if they don't exist
    conn = op.get_bind()
    
    # Check and create verification_status_enum
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'verification_status_enum')"
    ))
    if not result.scalar():
        conn.execute(sa.text(
            "CREATE TYPE verification_status_enum AS ENUM ('pending', 'verified', 'rejected')"
        ))
    
    # Check and create club_role_enum
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'club_role_enum')"
    ))
    if not result.scalar():
        conn.execute(sa.text(
            "CREATE TYPE club_role_enum AS ENUM ('owner', 'admin', 'manager', 'member', 'volunteer')"
        ))
    
    # Create clubs table
    op.create_table(
        'clubs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('banner_url', sa.String(length=500), nullable=True),
        sa.Column('address', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('verification_status', 
                  postgresql.ENUM('pending', 'verified', 'rejected', name='verification_status_enum', create_type=False),
                  nullable=False),
        sa.Column('verification_badge_date', sa.Date(), nullable=True),
        sa.Column('verification_notes', sa.String(length=1000), nullable=True),
        sa.Column('founded_date', sa.Date(), nullable=True),
        sa.Column('member_count', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for clubs
    op.create_index(op.f('ix_clubs_id'), 'clubs', ['id'], unique=False)
    op.create_index(op.f('ix_clubs_name'), 'clubs', ['name'], unique=True)
    op.create_index(op.f('ix_clubs_slug'), 'clubs', ['slug'], unique=True)
    
    # Create club_members table
    op.create_table(
        'club_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('club_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role',
                  postgresql.ENUM('owner', 'admin', 'manager', 'member', 'volunteer', name='club_role_enum', create_type=False),
                  nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for club_members
    op.create_index(op.f('ix_club_members_id'), 'club_members', ['id'], unique=False)
    op.create_index(op.f('ix_club_members_club_id'), 'club_members', ['club_id'], unique=False)
    op.create_index(op.f('ix_club_members_user_id'), 'club_members', ['user_id'], unique=False)
    
    # Create unique constraint for user-club combination
    op.create_unique_constraint(
        'uq_club_members_club_user',
        'club_members',
        ['club_id', 'user_id']
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_club_members_user_id'), table_name='club_members')
    op.drop_index(op.f('ix_club_members_club_id'), table_name='club_members')
    op.drop_index(op.f('ix_club_members_id'), table_name='club_members')
    
    op.drop_constraint('uq_club_members_club_user', 'club_members', type_='unique')
    
    # Drop tables
    op.drop_table('club_members')
    
    op.drop_index(op.f('ix_clubs_slug'), table_name='clubs')
    op.drop_index(op.f('ix_clubs_name'), table_name='clubs')
    op.drop_index(op.f('ix_clubs_id'), table_name='clubs')
    
    op.drop_table('clubs')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS club_role_enum')
    op.execute('DROP TYPE IF EXISTS verification_status_enum')
