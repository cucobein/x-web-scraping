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
- **Multi-Account Monitoring**: Monitor multiple accounts simultaneously
- **Telegram Notifications**: Real-time alerts via Telegram bot
- **Configurable**: JSON-based configuration for accounts and settings
- **State Persistence**: Saves and loads monitoring state
- **CDMX Government Focus**: Pre-configured with Mexico City government accounts
- **Extensible**: Modular architecture for easy extension
- **Tested**: Comprehensive test suite with real HTML fixtures
- **Git LFS**: Large HTML fixtures properly version controlled

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

Run the monitor with default settings:
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
  "sample_size": 5,
  "telegram": {
    "endpoint": "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
    "api_key": "your-api-key-here"
  }
}
```

### Monitoring Parameters

- `check_interval`: Seconds between monitoring cycles (default: 60)
- `sample_size`: Number of accounts to check per cycle (default: 5)
- `headless`: Whether to run browser in headless mode (default: True)

### Telegram Notifications

Configure Telegram notifications in `config/config.json`:
- `telegram.endpoint`: Telegram notification API endpoint
- `telegram.api_key`: Your API key for authentication

When enabled, the monitor will send real-time notifications to Telegram whenever new tweets are detected.

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

## 🛡️ Error Handling

The monitor includes robust error handling:
- Network timeouts and retries
- Page load failures
- Account access issues
- Graceful shutdown on Ctrl+C
- Comprehensive logging

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

- [x] **Telegram notifications**: Real-time alerts via Telegram bot
- [ ] **Multi-platform support**: Facebook, Instagram, YouTube
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
