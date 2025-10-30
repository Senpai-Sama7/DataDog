# DataDog Platform Deployment Guide

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, RHEL 8+), macOS 10.15+
- **Python**: 3.10 or higher
- **Memory**: Minimum 4GB RAM, Recommended 16GB+ for production
- **CPU**: Minimum 2 cores, Recommended 8+ cores for production
- **Disk**: Minimum 20GB, Recommended 100GB+ for data storage

### Software Dependencies

- Docker 20.10+ (for containerized deployment)
- Kubernetes 1.24+ (for orchestrated deployment)
- PostgreSQL 13+ (for metadata store)
- Redis 6+ (for state management and queuing)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Senpai-Sama7/DataDog.git
cd DataDog
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Run Tests

```bash
pytest
```

### 5. Start Development Server

```bash
datadog-server
```

The API will be available at `http://localhost:8000`

## Docker Deployment

### Build Docker Image

```bash
docker build -t datadog-platform:latest .
```

### Run with Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: datadog
      POSTGRES_USER: datadog
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  datadog-api:
    image: datadog-platform:latest
    command: datadog-server
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://datadog:${DB_PASSWORD}@postgres:5432/datadog
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  datadog-worker:
    image: datadog-platform:latest
    command: datadog-worker
    environment:
      DATABASE_URL: postgresql://datadog:${DB_PASSWORD}@postgres:5432/datadog
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 3

volumes:
  postgres_data:
  redis_data:
```

Start the services:

```bash
docker-compose up -d
```

## Kubernetes Deployment

### Prerequisites

- kubectl configured with cluster access
- Helm 3+ installed

### 1. Create Namespace

```bash
kubectl create namespace datadog-platform
```

### 2. Deploy PostgreSQL

```bash
helm install postgres bitnami/postgresql \
  --namespace datadog-platform \
  --set auth.database=datadog \
  --set auth.username=datadog \
  --set auth.password=${DB_PASSWORD}
```

### 3. Deploy Redis

```bash
helm install redis bitnami/redis \
  --namespace datadog-platform \
  --set auth.password=${REDIS_PASSWORD}
```

### 4. Deploy DataDog Platform

Create `datadog-platform.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: datadog-api
  namespace: datadog-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: datadog-api
  template:
    metadata:
      labels:
        app: datadog-api
    spec:
      containers:
      - name: api
        image: datadog-platform:latest
        command: ["datadog-server"]
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: datadog-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: datadog-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: datadog-api
  namespace: datadog-platform
spec:
  selector:
    app: datadog-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: datadog-worker
  namespace: datadog-platform
