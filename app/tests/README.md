# FastAPI Backend Test Suite

Comprehensive test suite for the FastShip delivery management system.

## Test Structure

### Test Files

- **`test_health.py`** - Health endpoint tests
- **`test_seller.py`** - Seller authentication and validation tests
- **`test_delivery_partner.py`** - Delivery partner authentication and validation tests
- **`test_shipment.py`** - Shipment CRUD operations tests
- **`test_integration.py`** - End-to-end workflow tests
- **`test_security.py`** - Security and authentication tests
- **`test_performance.py`** - Performance and load tests
- **`conftest.py`** - Test configuration and fixtures
- **`example.py`** - Test data creation utilities

## Running Tests

### Quick Start
```bash
# Run all tests
python -m pytest app/tests/ -v

# Run specific test file
python -m pytest app/tests/test_seller.py -v

# Run with coverage
python -m pytest app/tests/ --cov=app --cov-report=html
```

### Using Test Runner
```bash
# Run all tests automatically
python run_tests.py

# Interactive test selection
python run_tests.py --interactive
```

## Test Categories

### 1. Unit Tests
- **Seller Tests**: Registration, login, validation
- **Partner Tests**: Registration, login, validation  
- **Health Tests**: Basic endpoint functionality

### 2. Integration Tests
- Complete user workflows
- Cross-service interactions
- Data consistency checks
- Authorization boundaries

### 3. Security Tests
- Authentication mechanisms
- JWT token handling
- Input validation
- SQL injection prevention
- XSS protection
- Sensitive data exposure

### 4. Performance Tests
- Response time validation
- Concurrent operation handling
- Database query performance
- Memory usage stability
- Large payload handling

## Test Database

Tests use an in-memory SQLite database that is:
- Created fresh for each test session
- Automatically cleaned up after tests
- Isolated from production data
- Fast and reliable

## Fixtures

### Available Fixtures
- `client` - Async HTTP client for API testing
- `seller_data` - Sample seller registration data
- `partner_data` - Sample partner registration data
- `shipment_data` - Sample shipment creation data
- `seller_token` - Authenticated seller JWT token
- `partner_token` - Authenticated partner JWT token
- `created_shipment` - Pre-created shipment for testing

### Custom Fixtures
```python
@pytest_asyncio.fixture
async def authenticated_seller(client: AsyncClient):
    # Create and authenticate seller
    seller_data = {...}
    await client.post("/seller/signup", json=seller_data)
    response = await client.post("/seller/token", data=login_data)
    return response.json()["access_token"]
```

## Test Patterns

### API Testing Pattern
```python
async def test_endpoint(client: AsyncClient):
    response = await client.post("/endpoint", json=data)
    assert response.status_code == 200
    assert response.json()["field"] == expected_value
```

### Authentication Testing Pattern
```python
async def test_protected_endpoint(client: AsyncClient, seller_token):
    headers = {"Authorization": f"Bearer {seller_token}"}
    response = await client.post("/protected", json=data, headers=headers)
    assert response.status_code == 200
```

### Error Testing Pattern
```python
async def test_validation_error(client: AsyncClient):
    invalid_data = {...}
    response = await client.post("/endpoint", json=invalid_data)
    assert response.status_code == 422
```

## Coverage Goals

- **Unit Tests**: >90% code coverage
- **Integration Tests**: All major workflows
- **Security Tests**: All authentication paths
- **Performance Tests**: Critical endpoints

## Running Specific Test Types

```bash
# Authentication tests
python -m pytest app/tests/test_seller.py::TestSellerAuth -v

# Validation tests  
python -m pytest app/tests/test_seller.py::TestSellerValidation -v

# Integration workflows
python -m pytest app/tests/test_integration.py::TestIntegrationWorkflow -v

# Security features
python -m pytest app/tests/test_security.py::TestSecurityFeatures -v

# Performance benchmarks
python -m pytest app/tests/test_performance.py::TestPerformance -v
```

## Test Data

Test data is automatically generated and cleaned up. No manual setup required.

### Sample Test Data
- **Sellers**: Various valid/invalid seller profiles
- **Partners**: Different capacity and service area configurations
- **Shipments**: Various weights, destinations, and content types

## Debugging Tests

```bash
# Run with detailed output
python -m pytest app/tests/ -v -s

# Run single test with debugging
python -m pytest app/tests/test_seller.py::test_seller_signup -v -s

# Stop on first failure
python -m pytest app/tests/ -x

# Run last failed tests
python -m pytest app/tests/ --lf
```

## Continuous Integration

Tests are designed to run in CI/CD environments:
- No external dependencies
- Fast execution (< 30 seconds)
- Reliable and deterministic
- Clear pass/fail indicators

## Adding New Tests

1. Create test file in `app/tests/`
2. Import necessary fixtures from `conftest.py`
3. Follow existing naming conventions
4. Add to appropriate test category
5. Update this README if needed

### Test Naming Convention
- `test_<feature>_<scenario>.py` for files
- `test_<action>_<expected_result>` for functions
- `Test<Feature><Category>` for classes