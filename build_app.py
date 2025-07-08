#!/usr/bin/env python3
"""
Build script for creating Visual Learning Tracker Mac executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def build_mac_app():
    """Build the Mac application using PyInstaller"""

    print("🚀 Building Visual Learning Tracker Mac App...")

    # Ensure we're in the correct directory
    os.chdir(Path(__file__).parent)

    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onedir",  # Create a one-folder bundle
        "--windowed",  # No console window (GUI app)
        "--name=Visual Learning Tracker",
        "--icon=app_icon.icns" if os.path.exists("app_icon.icns") else "",
        "--add-data=requirements.txt:.",
        "--hidden-import=tkinter",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=matplotlib",
        "--hidden-import=matplotlib.backends.backend_tkagg",
        "--hidden-import=networkx",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=numpy",
        "--hidden-import=sqlite3",
        "--hidden-import=json",
        "--hidden-import=webbrowser",
        "--osx-bundle-identifier=com.visuallearningtracker.app",
        "main.py",
    ]

    # Remove empty icon parameter if no icon exists
    cmd = [arg for arg in cmd if arg]

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        print(result.stdout)

        # Check if the app was created
        app_path = "dist/Visual Learning Tracker.app"
        if os.path.exists(app_path):
            print(f"📱 App created at: {os.path.abspath(app_path)}")
            print("🎉 You can now run the app by double-clicking it in Finder!")

            # Make the app executable
            subprocess.run(
                ["chmod", "+x", f"{app_path}/Contents/MacOS/Visual Learning Tracker"]
            )

            return True
        else:
            print("❌ App bundle not found after build")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


if __name__ == "__main__":
    success = build_mac_app()
    sys.exit(0 if success else 1)
