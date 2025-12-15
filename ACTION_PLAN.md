# DataDog Platform - Critical Action Plan

**Date**: November 4, 2025  
**Status**: 🔴 IMMEDIATE ACTION REQUIRED  
**Production Readiness**: 30%

---

## 🚨 Critical Findings Summary

The DataDog platform has **excellent architecture and documentation** but is **NOT production-ready**. Critical infrastructure components are missing or mocked.

**Overall Grade**: B+ (85/100) for architecture  
**Production Readiness**: 30% (3-4 months to production)

### Critical Gaps
1. ❌ No metadata persistence (PostgreSQL not implemented)
2. ❌ No state management (Redis not implemented)
3. ❌ No authentication (API is open to all)
4. ❌ Connectors return mock data (not functional)
5. ❌ Minimal test coverage (~40-50%, need 80%)

---

## 📋 Sprint 1: Critical Foundation (Week 1-2)

### Priority 1: Metadata Persistence ⚡ CRITICAL
**Issue**: All pipeline definitions and execution history lost on restart

**Action Items**:
```sql
-- Create metadata database schema
CREATE DATABASE datadog_metadata;

CREATE TABLE pipelines (
    pipeline_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    definition JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255),
    enabled BOOLEAN DEFAULT true,
    schedule VARCHAR(255),
    tags JSONB
);

CREATE TABLE executions (
    execution_id UUID PRIMARY KEY,
    pipeline_id UUID REFERENCES pipelines(pipeline_id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,
    parameters JSONB,
    metrics JSONB,
    error TEXT,
    INDEX idx_pipeline_status (pipeline_id, status),
    INDEX idx_started_at (started_at)
);

CREATE TABLE tasks (
    task_id UUID PRIMARY KEY,
    execution_id UUID REFERENCES executions(execution_id) ON DELETE CASCADE,
    task_name VARCHAR(255) NOT NULL,
    task_type VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    error TEXT,
    INDEX idx_execution_status (execution_id, status)
);
```

**Code Implementation**:
```python
# src/datadog_platform/storage/metadata_store.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class MetadataStore:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=False)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def save_pipeline(self, pipeline: Pipeline) -> None:
        async with self.session_factory() as session:
            # Convert pipeline to ORM model
            db_pipeline = PipelineModel(
                pipeline_id=pipeline.pipeline_id,
                name=pipeline.name,
                definition=pipeline.model_dump(),
                created_at=pipeline.created_at,
            )
            session.add(db_pipeline)
            await session.commit()
    
    async def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        async with self.session_factory() as session:
            result = await session.get(PipelineModel, pipeline_id)
            if result:
                return Pipeline(**result.definition)
            return None
```

**Testing**:
```bash
# Add to tests/integration/test_metadata_store.py
pytest tests/integration/test_metadata_store.py -v
```

**Completion Criteria**:
- ✅ Database schema created
- ✅ SQLAlchemy models defined
- ✅ CRUD operations implemented
- ✅ Integration tests passing
- ✅ Data persists across restarts

---

### Priority 2: API Authentication ⚡ CRITICAL
**Issue**: Anyone can execute, delete, or modify pipelines

**Action Items**:

1. **Install dependencies**:
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

2. **Implement authentication**:
```python
# src/datadog_platform/api/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    user = await get_user_from_db(username)
    if user is None:
        raise credentials_exception
    return user
```

3. **Protect endpoints**:
```python
# src/datadog_platform/api/server.py
@app.post("/api/v1/pipelines/{id}/execute")
async def execute_pipeline(
    id: str,
    current_user: User = Depends(get_current_user)
):
    # User is now authenticated
    if not current_user.has_permission("pipeline.execute"):
        raise HTTPException(403, "Insufficient permissions")
    # ... execute pipeline
```

4. **Add login endpoint**:
```python
@app.post("/api/v1/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

**Testing**:
```python
# tests/security/test_authentication.py
async def test_unauthenticated_request_fails():
    response = await client.post("/api/v1/pipelines")
    assert response.status_code == 401

