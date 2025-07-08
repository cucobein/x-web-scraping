# Testing Architecture

This directory contains the comprehensive test suite for the X Web Scraping project, designed with a layered architecture that mirrors the main application structure.

## Quick Start

### 1. Setup Test Environment
```bash
# Set up environment (if not already done)
cp .env.template .env
# Edit .env and set ENVIRONMENT=dev for testing

# HTML fixtures are automatically managed with Git LFS
# No manual setup needed - fixtures are version controlled
git lfs pull  # If you need to download LFS files

# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v
```

### 2. Run Tests
```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage
make test-coverage

# Run specific test file
python -m pytest tests/unit/test_tweet_model_unit.py

# Run tests matching a pattern
python -m pytest -k "test_browser"
```

### 3. Code Quality Checks
Before running tests, ensure code quality:

```bash
# Format code
make format

# Check quality
make lint

# Auto-fix issues
make fix

# Run all checks
make check
```

## Test Structure

```
tests/
├── conftest.py              # Shared pytest fixtures
├── fixtures/                # Test data and HTML snapshots
│   ├── twitter/            # Real Twitter HTML fixtures (LFS tracked)
│   │   ├── nasa_profile.html
│   │   ├── elonmusk_profile.html
│   │   ├── MetroCDMX_profile.html
│   │   ├── GobCDMX_profile.html
│   │   ├── no_posts_profile.html
│   │   └── non_existing_user.html
│   ├── telegram/           # Telegram API response fixtures
│   ├── facebook/           # Future Facebook fixtures (LFS tracked)
│   ├── instagram/          # Future Instagram fixtures (LFS tracked)
│   └── youtube/            # Future YouTube fixtures (LFS tracked)
├── integration/            # Integration tests using real fixtures
│   ├── test_twitter_scraper_integration.py
│   └── test_monitor_integration.py
├── unit/                   # Unit tests for each layer (using mocks)
│   ├── test_config_manager_unit.py
│   ├── test_tweet_model_unit.py
│   ├── test_tweet_repository_unit.py
│   ├── test_http_client_unit.py
│   ├── test_twitter_scraper_unit.py
│   ├── test_telegram_notification_service_unit.py
│   ├── test_rate_limiter_unit.py
│   ├── test_notification_service_unit.py
│   ├── test_monitor_unit.py
│   └── test_pool_manager_unit.py
└── README.md              # This file
```

## 🌍 Environment Testing

The test suite supports environment-based testing to ensure configuration works correctly across different environments.

### Environment Variables in Testing

- **`ENVIRONMENT`**: Controls which environment-specific settings are used during tests
  - **Valid values**: `dev`, `prod`
  - **Default**: `dev` (if not set or invalid)
  - **Test usage**: Determines which configuration values are loaded from fixtures

### Environment-Specific Test Scenarios

**Development Environment (`ENVIRONMENT=dev`):**
- Uses development-specific configuration values
- Tests with development Firebase Remote Config keys
- Faster timeouts and development settings

**Production Environment (`ENVIRONMENT=prod`):**
- Uses production-specific configuration values  
- Tests with production Firebase Remote Config keys
- Production timeouts and settings

### Environment Testing in Integration Tests

Integration tests use environment-specific fixtures:
```python
# Test with development environment
config = ConfigManager(ConfigMode.FIXTURE, environment='dev')

# Test with production environment  
config = ConfigManager(ConfigMode.FIXTURE, environment='prod')
```

### Environment Fallback Testing

The `ConfigMode.FALLBACK` mode tests fallback scenarios:
- Tests behavior when Firebase config is invalid
- Verifies fallback to local configuration
- Ensures system resilience

## Test Classification

### Unit Tests (`tests/unit/`)
**Purpose:** Test individual components in isolation using mocks
**Naming Convention:** `test_<component>_unit.py`
**Characteristics:**
- Use mocks for external dependencies
- Fast execution
- Test specific functionality
- No network calls or browser instances

