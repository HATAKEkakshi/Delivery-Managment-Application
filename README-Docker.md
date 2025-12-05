# Docker Setup Guide

This guide explains how to run the FastAPI backend using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose
- Git

## Quick Start

### Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Fastapi-backend
   ```

2. **Copy environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your configuration.

3. **Start development environment**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Scalar Documentation: http://localhost:8000/scalar
   - PgAdmin: http://localhost:5050 (admin@example.com / admin)
   - Redis Commander: http://localhost:8081

### Production Environment

1. **Set up environment variables**
   ```bash
   cp .env.example .env.prod
   ```
   Edit `.env.prod` with production values.

2. **Start production environment**
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

## Available Services

### Core Services
- **fastapi-app**: Main FastAPI application
- **postgres**: PostgreSQL database
- **redis**: Redis for caching and message broker
- **celery-worker**: Background task processor
- **celery-beat**: Scheduled task scheduler
- **nginx**: Reverse proxy (production only)

### Development Tools (dev environment only)
- **pgadmin**: PostgreSQL administration
- **redis-commander**: Redis administration

## Docker Commands

### Build and Start
```bash
# Development
docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose -f docker-compose.prod.yml up -d --build
```

### Stop Services
```bash
# Development
docker-compose -f docker-compose.dev.yml down

# Production
docker-compose -f docker-compose.prod.yml down
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs

# Specific service
docker-compose -f docker-compose.dev.yml logs fastapi-app

# Follow logs
docker-compose -f docker-compose.dev.yml logs -f fastapi-app
```

### Execute Commands in Container
```bash
# Access FastAPI container shell
docker-compose -f docker-compose.dev.yml exec fastapi-app bash

# Run database migrations
docker-compose -f docker-compose.dev.yml exec fastapi-app alembic upgrade head

# Run tests
docker-compose -f docker-compose.dev.yml exec fastapi-app pytest
```

## Database Operations

### Initialize Database
```bash
# Run migrations
docker-compose -f docker-compose.dev.yml exec fastapi-app alembic upgrade head

# Create new migration
docker-compose -f docker-compose.dev.yml exec fastapi-app alembic revision --autogenerate -m "description"
```

### Backup Database
```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U fastapi_user fastapi_db > backup.sql

# Restore backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U fastapi_user fastapi_db < backup.sql
```

## Monitoring and Health Checks

### Health Check Endpoints
- Application: http://localhost:8000/health
- Database: Check container health status
- Redis: Check container health status

### Container Status
```bash
# Check container status
docker-compose -f docker-compose.dev.yml ps

# Check container health
docker-compose -f docker-compose.dev.yml exec fastapi-app curl http://localhost:8000/health
```

## Scaling Services

### Scale Celery Workers
```bash
# Scale to 3 workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3
```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   - Change ports in docker-compose.yml if needed
   - Check if ports are already in use: `netstat -tulpn | grep :8000`

2. **Database connection issues**
   - Ensure PostgreSQL container is healthy
   - Check DATABASE_URL in environment variables
   - Verify database credentials

3. **Redis connection issues**
   - Ensure Redis container is healthy
   - Check REDIS_URL in environment variables

4. **Permission issues**
   - Ensure proper file permissions
   - Check if user has Docker permissions

### Logs and Debugging
```bash
# View all container logs
docker-compose -f docker-compose.dev.yml logs

# Debug specific service
docker-compose -f docker-compose.dev.yml logs fastapi-app

# Check container resource usage
docker stats

# Inspect container
docker-compose -f docker-compose.dev.yml exec fastapi-app bash
```

## Security Considerations

### Production Security
- Change default passwords in `.env.prod`
- Use strong SECRET_KEY
- Configure SSL certificates for HTTPS
- Set up firewall rules
- Regular security updates
- Monitor logs for suspicious activity

### Environment Variables
Never commit `.env` files to version control. Use `.env.example` as template.

## Performance Tuning

### Resource Limits
Adjust resource limits in `docker-compose.prod.yml` based on your server capacity.

### Database Optimization
- Configure PostgreSQL settings for your workload
- Set up connection pooling
- Monitor query performance

### Caching
- Configure Redis memory limits
- Set appropriate cache expiration times
- Monitor cache hit rates

## Backup Strategy

### Automated Backups
Set up automated database backups using cron jobs or backup services.

### Data Persistence
All data is stored in Docker volumes:
- `postgres_data`: Database data
- `redis_data`: Redis data
- `./logs`: Application logs

## Updates and Maintenance

### Updating Services
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Restart with new images
docker-compose -f docker-compose.prod.yml up -d
```

### Maintenance Mode
```bash
# Stop application while keeping database running
docker-compose -f docker-compose.prod.yml stop fastapi-app nginx

# Start maintenance
docker-compose -f docker-compose.prod.yml restart fastapi-app nginx
```