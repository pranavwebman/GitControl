#!/data/data/com.termux/files/usr/bin/bash

echo "🚀 Installing GitControl for Termux..."
echo "====================================="

# Update packages
pkg update -y && pkg upgrade -y

# Install required packages
pkg install -y python python-pip git

# Install Python dependencies
pip install requests

# Create directory for GitControl
mkdir -p ~/gitcontrol

# Download the script
echo "📥 Downloading GitControl..."
curl -o ~/gitcontrol/gitcontrol.py https://pastebin.com/raw/your_script_url

# Make executable
chmod +x ~/gitcontrol/gitcontrol.py

# Create alias
echo "alias gitcontrol='python ~/gitcontrol/gitcontrol.py'" >> ~/.bashrc

# Source bashrc
source ~/.bashrc

echo "✅ GitControl installed successfully!"
echo "📌 Run 'gitcontrol' to start the tool"
echo "📌 Or: python ~/gitcontrol/gitcontrol.py"