**Files:**
- **`test_config_manager_unit.py`**: Configuration loading and validation
- **`test_tweet_model_unit.py`**: Tweet data model and parsing
- **`test_tweet_repository_unit.py`**: Data persistence and retrieval
- **`test_http_client_unit.py`**: HTTP client functionality and retry logic
- **`test_twitter_scraper_unit.py`**: Twitter scraper with mocked pages
- **`test_telegram_notification_service_unit.py`**: Telegram notifications with retry logic
- **`test_rate_limiter_unit.py`**: Rate limiting and anti-detection functionality
- **`test_notification_service_unit.py`**: Notification service initialization and configuration
- **`test_monitor_unit.py`**: Monitor class behavior with mocked dependencies
- **`test_pool_manager_unit.py`**: PoolManager context pooling logic (fully mocked, no real browser)
- **`test_context_pool_unit.py`**: ContextPool per-domain pooling logic (fully mocked)
- **`test_browser_manager_unit.py`**: BrowserManager integration with PoolManager, context pooling, and backward compatibility (all browser logic mocked)
- **`test_logger_service_unit.py`**: Comprehensive logging system testing including JSON output, async logging, performance timing, and log rotation with timestamped backups

### Integration Tests (`tests/integration/`)
**Purpose:** Test component interactions using real HTML fixtures
**Naming Convention:** `test_<component>_integration.py`
**Characteristics:**
- Use real fixtures (HTML/JSON) as the center and focus
- Test component interactions and workflows
- May use mocks for external dependencies (out of necessity)
- Test end-to-end scenarios with real data

**Files:**
- **`test_twitter_scraper_integration.py`**: Twitter scraper with real HTML fixtures and fast extraction
- **`test_monitor_integration.py`**: Full monitoring workflow with real HTML fixtures, rate limiting integration, and Telegram retry logic

## Test Fixtures

### HTML Fixtures with Git LFS
The `fixtures/twitter/` directory contains real HTML snapshots from social media profiles:

- **Size**: ~500KB+ each (real HTML is large)
- **Content**: Actual profile pages with real data
- **Purpose**: Enable testing against realistic data without hitting live servers
- **Git LFS**: All HTML files in `tests/fixtures/**/*.html` are tracked with LFS

### Twitter HTML Fixtures
- **`nasa_profile.html`**: NASA profile with real tweets
- **`elonmusk_profile.html`**: Elon Musk profile with real tweets
- **`MetroCDMX_profile.html`**: MetroCDMX profile with real tweets
- **`GobCDMX_profile.html`**: GobCDMX profile with real tweets
- **`no_posts_profile.html`**: Profile with no tweets (for zero-to-new scenarios)
- **`non_existing_user.html`**: 404 page for non-existing users

### API Response Fixtures
The `fixtures/telegram/` directory contains real API response data:

- **Success Responses**: Real successful API responses for testing
- **Error Responses**: Real error responses for testing error handling
- **Request Examples**: Sample request formats for validation

## Testing Scenarios

### Integration Test Scenarios
Our integration tests cover real-world monitoring scenarios:

1. **Normal Tweet Extraction**: Extract tweets from real profiles (NASA, Elon Musk)
2. **Pinned Tweet Handling**: Skip pinned tweets and get latest actual tweet
3. **Profile with No Posts**: Handle accounts that exist but have no tweets
4. **Non-Existing User**: Handle 404 pages for invalid usernames
5. **Unique ID Generation**: Verify tweet URLs are used as unique identifiers
6. **Full Monitoring Workflow**: First time monitoring, new tweet detection, API failures
7. **Component Integration**: How monitor orchestrates scraper, notification, and repository
8. **Rate Limiting Integration**: Test rate limiting behavior with multiple accounts
9. **Telegram Retry Logic**: Test notification retry with exponential backoff
10. **Fast HTML Extraction**: Optimized extraction methods for test performance

### Monitoring Workflow Scenarios
These scenarios are tested in the integration tests:

1. **First Time Monitoring**: Establish baseline without notification
2. **New Tweet Detected**: Send notification when new content is found
3. **No New Tweets**: Continue monitoring without notification
4. **Zero to New Post**: Account goes from no posts to having posts
5. **Post to Nothing**: Account goes from having posts to no posts
6. **Telegram API Failure**: System continues monitoring despite notification failures
7. **Rate Limiting Behavior**: Domain-specific request tracking and delays
8. **Multiple Account Processing**: Rate limiting across multiple accounts

## Best Practices

### 1. Use Real Data
- Integration tests use actual HTML fixtures
- Ensures realistic test scenarios
- Catches real-world parsing issues

### 2. Proper Test Classification
- **Unit tests**: Use mocks, test specific functionality
- **Integration tests**: Use real fixtures, test component interactions
- **No hybrid tests**: Each test file has a clear purpose
- **Context pooling**: All pooling logic is tested with mocks only; no real browser or network calls in unit tests

