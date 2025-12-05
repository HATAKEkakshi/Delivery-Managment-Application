# 📦 FastShip - Delivery Management Application

A comprehensive, production-ready delivery management system built with FastAPI, designed to streamline shipment operations between sellers and delivery partners. The application features real-time tracking, automated notifications, and robust authentication mechanisms.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7+-DC382D.svg?style=flat&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-20+-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com)

## 🌟 Key Features

### 👤 User Management
- **Dual Role System**: Separate authentication for sellers and delivery partners
- **Secure Authentication**: JWT-based token authentication with OAuth2
- **Email Verification**: Email confirmation for new user registrations
- **Password Management**: Secure password reset with token-based verification
- **Session Management**: Redis-backed token blacklisting for secure logout

### 📦 Shipment Management
- **Complete CRUD Operations**: Create, read, update, and track shipments
- **Real-time Status Updates**: Track shipments through multiple stages (placed, in_transit, out_for_delivery, delivered, cancelled)
- **Smart Tag System**: Categorize shipments with tags (express, fragile, heavy, international, etc.)
- **Event Timeline**: Complete audit trail of shipment status changes
- **Location Tracking**: ZIP code-based location tracking throughout delivery

### 🚚 Delivery Partner Features
- **Service Area Management**: Define serviceable ZIP codes for each partner
- **Capacity Management**: Track and manage maximum handling capacity
- **Active Shipment Monitoring**: Real-time view of assigned shipments
- **Status Updates**: Update shipment locations and statuses on-the-go
- **Performance Tracking**: Monitor delivery partner efficiency

### 🔔 Notification System
- **Multi-Channel Notifications**: Email and SMS support for shipment updates
- **Automated Alerts**: Trigger notifications on status changes
- **Email Templates**: Professional HTML email templates for all events
- **Twilio Integration**: SMS notifications via Twilio API
- **Background Processing**: Asynchronous notification delivery via Celery

### 🎨 User Interface
- **Tracking Portal**: Public shipment tracking interface
- **Review System**: Customer feedback and rating collection
- **Responsive Templates**: Mobile-friendly Jinja2 templates
- **Interactive Docs**: Auto-generated API documentation (Swagger UI & Scalar)

### 🔒 Security Features
- **Password Hashing**: Bcrypt-based secure password storage
- **JWT Tokens**: Secure token-based authentication
- **Token Blacklisting**: Redis-backed logout mechanism
- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Protection**: SQLModel/SQLAlchemy ORM
- **CORS Configuration**: Configurable cross-origin resource sharing

### ⚡ Performance & Scalability
- **Async Operations**: Fully asynchronous FastAPI endpoints
- **Database Connection Pooling**: Efficient PostgreSQL connections
- **Redis Caching**: Fast data access and session management
- **Background Jobs**: Celery workers for time-consuming tasks
- **Horizontal Scaling**: Docker Compose support for multi-instance deployment

## 🏗️ Architecture

### System Architecture
```
┌─────────────────┐
│   Client Apps   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Nginx Proxy   │ (Production)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌──────────────────────────────┐   │
│  │  API Endpoints & Routers     │   │
│  │  - Seller Routes             │   │
│  │  - Delivery Partner Routes   │   │
│  │  - Shipment Routes           │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │  Services Layer              │   │
│  │  - Business Logic            │   │
│  │  - Data Processing           │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │  Database Layer              │   │
│  │  - SQLModel ORM              │   │
│  │  - Async PostgreSQL          │   │
│  └──────────────────────────────┘   │
└─────────┬────────────────┬──────────┘
          │                │
          ▼                ▼
┌──────────────────┐  ┌──────────────┐
│   PostgreSQL     │  │    Redis     │
│   Database       │  │    Cache     │
└──────────────────┘  └──────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│      Celery Workers & Beat          │
│  - Background Task Processing       │
│  - Scheduled Jobs                   │
│  - Email/SMS Notifications          │
└─────────────────────────────────────┘
```

### Technology Stack

