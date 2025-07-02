"""
Add km_inicial column to DailyChecklist
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('daily_checklist', sa.Column('km_inicial', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('daily_checklist', 'km_inicial')
