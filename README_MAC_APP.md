# 📱 Visual Learning Tracker - Mac App

## 🎉 **Your Mac Application is Ready!**

The Visual Learning Tracker has been successfully compiled into a native Mac application that you can run without needing Python or the command line.

## 📍 **Where to Find Your App**

The Mac app is located at:
```
dist/Visual Learning Tracker.app
```

## 🚀 **How to Launch the App**

### Option 1: Direct Launch (Recommended)
1. Open Finder
2. Navigate to the `dist` folder
3. **Double-click** on `Visual Learning Tracker.app`

### Option 2: Using the Launcher Script
1. **Double-click** on `Launch_Visual_Learning_Tracker.command`
2. This will automatically open the app for you

### Option 3: From Dock (After First Launch)
1. After launching once, right-click the app icon in the Dock
2. Select **"Options" → "Keep in Dock"**
3. Now you can launch it anytime from the Dock!

## 📊 **App Details**

- **App Name**: Visual Learning Tracker
- **Version**: 1.0.0
- **Size**: ~69 MB
- **Platform**: macOS (Universal Binary)
- **Requirements**: macOS 10.13+ (High Sierra or later)

## ✨ **What's Included**

Your Mac app includes all the features you've been using:

### 🏠 **Core Features**
- **Dashboard** - Learning statistics and active courses overview
- **Courses** - Complete course management with progress tracking
- **Notes** - Rich text editor with search, tags, and formatting
- **Mind Maps** - Interactive drag-and-drop mind mapping canvas
- **Knowledge Graph** - Interactive graph visualization with networkx
- **🏋️ Exercises** - LLM conversation tracking and progress management
- **Flashcards** - Spaced repetition learning system
- **Analytics** - Learning insights with charts and visualizations
- **Settings** - Comprehensive preferences and configuration

### 🔗 **Advanced Features**
- **Quick Notes** - Fast note creation from sidebar
- **Concept Linking** - Connect courses, exercises, and materials to concepts
- **Data Persistence** - All your data is saved automatically in SQLite
- **Export/Import** - Backup and share your learning data
- **Visual Progress Tracking** - See your learning journey with charts and graphs

## 💾 **Data Storage**

Your learning data is stored in a SQLite database file that will be created automatically:
- **Location**: Same folder as the app
- **File**: `learning_tracker.db`
- **Backup**: You can copy this file to backup all your data

## 🔧 **Troubleshooting**

### If the app won't open:
1. **Right-click** the app → **"Open"** → **"Open"** (to bypass Gatekeeper)
2. Or go to **System Preferences** → **Security & Privacy** → **"Open Anyway"**

### If you see a security warning:
- This is normal for unsigned apps
- Choose **"Open"** when prompted
- The app is safe - it was built from your own source code

### If the app crashes:
1. Try launching from Terminal to see error messages:
   ```bash
   ./dist/Visual\ Learning\ Tracker.app/Contents/MacOS/Visual\ Learning\ Tracker
   ```
2. Check that all dependencies are working correctly

## 📁 **App Distribution**

To share the app with others or move it to Applications:

### Move to Applications Folder:
```bash
# Copy the app to Applications (optional)
cp -r "dist/Visual Learning Tracker.app" /Applications/
```

### Create a DMG (Disk Image):
```bash
# Create a distributable DMG file
hdiutil create -volname "Visual Learning Tracker" -srcfolder "dist/Visual Learning Tracker.app" -ov -format UDZO visual-learning-tracker.dmg
```

## 🎯 **Quick Start Guide**

1. **Launch the app** using any method above
2. **Create your first course** using the "+ New Course" button
3. **Add some notes** with the "Quick Note" feature
4. **Track exercises** in the new 🏋️ Exercises tab
5. **Visualize connections** with Mind Maps and Knowledge Graphs
6. **Monitor progress** in the Analytics tab

## 🔄 **Updates**

To update the app:
1. Get the latest source code
2. Rebuild using: `source .venv/bin/activate && pyinstaller visual_learning_tracker.spec`
3. Replace the old app with the new one in the `dist` folder

## 🆘 **Support**

If you encounter any issues:
1. Check the troubleshooting section above
2. Look at the terminal output when launching from command line
3. Verify all source files are present and unchanged

---

## 🎉 **Enjoy Your Visual Learning Journey!**

You now have a professional Mac application for tracking and enhancing your learning experience. No more command line needed - just double-click and start learning!

**Happy Learning!** 📚✨