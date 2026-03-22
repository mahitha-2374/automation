#!/bin/bash
# Linux/Mac Setup Script

echo "Installing IAM Automation Platform..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python 3.10+"
    exit 1
fi

# Create venv
echo "Creating virtual environment..."
python3 -m venv venv

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install packages
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "To start:"
echo "  1. Run: source venv/bin/activate"
echo "  2. Run: streamlit run app.py"
echo ""
echo "Browser will open to http://localhost:8501"
