# X (Twitter) Feed Monitor

A web scraping tool to monitor new posts from multiple X/Twitter accounts using Playwright. This tool avoids the need for Twitter's API by scraping the public timeline using a headless browser.

## Project Structure

```
x-web-scraping/
├── x_feed_monitor.py      # Main Python script
├── test_monitor.py        # Test script
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── notebooks/
    └── x_feed_monitor.ipynb  # Original Jupyter notebook (POC)
```

## Features

- **API-Free**: No Twitter API required
- **Multi-Account Monitoring**: Monitor multiple accounts simultaneously
- **Random Sampling**: Avoids detection by randomly sampling accounts
- **State Persistence**: Saves and loads monitoring state
- **CDMX Government Focus**: Pre-configured with Mexico City government accounts
- **Extensible**: Easy to add new accounts or modify behavior

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

## Usage

### Basic Usage

Run the monitor with default settings:
```bash
python x_feed_monitor.py
```

### Testing

Test the monitor with a single account:
```bash
python test_monitor.py
```

### Original Notebook

The original proof-of-concept Jupyter notebook is available in the `notebooks/` folder:
```bash
jupyter notebook notebooks/x_feed_monitor.ipynb
```

### Custom Usage

```python
from x_feed_monitor import XFeedMonitor
import asyncio

async def custom_monitor():
    monitor = XFeedMonitor(headless=False)  # Set to False to see browser
    
    try:
        # Monitor a single user
        await monitor.monitor_single_user("nasa", check_interval=30)
        
        # Or monitor random users from pool
        await monitor.monitor_random_users(check_interval=60, sample_size=5)
        
    except KeyboardInterrupt:
        monitor.save_state()
    finally:
        await monitor.cleanup()

asyncio.run(custom_monitor())
```

## Configuration

### Account Pool

The default account pool includes 40+ CDMX government accounts. You can modify the `user_pool` list in the `XFeedMonitor` class:

```python
monitor = XFeedMonitor()
monitor.user_pool = ["account1", "account2", "account3"]
```

### Monitoring Parameters

- `check_interval`: Seconds between monitoring cycles (default: 60)
- `sample_size`: Number of accounts to check per cycle (default: 5)
- `headless`: Whether to run browser in headless mode (default: True)

## State Management

The monitor automatically saves its state to `monitor_state.json` when stopped. This includes:
- Last seen tweets for each account
- Timestamp of last update
- Total number of tracked users

## CDMX Government Accounts

The tool comes pre-configured with official Mexico City government accounts including:

- **Emergency Services**: `Bomberos_CDMX`, `C5_CDMX`, `SSC_CDMX`
- **Transportation**: `MetroCDMX`, `MetrobusCDMX`, `LaSEMOVI`
- **Government**: `GobCDMX`, `ClaraBrugadaM`
- **Environment**: `SEDEMA_CDMX`
- **Health**: `SSaludCdMx`
- **And many more...**

## Error Handling

The monitor includes robust error handling:
- Network timeouts
- Page load failures
- Account access issues
- Graceful shutdown on Ctrl+C

## Legal Considerations

This tool is for educational and research purposes. Please ensure compliance with:
- Twitter's Terms of Service
- Local laws and regulations
- Respect for rate limits and server resources

## Contributing

Feel free to extend this tool with:
- Additional notification methods (email, Slack, etc.)
- More sophisticated content parsing
- Database storage
- Web interface
- Additional account sources
