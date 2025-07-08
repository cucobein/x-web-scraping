# X (Twitter) Feed Monitor

A web scraping tool to monitor new posts from multiple X/Twitter accounts using Playwright. This tool avoids the need for Twitter's API by scraping the public timeline using a headless browser.

## 🏗️ Project Structure

```
x-web-scraping/
├── src/                   # Main application package
│   ├── config/           # Configuration management
│   ├── core/             # Core monitoring logic
│   ├── models/           # Data models
│   ├── repositories/     # Data persistence
│   └── services/         # External services (browser, scraper, notifications)
├── config/               # Configuration files
├── scripts/              # Utility scripts
├── tests/                # Test suite with real HTML fixtures
├── notebooks/            # Jupyter notebooks
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## ✨ Features

- **API-Free**: No Twitter API required
- **Authenticated Scraping**: Uses browser cookies for authenticated access to X.com
- **Multi-Account Monitoring**: Monitor multiple accounts simultaneously
- **Telegram Notifications**: Real-time alerts via Telegram bot with retry logic
- **Anti-Detection**: Rate limiting, user agent rotation, and random delays
- **Browser Management**: Intelligent browser lifecycle management with Playwright
- **Conditional Browser Modes**: Optimized configurations for headless (production) and non-headless (development) modes
- **Fresh Context Strategy**: Creates fresh browser contexts for each account to ensure reliability
- **Configurable**: JSON-based configuration for accounts and settings
- **State Persistence**: Saves and loads monitoring state
- **CDMX Government Focus**: Pre-configured with Mexico City government accounts
- **Extensible**: Modular architecture for easy extension
- **Tested**: Comprehensive test suite with real HTML fixtures
- **Git LFS**: Large HTML fixtures properly version controlled

## 🚀 Quick Start

### Environment Setup

1. **Copy the environment template:**
   ```bash
   cp .env.template .env
   ```

2. **Configure your environment:**
   Edit `.env` and set the `ENVIRONMENT` variable:
   - `ENVIRONMENT=dev` - Development environment (default)
   - `ENVIRONMENT=prod` - Production environment

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

3. **Setup Git LFS (if not already done):**
   ```bash
   git lfs install
   git lfs pull  # Download HTML fixtures
   ```

### Basic Usage

1. **Export your X.com cookies** (see Cookie Setup section below)

2. **Run the monitor with default settings:**
   ```bash
   python main.py
   ```

### Testing

Run the comprehensive test suite:
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run with coverage
python -m pytest --cov=src
```

### Code Quality

The project uses several tools to maintain code quality:

```bash
# Install development dependencies (includes linting tools)
make install-dev

# Format code automatically
make format

# Check code quality
make lint

# Auto-fix issues
make fix

# Run all checks
make check
```

**Available tools:**
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Style and error checking
- **mypy**: Type checking
- **pre-commit**: Git hooks for automatic checks

### Development Setup

For a complete development environment setup:

```bash
# Complete setup (installs dependencies + pre-commit hooks)
make setup

# See all available commands
make help
```

**Pre-commit hooks** will automatically run on every commit to ensure code quality.

## 📁 Documentation

- **[Source Code](src/README.md)**: Detailed architecture and development guide
- **[Development Guide](DEVELOPMENT.md)**: Complete development setup and workflow
- **[Linting Guide](LINTING.md)**: Quick reference for code quality tools
- **[Scripts](scripts/README.md)**: Utility scripts for development and testing
- **[Tests](tests/README.md)**: Comprehensive testing documentation
- **[Configuration](config/)**: Configuration files and settings

## 🌐 Browser Modes

The application supports two browser modes optimized for different use cases:

### **Headless Mode** (Production)
- **Default**: `headless=True` in configuration
- **Purpose**: Production monitoring and automated scraping
- **Features**: 
  - Maximum anti-detection capabilities
  - Privacy-bypassing settings for stealth operation
  - Performance optimized (disabled images, extensions)
  - User agent rotation
- **Status**: ✅ Fully functional and production-ready