spec:
  replicas: 5
  selector:
    matchLabels:
      app: datadog-worker
  template:
    metadata:
      labels:
        app: datadog-worker
    spec:
      containers:
      - name: worker
        image: datadog-platform:latest
        command: ["datadog-worker"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: datadog-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: datadog-secrets
              key: redis-url
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "4000m"
```

Deploy:

```bash
kubectl apply -f datadog-platform.yaml
```

### 5. Create Horizontal Pod Autoscaler

```bash
kubectl autoscale deployment datadog-worker \
  --namespace datadog-platform \
  --cpu-percent=70 \
  --min=3 \
  --max=20
```

## Cloud-Specific Deployment

### AWS (ECS/EKS)

1. **Setup ECR Repository**
```bash
aws ecr create-repository --repository-name datadog-platform
```

2. **Push Docker Image**
```bash
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URL}
docker tag datadog-platform:latest ${ECR_URL}/datadog-platform:latest
docker push ${ECR_URL}/datadog-platform:latest
```

3. **Deploy to EKS**
```bash
eksctl create cluster --name datadog-cluster --region us-east-1
# Follow Kubernetes deployment steps above
```

### GCP (GKE)

1. **Setup GCR Repository**
```bash
gcloud container images list-tags gcr.io/${PROJECT_ID}/datadog-platform
```

2. **Deploy to GKE**
```bash
gcloud container clusters create datadog-cluster --num-nodes=3
# Follow Kubernetes deployment steps above
```

### Azure (AKS)

1. **Setup ACR**
```bash
az acr create --resource-group myResourceGroup --name datadog --sku Basic
```

2. **Deploy to AKS**
```bash
az aks create --resource-group myResourceGroup --name datadog-cluster --node-count 3
# Follow Kubernetes deployment steps above
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/datadog
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# API Server
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Workers
WORKER_CONCURRENCY=4
WORKER_POOL=prefork

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
SECRET_KEY=${SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

### Configuration File

Create `config.yaml`:

```yaml
database:
  url: postgresql://user:pass@localhost:5432/datadog
  pool_size: 20
  max_overflow: 10

redis:
  url: redis://localhost:6379/0
  pool_size: 10

api:
  host: 0.0.0.0
  port: 8000
  workers: 4
  cors_origins:
    - http://localhost:3000
    - https://app.example.com

workers:
  concurrency: 4
  max_tasks_per_child: 1000

logging:
  level: INFO
  format: json
  handlers:
    - console
    - file

monitoring:
  enabled: true
  prometheus_port: 9090
  metrics_interval: 60

security:
  secret_key: ${SECRET_KEY}
  jwt_algorithm: HS256
  jwt_expiration: 3600
  rate_limiting:
    enabled: true
    requests_per_minute: 60
```

## Monitoring

### Prometheus Metrics

DataDog Platform exposes Prometheus metrics at `/metrics`:

- `datadog_pipelines_total` - Total number of pipelines
- `datadog_pipelines_active` - Active pipelines
- `datadog_executions_total` - Total executions
- `datadog_executions_duration_seconds` - Execution duration
- `datadog_tasks_total` - Total tasks executed
- `datadog_tasks_failed_total` - Failed tasks

### Grafana Dashboards

Import the provided Grafana dashboard from `config/grafana-dashboard.json`

### Alerting

Configure alerts in Prometheus:

```yaml
groups:
- name: datadog
  rules:
  - alert: HighFailureRate
    expr: rate(datadog_tasks_failed_total[5m]) > 0.1
    for: 10m
    annotations:
      summary: "High task failure rate"
```

## Backup and Recovery

### Database Backup

```bash
# Backup
pg_dump -h localhost -U datadog datadog > backup.sql

# Restore
psql -h localhost -U datadog datadog < backup.sql
```

### Redis Backup

```bash
# Backup
redis-cli SAVE
cp /var/lib/redis/dump.rdb backup/

# Restore
cp backup/dump.rdb /var/lib/redis/
redis-cli
> FLUSHALL
> SHUTDOWN
# Restart Redis
```

## Troubleshooting

### Common Issues

**Issue: API not starting**
- Check database connectivity
- Verify environment variables
- Check logs: `kubectl logs -f deployment/datadog-api`

**Issue: Workers not processing tasks**
- Verify Redis connectivity
- Check worker logs
- Ensure task queue is not blocked

**Issue: Slow performance**
- Scale up workers
- Increase database pool size
- Enable caching
- Check resource limits

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
datadog-server
```

## Security Best Practices

1. Use secrets management (AWS Secrets Manager, HashiCorp Vault)
2. Enable TLS for all network communication
3. Rotate credentials regularly
4. Use least privilege access
5. Enable audit logging
6. Implement rate limiting
7. Regular security updates

## Performance Tuning

1. **Database Optimization**
   - Index frequently queried columns
   - Tune connection pool size
   - Use read replicas for read-heavy workloads

2. **Redis Optimization**
   - Configure maxmemory policy
   - Use Redis cluster for scalability
   - Enable persistence for durability

3. **Worker Optimization**
   - Adjust concurrency based on workload
   - Use appropriate task timeout values
   - Enable task prioritization

## Support

For issues and questions:
- GitHub Issues: https://github.com/Senpai-Sama7/DataDog/issues
- Documentation: https://datadog-platform.readthedocs.io
- Community: https://github.com/Senpai-Sama7/DataDog/discussions
