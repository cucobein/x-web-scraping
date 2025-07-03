# Development Guide

This guide covers the complete development setup, code quality tools, and workflow for the X Feed Monitor project.

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd x-web-scraping

# Complete development setup
make setup
```

This will:
- Install all dependencies (including linting tools)
- Install Playwright browsers
- Set up pre-commit hooks
- Configure the development environment

### 2. Verify Setup

```bash
# Check that everything is working
make help
make check
```

## 🛠️ Development Tools

### Code Quality Tools

The project uses several tools to maintain high code quality:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Black** | Code formatting | `pyproject.toml` |
| **isort** | Import sorting | `pyproject.toml` |
| **flake8** | Style and error checking | `.flake8` |
| **mypy** | Type checking | `pyproject.toml` |
| **pre-commit** | Git hooks | `.pre-commit-config.yaml` |

### Available Commands

```bash
# Format code
make format

# Check code quality
make lint

# Auto-fix issues
make fix

# Run all checks
make check

# Run tests
make test

# Run tests with coverage
make test-coverage

# Clean up generated files
make clean

# See all available commands
make help
```

## 🔄 Development Workflow

### 1. Before Starting Work

```bash
# Ensure you're on the latest code
git pull origin main

# Check current code quality
make check
```

### 2. During Development

```bash
# Format your code as you work
make format

# Check for issues
make lint

# Run tests
make test
```

### 3. Before Committing

The pre-commit hooks will automatically:
- Format your code with Black
- Sort imports with isort
- Check style with flake8
- Check types with mypy
- Run basic file checks

If any issues are found, the commit will be blocked until they're fixed.

### 4. Manual Pre-commit Checks

```bash
# Run pre-commit checks manually
pre-commit run --all-files

# Run specific hooks
pre-commit run black
pre-commit run isort
pre-commit run flake8
pre-commit run mypy
```

## 📋 Code Quality Standards

### Code Formatting

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Trailing commas**: Yes, for multi-line structures

### Import Organization

Imports are automatically sorted by isort in this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

### Type Hints

- Use type hints for all function parameters and return values
- Use `Optional[T]` for nullable types
- Use `List[T]`, `Dict[K, V]` for collections

### Error Handling

- Use specific exception types instead of bare `except:`
- Log errors with context information
- Use proper error messages

## 🔧 Configuration Files

### pyproject.toml

Contains configuration for:
- **Black**: Code formatting settings
- **isort**: Import sorting configuration
- **mypy**: Type checking settings

### .flake8

Contains:
- Style checking rules
- Ignored error codes
- Excluded directories

### .pre-commit-config.yaml

Defines:
- Pre-commit hooks
- Tool versions
- Hook configurations

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage
make test-coverage

# Run specific test file
python -m pytest tests/unit/test_browser_manager_unit.py

# Run tests matching a pattern
python -m pytest -k "test_browser"
```

### Test Organization

- **Unit tests**: `tests/unit/` - Test individual components
- **Integration tests**: `tests/integration/` - Test component interactions
- **Fixtures**: `tests/fixtures/` - Test data and HTML snapshots

## 🐛 Debugging

### Browser Debugging

```python
# Enable non-headless mode for debugging
browser_manager = BrowserManager(headless=False)
```

**Note**: Non-headless mode currently has detection issues with X.com and is primarily for development.

### Logging

The project uses a comprehensive logging system:

```python
from src.services.logger_service import LoggerService

logger = LoggerService()
logger.info("Debug message", {"context": "value"})
logger.error("Error message", {"error": str(e)})
```

Logs are written to:
- **Console**: Color-coded output
- **File**: `logs/app.log` with automatic rotation

## 📝 Contributing

### Before Submitting Changes

1. **Run all checks**:
   ```bash
   make check
   ```

2. **Run tests**:
   ```bash
   make test
   ```

3. **Ensure pre-commit hooks pass**:
   ```bash
   pre-commit run --all-files
   ```

### Commit Message Format

Use clear, descriptive commit messages:

```
feat: add new browser configuration mode
fix: resolve f-string linting issues
docs: update development guide
test: add unit tests for rate limiter
```

## 🚨 Common Issues

### Import Errors

If you see import errors in your IDE:
1. Ensure you're using the correct Python interpreter
2. Install dependencies: `pip install -r requirements.txt`
3. Restart your IDE

### Pre-commit Hook Failures

If pre-commit hooks fail:
1. Check the error message
2. Run `make fix` to auto-fix issues
3. Manually fix any remaining issues
4. Try committing again

### Type Checking Errors

If mypy reports errors:
1. Add proper type hints
2. Use `# type: ignore` for external libraries
3. Check the mypy configuration in `pyproject.toml`

## 🔄 Continuous Integration

The project is configured to run quality checks automatically:
- Code formatting
- Import sorting
- Style checking
- Type checking
- Unit tests
- Integration tests

## 📚 Additional Resources

- **[Black Documentation](https://black.readthedocs.io/)**: Code formatter
- **[isort Documentation](https://pycqa.github.io/isort/)**: Import sorter
- **[flake8 Documentation](https://flake8.pycqa.org/)**: Style checker
- **[mypy Documentation](https://mypy.readthedocs.io/)**: Type checker
- **[pre-commit Documentation](https://pre-commit.com/)**: Git hooks

## 🤝 Getting Help

If you encounter issues:
1. Check this development guide
2. Review the tool documentation
3. Check existing issues in the repository
4. Create a new issue with detailed information 