### **Non-Headless Mode** (Development)
- **Configuration**: `headless=False` in configuration
- **Purpose**: Development, debugging, and visual verification
- **Features**:
  - Pro-normal-browser settings
  - Standard browser headers
  - User agent rotation
  - Visual browser window for debugging
- **Status**: ⚠️ Currently experiencing detection issues with X.com
- **Note**: Primarily intended for development purposes. Production use should utilize headless mode.

### **Mode Selection**
The browser mode is controlled by the `headless` parameter in the configuration:
```python
# Production (recommended)
browser_manager = BrowserManager(headless=True)

# Development (limited functionality)
browser_manager = BrowserManager(headless=False)
```

## 🍪 Cookie Setup

### Domain-Specific Cookie Management

The app now supports domain-specific cookie injection for different platforms. Each domain can have its own cookie configuration:

#### X.com/Twitter Cookies

To enable authenticated scraping for X.com, export your cookies:

1. **Open Chrome/Edge** and go to `https://x.com`
2. **Log in** to your X.com account
3. **Open DevTools** (F12 or right-click → Inspect)
4. **Go to Application/Storage tab** → Cookies → `https://x.com`
5. **Export the following cookies** to `config/twitter_cookies.json`:
   - `auth_token` (essential for authentication)
   - `ct0` (CSRF token)
   - Any other cookies for `.x.com` domain

#### Adding Support for Other Domains

To add cookie support for new domains (Facebook, Instagram, YouTube, etc.):
1. Create a cookie file: `config/{domain}_cookies.json`
2. Export cookies for that domain
3. The browser manager will automatically load and inject domain-specific cookies

**Example cookie format:**
```json
[
  {
    "name": "auth_token",
    "value": "your_auth_token_here",
    "domain": ".x.com",
    "path": "/",
    "secure": true,
    "httpOnly": false,
    "sameSite": "Lax"
  },
  {
    "name": "ct0",
    "value": "your_csrf_token_here", 
    "domain": ".x.com",
    "path": "/",
    "secure": true,
    "httpOnly": false,
    "sameSite": "Lax"
  }
]
```

**Important Notes:**
- Cookies expire periodically - you may need to refresh them
- Keep your cookies secure and don't share them
- The tool will work without cookies but with limited access

## 🌍 Environment Management

The application uses environment-based configuration to support different deployment scenarios.

### Environment Variables

The application uses a single environment variable to determine the configuration context:

- **`ENVIRONMENT`**: Controls which environment-specific settings are loaded
  - **Valid values**: `dev`, `prod`
  - **Default**: `dev` (if not set or invalid)
  - **Usage**: Determines which Firebase Remote Config keys are used (e.g., `monitoring_check_interval_dev` vs `monitoring_check_interval_prod`)

### Environment Setup

1. **Copy the template:**
   ```bash
   cp .env.template .env
   ```

2. **Configure your environment:**
   ```bash
   # For development
   ENVIRONMENT=dev
   
   # For production
   ENVIRONMENT=prod
   ```

### Environment Behavior

- **Development (`ENVIRONMENT=dev`)**: Uses development-specific configuration values
- **Production (`ENVIRONMENT=prod`)**: Uses production-specific configuration values
- **Invalid values**: Automatically defaults to `dev` with a warning message

The environment variable is used throughout the application to:
- Load environment-specific Firebase Remote Config values
- Create environment-specific configuration keys
- Determine which settings to use for monitoring, notifications, and other features

## ⚙️ Configuration

The application supports multiple configuration modes for different environments:

### Configuration Modes

The application uses a flexible configuration system with the following modes:

- **LOCAL**: Load configuration from local JSON files (default for development)
- **FIREBASE**: Load configuration from Firebase Remote Config (production)
- **FIXTURE**: Load configuration from test fixtures (integration testing)
- **FALLBACK**: Test fallback scenarios with invalid fixtures

### Local Configuration