### 3. Fast Execution
- Unit tests run quickly with mocks
- Integration tests use offline fixtures with optimized timeouts
- **Performance**: Edge case tests (no tweets, errors) complete in ~2 seconds vs 15+ seconds
- Parallel test execution supported

### 4. Comprehensive Coverage
- Test both success and error cases
- Validate edge cases
- Test real-world monitoring scenarios

### 5. Performance Optimization
- **Fast HTML Processing**: Integration tests use optimized extraction methods (`get_latest_tweet_from_html`)
- **Reduced Timeouts**: Test-specific timeouts (500ms vs 5000ms) for faster execution
- **Browser Efficiency**: Tests complete in seconds, not minutes
- **Real-world Performance**: Production scraping still uses full timeouts for reliability
- **Rate Limiter Testing**: Async tests with mocked `asyncio.sleep` for fast execution
- **Shared Browser Manager**: Efficient resource usage across integration tests

## Test Data Management

### Fixture Lifecycle
1. **Capture**: Use browser to save real HTML pages
2. **Test**: Tests load fixtures from `tests/fixtures/`
3. **Update**: Re-capture when social media sites change their HTML structure

### Fixture Maintenance
- HTML fixtures may become outdated as sites update their structure
- Monitor test failures that might indicate HTML structure changes
- Re-capture fixtures when needed

### Git LFS Workflow
```bash
# Normal development workflow
git pull                    # Gets latest code and LFS files
python -m pytest           # Run tests with fixtures
git add tests/fixtures/new_file.html  # New fixtures automatically tracked
git commit -m "Add new fixtures"
git push                   # Pushes code and LFS files
```

## Recent Improvements

### Test Organization Cleanup (Latest)
- **Proper Separation**: Moved unit tests from integration files to dedicated unit test files
- **New Unit Test Files**: 
  - `test_notification_service_unit.py`: Tests NotificationService initialization
  - `test_monitor_unit.py`: Tests Monitor class behavior with mocked dependencies
- **Clean Integration Tests**: Removed commented-out unit tests from integration files
- **Clear Boundaries**: Unit tests use mocks, integration tests use real fixtures

### Performance Enhancements
- **Fast HTML Extraction**: Integration tests use `get_latest_tweet_from_html` method
- **Optimized Timeouts**: Test-specific timeouts for faster execution
- **Shared Resources**: Browser manager fixtures shared across integration tests
- **Async Rate Limiter Tests**: Mocked `asyncio.sleep` for fast rate limiter testing

### New Features Tested
- **Rate Limiting**: Comprehensive unit and integration tests for anti-detection
- **Telegram Retry Logic**: Tests for exponential backoff and retry exhaustion
- **Browser Manager Integration**: Tests for rate limiting integration
- **User Agent Rotation**: Tests for anti-detection measures

## Running Tests in CI/CD

For continuous integration, Git LFS handles fixture management automatically:

```yaml
# Example GitHub Actions step
- name: Setup Git LFS
  run: |
    git lfs install
    git lfs pull

- name: Run tests
  run: python -m pytest
```

## Troubleshooting

### Missing LFS Files
If tests fail with "file not found" errors:

```bash
# Download LFS files
git lfs pull

# Or clone with LFS files
git clone --recurse-submodules <repo-url>
```

### Outdated Fixtures
If tests fail due to HTML structure changes:

```bash
# Re-capture fixtures using browser
# Save as HTML only (not complete webpage)
# Place in appropriate fixtures directory
```

### Test Performance
- Integration tests with browser instances are slower
- Unit tests with mocks are fast
- Use `-k` flag to run specific tests during development

## Future Enhancements

- [ ] Integration tests for full workflow
- [ ] Performance benchmarks
- [ ] Visual regression testing
- [ ] Automated fixture updates
- [ ] Test data factories for edge cases
- [ ] Multi-platform fixture support (Facebook, Instagram, YouTube)

# Testing Documentation

This directory contains the comprehensive test suite for the X Feed Monitor application.

