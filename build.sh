#!/bin/bash
set -e

echo "Cloning Hermes Agent..."
git clone https://github.com/cyanheads/hermes-agent.git hermes-agent

echo "Installing Hermes dependencies..."
cd hermes-agent
pip install -r requirements.txt

echo "Installing Telegram bot dependencies..."
cd ..
pip install python-telegram-bot==20.7 aiohttp==3.9.1

echo "Build complete!"