For development and testing, edit `config/config.json`:
```json
{
  "accounts": [
    "GobCDMX",
    "MetroCDMX", 
    "Bomberos_CDMX"
  ],
  "check_interval": 60,
  "headless": true,
  "page_timeout": 5000,
  "telegram": {
    "endpoint": "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
    "api_key": "your-api-key-here"
  }
}
```

### Firebase Remote Config (Production)

For production environments, the application uses Firebase Remote Config for centralized configuration management:

- **Environment-aware**: Different settings for dev/prod environments
- **Real-time updates**: Configuration can be updated without redeployment
- **Fallback support**: Falls back to local config if Firebase is unavailable
- **Secure**: Uses Firebase service account authentication

**Firebase Configuration Keys:**
- `monitoring_check_interval_dev/prod`: Seconds between monitoring cycles
- `monitoring_headless_dev/prod`: Whether to run browser in headless mode
- `monitoring_page_timeout_dev/prod`: Page load timeout in milliseconds
- `twitter_accounts_dev/prod`: JSON array of accounts to monitor
- `telegram_endpoint_dev/prod`: Telegram notification API endpoint
- `telegram_api_key_dev/prod`: Telegram API key for authentication

### Configuration Properties

The application provides easy access to configuration through properties:

```python
from src.config.config_manager import ConfigManager, ConfigMode

# Create config manager with Firebase mode (production)
config = ConfigManager(ConfigMode.FIREBASE, environment='prod')

# Access configuration values
check_interval = config.check_interval      # int
headless = config.headless                  # bool
page_timeout = config.page_timeout          # int
accounts = config.accounts                  # List[str]
telegram_endpoint = config.telegram_endpoint # str
telegram_api_key = config.telegram_api_key  # str
telegram_enabled = config.telegram_enabled  # bool
```

### Monitoring Parameters

- `check_interval`: Seconds between monitoring cycles (default: 60)
- `headless`: Whether to run browser in headless mode (default: True)
- `page_timeout`: Page load timeout in milliseconds (default: 5000)
- `accounts`: List of Twitter accounts to monitor

### Telegram Notifications

Configure Telegram notifications in your configuration:
- `telegram.endpoint`: Telegram notification API endpoint
- `telegram.api_key`: Your API key for authentication

When enabled, the monitor will send real-time notifications to Telegram whenever new tweets are detected. The notification service includes:
- **Retry Logic**: Exponential backoff for failed API calls
- **Error Handling**: Graceful handling of API failures
- **Message Formatting**: Rich formatting with tweet content and metadata

## 🏛️ CDMX Government Accounts

The tool comes pre-configured with official Mexico City government accounts including:

- **Emergency Services**: `Bomberos_CDMX`, `C5_CDMX`, `SSC_CDMX`
- **Transportation**: `MetroCDMX`, `MetrobusCDMX`, `LaSEMOVI`
- **Government**: `GobCDMX`, `ClaraBrugadaM`
- **Environment**: `SEDEMA_CDMX`
- **Health**: `SSaludCdMx`
- **And many more...**

## 🧪 Testing Architecture

### Comprehensive Test Suite
The application includes a comprehensive test suite with multiple testing strategies:

- **Unit Tests**: Individual component testing with mocked dependencies
- **Integration Tests**: Component interaction testing with real fixtures
- **Configuration Testing**: Tests for all configuration modes (LOCAL, FIREBASE, FIXTURE, FALLBACK)

### Configuration Testing
The test suite includes specialized tests for the configuration system:

- **LOCAL Mode**: Tests local JSON configuration loading
- **FIXTURE Mode**: Tests configuration loading from captured Firebase fixtures
- **FALLBACK Mode**: Tests fallback scenarios when primary config fails
- **Property Access**: Tests all configuration properties work correctly

### Real Data Testing
- Uses actual HTML snapshots from Twitter profiles
- Catches DOM changes when Twitter updates their site
- Comprehensive test coverage with realistic scenarios
- Git LFS manages large HTML fixtures automatically

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Fixtures**: Real HTML data for testing
- **Configuration Tests**: All configuration modes and scenarios

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run with coverage
python -m pytest --cov=src