#### Backend Framework
- **FastAPI 0.109+**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for serving FastAPI applications
- **Pydantic**: Data validation and settings management
- **Python 3.12+**: Latest Python features and performance improvements

#### Database & ORM
- **PostgreSQL 15+**: Production-grade relational database
- **SQLModel**: Modern ORM combining SQLAlchemy and Pydantic
- **AsyncPG**: Asynchronous PostgreSQL driver
- **Redis 7+**: In-memory data store for caching and sessions

#### Authentication & Security
- **JWT (PyJWT)**: JSON Web Token implementation
- **Passlib & Bcrypt**: Password hashing and verification
- **OAuth2**: Industry-standard authorization framework
- **FastAPI Security**: Built-in security utilities

#### Background Processing
- **Celery**: Distributed task queue
- **Redis**: Message broker for Celery
- **Celery Beat**: Periodic task scheduler

#### Notifications
- **FastAPI-Mail**: Email sending with template support
- **Twilio**: SMS notification service
- **Jinja2**: Template engine for HTML emails

#### Development Tools
- **Pytest**: Testing framework with async support
- **Docker & Docker Compose**: Containerization and orchestration
- **Nginx**: Reverse proxy for production deployment

#### API Documentation
- **Swagger UI**: Interactive API documentation
- **Scalar**: Modern API documentation interface
- **OpenAPI 3.0**: API specification standard

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12 or higher**
- **PostgreSQL 15+** (or Docker to run it in a container)
- **Redis 7+** (or Docker to run it in a container)
- **Git** for version control
- **Docker & Docker Compose** (optional, for containerized deployment)

### Additional Requirements
- SMTP server credentials (Gmail, SendGrid, etc.) for email notifications
- Twilio account (optional, for SMS notifications)
- Domain name (optional, for production deployment)

## 🚀 Installation & Setup

### Option 1: Local Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/HATAKEkakshi/Delivery-Managment-Application.git
cd Delivery-Managment-Application
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r app/requirements.txt
```

#### 4. Configure Environment Variables
Create a `.env` file in the project root:

```bash
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_DB=fastapi_db
POSTGRES_PORT=5432
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT Security
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256

# Email Configuration (Gmail example)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=FastShip Notifications
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True
VALIDATE_CERTS=True

# Twilio Configuration (Optional)
TWILIO_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_NUMBER=+1234567890

# Application Settings
APP_DOMAIN=localhost:8000
```

#### 5. Set Up Database
```bash
# Make sure PostgreSQL is running
# Create the database
createdb fastapi_db

# Run database migrations (if using Alembic)
# cd app && alembic upgrade head
```

#### 6. Start Redis
```bash
# Start Redis server
redis-server
```

#### 7. Start Celery Worker (Optional, for background tasks)
```bash
# In a separate terminal
celery -A app.worker.celery_app worker --loglevel=info
```

#### 8. Start the Application
```bash
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Scalar Docs**: http://localhost:8000/scalar
- **Health Check**: http://localhost:8000/health

### Option 2: Docker Deployment

For containerized deployment with all services, see the [Docker Setup Guide](README-Docker.md).

#### Quick Start with Docker
```bash
# Development environment
docker-compose -f docker-compose.dev.yml up --build

# Production environment
docker-compose -f docker-compose.prod.yml up -d --build
```

## 📚 API Documentation

### Authentication Endpoints

#### Seller Authentication
- `POST /seller/signup` - Register a new seller
- `POST /seller/token` - Login and get JWT token
- `GET /seller/verify` - Verify email address
- `GET /seller/forgot_password` - Request password reset
- `POST /seller/reset_password` - Reset password

#### Delivery Partner Authentication
- `POST /partner/signup` - Register a new delivery partner
- `POST /partner/token` - Login and get JWT token
- `GET /partner/verify` - Verify email address
- `GET /partner/logout` - Logout (blacklist token)
- `POST /partner/` - Update partner profile

