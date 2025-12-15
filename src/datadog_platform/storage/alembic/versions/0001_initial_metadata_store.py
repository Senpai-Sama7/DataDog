"""Initial migration for DataDog metadata store.

Revision ID: 0001_initial_metadata_store
Revises: 
Create Date: 2023-11-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '0001_initial_metadata_store'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create pipelines table
    op.create_table(
        'pipelines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('definition', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create executions table
    op.create_table(
        'executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pipeline_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('execution_id', sa.String(length=255), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('parameters', postgresql.JSONB(), nullable=True),
        sa.Column('metrics', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('execution_id')
    )
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('execution_id', sa.String(length=255), nullable=False),
        sa.Column('task_name', sa.String(length=255), nullable=False),
        sa.Column('task_type', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('input_data', postgresql.JSONB(), nullable=True),
        sa.Column('output_data', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.execution_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create data_lineage table
    op.create_table(
        'data_lineage',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_id', sa.String(length=255), nullable=True),
        sa.Column('source_type', sa.String(length=100), nullable=True),
        sa.Column('destination_id', sa.String(length=255), nullable=True),
        sa.Column('destination_type', sa.String(length=100), nullable=True),
        sa.Column('pipeline_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('execution_id', sa.String(length=255), nullable=True),
        sa.Column('data_flow', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.execution_id'], ),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_executions_pipeline_id', 'executions', ['pipeline_id'])
    op.create_index('ix_executions_status', 'executions', ['status'])
    op.create_index('ix_executions_started_at', 'executions', ['started_at'])
    op.create_index('ix_tasks_execution_id', 'tasks', ['execution_id'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_data_lineage_pipeline_id', 'data_lineage', ['pipeline_id'])
    op.create_index('ix_data_lineage_execution_id', 'data_lineage', ['execution_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_data_lineage_execution_id', table_name='data_lineage')
    op.drop_index('ix_data_lineage_pipeline_id', table_name='data_lineage')
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_index('ix_tasks_execution_id', table_name='tasks')
    op.drop_index('ix_executions_started_at', table_name='executions')
    op.drop_index('ix_executions_status', table_name='executions')
    op.drop_index('ix_executions_pipeline_id', table_name='executions')
    
    # Drop tables
    op.drop_table('data_lineage')
    op.drop_table('tasks')
    op.drop_table('executions')
    op.drop_table('pipelines')