# Run specific test categories
python -m pytest tests/unit/           # Unit tests only
python -m pytest tests/integration/    # Integration tests only
```

## 🔧 Development

### Architecture
The application follows a **Clean Architecture** pattern:
- **Config Layer**: Configuration management
- **Models Layer**: Data structures and validation
- **Services Layer**: External interactions and business logic
- **Repository Layer**: Data persistence
- **Core Layer**: Application orchestration

### Adding New Features
1. **Choose the right layer** for your functionality
2. **Follow existing patterns** and conventions
3. **Add tests** for new functionality
4. **Update documentation** when adding features

### Extensibility Points
- **New Platforms**: Easy to add Facebook, Instagram, YouTube, etc.
- **New Services**: Notification methods, data sources, etc.
- **New Features**: Monitoring strategies, data processing, etc.

## 📊 State Management

The monitor automatically saves its state to `monitor_state.json` when stopped. This includes:
- Last seen tweets for each account
- Timestamp of last update
- Total number of tracked users

## 🛡️ Error Handling & Anti-Detection

The monitor includes robust error handling and anti-detection measures:
- **Network timeouts and retries**: Exponential backoff for failed requests
- **Page load failures**: Graceful handling of network issues
- **Account access issues**: Proper error reporting and recovery
- **Domain-specific rate limiting**: Intelligent backoff strategies per domain
- **User agent rotation**: Random browser user agents to avoid detection
- **Random delays**: Unpredictable timing between requests
- **Domain-specific cookie injection**: Authenticated access per platform
- **Graceful shutdown**: Clean shutdown on Ctrl+C
- **Comprehensive logging**: Detailed error reporting and monitoring

## ⚖️ Legal Considerations

This tool is for educational and research purposes. Please ensure compliance with:
- Twitter's Terms of Service
- Local laws and regulations
- Respect for rate limits and server resources

## 🤝 Contributing

Feel free to extend this tool with:
- Additional notification methods (email, Slack, etc.)
- More sophisticated content parsing
- Database storage
- Web interface
- Additional account sources
- New social media platforms

## 📈 Future Roadmap

- [x] **Telegram notifications**: Real-time alerts via Telegram bot with retry logic
- [x] **Anti-detection measures**: Rate limiting, user agent rotation, random delays
- [x] **Browser management**: Intelligent browser lifecycle management
- [x] **Comprehensive testing**: Unit and integration tests with real HTML fixtures
- [x] **Domain-specific rate limiting**: Intelligent backoff strategies per domain
- [x] **Domain-specific cookie injection**: Authenticated access per platform
- [x] **Headless mode reliability**: Fixed context corruption issues with fresh context strategy
- [x] **Firebase Remote Config**: Centralized configuration management with environment support
- [x] **Flexible configuration system**: Multiple modes (LOCAL, FIREBASE, FIXTURE, FALLBACK)
- [x] **Configuration testing**: Comprehensive tests for all configuration scenarios
- [ ] **Multi-platform support**: Facebook, Instagram, YouTube
- [ ] **Database storage**: Persistent storage for monitoring history
- [ ] **Web interface**: Dashboard for monitoring status
- [ ] **Advanced notifications**: Email, Slack, Discord
- [ ] **Database integration**: PostgreSQL, MongoDB
- [ ] **Web dashboard**: Real-time monitoring interface
- [ ] **AI-powered analysis**: Content sentiment, trend detection
- [ ] **Performance optimization**: Caching, parallel processing

## 🔗 Related Documentation

- **[Source Code Guide](src/README.md)**: Detailed architecture and development
- **[Scripts Documentation](scripts/README.md)**: Utility scripts and tools
- **[Testing Guide](tests/README.md)**: Comprehensive testing documentation
- **[Configuration](config/)**: Settings and configuration files

## 🔄 Monitoring Behavior

The monitor now processes **all accounts in each cycle** for maximum efficiency:

- **No more batching**: Removed the legacy `sample_size` parameter and batching logic
- **Full cycle processing**: Each monitoring cycle processes all configured accounts
- **Rate limiting**: Domain-specific rate limiting handles timing between requests
- **Cycle timing**: `check_interval` controls time between complete cycles
- **Fresh contexts**: Each account gets a fresh browser context for maximum reliability

**Example cycle:**
```
Cycle 1: Process all 12 accounts → Wait 10 seconds
Cycle 2: Process all 12 accounts → Wait 10 seconds
Cycle 3: Process all 12 accounts → Wait 10 seconds
```

This approach eliminates duplicate processing within cycles and lets the sophisticated rate limiter handle all timing concerns.

## 📝 Logging System

The application features a comprehensive, production-ready logging system with advanced capabilities for both development and production use:

### Core Features
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Console Output**: Color-coded and multi-line for readability
- **File Output**: All logs are written to `logs/app.log` with automatic rotation
- **Context Support**: Structured context data is logged as pretty-printed JSON
- **Exception Logging**: Full stack traces for errors and exceptions
- **Centralized Management**: Singleton pattern ensures consistent logging across the application
- **Remote Logging**: Firebase integration for cloud-based log storage and monitoring

### Advanced Features

#### Firebase Remote Logging
The application supports remote logging to Firebase for centralized log management:

**What Gets Logged:**
- **Individual log entries** → Cloud Firestore (database)
- **Complete log files** → Firebase Storage (file storage)

**Setup Requirements:**
1. **Enable Cloud Firestore** in Firebase Console
2. **Enable Firebase Storage** in Firebase Console
3. **Set up security rules** for both services
4. **Generate service account key** and save as JSON file
5. **Set environment variables**:
   ```bash
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_SERVICE_ACCOUNT_PATH=config/your-service-account.json
   ```

**Automatic Behavior:**
- **Enabled by default** when Firebase config is available
- **Auto-disabled** when environment variables are missing
- **Graceful fallback** to local-only logging if Firebase fails
- **Test-friendly** with `disabled=True` parameter for unit tests

**Monitoring Integration:**
- Log files are automatically uploaded after each monitoring cycle
- Individual log entries are sent to Firestore in real-time
- All logs include environment, timestamp, and structured context

#### JSON Output for Log Aggregation
Enable JSON output for machine parsing and log aggregation systems:
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
Built-in timing support for performance monitoring:
```python
# Context manager for timing code blocks
with logger.timing("database_query"):
    result = database.execute_query()

