"""
Unit tests for data sources.
"""

import pytest

from datadog_platform.core.data_source import DataSource
from datadog_platform.core.base import ConnectorType


class TestDataSource:
    """Test cases for DataSource class."""
    
    def test_data_source_creation(self) -> None:
        """Test creating a data source."""
        source = DataSource(
            name="test_source",
            connector_type=ConnectorType.POSTGRESQL,
            connection_config={
                "host": "localhost",
                "database": "testdb",
                "username": "user",
                "password": "pass"
            }
        )
        
        assert source.name == "test_source"
        assert source.connector_type == ConnectorType.POSTGRESQL
        assert source.source_id is not None
        assert source.enabled is True
    
    def test_validate_config_valid(self) -> None:
        """Test validation with valid config."""
        source = DataSource(
            name="valid_source",
            connector_type=ConnectorType.POSTGRESQL,
            connection_config={
                "host": "localhost",
                "database": "testdb"
            }
        )
        
        assert source.validate_config() is True
    
    def test_validate_config_missing_required_fields(self) -> None:
        """Test validation with missing required fields."""
        source = DataSource(
            name="invalid_source",
            connector_type=ConnectorType.POSTGRESQL,
            connection_config={"host": "localhost"}  # Missing database
        )
        
        assert source.validate_config() is False
    
    def test_validate_config_no_name(self) -> None:
        """Test validation with no name."""
        source = DataSource(
            name="",
            connector_type=ConnectorType.POSTGRESQL,
            connection_config={"host": "localhost", "database": "db"}
        )
        
        assert source.validate_config() is False
    
    def test_to_connector_config(self) -> None:
        """Test converting to connector config."""
        source = DataSource(
            name="test_source",
            connector_type=ConnectorType.POSTGRESQL,
            connection_config={"host": "localhost", "database": "testdb"}
        )
        
        config = source.to_connector_config()
        
        assert config["type"] == ConnectorType.POSTGRESQL
        assert config["name"] == "test_source"
        assert "config" in config
        assert config["config"]["host"] == "localhost"
    
    def test_different_connector_types(self) -> None:
        """Test various connector types."""
        # PostgreSQL
        pg_source = DataSource(
            name="pg",
            connector_type=ConnectorType.POSTGRESQL,
            connection_config={"host": "localhost", "database": "db"}
        )
        assert pg_source.validate_config() is True
        
        # MongoDB
        mongo_source = DataSource(
            name="mongo",
            connector_type=ConnectorType.MONGODB,
            connection_config={"host": "localhost", "database": "db"}
        )
        assert mongo_source.validate_config() is True
        
        # S3
        s3_source = DataSource(
            name="s3",
            connector_type=ConnectorType.S3,
            connection_config={"bucket": "my-bucket"}
        )
        assert s3_source.validate_config() is True
        
        # REST API
        api_source = DataSource(
            name="api",
            connector_type=ConnectorType.REST_API,
            connection_config={"url": "https://api.example.com"}
        )
        assert api_source.validate_config() is True
    
    def test_schema_and_query(self) -> None:
        """Test data source with schema and query."""
        source = DataSource(
            name="test_source",
            connector_type=ConnectorType.POSTGRESQL,
            connection_config={"host": "localhost", "database": "db"},
            schema={
                "columns": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"}
                ]
            },
            query="SELECT * FROM users WHERE active = true"
        )
        
        assert source.schema is not None
        assert source.query is not None
        assert "SELECT" in source.query
