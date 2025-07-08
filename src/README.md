# Source Code Architecture

This directory contains the main application code organized in a layered architecture for maintainability, testability, and extensibility.

## 🏗️ Architecture Overview

The application follows a **Clean Architecture** pattern with clear separation of concerns:

```
src/
├── config/          # Configuration management layer
├── models/          # Data models and entities
├── services/        # External services and business logic
├── repositories/    # Data persistence layer
└── core/            # Application orchestration
```

## 🌍 Environment Management

The application uses environment-based configuration to support different deployment scenarios.

### Environment Variables

- **`ENVIRONMENT`**: Controls which environment-specific settings are loaded
  - **Valid values**: `dev`, `prod`
  - **Default**: `dev` (if not set or invalid)
  - **Usage**: Determines which Firebase Remote Config keys are used (e.g., `monitoring_check_interval_dev` vs `monitoring_check_interval_prod`)

### Environment Behavior

- **Development (`ENVIRONMENT=dev`)**: Uses development-specific configuration values
- **Production (`ENVIRONMENT=prod`)**: Uses production-specific configuration values
- **Invalid values**: Automatically defaults to `dev` with a warning message

### Environment Implementation

The environment system is implemented using the `EnvironmentService` for dependency injection:
```python
from src.services.environment_service import EnvironmentService

# Get environment service (injected via DI)
env_service = EnvironmentService()

# Get current environment
env = env_service.get_environment()  # Returns "dev" or "prod"

# Check environment type
if env_service.is_development():
    # Use development settings
    pass

if env_service.is_production():
    # Use production settings
    pass
```

## 📁 Layer Details

### **Config Layer** (`config/`)
**Purpose**: Manage application configuration with Firebase Remote Config support

**Components:**
- `config_manager.py`: Flexible configuration management with multiple modes
- `firebase_config_manager.py`: Firebase Remote Config integration

**Configuration Modes:**
- **LOCAL**: Load from local JSON files (development)
- **FIREBASE**: Load from Firebase Remote Config (production)
- **FIXTURE**: Load from test fixtures (integration testing)
- **FALLBACK**: Test fallback scenarios with invalid fixtures

**Key Features:**
- **Environment-aware**: Different settings for dev/prod environments
- **Automatic loading**: Configuration loaded during instantiation
- **Fallback support**: Falls back to local config if Firebase unavailable
- **Property-based access**: Easy access to configuration values
- **Caching**: Efficient configuration caching
- **Type safety**: Strongly typed configuration properties

**Usage:**
```python
from src.config.config_manager import ConfigManager, ConfigMode

# Production: Firebase Remote Config with environment from ENV var
config = ConfigManager(ConfigMode.FIREBASE)  # Uses ENVIRONMENT env var

# Development: Local JSON with environment from ENV var
config = ConfigManager(ConfigMode.LOCAL)  # Uses ENVIRONMENT env var

# Testing: Fixture files with specific environment
config = ConfigManager(ConfigMode.FIXTURE, environment='dev')

# Access configuration
accounts = config.accounts
check_interval = config.check_interval
telegram_enabled = config.telegram_enabled
```

**Responsibilities:**
- Load configuration from multiple sources
- Provide environment-specific settings
- Handle configuration fallbacks
- Cache configuration for performance
- Validate configuration values
- Support real-time configuration updates (Firebase)

### **Models Layer** (`models/`)
**Purpose**: Define data structures and business entities

**Components:**
- `tweet.py`: Tweet data model with validation and serialization
- `telegram_message.py`: Telegram request/response data models

**Responsibilities:**
- Define data structures
- Implement validation logic
- Handle serialization/deserialization
- Ensure data integrity

### **Services Layer** (`services/`)
**Purpose**: External interactions and business logic

**Components:**
- `browser_manager.py`: Playwright browser lifecycle management with conditional headless/non-headless configurations, domain-specific cookie injection, rate limiting, and context pooling
- `pool_manager.py`: PoolManager for efficient, domain-specific browser context pooling
- `context_pool.py`: ContextPool for per-domain context reuse and cleanup
- `twitter_scraper.py`: Twitter-specific scraping logic with anti-detection
- `notification_service.py`: Notification delivery system with retry logic
- `telegram_notification_service.py`: Telegram-specific notification service with exponential backoff
- `http_client.py`: Reusable HTTP client for external APIs
- `rate_limiter.py`: Domain-specific rate limiting with intelligent backoff strategies
- `logger_service.py`: Robust, centralized logging system for all core services and modules
- `firebase_log_service.py`: Firebase integration for remote log storage and monitoring

