# Scripts Directory

This directory contains utility scripts for development, testing, and maintenance tasks.

## 📁 Contents

### `capture_fixtures.py`
**Purpose**: Capture real HTML snapshots from social media profiles for testing

**What it does:**
- Uses Playwright to visit Twitter profiles
- Captures the full HTML content
- Saves it as fixtures for testing
- Ensures tests use realistic data

**Usage:**
```bash
# Capture a specific profile
python scripts/capture_fixtures.py nasa

# Capture multiple profiles
python scripts/capture_fixtures.py nasa GobCDMX MetroCDMX

# Capture with custom output path
python scripts/capture_fixtures.py nasa --output custom_path.html
```

**Output:**
- Creates HTML files in `tests/fixtures/twitter/`
- Files are ~500KB+ each (real Twitter HTML is large)
- Automatically tracked with Git LFS

**Why this matters:**
- Tests use real HTML instead of mocks
- Catches when Twitter changes their DOM structure
- Provides realistic test scenarios
- Documents actual HTML structure

## 🔧 Development Workflow

### When to use:
- **Adding new test fixtures** for new accounts
- **Updating existing fixtures** when tests fail due to HTML changes
- **Debugging parsing issues** by examining real HTML
- **Documentation** of current HTML structure

### Best practices:
- **Be respectful**: Add delays between requests
- **Use real accounts**: Capture from actual profiles
- **Keep fixtures current**: Update when tests break
- **Version control**: Fixtures are tracked with Git LFS

## 🚀 Future Scripts

This directory is ready for additional utilities:
- **Database migration scripts**
- **Data analysis tools**
- **Performance benchmarking**
- **Deployment automation**
- **Monitoring setup scripts**

## 📋 Script Requirements

All scripts in this directory should:
- **Be self-contained**: Minimal external dependencies
- **Have clear documentation**: Explain purpose and usage
- **Follow project conventions**: Use same coding standards
- **Be testable**: Include tests where appropriate
- **Handle errors gracefully**: Provide useful error messages 