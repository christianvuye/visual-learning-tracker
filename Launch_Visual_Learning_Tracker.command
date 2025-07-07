#!/bin/bash

# Visual Learning Tracker Launcher
# Double-click this file to launch the application

echo "🚀 Launching Visual Learning Tracker..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Launch the app
open "$SCRIPT_DIR/dist/Visual Learning Tracker.app"

echo "✅ Visual Learning Tracker launched!"

# Keep terminal open for a moment to show the message
sleep 2