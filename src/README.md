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

## 📁 Layer Details

### **Config Layer** (`config/`)
**Purpose**: Manage application configuration and settings

**Components:**
- `config_manager.py`: Load and validate JSON configuration
- Handles defaults, validation, and configuration caching

**Responsibilities:**
- Load configuration from files
- Provide fallback defaults
- Validate configuration values
- Cache configuration for performance

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
- `browser_manager.py`: Playwright browser lifecycle management with domain-specific cookie injection, rate limiting, and context pooling
- `pool_manager.py`: PoolManager for efficient, domain-specific browser context pooling
- `context_pool.py`: ContextPool for per-domain context reuse and cleanup
- `twitter_scraper.py`: Twitter-specific scraping logic with anti-detection
- `notification_service.py`: Notification delivery system with retry logic
- `telegram_notification_service.py`: Telegram-specific notification service with exponential backoff
- `http_client.py`: Reusable HTTP client for external APIs
- `rate_limiter.py`: Domain-specific rate limiting with intelligent backoff strategies

**Responsibilities:**
- Manage external dependencies (browser, APIs)
- Implement platform-specific logic
- Handle communication with external services
- Provide business logic implementation
- Implement anti-detection measures (domain-specific rate limiting, user agent rotation)
- Manage domain-specific cookie injection and authentication
- Efficiently pool and reuse browser contexts per domain for high concurrency
- Manage request timing and delays

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

### **Code Organization**
- **One class per file** for clarity
- **Consistent imports** (standard library, third-party, local)
- **Clear docstrings** for public methods
- **Error handling** at appropriate levels

### **Performance Considerations**
- **Async/await** for I/O operations
- **Caching** for expensive operations
- **Resource management** (browser cleanup, file handles)
- **Memory efficiency** for large datasets

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