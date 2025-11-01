#!/bin/bash

# PrepSmart Security Setup Script
# This script sets up pre-commit hooks and security scanning tools

set -e

echo "========================================"
echo "PrepSmart Security Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python and pip found"
echo ""

# Install pre-commit
echo "📦 Step 1/4: Installing pre-commit..."
pip3 install pre-commit detect-secrets bandit[toml] safety || pip install pre-commit detect-secrets bandit[toml] safety
echo "✅ Security tools installed"
echo ""

# Install pre-commit hooks
echo "🔧 Step 2/4: Setting up pre-commit hooks..."
if [ -f .pre-commit-config.yaml ]; then
    pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  .pre-commit-config.yaml not found. Skipping hook installation."
fi
echo ""

# Initialize detect-secrets baseline
echo "🔍 Step 3/4: Initializing secret detection baseline..."
if [ ! -f .secrets.baseline ]; then
    detect-secrets scan > .secrets.baseline
    echo "✅ Secret detection baseline created"
else
    echo "✅ Secret detection baseline already exists"
fi
echo ""

# Run initial security scan
echo "🛡️  Step 4/4: Running initial security scan..."
echo ""

echo "   Testing pre-commit hooks..."
if pre-commit run --all-files; then
    echo "   ✅ All pre-commit checks passed"
else
    echo "   ⚠️  Some checks failed. Review the output above."
    echo "   This is normal for first-time setup."
fi
echo ""

# Check for common security issues
echo "   Checking for .env files in git..."
if git ls-files | grep -E "^\.env$" | grep -v ".env.example"; then
    echo "   ⚠️  WARNING: .env file found in git! This should be removed."
    echo "   Run: git rm --cached .env"
else
    echo "   ✅ No .env files in git"
fi
echo ""

echo "========================================"
echo "✅ Security Setup Complete!"
echo "========================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Verify pre-commit hooks are working:"
echo "   git add ."
echo "   git commit -m 'test' --dry-run"
echo ""
echo "2. Before committing sensitive files, test them:"
echo "   detect-secrets scan backend/.env"
echo ""
echo "3. Run security scans manually:"
echo "   bandit -r backend/src -c .bandit"
echo "   safety check --file backend/requirements.txt"
echo ""
echo "4. Review security documentation:"
echo "   cat SECURITY.md"
echo "   cat docs/GITHUB_SECRETS.md"
echo ""
echo "🔒 Security features enabled:"
echo "   ✓ Pre-commit hooks (prevents committing secrets)"
echo "   ✓ Secret detection (detect-secrets)"
echo "   ✓ Security linting (bandit)"
echo "   ✓ Dependency scanning (safety)"
echo "   ✓ Private key detection"
echo "   ✓ .env file blocking"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Never commit .env files"
echo "   - Rotate API keys after any leak"
echo "   - Use different keys for dev/staging/prod"
echo ""
