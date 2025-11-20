# Publishing MATILDA to PyPI

This guide explains how to publish MATILDA CLI to PyPI.

## Prerequisites

1. **Install build tools:**
   ```bash
   pip install --upgrade build twine
   ```

2. **Create PyPI account:**
   - Register at https://pypi.org/account/register/
   - Verify your email
   - (Optional) Register at https://test.pypi.org for testing

3. **Create API token:**
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token (save it securely!)
   - Configure in `~/.pypirc`:
     ```ini
     [pypi]
     username = __token__
     password = pypi-YOUR_TOKEN_HERE
     ```

## Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build distribution packages
python -m build
```

This creates:
- `dist/matilda_cli-0.1.0.tar.gz` (source distribution)
- `dist/matilda_cli-0.1.0-py3-none-any.whl` (wheel)

## Test Package Locally

```bash
# Install in editable mode
pip install -e .

# Test CLI
matilda --help

# Run tests
pytest
```

## Upload to Test PyPI (Optional)

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps matilda-cli
```

## Upload to PyPI

```bash
# Upload to production PyPI
python -m twine upload dist/*

# Verify
pip install matilda-cli
matilda --help
```

## Version Bumping

Update version in:
1. `pyproject.toml` → `version = "x.y.z"`
2. `matilda_cli/__version__.py` → `__version__ = "x.y.z"`

Then rebuild and republish.

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: python -m twine upload dist/*
```

Add `PYPI_API_TOKEN` to GitHub repository secrets.

## Checklist Before Publishing

- [ ] All tests pass (`pytest`)
- [ ] Version number updated
- [ ] CHANGELOG.md updated
- [ ] README.md accurate
- [ ] LICENSE file present
- [ ] No sensitive data in code
- [ ] Package builds without errors
- [ ] Documentation is up-to-date

## Post-Publication

1. Create GitHub release with tag matching version
2. Update documentation
3. Announce on social media / research forums
4. Monitor PyPI downloads and issues

## Troubleshooting

**Import Error after installation:**
- Check package structure in `pyproject.toml`
- Verify all `__init__.py` files exist

**Version conflict:**
- Ensure version doesn't already exist on PyPI
- You cannot re-upload the same version

**Missing files:**
- Check `MANIFEST.in`
- Use `python -m build --sdist --wheel` and inspect contents
