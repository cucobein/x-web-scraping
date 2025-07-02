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
- **Context Pooling**: Efficient, domain-specific browser context pooling for high concurrency and resource reuse
- **Configurable**: JSON-based configuration for accounts and settings
- **State Persistence**: Saves and loads monitoring state
- **CDMX Government Focus**: Pre-configured with Mexico City government accounts
- **Extensible**: Modular architecture for easy extension
- **Tested**: Comprehensive test suite with real HTML fixtures
- **Git LFS**: Large HTML fixtures properly version controlled
- **Context Pooling**: PoolManager provides efficient reuse of browser contexts per domain, reducing overhead and improving performance for high-frequency or multi-account monitoring. Pooling is enabled by default and can be configured or disabled in the BrowserManager constructor.

## 🚀 Quick Start

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

## 📁 Documentation

- **[Source Code](src/README.md)**: Detailed architecture and development guide
- **[Scripts](scripts/README.md)**: Utility scripts for development and testing
- **[Tests](tests/README.md)**: Comprehensive testing documentation
- **[Configuration](config/)**: Configuration files and settings

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

## ⚙️ Configuration

### Account Management

Edit `config/config.json` to customize:
```json
{
  "accounts": [
    "GobCDMX",
    "MetroCDMX", 
    "Bomberos_CDMX"
  ],
  "check_interval": 60,
  "telegram": {
    "endpoint": "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
    "api_key": "your-api-key-here"
  }
}
```

### Monitoring Parameters

- `check_interval`: Seconds between monitoring cycles (default: 60)
- `headless`: Whether to run browser in headless mode (default: True)

### Telegram Notifications

Configure Telegram notifications in `config/config.json`:
- `telegram.endpoint`: Telegram notification API endpoint
- `telegram.api_key`: Your API key for authentication

When enabled, the monitor will send real-time notifications to Telegram whenever new tweets are detected. The notification service includes:
- **Retry Logic**: Exponential backoff for failed API calls
- **Error Handling**: Graceful handling of API failures
- **Message Formatting**: Rich formatting with tweet content and metadata

### Anti-Detection Features

The monitor includes several anti-detection measures:
- **Domain-Specific Rate Limiting**: Intelligent rate limiting with domain-specific backoff strategies
- **User Agent Rotation**: Random browser user agents to avoid detection
- **Random Delays**: Unpredictable timing between requests
- **Request Tracking**: Per-domain request counting and limiting
- **Domain-Specific Cookie Injection**: Authenticated access with domain-specific cookie management
- **Dynamic Content Handling**: Smart page loading detection for modern web apps

## 🏛️ CDMX Government Accounts

The tool comes pre-configured with official Mexico City government accounts including:

- **Emergency Services**: `Bomberos_CDMX`, `C5_CDMX`, `SSC_CDMX`
- **Transportation**: `MetroCDMX`, `MetrobusCDMX`, `LaSEMOVI`
- **Government**: `GobCDMX`, `ClaraBrugadaM`
- **Environment**: `SEDEMA_CDMX`
- **Health**: `SSaludCdMx`
- **And many more...**

## 🧪 Testing Architecture

### Real Data Testing
- Uses actual HTML snapshots from Twitter profiles
- Catches DOM changes when Twitter updates their site
- Comprehensive test coverage with realistic scenarios
- Git LFS manages large HTML fixtures automatically

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Fixtures**: Real HTML data for testing

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
- [ ] **Context pooling**: Efficient browser context reuse and management
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

## 🧠 Advanced: Context Pooling & PoolManager

The app supports **domain-specific browser context pooling** for maximum efficiency and scalability:

- **PoolManager**: Manages a pool of browser contexts for each domain (e.g., x.com, twitter.com)
- **ContextPool**: Handles creation, reuse, and cleanup of contexts for each domain
- **Automatic Integration**: Pooling is enabled by default; you can disable it by passing `enable_pooling=False` to `BrowserManager`
- **Usage**:
  - Use `create_context_for_domain(domain)` to get a context (from the pool if enabled)
  - When done, call `return_context_to_pool(domain, context)` to return it for reuse
- **Configuration**: Pool size is configurable via `max_contexts_per_domain` in `BrowserManager`
- **Benefits**: Reduces browser overhead, increases throughput, and supports high-concurrency scraping

## 🔄 Monitoring Behavior

The monitor now processes **all accounts in each cycle** for maximum efficiency:

- **No more batching**: Removed the legacy `sample_size` parameter and batching logic
- **Full cycle processing**: Each monitoring cycle processes all configured accounts
- **Rate limiting**: Domain-specific rate limiting handles timing between requests
- **Cycle timing**: `check_interval` controls time between complete cycles
- **Context pooling**: Efficient browser context reuse across all accounts

**Example cycle:**
```
Cycle 1: Process all 12 accounts → Wait 10 seconds
Cycle 2: Process all 12 accounts → Wait 10 seconds
Cycle 3: Process all 12 accounts → Wait 10 seconds
```

This approach eliminates duplicate processing within cycles and lets the sophisticated rate limiter handle all timing concerns.
