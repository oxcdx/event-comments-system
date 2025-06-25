#!/bin/bash

# Text Annotator Setup Script
set -e

echo "Setting up Text Annotator Flask Application..."

# Create virtual environment
echo "Creating virtual environment..."
cd /home/copmiler-ox/text-annotator
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create database directory
echo "Setting up database..."
mkdir -p data

# Set proper permissions
echo "Setting permissions..."
chmod +x setup.sh
chown -R copmiler-ox:copmiler-ox /home/copmiler-ox/text-annotator

# Copy nginx configuration
echo "Setting up nginx configuration..."
sudo cp nginx-text-annotator.conf /etc/nginx/sites-available/text-annotator
sudo ln -sf /etc/nginx/sites-available/text-annotator /etc/nginx/sites-enabled/text-annotator

# Remove default nginx site if it exists
sudo rm -f /etc/nginx/sites-enabled/default

# Copy systemd service
echo "Setting up systemd service..."
sudo cp text-annotator.service /etc/systemd/system/
sudo systemctl daemon-reload

# Test nginx configuration
echo "Testing nginx configuration..."
sudo nginx -t

# Restart nginx
echo "Restarting nginx..."
sudo systemctl restart nginx

# Enable and start the text-annotator service
echo "Starting text-annotator service..."
sudo systemctl enable text-annotator
sudo systemctl start text-annotator

echo ""
echo "Setup complete!"
echo ""
echo "Your text annotator is now running at:"
echo "  http://localhost"
echo "  http://$(hostname -I | awk '{print $1}')"
echo ""
echo "To check the status:"
echo "  sudo systemctl status text-annotator"
echo "  sudo systemctl status nginx"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u text-annotator -f"
echo "  sudo tail -f /var/log/nginx/error.log"
echo ""