## 📁 Directory Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Pytest configuration and shared fixtures
├── fixtures/                    # Real HTML snapshots for testing
│   └── twitter/                 # Twitter profile HTML fixtures
│       ├── nasa_profile.html    # NASA's actual Twitter profile
│       ├── GobCDMX_profile.html # Mexico City Government profile
│       ├── MetroCDMX_profile.html # Metro CDMX profile
│       └── elonmusk_profile.html # High-activity profile
├── unit/                        # Unit tests
│   ├── test_tweet_model.py      # Tweet data model tests
│   ├── test_config_manager.py   # Configuration management tests
│   └── test_tweet_repository.py # Data persistence tests
└── integration/                 # Integration tests (future)
```

## 🧪 Test Architecture

### **Testing Philosophy**
- **Real Data Testing**: Uses actual HTML snapshots from Twitter profiles
- **Regression Detection**: Catches DOM changes when websites update
- **Comprehensive Coverage**: Tests all core functionality
- **Fast Execution**: Unit tests run in milliseconds
- **Reliable**: No flaky network-dependent tests

### **Test Categories**

#### **Unit Tests** (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Dependencies**: Mocked external dependencies
- **Speed**: Very fast (< 0.1s total)
- **Coverage**: Core business logic

#### **Integration Tests** (`tests/integration/`)
- **Purpose**: Test component interactions
- **Dependencies**: Real HTML fixtures
- **Speed**: Medium (uses real data)
- **Coverage**: End-to-end workflows

#### **Logging Tests** (`tests/unit/test_logger_service_unit.py`)
- **Purpose**: Test comprehensive logging system functionality
- **Dependencies**: Mocked file system and datetime
- **Speed**: Very fast (uses temp files and mocks)
- **Coverage**: JSON output, async logging, performance timing, log rotation with timestamped backups

## 📊 Test Coverage

### **Tweet Model Tests** (13 tests)
- ✅ Valid tweet creation and validation
- ✅ Data serialization (to_dict/from_dict)
- ✅ Unique ID generation
- ✅ Error handling for invalid data
- ✅ Equality and comparison logic

### **Config Manager Tests** (7 tests)
- ✅ JSON config file loading
- ✅ Fallback to default values
- ✅ Invalid JSON error handling
- ✅ Property accessors
- ✅ Config caching behavior
- ✅ Real config file integration

### **Tweet Repository Tests** (10 tests)
- ✅ Save/retrieve operations
- ✅ New tweet detection logic
- ✅ Multi-user tracking
- ✅ State management
- ✅ Data clearing operations

### **Logger Service Tests** (22 tests)
- ✅ Singleton pattern and instance management
- ✅ Sync and async logging methods
- ✅ Context support with structured data
- ✅ Exception logging with stack traces
- ✅ JSON output format for log aggregation
- ✅ Performance timing (context manager and decorator)
- ✅ Runtime log rotation with timestamped backups
- ✅ Async worker and queue management
- ✅ Error handling and fallback mechanisms

## 🎯 Running Tests

### **Quick Commands**
```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py unit

# Run specific test file
python run_tests.py test_tweet_model.py

# Run with pytest directly
python -m pytest tests/unit/ -v
```

### **Detailed Commands**
```bash
# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test class
python -m pytest tests/unit/test_tweet_model.py::TestTweetModel -v

# Run specific test method
python -m pytest tests/unit/test_tweet_model.py::TestTweetModel::test_tweet_creation_with_valid_data -v

# Run tests matching pattern
python -m pytest tests/ -k "tweet" -v
```

## 🔧 Test Configuration

### **Pytest Configuration** (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
asyncio_mode = auto
```

### **Shared Fixtures** (`conftest.py`)
- **event_loop**: Async event loop for tests
- **sample_tweet**: Pre-configured Tweet object
- **mock_page**: Mocked Playwright page
- **load_html_fixture()**: Load real HTML from files
- **create_mock_page_with_html()**: Create mock page with real HTML

## 📄 HTML Fixtures

### **Real Data Strategy**
Instead of pure mocks, we use actual HTML snapshots from Twitter profiles. This approach:

1. **Catches Real Changes**: Tests fail when Twitter updates their DOM
2. **Realistic Testing**: Tests against actual HTML structures
3. **Regression Detection**: Compare "before" vs "after" HTML
4. **Documentation**: HTML files serve as documentation

### **Capturing New Fixtures**
```bash
# Capture HTML from Twitter profiles
python scripts/capture_fixtures.py

# This creates:
# - tests/fixtures/twitter/nasa_profile.html
# - tests/fixtures/twitter/GobCDMX_profile.html
# - tests/fixtures/twitter/MetroCDMX_profile.html
# - tests/fixtures/twitter/elonmusk_profile.html
```

