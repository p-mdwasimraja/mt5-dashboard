#!/bin/bash
# MT5 Dashboard API - Setup Script for Linux/Mac
# This script sets up the complete environment

set -e  # Exit on error

echo "=========================================="
echo "  MT5 Dashboard API Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
print_success "Found Python $PYTHON_VERSION"

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "Pip upgraded"

# Install requirements
echo ""
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet
print_success "Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directory structure..."
mkdir -p config
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/backup
mkdir -p logs
mkdir -p app/static/css
mkdir -p app/static/js
mkdir -p app/static/images
print_success "Directories created"

# Copy example config if not exists
echo ""
if [ -f "config/settings.yaml" ]; then
    print_warning "config/settings.yaml already exists. Skipping copy."
else
    if [ -f "config/settings.yaml.example" ]; then
        cp config/settings.yaml.example config/settings.yaml
        print_success "Created config/settings.yaml from example"
        print_warning "Please edit config/settings.yaml with your MT5 data paths!"
    else
        print_warning "config/settings.yaml.example not found"
    fi
fi

# Copy .env if not exists
if [ -f ".env" ]; then
    print_warning ".env already exists. Skipping copy."
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env from example"
    else
        print_warning ".env.example not found"
    fi
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x start.sh 2>/dev/null || true
chmod +x install.sh 2>/dev/null || true
chmod +x setup.sh 2>/dev/null || true
print_success "Scripts made executable"

# Display success message
echo ""
echo "=========================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your MT5 data sources:"
echo "   ${YELLOW}nano config/settings.yaml${NC}"
echo ""
echo "2. Start the server:"
echo "   ${YELLOW}./start.sh${NC}"
echo ""
echo "3. Access the dashboard:"
echo "   ${YELLOW}http://localhost:8000${NC}"
echo ""
echo "4. View API documentation:"
echo "   ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo "For VPS deployment, see README.md"
echo ""
