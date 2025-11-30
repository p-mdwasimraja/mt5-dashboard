#!/bin/bash
# Installation script for MT5 Dashboard API

echo "Installing MT5 Dashboard API..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p config
mkdir -p data
mkdir -p logs
mkdir -p app/static/css
mkdir -p app/static/js
mkdir -p app/static/images

# Copy example config files
if [ ! -f config/settings.yaml ]; then
    echo "Copying example config..."
    cp config/settings.yaml.example config/settings.yaml
    echo "Please edit config/settings.yaml with your MT5 data paths"
fi

if [ ! -f .env ]; then
    echo "Copying example .env..."
    cp .env.example .env
fi

# Make scripts executable
chmod +x start.sh
chmod +x install.sh

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config/settings.yaml with your MT5 data paths"
echo "2. Optionally edit .env for custom settings"
echo "3. Run ./start.sh to start the server"
echo ""
