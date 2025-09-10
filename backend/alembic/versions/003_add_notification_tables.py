"""Add notification tables

Revision ID: 003_add_notification_tables
Revises: 002_add_task_tables
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_notification_tables'
down_revision = '002_add_task_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create notification_type enum
    notification_type_enum = postgresql.ENUM(
        'task_reminder', 'due_date_alert', 'task_completed', 
        'welcome', 'category_created', 'file_uploaded',
        name='notificationtype'
    )
    notification_type_enum.create(op.get_bind())

    # Create notification_status enum
    notification_status_enum = postgresql.ENUM(
        'pending', 'sent', 'failed', 'bounced',
        name='notificationstatus'
    )
    notification_status_enum.create(op.get_bind())

    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', notification_type_enum, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', notification_status_enum, nullable=False),
        sa.Column('email_sent', sa.Boolean(), nullable=True),
        sa.Column('email_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)

    # Create notification_preferences table
    op.create_table('notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email_enabled', sa.Boolean(), nullable=False),
        sa.Column('task_reminders', sa.Boolean(), nullable=False),
        sa.Column('due_date_alerts', sa.Boolean(), nullable=False),
        sa.Column('task_completed_notifications', sa.Boolean(), nullable=False),
        sa.Column('welcome_emails', sa.Boolean(), nullable=False),
        sa.Column('category_notifications', sa.Boolean(), nullable=False),
        sa.Column('file_notifications', sa.Boolean(), nullable=False),
        sa.Column('reminder_frequency', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_notification_preferences_id'), 'notification_preferences', ['id'], unique=False)

    # Create email_templates table
    op.create_table('email_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=False),
        sa.Column('text_content', sa.Text(), nullable=True),
        sa.Column('template_type', notification_type_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_email_templates_id'), 'email_templates', ['id'], unique=False)


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_email_templates_id'), table_name='email_templates')
    op.drop_table('email_templates')
    op.drop_index(op.f('ix_notification_preferences_id'), table_name='notification_preferences')
    op.drop_table('notification_preferences')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')

    # Drop enums
    op.execute('DROP TYPE notificationstatus')
    op.execute('DROP TYPE notificationtype')
