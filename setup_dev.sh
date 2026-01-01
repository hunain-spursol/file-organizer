#!/bin/bash
# Setup development environment for File Organizer

set -e  # Exit on error

echo "Creating virtual environment..."
python3 -m venv venv

if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing development dependencies..."
# Use the venv's pip explicitly to be sure
venv/bin/pip install -r requirements-dev.txt

echo ""
echo "========================================"
echo "Development environment setup complete!"
echo "========================================"
echo ""
echo "Virtual environment created at: venv/"
echo ""
echo "To activate the virtual environment, run:"
echo "    source venv/bin/activate"
echo ""
echo "To run tests:"
echo "    pytest"
echo "    python run_tests.py all"
echo ""