# Decorator for timing functions
@logger.timeit("api_call")
def call_external_api():
    return requests.get("https://api.example.com")

# Async function timing
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

### Example Log Output
```
[2025-07-03 03:26:08] [ERROR] [DEV] An error occurred
  Exception: ValueError: Test error for logging
  Context:
{
  "component": "example"
}
  Traceback:
Traceback (most recent call last):
  ...
ValueError: Test error for logging
```

### Log File Location
- All logs are stored in `logs/app.log` (rotated automatically)
- Backup files: `logs/app.log.20240607_153045.log`, `logs/app.log.20240607_153100.log`, etc.
- The `logs/` directory is ignored by git and will not be committed

### How to Use
- All core services and modules use the logger automatically
- For custom logging, use the `LoggerService` class:
  ```python
  from src.services.logger_service import LoggerService
  
  # Get the singleton instance
  logger = LoggerService.get_instance()
  
  # Basic logging
  logger.info("Something happened", {"context": "value"})
  logger.error("Error occurred", {"error": str(e)})
  
  # Performance logging
  with logger.timing("operation_name"):
      # Your code here
      pass
  
  # JSON output for log aggregation
  logger.set_json_output(True)
  logger.info("Structured log", {"metric": "value"})
  
  # Disable Firebase logging for tests
  logger = LoggerService(firebase_disabled=True)
  ```

### Configuration
```python
# Custom logger configuration
logger = LoggerService(
    log_file_path="logs/custom.log",
    max_file_size_mb=50,      # 50MB before rotation
    backup_count=10,          # Keep 10 backup files
    json_output=False,        # Human-readable format
    firebase_disabled=False   # Enable/disable Firebase logging
)
```
