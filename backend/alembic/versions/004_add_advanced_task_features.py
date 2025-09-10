"""Add advanced task features

Revision ID: 004_add_advanced_task_features
Revises: 003_add_notification_tables
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_advanced_task_features'
down_revision = '003_add_notification_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to tasks table
    op.add_column('tasks', sa.Column('parent_task_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('estimated_duration', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('actual_duration', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('tags', sa.JSON(), nullable=True))
    op.add_column('tasks', sa.Column('is_template', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tasks', sa.Column('template_name', sa.String(length=255), nullable=True))
    
    # Add foreign key constraint for parent_task_id
    op.create_foreign_key('fk_tasks_parent_task_id', 'tasks', 'tasks', ['parent_task_id'], ['id'])
    
    # Create task_dependencies table
    op.create_table('task_dependencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('depends_on_task_id', sa.Integer(), nullable=False),
        sa.Column('dependency_type', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['depends_on_task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_dependencies_id'), 'task_dependencies', ['id'], unique=False)
    
    # Create task_templates table
    op.create_table('task_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('priority', postgresql.ENUM('low', 'medium', 'high', 'urgent', name='taskpriority'), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('template_data', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_templates_id'), 'task_templates', ['id'], unique=False)


def downgrade():
    # Drop task_templates table
    op.drop_index(op.f('ix_task_templates_id'), table_name='task_templates')
    op.drop_table('task_templates')
    
    # Drop task_dependencies table
    op.drop_index(op.f('ix_task_dependencies_id'), table_name='task_dependencies')
    op.drop_table('task_dependencies')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_tasks_parent_task_id', 'tasks', type_='foreignkey')
    
    # Remove columns from tasks table
    op.drop_column('tasks', 'template_name')
    op.drop_column('tasks', 'is_template')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'actual_duration')
    op.drop_column('tasks', 'estimated_duration')
    op.drop_column('tasks', 'parent_task_id')