### Shipment Endpoints
- `GET /shipment/?id={uuid}` - Get shipment details
- `GET /shipment/track?id={uuid}` - Track shipment (web interface)
- `POST /shipment/` - Create new shipment (seller only)
- `PATCH /shipment/?id={uuid}` - Update shipment status (partner only)

### Health Check
- `GET /health` - Application health status

### Example API Calls

#### Register a Seller
```bash
curl -X POST "http://localhost:8000/seller/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

#### Login as Seller
```bash
curl -X POST "http://localhost:8000/seller/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=SecurePass123!"
```

#### Create a Shipment
```bash
curl -X POST "http://localhost:8000/shipment/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Electronics",
    "weight": 2.5,
    "destination": 12345,
    "client_email_id": "customer@example.com",
    "client_contact_phone": "+1234567890"
  }'
```

#### Track a Shipment
```bash
curl -X GET "http://localhost:8000/shipment/?id=SHIPMENT_UUID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

For complete API documentation with request/response examples, visit:
- **Swagger UI**: http://localhost:8000/docs
- **Scalar**: http://localhost:8000/scalar

## 🧪 Testing

### Running Tests

The project includes comprehensive test suites covering unit, integration, security, and performance tests.

#### Run All Tests
```bash
# Using pytest directly
python -m pytest app/tests/ -v

# Using the test runner script
python run_tests.py
```

#### Run Specific Test Categories
```bash
# Health check tests
python -m pytest app/tests/test_health.py -v

# Seller tests
python -m pytest app/tests/test_seller.py -v

# Delivery partner tests
python -m pytest app/tests/test_delivery_partner.py -v

# Shipment tests
python -m pytest app/tests/test_shipment.py -v

# Integration tests
python -m pytest app/tests/test_integration.py -v

# Security tests
python -m pytest app/tests/test_security.py -v

# Performance tests
python -m pytest app/tests/test_performance.py -v
```

#### Run Tests with Coverage
```bash
python -m pytest app/tests/ --cov=app --cov-report=html --cov-report=term
```

Coverage report will be generated in `htmlcov/index.html`.

For detailed testing documentation, see [app/tests/README.md](app/tests/README.md).

## 📁 Project Structure

```
Delivery-Managment-Application/
├── app/                          # Main application directory
│   ├── api/                      # API layer
│   │   ├── dependencies.py       # Dependency injection functions
│   │   └── shipment.py          # Additional shipment API handlers
│   ├── core/                     # Core functionality
│   │   ├── exceptions.py        # Custom exception handlers
│   │   └── security.py          # Security configurations
│   ├── database/                 # Database layer
│   │   ├── config.py            # Database and app settings
│   │   ├── model.py             # SQLModel database models
│   │   ├── redis.py             # Redis operations
│   │   └── session.py           # Database session management
│   ├── helper/                   # Utility functions
│   │   └── utils.py             # Helper utilities
│   ├── routers/                  # API routers
│   │   ├── router.py            # Shipment routes
│   │   ├── seller.py            # Seller routes
│   │   └── delivery_partner.py  # Delivery partner routes
│   ├── schemas/                  # Pydantic schemas
│   │   └── schemas.py           # Request/response models
│   ├── services/                 # Business logic layer
│   │   ├── base.py              # Base service class
│   │   ├── seller.py            # Seller service
│   │   ├── delivery_partner.py  # Delivery partner service
│   │   ├── shipment.py          # Shipment service
│   │   ├── shipmentevent.py     # Shipment event service
│   │   ├── notification.py      # Notification service
│   │   └── user.py              # User service
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── track.html           # Shipment tracking page
│   │   ├── reset.html           # Password reset page
│   │   ├── review.html          # Review submission page
│   │   └── mail_*.html          # Email notification templates
│   ├── tests/                    # Test suite
│   │   ├── conftest.py          # Test fixtures and configuration
│   │   ├── test_*.py            # Test modules
│   │   └── README.md            # Testing documentation
│   ├── worker/                   # Background job processing
│   │   ├── celery_app.py        # Celery configuration
│   │   └── tasks.py             # Celery tasks
│   ├── alembic.ini              # Alembic migration config
│   └── requirements.txt         # Python dependencies
├── main.py                       # Application entry point
├── Dockerfile                    # Docker container definition
├── docker-compose.yml           # Docker Compose configuration
├── pytest.ini                   # Pytest configuration
├── run_tests.py                 # Test runner script
├── README.md                    # This file
└── README-Docker.md             # Docker deployment guide
```

