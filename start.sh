#!/bin/bash

# Install Node.js if not available
if ! command -v node &> /dev/null; then
    echo "Node.js not found, installing..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    echo "Node.js installed successfully"
fi

# Install npm dependencies
if [ -f "package.json" ]; then
    npm install
    echo "NPM dependencies installed"
fi

# Set Puppeteer environment variables
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

# Start the application
gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 main:app