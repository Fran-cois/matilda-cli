#!/usr/bin/env bash
# Build and publish MATILDA to PyPI

set -e

echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

echo "📦 Building package..."
python3 -m build

echo "✅ Build complete! Files created:"
ls -lh dist/

echo ""
echo "To upload to TestPyPI (for testing):"
echo "  python3 -m twine upload --repository testpypi dist/*"
echo ""
echo "To upload to PyPI (production):"
echo "  python3 -m twine upload dist/*"
echo ""
echo "Make sure you have configured your PyPI API token in ~/.pypirc"