**Responsibilities:**
- Manage external dependencies (browser, APIs)
- Implement platform-specific logic
- Handle communication with external services
- Provide business logic implementation
- Implement anti-detection measures (domain-specific rate limiting, user agent rotation)
- Manage domain-specific cookie injection and authentication
- Efficiently pool and reuse browser contexts per domain for high concurrency
- Manage request timing and delays
- Implement conditional browser configurations for headless vs non-headless modes
- Implement a robust, centralized logging system for all core services and modules
- Provide remote logging capabilities via Firebase Firestore and Storage

### **Repository Layer** (`repositories/`)
**Purpose**: Data persistence and state management

**Components:**
- `tweet_repository.py`: Tweet data storage and retrieval

**Responsibilities:**
- Persist application state
- Manage data lifecycle
- Provide data access patterns
- Handle state synchronization

### **Core Layer** (`core/`)
**Purpose**: Application orchestration and workflow management

**Components:**
- `monitor.py`: Main monitoring workflow and coordination

**Responsibilities:**
- Coordinate between layers
- Manage application lifecycle
- Implement main workflows
- Handle error recovery
- Process all accounts in each monitoring cycle
- Manage efficient resource usage with context pooling

## 🔄 Data Flow

```
Config → Core → Services → Repositories
  ↑        ↓        ↓          ↓
Models ← Core ← Services ← Repositories
```

1. **Configuration** provides settings to all layers
2. **Core** orchestrates the monitoring workflow
3. **Services** handle external interactions
4. **Repositories** persist state and data
5. **Models** ensure data integrity throughout

## 🔥 Firebase Logging Service

The `FirebaseLogService` provides remote logging capabilities for centralized log management and monitoring.

### **Features**
- **Dual Storage**: Individual logs to Cloud Firestore, complete files to Firebase Storage
- **Environment-Aware**: Logs include environment (dev/prod) and structured context
- **Auto-Discovery**: Automatically enables/disables based on environment variables
- **Test-Friendly**: Can be disabled for unit tests with `disabled=True` parameter
- **Graceful Degradation**: Falls back to local-only logging if Firebase is unavailable

### **Configuration**
```python
# Environment variables required for Firebase logging
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_PATH=config/service-account.json

# Disable for tests
firebase_logger = FirebaseLogService(disabled=True)

# Enable with logger integration
firebase_logger = FirebaseLogService(logger=logger_service)
```

### **Usage**
```python
from src.services.firebase_log_service import FirebaseLogService

# Individual log entries
await firebase_logger.log_entry(LogLevel.INFO, "Message", {"context": "value"})

# Upload complete log file
await firebase_logger.upload_log_file("logs/app.log")

# Clean up old logs
await firebase_logger.cleanup_old_logs(days_to_keep=30)
```

### **Integration with LoggerService**
The `LoggerService` automatically integrates with `FirebaseLogService`:
- All log calls are sent to Firebase (when enabled)
- Log files are uploaded after each monitoring cycle
- Firebase failures don't break local logging

## 🎯 Design Principles

### **Dependency Inversion**
- High-level modules don't depend on low-level modules
- Both depend on abstractions
- Abstractions don't depend on details

### **Single Responsibility**
- Each class has one reason to change
- Clear separation of concerns
- Focused, testable components

### **Open/Closed Principle**
- Open for extension, closed for modification
- Easy to add new platforms (Facebook, Instagram, etc.)
- Easy to add new notification methods

### **Interface Segregation**
- Clients depend only on interfaces they use
- Clean, focused interfaces
- Easy to mock for testing

## 🚀 Extensibility Points

### **Adding New Platforms**
1. Create new scraper in `services/` (e.g., `facebook_scraper.py`)
2. Add platform-specific models in `models/`
3. Update configuration schema
4. Extend core monitoring logic

### **Adding New Notification Methods**
1. Create new notification service in `services/` (e.g., `slack_notification_service.py`)
2. Add notification models in `models/`
3. Update configuration schema
4. Integrate with existing notification service

### **Adding New Features**
1. Identify the appropriate layer
2. Follow existing patterns
3. Add tests for new functionality
4. Update documentation

### **Adding New Data Sources**
1. Create new repository in `repositories/`
2. Define data models in `models/`
3. Update configuration
4. Integrate with core workflow

## 🧪 Testing Strategy

