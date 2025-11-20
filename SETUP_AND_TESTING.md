# Setup and Testing Guide

## Quick Start

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- **Testing**: pytest, pytest-cov, pytest-asyncio, pytest-mock, coverage
- **Formatting**: black, isort
- **Linting**: ruff
- **Type Checking**: mypy
- **Pre-commit Hooks**: pre-commit

### Format Code

```bash
# Format with Black (100 char line length)
python -m black matilda_cli/ --line-length=100

# Sort imports with isort
python -m isort matilda_cli/ --profile black --line-length=100

# Auto-fix linting issues
python -m ruff check matilda_cli/ --fix --line-length=100
```

### Lint Code

```bash
# Check with Ruff (no auto-fix)
python -m ruff check matilda_cli/ --line-length=100

# View detailed lint errors
python -m ruff check matilda_cli/ --line-length=100 --show-fixes
```

### Type Checking

```bash
# Run mypy (ignore missing imports from external packages)
python -m mypy matilda_cli/algorithms/MATILDA/ --ignore-missing-imports
```

### Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=matilda_cli --cov-report=html

# Run specific test module
python -m pytest tests/algorithms/test_matilda_candidate_rule_chains.py -v

# Run tests excluding slow/benchmark tests
python -m pytest tests/ -v -m "not slow and not benchmark"

# Run only benchmark tests
python -m pytest tests/ -v -m benchmark
```

## Test Structure

Tests are located in the `tests/` directory with the following structure:

```
tests/
├── algorithms/           # Algorithm tests
│   ├── test_matilda_candidate_rule_chains.py
│   ├── test_matilda_constraint_graphs.py
│   ├── test_matilda_main.py
│   └── test_matilda_tgd_discovery.py
├── benchmarks/          # Performance benchmark tests
│   └── test_performance.py
├── database/            # Database utilities tests
│   └── test_alchemy_utility.py
├── fixtures/            # Test fixtures
│   └── test_databases.py
├── integration/         # Integration tests
│   └── test_matilda_integration.py
├── scripts/            # Test scripts
└── conftest.py         # Pytest configuration
```

## pytest Configuration

Configuration is defined in `pytest.ini`:

- **Test paths**: `tests/`
- **Test discovery**: Files matching `test_*.py`, classes matching `Test*`, functions matching `test_*`
- **Markers**:
  - `@pytest.mark.benchmark` - Performance benchmark tests
  - `@pytest.mark.integration` - Integration tests
  - `@pytest.mark.slow` - Tests that take a long time
  - `@pytest.mark.unit` - Fast unit tests
  - `@pytest.mark.database` - Tests requiring database access
- **Options**: `-v --strict-markers --tb=short --disable-warnings`

## Code Quality Tools

### Black (Code Formatting)

Configuration in `pyproject.toml`:
- Line length: 100
- Target Python versions: 3.8, 3.9, 3.10, 3.11, 3.12

### isort (Import Sorting)

Configuration in `pyproject.toml`:
- Profile: black (compatible with Black)
- Line length: 100
- Groups imports into: future, stdlib, third-party, first-party (matilda_cli)

### Ruff (Linting)

Configuration in `pyproject.toml`:
- Line length: 100
- Enabled rules:
  - `E` - pycodestyle errors
  - `W` - pycodestyle warnings
  - `F` - Pyflakes
  - `I` - isort (import sorting)
  - `C` - flake8-comprehensions
  - `B` - flake8-bugbear
  - `UP` - pyupgrade
  - `ARG` - flake8-unused-arguments
  - `SIM` - flake8-simplify
- Ignores: `E501` (line-too-long, handled by Black)

### mypy (Type Checking)

Configuration in `pyproject.toml`:
- Python version: 3.9+
- Strict settings enabled for type safety

## Pre-commit Hooks (Optional)

To enable automatic formatting and linting on every commit:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

See `.pre-commit-config.yaml` for hook configuration.

## .gitignore

Comprehensive `.gitignore` covers:
- Python bytecode (`__pycache__/`, `*.pyc`)
- Virtual environments (`venv/`, `env/`, etc.)
- Build artifacts (`build/`, `dist/`, `*.egg-info/`)
- IDE settings (`.vscode/`, `.idea/`, `*.iml`)
- OS files (`.DS_Store`, `._*` on macOS)
- Tool caches (`.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, etc.)
- Coverage reports (`htmlcov/`, `.coverage`)
- Logs and databases
- Local config files (keeps tracked `config.yaml`)

## Complete Workflow Example

```bash
# 1. Make changes to code
# ... edit files ...

# 2. Format code
python -m black matilda_cli/ --line-length=100
python -m isort matilda_cli/ --profile black --line-length=100

# 3. Check for linting issues
python -m ruff check matilda_cli/ --fix --line-length=100

# 4. Run tests
python -m pytest tests/ -v

# 5. Check type safety (optional)
python -m mypy matilda_cli/algorithms/MATILDA/ --ignore-missing-imports

# 6. Commit changes
git add .
git commit -m "feat: add feature"
```

## Troubleshooting

### "module not found" errors
Ensure you've installed the package in editable mode:
```bash
pip install -e ".[dev]"
```

### pytest marker issues
Verify `pytest.ini` exists and contains all markers.

### Black vs. Ruff conflicts
Both tools follow similar style rules. Ruff is configured to be compatible with Black.

### mypy issues with package name
The project name contains a dash, which mypy doesn't like. Run mypy on specific subdirectories instead of the root.