async def test_authenticated_request_succeeds():
    token = create_test_token()
    response = await client.post(
        "/api/v1/pipelines",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

**Completion Criteria**:
- ✅ JWT authentication implemented
- ✅ Login endpoint working
- ✅ All API endpoints protected
- ✅ Security tests passing
- ✅ Token expiration working

---

### Priority 3: Functional PostgreSQL Connector ⚡ CRITICAL
**Issue**: Connector returns mock data, not actual database queries

**Action Items**:

1. **Install asyncpg**:
```bash
pip install asyncpg
```

2. **Implement real connector**:
```python
# src/datadog_platform/connectors/postgresql_connector.py
import asyncpg
from typing import Any, Dict, List, Optional

class PostgreSQLConnector(BaseConnector):
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 5432)
        self.database = config.get("database")
        self.username = config.get("username")
        self.password = config.get("password")
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Create connection pool."""
        self._pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.username,
            password=self.password,
            min_size=5,
            max_size=20,
            command_timeout=30,
            timeout=10
        )
        logger.info(f"PostgreSQL pool created: {self.host}:{self.port}/{self.database}")
    
    async def disconnect(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("PostgreSQL pool closed")
    
    async def read(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results."""
        if not self._pool:
            raise RuntimeError("Not connected to database. Call connect() first.")
        
        # Build query if not provided
        if query is None:
            table = self.config.get("table")
            if not table:
                raise ValueError("Either 'query' or 'table' config must be provided")
            query = f"SELECT * FROM {table}"
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
        
        # Execute query
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    
    async def write(
        self,
        data: List[Dict[str, Any]],
        table: Optional[str] = None,
        if_exists: str = "append",
        **kwargs: Any
    ) -> None:
        """Write data to table."""
        if not self._pool:
            raise RuntimeError("Not connected to database")
        
        target_table = table or self.config.get("table")
        if not target_table:
            raise ValueError("No table specified")
        
        if not data:
            return
        
        # Use COPY for bulk insert (much faster)
        columns = list(data[0].keys())
        records = [tuple(row[col] for col in columns) for row in data]
        
        async with self._pool.acquire() as conn:
            await conn.copy_records_to_table(
                target_table,
                records=records,
                columns=columns
            )
            logger.info(f"Inserted {len(records)} rows into {target_table}")
    
    async def validate_connection(self) -> bool:
        """Test database connectivity."""
        try:
            if not self._pool:
                await self.connect()
            
            async with self._pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False
```

3. **Integration test with real database**:
```python
# tests/integration/test_postgresql_connector.py
import pytest
import asyncpg

@pytest.fixture
async def test_db():
    """Create test database."""
    conn = await asyncpg.connect(
        host="localhost",
        user="postgres",
        password="testpass",
        database="postgres"
    )
    await conn.execute("CREATE DATABASE test_datadog")
    await conn.close()
    
    yield
    
    conn = await asyncpg.connect(
        host="localhost",
        user="postgres",
        password="testpass",
        database="postgres"
    )
    await conn.execute("DROP DATABASE test_datadog")
    await conn.close()

@pytest.mark.asyncio
async def test_postgresql_read_write(test_db):
    connector = PostgreSQLConnector({
        "host": "localhost",
        "database": "test_datadog",
        "username": "postgres",
        "password": "testpass",
        "table": "test_table"
    })
    
    async with connector:
        # Create table
        await connector.execute_query("""
            CREATE TABLE test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                value INTEGER
            )
        """)
        
        # Write data
        data = [
            {"id": 1, "name": "Alice", "value": 100},
            {"id": 2, "name": "Bob", "value": 200}
        ]
        await connector.write(data, table="test_table")
        
        # Read data
        results = await connector.read("SELECT * FROM test_table ORDER BY id")
        assert len(results) == 2
        assert results[0]["name"] == "Alice"
        assert results[1]["value"] == 200
```

**Completion Criteria**:
- ✅ asyncpg integration working
- ✅ Connection pooling configured
- ✅ Read/write operations functional
- ✅ Integration tests with real database passing
- ✅ Error handling for connection failures

---

### Priority 4: Integration Tests ⚡ CRITICAL
**Issue**: Only unit tests exist, no end-to-end testing

**Action Items**:

1. **Create integration test structure**:
```bash
mkdir -p tests/integration
touch tests/integration/__init__.py
touch tests/integration/conftest.py
```

2. **Add test fixtures**:
```python
# tests/integration/conftest.py
import pytest
from datadog_platform.storage.metadata_store import MetadataStore
from datadog_platform.core.executor import LocalExecutor

@pytest.fixture
async def metadata_store():
    """Provide test metadata store."""
    store = MetadataStore("postgresql://postgres:test@localhost/test_datadog")
    yield store
    # Cleanup
    await store.cleanup()

@pytest.fixture
def executor():
    """Provide test executor."""
    return LocalExecutor(max_workers=2)
```

3. **Create end-to-end pipeline test**:
```python
# tests/integration/test_pipeline_execution.py
@pytest.mark.asyncio
async def test_complete_pipeline_execution(metadata_store, executor):
    """Test complete pipeline from creation to execution."""
    
    # 1. Create pipeline
    pipeline = Pipeline(
        name="test_etl_pipeline",
        description="Integration test pipeline"
    )
    
    # 2. Add data source
    source = DataSource(
        name="test_source",
        connector_type=ConnectorType.POSTGRESQL,
        config={
            "host": "localhost",
            "database": "test_db",
            "table": "source_table"
        }
    )
    pipeline.add_source(source)
    
    # 3. Add transformation
    transform = Transformation(
        name="filter_nulls",
        function="filter",
        params={"columns": ["email"]}
    )
    pipeline.add_transformation(transform)
    
    # 4. Save pipeline
    await metadata_store.save_pipeline(pipeline)
    
    # 5. Execute pipeline
    context = ExecutionContext(
        pipeline_id=pipeline.pipeline_id,
        parameters={}
    )
    result = await executor.execute_dag(pipeline.tasks, context)
    
    # 6. Verify execution
    assert context.status == ExecutionStatus.SUCCESS
    assert context.metrics["tasks_completed"] > 0
    
    # 7. Verify persistence
    saved_context = await metadata_store.get_execution(context.execution_id)
    assert saved_context.status == ExecutionStatus.SUCCESS
```

4. **Add API integration test**:
```python
# tests/integration/test_api_workflows.py
@pytest.mark.asyncio
async def test_api_pipeline_workflow():
    """Test complete workflow through API."""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Login
        response = await client.post("/api/v1/auth/token", data={
            "username": "test_user",
            "password": "test_pass"
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create pipeline
        pipeline_data = {
            "name": "api_test_pipeline",
            "sources": [...],
            "transformations": [...]
        }
        response = await client.post(
            "/api/v1/pipelines",
            json=pipeline_data,
            headers=headers
        )
        assert response.status_code == 201
        pipeline_id = response.json()["pipeline_id"]
        
        # 3. Execute pipeline
        response = await client.post(
            f"/api/v1/pipelines/{pipeline_id}/execute",
            headers=headers
        )
        assert response.status_code == 200
        execution_id = response.json()["execution_id"]
        
        # 4. Check status
        response = await client.get(
            f"/api/v1/executions/{execution_id}/status",
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["status"] in ["running", "success"]
```

**Completion Criteria**:
- ✅ Integration test infrastructure set up
- ✅ Pipeline execution tests passing
- ✅ API workflow tests passing
- ✅ Database integration tests passing
- ✅ Test coverage > 60%

---

### Priority 5: Fix CORS Security 🔒 HIGH
**Issue**: CORS allows all origins, enabling CSRF attacks

**Action Items**:

```python
# src/datadog_platform/api/server.py
from fastapi.middleware.cors import CORSMiddleware
import os

# Get allowed origins from environment
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8080"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)
```

**Environment configuration**:
```bash
# .env
ALLOWED_ORIGINS=https://datadog.example.com,https://app.example.com
```

**Completion Criteria**:
- ✅ CORS restricted to whitelist
- ✅ Environment-based configuration
- ✅ Security test validates restriction

---

## 📋 Sprint 2: Production Essentials (Week 3-4)

### State Management (Redis)
```python
# src/datadog_platform/storage/state_store.py
import redis.asyncio as redis

class RedisStateStore:
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url)
    
    async def save_checkpoint(
        self,
        execution_id: str,
        task_id: str,
        data: Dict[str, Any]
    ) -> None:
        key = f"checkpoint:{execution_id}:{task_id}"
        await self.client.hset(key, mapping=data)
        await self.client.expire(key, 86400)  # 24h TTL
```

### Connection Pooling
- Add to all SQL connectors
- Configure min/max pool size
- Add connection timeout handling
- Monitor pool metrics

### Basic RBAC
```python
class Role(Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    OPERATOR = "operator"
    VIEWER = "viewer"

class Permission(Enum):
    PIPELINE_CREATE = "pipeline.create"
    PIPELINE_EXECUTE = "pipeline.execute"
    PIPELINE_DELETE = "pipeline.delete"
    PIPELINE_VIEW = "pipeline.view"
```

### Monitoring Setup
```python
# src/datadog_platform/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

pipeline_executions = Counter(
    'pipeline_executions_total',
    'Total pipeline executions',
    ['pipeline_id', 'status']
)

execution_duration = Histogram(
    'pipeline_execution_duration_seconds',
    'Pipeline execution duration',
    ['pipeline_id']
)
```

### Load Testing
```bash
# tests/performance/test_load.py
locust -f tests/performance/test_load.py --host=http://localhost:8000
```

---

## 📊 Success Metrics

### Week 1-2 Goals
- ✅ Metadata persists across restarts
- ✅ API requires authentication
- ✅ PostgreSQL connector functional
- ✅ 3+ integration tests passing
- ✅ CORS properly configured

### Week 3-4 Goals
- ✅ State saved to Redis
- ✅ Connection pools working
- ✅ RBAC with 3 roles
- ✅ Prometheus metrics exported
- ✅ Load test baseline established

### Success Criteria for Production (Month 3-4)
- ✅ 80% test coverage
- ✅ All critical paths tested end-to-end
- ✅ Monitoring dashboards deployed
- ✅ Disaster recovery tested
- ✅ Security audit passed
- ✅ Performance benchmarks met
- ✅ Documentation complete
- ✅ Production deployment successful

---

## 🚀 Quick Start Commands

```bash
# Setup development environment
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/unit -v
pytest tests/integration -v

# Start database
docker-compose up -d postgres redis

# Initialize database
python scripts/init_db.py

# Run server
datadog-server --reload

# Run tests with coverage
pytest --cov=datadog_platform --cov-report=html
```

---

## 📞 Support & Questions

**Review Document**: See `ARCHITECTURE_ANALYSIS_REPORT.md` for full details

**Priority Questions**:
1. Do we have budget for PostgreSQL RDS instance?
2. Which secret manager should we use (Vault, AWS Secrets Manager)?
3. What's the target production date?
4. Who will be the primary maintainers?

---

**Created**: November 4, 2025  
**Next Review**: November 18, 2025 (end of Sprint 1)  
**Status**: 🔴 ACTIVE - Immediate action required