### **Unit Testing**
- Each layer tested in isolation
- Mocked dependencies
- Fast, reliable tests

### **Integration Testing**
- Test layer interactions
- Use real fixtures
- Validate workflows

### **Test Organization**
- Tests mirror source structure
- Shared fixtures in `conftest.py`
- Real HTML data for realistic testing

## 📋 Development Guidelines

### **Adding New Code**
1. **Choose the right layer** for your functionality
2. **Follow naming conventions** (snake_case for files, PascalCase for classes)
3. **Add type hints** for better IDE support
4. **Write tests** for new functionality
5. **Update documentation** when adding new features
6. **Run code quality checks** before committing

### **Code Organization**
- **One class per file** for clarity
- **Consistent imports** (standard library, third-party, local)
- **Clear docstrings** for public methods
- **Error handling** at appropriate levels

### **Code Quality Standards**
- **Format code** with Black (88 character line length)
- **Sort imports** with isort
- **Follow PEP 8** style guidelines (enforced by flake8)
- **Use type hints** (checked by mypy)
- **Handle exceptions** properly (no bare `except:`)

### **Performance Considerations**
- **Async/await** for I/O operations
- **Caching** for expensive operations
- **Resource management** (browser cleanup, file handles)
- **Memory efficiency** for large datasets

### **Development Workflow**
```bash
# Format code
make format

# Check quality
make lint

# Run tests
make test

# Auto-fix issues
make fix
```

## 🧠 Context Pooling & PoolManager

- **PoolManager**: Manages a pool of browser contexts for each domain, enabling efficient reuse and reducing browser overhead.
- **ContextPool**: Handles the creation, reuse, and cleanup of contexts for each domain.
- **Integration**: Pooling is enabled by default in `BrowserManager` and can be configured or disabled as needed.
- **Usage**:
  - Use `create_context_for_domain(domain)` to get a context (from the pool if enabled)
  - When done, call `return_context_to_pool(domain, context)` to return it for reuse
- **Benefits**: Reduces resource usage, increases throughput, and supports high-concurrency scraping workflows.
- **Context pooling**: All pooling logic is tested with mocks only; no real browser or network calls in unit tests
- **No batching**: Removed legacy batching logic; all accounts processed per cycle

## 🌐 Browser Configuration Modes

The `BrowserManager` implements conditional configurations based on headless mode to optimize for different use cases:

### **Headless Mode** (`headless=True`)
**Purpose**: Production-ready configuration with maximum anti-detection capabilities

**Features**:
- **Anti-detection settings**: `bypass_csp=True`, `ignore_https_errors=True`
- **Privacy headers**: `DNT: "1"` header
- **Browser arguments**: Extensive anti-detection flags
- **User agent rotation**: Random user agent selection
- **Performance optimized**: Disabled images, extensions, plugins

**Use case**: Production monitoring, automated scraping

### **Non-Headless Mode** (`headless=False`)
**Purpose**: Development and debugging configuration (currently limited)

**Features**:
- **Pro-normal-browser settings**: `accept_downloads=True`, `has_touch=False`, `is_mobile=False`
- **Standard headers**: Normal browser headers (`sec-ch-ua`, `sec-fetch-*`)
- **User agent rotation**: Random user agent selection
- **Locale/timezone**: `en-US` locale, `America/New_York` timezone

**Current limitation**: May trigger X.com's privacy extension detection
**Use case**: Development, debugging, visual verification

### **Configuration Logic**
```python
# Headless mode: Anti-detection settings
if self.headless:
    context_settings.update({
        "bypass_csp": True,
        "ignore_https_errors": True,
    })
    context_settings["extra_http_headers"]["DNT"] = "1"

# Non-headless mode: Pro-normal-browser settings
else:
    context_settings.update({
        "accept_downloads": True,
        "has_touch": False,
        "is_mobile": False,
        "locale": "en-US",
        "timezone_id": "America/New_York",
    })
    # Add standard browser headers
```

**Note**: Non-headless mode is currently experiencing detection issues with X.com and is primarily intended for development purposes. Production use should utilize headless mode.

## 📝 Logging System

The codebase uses a comprehensive, production-ready logging system with advanced capabilities for all core services and modules:

### Core Features
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Console Output**: Color-coded, multi-line, and context-rich for easy reading
- **File Output**: All logs are written to `logs/app.log` with automatic rotation
- **Context Support**: Structured context data is logged as pretty-printed JSON
- **Exception Logging**: Full stack traces for errors and exceptions
- **Centralized Management**: Singleton pattern ensures consistent logging across the application
- **Integration**: All services accept an optional `logger` parameter; if not provided, a default logger is used

