# Linting Quick Reference

This is a quick reference guide for the code quality tools used in this project.

## 🚀 Quick Commands

```bash
# Complete setup (first time only)
make setup

# Format and check everything
make check

# Format code only
make format

# Check quality only
make lint

# Auto-fix issues
make fix

# See all available commands
make help
```

## 🛠️ Individual Tools

### Black (Code Formatter)
```bash
# Format all Python files
black .

# Format specific file
black src/services/browser_manager.py

# Check what would be formatted (dry run)
black --check .
```

**Configuration**: `pyproject.toml`
- Line length: 88 characters
- Target Python: 3.8+

### isort (Import Sorter)
```bash
# Sort imports in all files
isort .

# Sort imports in specific file
isort src/services/browser_manager.py

# Check what would be sorted (dry run)
isort --check-only .
```

**Configuration**: `pyproject.toml`
- Groups: stdlib, third-party, local
- Line length: 88 characters

### flake8 (Style Checker)
```bash
# Check all Python files
flake8 .

# Check specific file
flake8 src/services/browser_manager.py

# Show error codes
flake8 --show-source .
```

**Configuration**: `.flake8`
- Max line length: 88
- Ignored errors: E203, W503
- Excluded: `__pycache__`, `.git`, `tests/fixtures`

### mypy (Type Checker)
```bash
# Check types in all files
mypy src/

# Check specific file
mypy src/services/browser_manager.py

# Show error details
mypy --show-error-codes src/
```

**Configuration**: `pyproject.toml`
- Python version: 3.8+
- Strict mode: enabled
- Ignore missing imports for external libraries

### pre-commit (Git Hooks)
```bash
# Install hooks
pre-commit install

# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black

# Run hooks on staged files only
pre-commit run
```

**Configuration**: `.pre-commit-config.yaml`
- Runs automatically on commit
- Includes: black, isort, flake8, mypy, trailing-whitespace, end-of-file-fixer

## 🔧 Common Issues & Solutions

### Import Errors
```bash
# Problem: Import not found
from src.services.browser_manager import BrowserManager

# Solution: Add to pyproject.toml [tool.mypy] section
[[tool.mypy.overrides]]
module = "playwright.*"
ignore_missing_imports = true
```

### Line Length Issues
```bash
# Problem: Line too long
very_long_variable_name = some_very_long_function_call_with_many_parameters()

# Solution: Break into multiple lines
very_long_variable_name = (
    some_very_long_function_call_with_many_parameters()
)
```

### Type Annotation Issues
```python
# Problem: Missing type hints
def process_data(data):
    return data.upper()

# Solution: Add type hints
def process_data(data: str) -> str:
    return data.upper()
```

### Exception Handling
```python
# Problem: Bare except
try:
    risky_operation()
except:
    pass

# Solution: Specific exception
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Value error: {e}")
```

## 📋 Pre-commit Workflow

1. **Make changes** to your code
2. **Stage files**: `git add .`
3. **Commit**: `git commit -m "your message"`
4. **Pre-commit hooks run automatically**
5. **If hooks fail**: Fix issues and commit again

### Manual Pre-commit Check
```bash
# Check before committing
pre-commit run --all-files

# If issues found, fix them:
make fix
pre-commit run --all-files
```

## 🎯 IDE Integration

### VS Code
Add to `.vscode/settings.json`:
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm
- Install Black plugin
- Configure external tools for Black, isort, flake8
- Enable "Format on Save"

## 📚 Tool Documentation

- **[Black](https://black.readthedocs.io/)**: Code formatter
- **[isort](https://pycqa.github.io/isort/)**: Import sorter
- **[flake8](https://flake8.pycqa.org/)**: Style checker
- **[mypy](https://mypy.readthedocs.io/)**: Type checker
- **[pre-commit](https://pre-commit.com/)**: Git hooks

## 🚨 Troubleshooting

### Hooks Not Running
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### Configuration Issues
```bash
# Check tool versions
black --version
isort --version
flake8 --version
mypy --version
pre-commit --version

# Update tools
pip install --upgrade black isort flake8 mypy pre-commit
```

### Performance Issues
```bash
# Run only changed files
pre-commit run --files src/services/browser_manager.py

# Skip slow hooks temporarily
SKIP=mypy git commit -m "skip type checking"
``` 