# Production Deployment Guide

## Overview

This guide covers deploying the PROACTIVA AI Simulation platform to production environments.

## Architecture

### Components
- **Frontend** - React application served by Nginx
- **Backend** - FastAPI application with Uvicorn
- **Database** - PostgreSQL with TimescaleDB extension
- **Cache** - Redis for session management and caching
- **Message Queue** - Celery with Redis for background tasks
- **Monitoring** - Prometheus and Grafana for metrics

### Infrastructure Requirements

#### Minimum Requirements
- **CPU:** 4 cores
- **RAM:** 8GB
- **Storage:** 50GB SSD
- **Network:** 100 Mbps

#### Recommended Requirements
- **CPU:** 8 cores
- **RAM:** 16GB
- **Storage:** 100GB SSD
- **Network:** 1 Gbps

#### Large Scale Requirements
- **CPU:** 16+ cores
- **RAM:** 32GB+
- **Storage:** 200GB+ SSD
- **Network:** 10 Gbps

## Docker Deployment

### Docker Compose Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    depends_on:
      - database
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@database:5432/proactiva
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Database
  database:
    image: timescale/timescaledb:latest-pg14
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=proactiva
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Background Workers
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - database
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@database:5432/proactiva
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### Backend Dockerfile

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile.prod`:

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

## Environment Configuration

### Backend Environment Variables

Create `.env.prod`:

```bash
# Database
DATABASE_URL=postgresql://user:password@database:5432/proactiva
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://redis:6379
REDIS_POOL_SIZE=10

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=false

# Simulation Settings
MAX_CONCURRENT_SIMULATIONS=10
MAX_SIMULATION_DURATION=7200
SIMULATION_CLEANUP_INTERVAL=300

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
LOG_LEVEL=INFO
LOG_FORMAT=json

# External Services
OPENAI_API_KEY=your-openai-key
SENTRY_DSN=your-sentry-dsn
```

### Frontend Environment Variables

Create `frontend/.env.prod`:

```bash
REACT_APP_API_URL=https://api.proactiva.example.com
REACT_APP_WS_URL=wss://api.proactiva.example.com
REACT_APP_ENVIRONMENT=production
REACT_APP_SENTRY_DSN=your-sentry-dsn
REACT_APP_ANALYTICS_ID=your-analytics-id
```

## SSL/TLS Configuration

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name proactiva.example.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name proactiva.example.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Frontend static files
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # API proxy
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket proxy
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Database Setup

### PostgreSQL with TimescaleDB

Create `init.sql`:

```sql
-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create application database
CREATE DATABASE proactiva;

-- Connect to application database
\c proactiva;

-- Create tables
CREATE TABLE simulations (
    id SERIAL PRIMARY KEY,
    simulation_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    config JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'created',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE simulation_metrics (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    simulation_id VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    metadata JSONB
);

CREATE TABLE insights (
    id SERIAL PRIMARY KEY,
    simulation_id VARCHAR(50) NOT NULL,
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT,
    confidence DOUBLE PRECISION NOT NULL,
    severity VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create hypertable for time-series data
SELECT create_hypertable('simulation_metrics', 'time');

-- Create indexes
CREATE INDEX idx_simulation_metrics_sim_id ON simulation_metrics(simulation_id);
CREATE INDEX idx_simulation_metrics_name ON simulation_metrics(metric_name);
CREATE INDEX idx_insights_sim_id ON insights(simulation_id);
CREATE INDEX idx_insights_type ON insights(insight_type);
```

## Monitoring Setup

### Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'proactiva-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'nginx-exporter'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### Grafana Dashboards

Import dashboard configurations for:
- **Application Metrics** - Request rates, response times, error rates
- **Simulation Metrics** - Active simulations, agent counts, performance
- **Infrastructure Metrics** - CPU, memory, disk, network usage
- **Database Metrics** - Query performance, connection pools
- **Business Metrics** - User engagement, feature adoption

## Security Considerations

### Authentication and Authorization
- **JWT tokens** for API authentication
- **Role-based access control** (RBAC)
- **API rate limiting** to prevent abuse
- **Input validation** and sanitization

### Network Security
- **TLS 1.3** for all communications
- **Certificate pinning** for mobile apps
- **CORS configuration** for cross-origin requests
- **Firewall rules** for port access

### Data Protection
- **Database encryption** at rest
- **Backup encryption** for data backups
- **PII handling** for patient data
- **Audit logging** for compliance

## Deployment Process

### Automated Deployment

Create `deploy.sh`:

```bash
#!/bin/bash

set -e

# Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
sleep 30

# Run health checks
curl -f http://localhost/health || exit 1

# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser (if needed)
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser --noinput

echo "Deployment completed successfully!"
```

### Rollback Process

Create `rollback.sh`:

```bash
#!/bin/bash

set -e

# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Restore from backup
docker-compose -f docker-compose.prod.yml run --rm database pg_restore -d proactiva /backups/latest.dump

# Deploy previous version
docker-compose -f docker-compose.prod.yml up -d

echo "Rollback completed successfully!"
```

## Performance Tuning

### Database Optimization
- **Connection pooling** with PgBouncer
- **Query optimization** with proper indexes
- **Partitioning** for large time-series tables
- **Vacuum scheduling** for maintenance

### Application Optimization
- **Caching strategy** with Redis
- **Background tasks** with Celery
- **Load balancing** with multiple workers
- **Resource limits** for simulations

### Infrastructure Optimization
- **Auto-scaling** based on metrics
- **CDN** for static assets
- **Database replicas** for read scaling
- **Message queue clustering** for high availability

## Backup and Recovery

### Database Backups
```bash
# Daily backup
docker-compose -f docker-compose.prod.yml exec database pg_dump -U user proactiva > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose -f docker-compose.prod.yml exec database psql -U user proactiva < backup_20240101.sql
```

### Application Backups
- **Configuration files** backup
- **User data** backup
- **Log files** archival
- **Metrics data** retention

## Maintenance

### Regular Tasks
- **Security updates** monthly
- **Dependency updates** quarterly
- **Performance monitoring** daily
- **Log rotation** weekly
- **Backup verification** weekly

### Health Checks
- **Application health** endpoints
- **Database connectivity** checks
- **External service** availability
- **Resource utilization** monitoring