# 🧠 Visual Learning Tracker

A comprehensive Python GUI application designed for visual learners to manage their learning journey with interactive mind maps, knowledge graphs, and rich note-taking capabilities.

## ✨ Features

### 📚 Course Management
- Create and organize learning courses with categories and difficulty levels
- Track progress with visual progress bars and completion percentages
- Set learning goals and deadlines
- Time estimation and actual time tracking

### 🧠 Mind Mapping
- Interactive drag-and-drop mind map canvas
- Create nodes with custom colors and types
- Connect concepts with labeled relationships
- Export and import mind maps
- Real-time collaboration support

### 📝 Advanced Note-Taking
- Rich text editor with formatting options (bold, italic, underline)
- Syntax highlighting for code snippets
- Tag-based organization system
- Search functionality across all notes
- Export notes to various formats (TXT, MD)

### 🔗 Knowledge Graph Visualization
- Visual representation of concept relationships
- Node-based learning structure
- Connection strength indicators
- Interactive exploration of knowledge domains

### 🃏 Flashcard System
- Create flashcards from notes automatically
- Spaced repetition algorithm
- Performance tracking and analytics
- Custom difficulty levels

### 📊 Learning Analytics
- Study time tracking and visualization
- Progress charts and statistics
- Learning velocity analysis
- Goal achievement tracking

### ⏱️ Study Timer
- Built-in Pomodoro timer
- Session tracking with mood and energy levels
- Automatic break reminders
- Study streak counters

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- tkinter (usually included with Python)
- Git

### Setup

1. **Clone the repository:**
   ```bash
   cd /Users/christianvuye/Projects_Programming/claude_autonomous_tools
   cd visual-learning-tracker
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## 📖 Quick Start Guide

### Creating Your First Course

1. Click **"+ New Course"** in the sidebar
2. Fill in course details:
   - **Title**: Name of your course
   - **Category**: Programming, Language, Business, etc.
   - **Difficulty**: 1-5 scale
   - **Estimated Hours**: Time commitment
3. Click **"Create Course"**

### Using the Mind Map Feature

1. Navigate to **"🧠 Mind Maps"** in the sidebar
2. **Double-click** anywhere on the canvas to create a new node
3. **Select a node** and click **"🔗 Connect"** to link concepts
4. **Right-click** nodes for context menu options
5. Use the toolbar to save, load, and customize your mind maps

### Taking Notes

1. Go to **"📝 Notes"** section
2. Click **"+ New"** to create a note
3. Use the rich text editor with formatting tools
4. **Associate notes with courses** using the dropdown
5. **Tag your notes** for easy organization
6. **Search** through all notes using the search bar

### Creating Flashcards

1. In the notes editor, **select any text**
2. Click **"🃏 Create Flashcard"**
3. Edit the question and answer
4. Review flashcards in the **"🃏 Flashcards"** section

### Tracking Your Progress

1. Start a study session using the **"Study Timer"** in the sidebar
2. Select a course and click **"📖 Study"**
3. View your progress in the **"📊 Analytics"** dashboard
4. Monitor daily, weekly, and monthly learning statistics

## 🗂️ Project Structure

```
visual-learning-tracker/
├── main.py                 # Main application entry point
├── database.py             # SQLite database management
├── mind_map.py             # Mind mapping canvas and nodes
├── notes_editor.py         # Rich text note-taking system
├── test_app.py             # Component testing
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .venv/                  # Virtual environment
└── .git/                   # Git repository
```

## 🛠️ Technical Details

### Database Schema
- **SQLite** database for local storage
- Tables for courses, modules, notes, mind maps, flashcards
- Relationships between learning materials
- Session tracking and analytics data

### GUI Framework
- **ttkbootstrap** for modern, themed interface
- **tkinter** for cross-platform compatibility
- **matplotlib** for charts and visualizations
- **networkx** for knowledge graph algorithms

### Key Components

#### DatabaseManager (`database.py`)
- Handles all database operations
- Course and module management
- Note and flashcard storage
- Session tracking and statistics

#### MindMapCanvas (`mind_map.py`)
- Interactive canvas with drag-and-drop
- Node and connection management
- Export/import functionality
- Real-time visual updates

#### NotesEditor (`notes_editor.py`)
- Rich text editing capabilities
- Tag-based organization
- Search and filter functionality
- Export to multiple formats

## 🎨 Customization

### Themes
The application uses ttkbootstrap themes. You can change the theme by modifying the `themename` parameter in `main.py`:

```python
self.root = ttk_bs.Window(
    title="Visual Learning Tracker",
    themename="superhero",  # Try: cosmo, flatly, litera, minty, etc.
    size=(1400, 900)
)
```

### Adding New Features
The modular design makes it easy to extend:

1. **New visualizations**: Add to the analytics dashboard
2. **Additional note types**: Extend the notes editor
3. **Custom mind map nodes**: Modify the MindMapNode class
4. **Integration APIs**: Add export to external services

## 🧪 Testing

Run the component tests to verify functionality:

```bash
python test_app.py
```

This will test:
- Database operations
- Course and note management
- Mind map data structures
- Learning session tracking

## 🔧 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named '_tkinter'"**
- Install tkinter: `sudo apt-get install python3-tk` (Linux)
- On macOS: tkinter is included with Python from python.org
- On Windows: tkinter is included with standard Python installation

**Application won't start**
- Ensure you're in the virtual environment: `source .venv/bin/activate`
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.8+)

**Database errors**
- Delete the database file to reset: `rm learning_tracker.db`
- The application will recreate the database on next startup

## 🛣️ Roadmap

### Planned Features
- [ ] Cloud synchronization
- [ ] Mobile companion app
- [ ] AI-powered learning recommendations
- [ ] Collaborative study groups
- [ ] Voice note integration
- [ ] OCR for handwritten notes
- [ ] Integration with learning platforms (Coursera, Udemy)

### Known Limitations
- Currently single-user application
- No real-time collaboration yet
- Limited export formats
- Basic analytics (more advanced charts planned)

## 🤝 Contributing

This is a personal learning project, but suggestions and improvements are welcome!

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request with detailed description

## 📄 License

This project is open source and available under the MIT License.

## 💡 Tips for Visual Learners

### Maximizing the Mind Map Feature
- **Use colors strategically**: Assign colors to different types of concepts
- **Keep nodes concise**: Short, memorable labels work best
- **Create hierarchies**: Use parent-child relationships for complex topics
- **Regular reviews**: Revisit and update your mind maps as you learn

### Effective Note-Taking
- **Use headings**: Structure your notes with clear headings
- **Add visual elements**: Use the drawing tools for diagrams
- **Tag consistently**: Develop a tagging system early
- **Link concepts**: Reference related notes and mind maps

### Optimizing Study Sessions
- **Set realistic goals**: Use the time estimation features
- **Track your mood**: Note your energy levels for pattern recognition
- **Take breaks**: Use the built-in timer for regular breaks
- **Review analytics**: Use data to optimize your learning schedule

## 🙋‍♀️ Support

For questions, bug reports, or feature requests, please create an issue in the repository or contact the developer.

---

**Happy Learning! 🎓**

*Visual Learning Tracker - Designed for visual learners, by visual learners.*