### **Fixture Usage**
```python
from tests.conftest import load_html_fixture, create_mock_page_with_html

# Load real HTML
html_content = load_html_fixture("nasa_profile.html")

# Create mock page with real HTML
mock_page = create_mock_page_with_html(html_content)
```

## 🚀 Adding New Tests

### **Unit Test Template**
```python
"""
Unit tests for [Component Name]
"""
import pytest
from src.[module] import [Class]


class Test[ClassName]:
    """Test cases for [Class]"""
    
    def setup_method(self):
        """Set up fresh instance for each test"""
        self.instance = [Class]()
    
    def test_[specific_behavior](self):
        """Test [specific behavior description]"""
        # Arrange
        # Act
        # Assert
        pass
```

### **Integration Test Template**
```python
"""
Integration tests for [Feature]
"""
import pytest
from tests.conftest import load_html_fixture


class Test[Feature]Integration:
    """Integration tests for [Feature]"""
    
    @pytest.mark.integration
    async def test_[feature_with_real_data](self):
        """Test [feature] with real HTML data"""
        # Load real HTML fixture
        html_content = load_html_fixture("profile.html")
        
        # Test with real data
        pass
```

## 🔍 Test Patterns

### **Mocking Strategy**
```python
# Mock file I/O
with patch("builtins.open", mock_open(read_data=json.dumps(data))):
    # Test code here

# Mock Playwright page
mock_page = AsyncMock(spec=Page)
mock_page.locator = AsyncMock()
mock_page.goto = AsyncMock()

# Mock with real HTML
mock_page = create_mock_page_with_html(real_html_content)
```

### **Async Testing**
```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async functions"""
    result = await async_function()
    assert result == expected_value
```

### **Data Validation Testing**
```python
def test_validation_error():
    """Test that invalid data raises appropriate errors"""
    with pytest.raises(ValueError, match="specific error message"):
        create_invalid_object()
```

## 📈 Test Metrics

### **Current Coverage**
- **Total Tests**: 29
- **Unit Tests**: 29
- **Integration Tests**: 0 (ready for future)
- **Execution Time**: ~0.06s
- **Success Rate**: 100%

### **Test Categories**
- **Data Models**: 13 tests
- **Configuration**: 7 tests
- **Data Persistence**: 10 tests
- **Services**: 0 tests (ready for future)
- **Integration**: 0 tests (ready for future)

## 🛠️ Troubleshooting

### **Common Issues**

#### **Import Errors**
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### **Async Test Issues**
```python
# Ensure proper async setup
@pytest.mark.asyncio
async def test_async_function():
    # Use await properly
    result = await function()
```

#### **Mock Issues**
```python
# Reset mocks between tests
def setup_method(self):
    self.mock.reset_mock()
```

### **Debugging Tests**
```bash
# Run with debug output
python -m pytest tests/ -v -s

# Run single test with debugger
python -m pytest tests/unit/test_file.py::TestClass::test_method -s --pdb
```

## 🔮 Future Enhancements

### **Planned Test Additions**
- **Service Layer Tests**: TwitterScraper, BrowserManager, NotificationService
- **Integration Tests**: End-to-end monitoring workflows
- **Performance Tests**: Load testing with multiple accounts
- **Error Handling Tests**: Network failures, rate limiting
- **Multi-Platform Tests**: Facebook, YouTube scraping

### **Advanced Testing Features**
- **Test Data Factories**: Generate test data programmatically
- **Property-Based Testing**: Test with random valid inputs
- **Mutation Testing**: Ensure tests catch code changes
- **Visual Regression Testing**: Screenshot comparison
- **API Contract Testing**: Test against real APIs when available

## 📚 Best Practices

### **Test Naming**
- Use descriptive test names: `test_tweet_creation_with_valid_data`
- Follow pattern: `test_[method]_[scenario]_[expected_result]`
- Group related tests in classes

### **Test Structure**
- **Arrange**: Set up test data and mocks
- **Act**: Execute the code being tested
- **Assert**: Verify the expected results

### **Test Independence**
- Each test should be independent
- Use `setup_method()` for fresh instances
- Don't rely on test execution order

### **Real Data Usage**
- Use real HTML fixtures when possible
- Update fixtures when websites change
- Document fixture sources and dates

---

**Last Updated**: June 2024  
**Test Framework**: pytest 8.4.1  
**Coverage**: 29 tests, 100% pass rate 