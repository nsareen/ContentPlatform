"""
Migration script for brand voice generator feature.

This script adds a 'source_content' field to the BrandVoice model to store the original content
used to generate the brand voice profile.
"""

from sqlalchemy import Column, String, Text, JSON
from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = '2025_05_24_brand_voice_generator'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade database schema for brand voice generator feature."""
    # Add source_content column to brand_voices table
    op.add_column('brand_voices', sa.Column('source_content', sa.Text(), nullable=True))
    
    # Add source_content column to brand_voice_versions table to maintain version history
    op.add_column('brand_voice_versions', sa.Column('source_content', sa.Text(), nullable=True))
    
    # Add generation_metadata column to brand_voices table
    op.add_column('brand_voices', sa.Column('generation_metadata', sa.JSON(), nullable=True))
    
    # Add generation_metadata column to brand_voice_versions table
    op.add_column('brand_voice_versions', sa.Column('generation_metadata', sa.JSON(), nullable=True))

def downgrade():
    """Downgrade database schema (remove added columns)."""
    # Remove source_content column from brand_voices table
    op.drop_column('brand_voices', 'source_content')
    
    # Remove source_content column from brand_voice_versions table
    op.drop_column('brand_voice_versions', 'source_content')
    
    # Remove generation_metadata column from brand_voices table
    op.drop_column('brand_voices', 'generation_metadata')
    
    # Remove generation_metadata column from brand_voice_versions table
    op.drop_column('brand_voice_versions', 'generation_metadata')
