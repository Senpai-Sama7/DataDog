
from pydantic import BaseModel


class PostgreSQLConfig(BaseModel):
    """Configuration for PostgreSQL database connection."""

    host: str = "localhost"
    port: int = 5433
    database: str = "datadog_metadata"
    user: str = "user"
    password: str = "mysecretpassword"
    min_size: int = 1
    max_size: int = 10