### Advanced Features

#### JSON Output for Log Aggregation
Enable structured JSON output for machine parsing and log aggregation systems:
```python
from src.services.logger_service import LoggerService

# Enable JSON output
logger = LoggerService(json_output=True)
logger.set_json_output(True)  # Runtime toggle

# JSON log format
{
  "timestamp": "2024-06-07T15:30:45.123456",
  "level": "INFO", 
  "environment": "DEV",
  "message": "Operation completed",
  "context": {"operation": "data_processing", "duration_seconds": 1.234}
}
```

#### Performance/Timing Logging
Built-in timing support for performance monitoring and optimization:
```python
# Context manager for timing code blocks
with logger.timing("database_query"):
    result = database.execute_query()

# Decorator for timing functions (sync and async)
@logger.timeit("api_call")
def call_external_api():
    return requests.get("https://api.example.com")

@logger.timeit("async_operation")
async def async_function():
    await asyncio.sleep(1)
```

#### Runtime Log Rotation with Timestamped Backups
- **Automatic Rotation**: Log files are rotated when they exceed the size limit
- **Timestamped Backups**: Backup files use format `app.log.YYYYMMDD_HHMMSS.log`
- **Configurable**: Set `max_file_size_mb` and `backup_count` during initialization
- **Thread-Safe**: Rotation works correctly with async logging

#### Async Logging Support
Non-blocking logging for high-performance applications:
```python
# Async logging methods
logger.info_async("Message", {"context": "value"})
logger.error_async("Error occurred", {"error": str(e)})
logger.log_exception_async("Exception", exception, {"context": "value"})
```

### LoggerService Usage

```python
from src.services.logger_service import LoggerService

# Get the singleton instance
logger = LoggerService.get_instance()

# Basic logging
logger.info("Something happened", {"context": "value"})
logger.error("Something failed", {"error": str(e)})

# Performance logging
with logger.timing("operation_name"):
    # Your code here
    pass

# JSON output for log aggregation
logger.set_json_output(True)
logger.info("Structured log", {"metric": "value"})
```

### Service Integration Example

```python
from src.services.browser_manager import BrowserManager
from src.services.logger_service import LoggerService

logger = LoggerService.get_instance()
browser_manager = BrowserManager(headless=True, logger=logger)
```

### Configuration
```python
# Custom logger configuration
logger = LoggerService(
    log_file_path="logs/custom.log",
    max_file_size_mb=50,      # 50MB before rotation
    backup_count=10,          # Keep 10 backup files
    json_output=False         # Human-readable format
)
```

All log files are stored in `logs/` (ignored by git). The logging system is robust, extensible, and easy to use throughout the codebase.

## 🛠️ Service Registration & Dependency Injection

This project uses a robust **Dependency Injection (DI)** pattern to manage all core services, making the codebase modular, testable, and easy to extend.

### How It Works
- All services (Logger, Config, Notification, Scraper, etc.) are registered in one place: `src/services/service_registration.py` (the "composition root").
- The custom `ServiceProvider` class manages singleton and transient service lifetimes, ensuring thread safety and explicit wiring.
- Services are injected via constructors—no hidden singletons or fallback instantiation.
- Environment management is handled by the `EnvironmentService`, which is injected where needed.

### Example: Registering and Using Services

```python
from src.services.service_registration import setup_services

provider = setup_services()
logger = provider.get(LoggerService)
config = provider.get(ConfigManager)
notification = provider.get(NotificationService)
```

**Adding a New Service:**
1. Register it in `service_registration.py` using `provider.register_singleton(...)`.
2. Inject it into consumers via constructor arguments.

### Environment Management
- The `EnvironmentService` provides environment info (`dev`/`prod`) and is injected into services that need it.
- No direct environment variable access in business logic—always use the service.

### Benefits
- **Explicit dependencies**: No hidden state or magic singletons.
- **Testability**: All services can be mocked or swapped in tests.
- **Environment safety**: No accidental production/test config leaks.
- **Maintainability**: All wiring is in one place, easy to audit and change.

### Migration Note
All legacy fallback logic and the old `env_helper.py` have been removed. All services now require explicit injection of their dependencies. All environment checks use `EnvironmentService`. All tests use explicit DI. All documentation is up to date.