## 🔧 Configuration

### Database Configuration

Update `app/database/config.py` or set environment variables:

```python
POSTGRES_SERVER=localhost
POSTGRES_DB=fastapi_db
POSTGRES_PORT=5432
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```

### Redis Configuration

```python
REDIS_HOST=localhost
REDIS_PORT=6379
```

### JWT Configuration

```python
JWT_SECRET=your-secret-key  # Change in production!
JWT_ALGORITHM=HS256
```

### Email Configuration

For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in `MAIL_PASSWORD`

```python
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

### Twilio SMS Configuration (Optional)

```python
TWILIO_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_NUMBER=+1234567890
```

## 🚢 Deployment

### Production Deployment Checklist

- [ ] **Change all default passwords and secrets**
- [ ] **Set strong `JWT_SECRET` key**
- [ ] **Configure proper CORS origins**
- [ ] **Set up SSL/TLS certificates**
- [ ] **Configure proper logging**
- [ ] **Set up database backups**
- [ ] **Configure monitoring and alerting**
- [ ] **Set resource limits in Docker Compose**
- [ ] **Use environment-specific configuration files**
- [ ] **Set up firewall rules**

### Using Docker in Production

```bash
# Build and start production environment
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### Environment Variables in Production

Create a `.env.prod` file with production values:
```bash
cp .env.example .env.prod
# Edit .env.prod with production values
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## 🔍 Monitoring & Logging

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check container health
docker-compose ps
```

### Viewing Logs

```bash
# Application logs
docker-compose logs -f fastapi-app

# Database logs
docker-compose logs -f postgres

# Celery worker logs
docker-compose logs -f celery-worker
```

### Performance Monitoring

Monitor the following metrics:
- API response times (middleware logging)
- Database query performance
- Redis cache hit rates
- Celery task queue length
- Resource usage (CPU, memory)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `python run_tests.py`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use type hints for all function parameters and returns
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Write tests for new features

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify connection string in .env file
# Ensure credentials match database setup
```

#### Redis Connection Errors
```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG
```

#### Import Errors
```bash
# Ensure you're in the project root
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r app/requirements.txt
```

#### Celery Worker Not Starting
```bash
# Check Redis connection
# Verify REDIS_URL in environment variables
# Check for port conflicts
```

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Authors & Contact

**Hemant Kumar**
- Email: hemant.kumardeveloper@gmail.com
- GitHub: [@HATAKEkakshi](https://github.com/HATAKEkakshi)

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL database ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Celery](https://docs.celeryproject.org/) - Distributed task queue
- [Twilio](https://www.twilio.com/) - SMS notifications

## 📊 Project Status

🚀 **Active Development** - This project is actively maintained and accepting contributions.

### Recent Updates
- ✅ Comprehensive test suite with 90%+ coverage
- ✅ Docker deployment support
- ✅ Email and SMS notifications
- ✅ JWT authentication with token blacklisting
- ✅ Real-time shipment tracking
- ✅ Background task processing with Celery

### Planned Features
- [ ] WebSocket support for real-time updates
- [ ] Admin dashboard
- [ ] Analytics and reporting
- [ ] Multi-language support
- [ ] Mobile app API optimization
- [ ] GraphQL API support

## 📚 Additional Resources

- **Docker Setup**: [README-Docker.md](README-Docker.md)
- **Testing Guide**: [app/tests/README.md](app/tests/README.md)
- **API Documentation**: http://localhost:8000/docs (when running)
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com

---

**Made with ❤️ using FastAPI**
