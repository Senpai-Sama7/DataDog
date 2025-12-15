
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    String,
    Text,
    Integer,
    create_engine,
)
from sqlalchemy.orm import declarative_base

from datadog_platform.core.base import (
    ConnectorType,
    ExecutionStatus,
    ProcessingMode,
)

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/datadog_metadata")

Base = declarative_base()


class PipelineModel(Base):
    __tablename__ = "pipelines"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    processing_mode = Column(Enum(ProcessingMode), nullable=False)
    schedule = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = Column(JSON, default={})
    metadata_ = Column(JSON, default={}, name="metadata")  # Use metadata_ to avoid conflict with metadata attribute

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "processing_mode": self.processing_mode.value,
            "schedule": self.schedule,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata_,
        }


class DataSourceModel(Base):
    __tablename__ = "data_sources"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    pipeline_id = Column(String, nullable=False)  # Foreign key to Pipeline
    name = Column(String, nullable=False)
    connector_type = Column(Enum(ConnectorType), nullable=False)
    connection_config = Column(JSON, default={})
    query = Column(Text, nullable=True)
    schema_ = Column(JSON, default={}, name="schema")  # Use schema_ to avoid conflict
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "connector_type": self.connector_type.value,
            "connection_config": self.connection_config,
            "query": self.query,
            "schema": self.schema_,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class TransformationModel(Base):
    __tablename__ = "transformations"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    pipeline_id = Column(String, nullable=False)  # Foreign key to Pipeline
    name = Column(String, nullable=False)
    function_name = Column(String, nullable=False)
    parameters = Column(JSON, default={})
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "function_name": self.function_name,
            "parameters": self.parameters,
            "order": self.order,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ExecutionContextModel(Base):
    __tablename__ = "execution_contexts"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    pipeline_id = Column(String, nullable=False)  # Foreign key to Pipeline
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(Enum(ExecutionStatus), nullable=False)
    parameters = Column(JSON, default={})
    metrics = Column(JSON, default={})
    error = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "pipeline_id": self.pipeline_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "status": self.status.value,
            "parameters": self.parameters,
            "metrics": self.metrics,
            "error": self.error,
        }


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    execution_id = Column(String, nullable=False)  # Foreign key to ExecutionContext
    task_name = Column(String, nullable=False)
    task_type = Column(String, nullable=False)
    status = Column(Enum(ExecutionStatus), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    input_data = Column(JSON, default={})
    output_data = Column(JSON, default={})

    def to_dict(self):
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "task_name": self.task_name,
            "task_type": self.task_type,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "error": self.error,
            "input_data": self.input_data,
            "output_data": self.output_data,
        }


class DataLineageModel(Base):
    __tablename__ = "data_lineage"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    pipeline_id = Column(String, nullable=False)  # Foreign key to Pipeline
    execution_id = Column(String, nullable=False)  # Foreign key to ExecutionContext
    source_id = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    destination_id = Column(String, nullable=False)
    destination_type = Column(String, nullable=False)
    data_flow = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "pipeline_id": self.pipeline_id,
            "execution_id": self.execution_id,
            "source_id": self.source_id,
            "source_type": self.source_type,
            "destination_id": self.destination_id,
            "destination_type": self.destination_type,
            "data_flow": self.data_flow,
            "created_at": self.created_at.isoformat(),
        }
