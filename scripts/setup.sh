#!/bin/bash
# PrepSmart MVP Setup Script
# Automates environment setup for local development

set -e  # Exit on error

echo "🚀 PrepSmart MVP Setup"
echo "====================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $python_version"

if [[ $(echo "$python_version 3.11" | awk '{print ($1 < $2)}') -eq 1 ]]; then
    echo -e "${RED}❌ Python 3.11+ required. Please upgrade Python.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python version OK${NC}"
echo ""

# Check Node.js version
echo "📋 Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found. Install Node.js 18+ for frontend.${NC}"
else
    node_version=$(node --version | cut -d'v' -f2)
    echo "   Found: Node.js v$node_version"
    echo -e "${GREEN}✅ Node.js installed${NC}"
fi
echo ""

# Backend setup
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo "   Virtual environment already exists"
fi

# Activate virtual environment
echo "   Activating virtual environment..."
source venv/bin/activate || true

# Install dependencies
echo "   Installing Python dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "   Creating .env file..."
    cat > .env << 'EOL'
# PrepSmart Backend Configuration

# Claude API (REQUIRED - Get key from https://console.anthropic.com)
ANTHROPIC_API_KEY=your_api_key_here_REPLACE_ME

# Database
DATABASE_URL=sqlite:///prepsmart.db

# Flask
FLASK_SECRET_KEY=dev_secret_key_change_in_production
FLASK_DEBUG=True

# CORS (allow frontend origin)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
EOL
    echo -e "${YELLOW}⚠️  Created .env file - PLEASE UPDATE ANTHROPIC_API_KEY${NC}"
else
    echo "   .env file already exists"
fi

# Initialize database
echo "   Initializing database..."
python3 -c "import sys; sys.path.insert(0, 'src'); from api.app import init_db; init_db()"
echo -e "${GREEN}✅ Database initialized${NC}"

# Create output directory for PDFs
mkdir -p output/pdfs
echo -e "${GREEN}✅ Output directory created${NC}"

cd ..
echo ""

# E2E Tests setup
echo "🧪 Setting up E2E Tests..."
cd tests/e2e

if [ -f "package.json" ]; then
    if command -v npm &> /dev/null; then
        echo "   Installing Playwright dependencies..."
        npm install
        echo "   Installing Playwright browsers..."
        npx playwright install --with-deps chromium
        echo -e "${GREEN}✅ Playwright setup complete${NC}"
    else
        echo -e "${YELLOW}⚠️  npm not found. Skipping Playwright setup.${NC}"
    fi
else
    echo "   No package.json found. Skipping."
fi

cd ../..
echo ""

# Summary
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next Steps:"
echo ""
echo "1. ${YELLOW}Update backend/.env with your Claude API key${NC}"
echo "   Get your key from: https://console.anthropic.com"
echo ""
echo "2. Start the backend server:"
echo "   ${GREEN}cd backend${NC}"
echo "   ${GREEN}source venv/bin/activate${NC} (if using venv)"
echo "   ${GREEN}python src/api/app.py${NC}"
echo ""
echo "3. Test the backend:"
echo "   ${GREEN}curl http://localhost:5000/api/health${NC}"
echo ""
echo "4. Run end-to-end backend test:"
echo "   ${GREEN}python backend/test_end_to_end.py${NC}"
echo ""
echo "5. Build the frontend (when ready):"
echo "   ${GREEN}cd frontend${NC}"
echo "   ${GREEN}npm install && npm run dev${NC}"
echo ""
echo "6. Run E2E tests (when frontend is ready):"
echo "   ${GREEN}cd tests/e2e${NC}"
echo "   ${GREEN}npm test${NC}"
echo ""
echo "📚 Documentation:"
echo "   - MVP Status: ./MVP_STATUS.md"
echo "   - E2E Tests: ./tests/e2e/README.md"
echo "   - Spec: ./.specify/specs/001-prepsmart-mvp/spec.md"
echo ""
echo "💡 Tip: The backend is fully functional. Frontend needs to be built."
echo ""
