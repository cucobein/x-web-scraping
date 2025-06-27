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