"""Add brand_voice_versions table

Revision ID: 22ee309eff1d
Revises: 11ee309eff1d
Create Date: 2025-05-20 06:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22ee309eff1d'
down_revision = '11ee309eff1d'
branch_labels = None
depends_on = None


def upgrade():
    # Check if brand_voice_versions table already exists
    from sqlalchemy import inspect
    from sqlalchemy.sql import text
    from sqlalchemy import create_engine
    import os
    
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./sql_app.db')
    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    if 'brand_voice_versions' not in inspector.get_table_names():
        # Create brand_voice_versions table if it doesn't exist
        print("Creating brand_voice_versions table")
        op.create_table('brand_voice_versions',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('brand_voice_id', sa.String(), nullable=False),
            sa.Column('version_number', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('voice_metadata', sa.JSON(), nullable=True),
            sa.Column('dos', sa.Text(), nullable=True),
            sa.Column('donts', sa.Text(), nullable=True),
            sa.Column('status', sa.Enum('DRAFT', 'PUBLISHED', 'UNDER_REVIEW', 'INACTIVE', name='brandvoicestatus'), nullable=False),
            sa.Column('created_by_id', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['brand_voice_id'], ['brand_voices.id'], ),
            sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        # Check if published_at column exists
        conn = engine.connect()
        columns = [col['name'] for col in inspector.get_columns('brand_voice_versions')]
        if 'published_at' not in columns:
            print("Adding published_at column to brand_voice_versions table")
            op.add_column('brand_voice_versions', sa.Column('published_at', sa.DateTime(timezone=True), nullable=True))
        conn.close()


def downgrade():
    # Drop brand_voice_versions table
    op.drop_table('brand_voice_versions')
