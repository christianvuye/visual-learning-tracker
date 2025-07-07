#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import threading
from database import DatabaseManager
from datetime import datetime, date
import json


class VisualLearningTracker:
    def __init__(self):
        self.db = DatabaseManager()
        self.setup_gui()
        self.current_session_id = None
        
    def setup_gui(self):
        # Create main window with modern theme
        self.root = ttk_bs.Window(
            title="Visual Learning Tracker",
            themename="superhero",  # Dark modern theme
            size=(1400, 900),
            minsize=(1200, 700)
        )
        
        # Center window on screen
        self.center_window()
        
        # Configure styles
        self.setup_styles()
        
        # Create main layout
        self.create_layout()
        
        # Load initial data
        self.refresh_dashboard()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        style = ttk_bs.Style()
        
        # Custom styles for cards
        style.configure('Card.TFrame', relief='raised', borderwidth=1)
        style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Subheader.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Progress.TLabel', font=('Helvetica', 10))
        
    def create_layout(self):
        # Main container
        main_container = ttk_bs.Frame(self.root)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Navigation sidebar
        self.create_sidebar(main_container)
        
        # Main content area
        self.create_main_content(main_container)
        
    def create_sidebar(self, parent):
        # Sidebar frame
        sidebar = ttk_bs.Frame(parent, width=250)
        sidebar.pack(side=LEFT, fill=Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Logo/Title
        title_frame = ttk_bs.Frame(sidebar)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk_bs.Label(
            title_frame, 
            text="📚 Visual Learning\nTracker", 
            style='Header.TLabel',
            anchor=CENTER
        )
        title_label.pack()
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("📖 Courses", self.show_courses),
            ("📝 Notes", self.show_notes),
            ("🧠 Mind Maps", self.show_mind_maps),
            ("🔗 Knowledge Graph", self.show_knowledge_graph),
            ("🏋️ Exercises", self.show_exercises),
            ("🃏 Flashcards", self.show_flashcards),
            ("📊 Analytics", self.show_analytics),
            ("⚙️ Settings", self.show_settings)
        ]
        
        self.nav_buttons = {}
        for text, command in nav_buttons:
            btn = ttk_bs.Button(
                sidebar,
                text=text,
                command=command,
                style='Outline.TButton',
                width=25
            )
            btn.pack(fill=X, pady=2)
            self.nav_buttons[text] = btn
        
        # Quick actions
        ttk_bs.Separator(sidebar, orient=HORIZONTAL).pack(fill=X, pady=10)
        
        quick_label = ttk_bs.Label(sidebar, text="Quick Actions", style='Subheader.TLabel')
        quick_label.pack(pady=(0, 10))
        
        quick_new_course = ttk_bs.Button(
            sidebar,
            text="+ New Course",
            command=self.new_course_dialog,
            style='Success.TButton'
        )
        quick_new_course.pack(fill=X, pady=2)
        
        quick_new_note = ttk_bs.Button(
            sidebar,
            text="+ Quick Note",
            command=self.quick_note_dialog,
            style='Info.TButton'
        )
        quick_new_note.pack(fill=X, pady=2)
        
        # Study timer section
        ttk_bs.Separator(sidebar, orient=HORIZONTAL).pack(fill=X, pady=10)
        
        timer_label = ttk_bs.Label(sidebar, text="Study Timer", style='Subheader.TLabel')
        timer_label.pack(pady=(0, 10))
        
        self.timer_frame = ttk_bs.Frame(sidebar)
        self.timer_frame.pack(fill=X)
        
        self.timer_display = ttk_bs.Label(
            self.timer_frame, 
            text="00:00:00", 
            font=('Helvetica', 14, 'bold')
        )
        self.timer_display.pack()
        
        self.start_timer_btn = ttk_bs.Button(
            self.timer_frame,
            text="Start Session",
            command=self.toggle_timer,
            style='Warning.TButton'
        )
        self.start_timer_btn.pack(fill=X, pady=2)
        
    def create_main_content(self, parent):
        # Main content frame
        self.content_frame = ttk_bs.Frame(parent)
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Create notebook for different views
        self.notebook = ttk_bs.Notebook(self.content_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Initialize with dashboard
        self.show_dashboard()
        
    def show_dashboard(self):
        # Clear notebook and create dashboard
        self.clear_notebook()
        
        dashboard_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Header
        header_frame = ttk_bs.Frame(dashboard_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        welcome_label = ttk_bs.Label(
            header_frame,
            text=f"Welcome back! Today is {date.today().strftime('%B %d, %Y')}",
            style='Header.TLabel'
        )
        welcome_label.pack(anchor=W)
        
        # Statistics cards
        self.create_stats_cards(dashboard_frame)
        
        # Recent activity
        self.create_recent_activity(dashboard_frame)
        
        # Active courses grid
        self.create_active_courses_grid(dashboard_frame)
        
    def create_stats_cards(self, parent):
        stats_frame = ttk_bs.Frame(parent)
        stats_frame.pack(fill=X, pady=(0, 20))
        
        # Get statistics
        stats = self.db.get_learning_statistics()
        
        # Create cards
        cards_data = [
            ("📚 Active Courses", str(stats['active_courses']), "primary"),
            ("⏱️ Study Hours (30d)", str(stats['total_study_hours']), "success"),
            ("🎯 Sessions (30d)", str(stats['study_sessions']), "info"),
            ("✅ Modules Done", str(stats['completed_modules']), "warning")
        ]
        
        for i, (title, value, style) in enumerate(cards_data):
            card = ttk_bs.Frame(stats_frame, style='Card.TFrame')
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=5 if i > 0 else 0)
            
            # Card content
            ttk_bs.Label(card, text=title, style='Progress.TLabel').pack(pady=(10, 5))
            ttk_bs.Label(card, text=value, font=('Helvetica', 24, 'bold')).pack()
            ttk_bs.Label(card, text=" ", font=('Helvetica', 8)).pack(pady=(0, 10))
            
    def create_recent_activity(self, parent):
        activity_frame = ttk_bs.LabelFrame(parent, text="Recent Activity", padding=10)
        activity_frame.pack(fill=X, pady=(0, 20))
        
        # TODO: Implement recent activity list
        placeholder = ttk_bs.Label(
            activity_frame, 
            text="Recent learning sessions and achievements will appear here...",
            foreground="gray"
        )
        placeholder.pack()
        
    def create_active_courses_grid(self, parent):
        courses_frame = ttk_bs.LabelFrame(parent, text="Active Courses", padding=10)
        courses_frame.pack(fill=BOTH, expand=True)
        
        # Get active courses
        courses = self.db.get_courses(status='active')
        
        if not courses:
            placeholder = ttk_bs.Label(
                courses_frame,
                text="No active courses. Click 'New Course' to get started!",
                foreground="gray"
            )
            placeholder.pack(expand=True)
            return
        
        # Create scrollable frame
        canvas = tk.Canvas(courses_frame)
        scrollbar = ttk_bs.Scrollbar(courses_frame, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = ttk_bs.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Course cards
        for i, course in enumerate(courses):
            self.create_course_card(scrollable_frame, course, i)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
    def create_course_card(self, parent, course, row):
        card_frame = ttk_bs.Frame(parent, style='Card.TFrame')
        card_frame.pack(fill=X, pady=5, padx=5)
        
        # Course info
        info_frame = ttk_bs.Frame(card_frame)
        info_frame.pack(fill=X, padx=10, pady=10)
        
        # Title and category
        title_label = ttk_bs.Label(
            info_frame, 
            text=course['title'], 
            style='Subheader.TLabel'
        )
        title_label.pack(anchor=W)
        
        if course['category']:
            category_label = ttk_bs.Label(
                info_frame,
                text=f"📂 {course['category']}",
                foreground="gray"
            )
            category_label.pack(anchor=W)
        
        # Progress bar
        progress_frame = ttk_bs.Frame(info_frame)
        progress_frame.pack(fill=X, pady=(5, 0))
        
        progress_bar = ttk_bs.Progressbar(
            progress_frame,
            value=course['current_progress'],
            style='Success.Horizontal.TProgressbar'
        )
        progress_bar.pack(fill=X, side=LEFT, expand=True)
        
        progress_label = ttk_bs.Label(
            progress_frame,
            text=f"{course['current_progress']:.0f}%"
        )
        progress_label.pack(side=RIGHT, padx=(10, 0))
        
        # Action buttons
        btn_frame = ttk_bs.Frame(info_frame)
        btn_frame.pack(anchor=E, pady=(5, 0))
        
        study_btn = ttk_bs.Button(
            btn_frame,
            text="📖 Study",
            command=lambda c=course: self.start_study_session(c),
            style='Success.Outline.TButton'
        )
        study_btn.pack(side=RIGHT, padx=(5, 0))
        
    def show_courses(self):
        self.clear_notebook()
        
        courses_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(courses_frame, text="Courses")
        
        # Import and create the course manager
        from course_manager import CourseManagerWidget
        self.course_manager = CourseManagerWidget(courses_frame, self.db)
        
    def show_notes(self):
        self.clear_notebook()
        
        notes_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(notes_frame, text="Notes")
        
        # Import and create the notes editor
        from notes_editor import NotesWidget
        self.notes_widget = NotesWidget(notes_frame, self.db)
        
    def show_mind_maps(self):
        self.clear_notebook()
        
        mindmap_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(mindmap_frame, text="Mind Maps")
        
        # Import and create the mind map widget
        from mind_map import MindMapWidget
        self.mindmap_widget = MindMapWidget(mindmap_frame)
        
    def show_knowledge_graph(self):
        self.clear_notebook()
        
        graph_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(graph_frame, text="Knowledge Graph")
        
        # Import and create the knowledge graph widget
        from knowledge_graph import KnowledgeGraphWidget
        self.knowledge_graph_widget = KnowledgeGraphWidget(graph_frame, self.db)
        
    def show_exercises(self):
        self.clear_notebook()
        
        exercises_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(exercises_frame, text="Exercises")
        
        # Import and create the exercises widget
        from exercises_widget import ExercisesWidget
        self.exercises_widget = ExercisesWidget(exercises_frame, self.db)
        
    def show_flashcards(self):
        self.clear_notebook()
        
        flashcards_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(flashcards_frame, text="Flashcards")
        
        # Import and create the flashcard widget
        from flashcard_widget import FlashcardWidget
        self.flashcard_widget = FlashcardWidget(flashcards_frame, self.db)
        
    def show_analytics(self):
        self.clear_notebook()
        
        analytics_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="Analytics")
        
        # Import and create the analytics widget
        from analytics_widget import AnalyticsWidget
        self.analytics_widget = AnalyticsWidget(analytics_frame, self.db)
        
    def show_settings(self):
        self.clear_notebook()
        
        settings_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Import and create the settings widget
        from settings_widget import SettingsWidget
        self.settings_widget = SettingsWidget(settings_frame, self.db)
        
    def clear_notebook(self):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
            
    def new_course_dialog(self):
        dialog = CourseDialog(self.root, self.db)
        if dialog.result:
            self.refresh_dashboard()
            
    def quick_note_dialog(self):
        dialog = QuickNoteDialog(self.root, self.db)
        if dialog.result:
            self.refresh_dashboard()
        
    def start_study_session(self, course):
        if self.current_session_id:
            messagebox.showwarning("Active Session", "Please end your current study session first.")
            return
            
        self.current_session_id = self.db.start_learning_session(course['id'])
        self.start_timer_btn.config(text="End Session", style='Danger.TButton')
        messagebox.showinfo("Study Session", f"Started studying: {course['title']}")
        
    def toggle_timer(self):
        if self.current_session_id:
            # End session
            self.db.end_learning_session(self.current_session_id)
            self.current_session_id = None
            self.start_timer_btn.config(text="Start Session", style='Warning.TButton')
            self.timer_display.config(text="00:00:00")
            messagebox.showinfo("Study Session", "Study session ended!")
        else:
            messagebox.showinfo("Timer", "Please select a course to study first.")
            
    def refresh_dashboard(self):
        if hasattr(self, 'notebook') and self.notebook.tab('current')['text'] == 'Dashboard':
            self.show_dashboard()
            
    def run(self):
        self.root.mainloop()


class CourseDialog:
    def __init__(self, parent, db):
        self.db = db
        self.result = None
        
        # Create dialog window
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("New Course")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_form()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
        
    def create_form(self):
        main_frame = ttk_bs.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Title
        ttk_bs.Label(main_frame, text="Create New Course", style='Header.TLabel').pack(pady=(0, 20))
        
        # Form fields
        self.title_var = tk.StringVar()
        ttk_bs.Label(main_frame, text="Course Title:").pack(anchor=W)
        ttk_bs.Entry(main_frame, textvariable=self.title_var, width=50).pack(fill=X, pady=(0, 10))
        
        self.desc_var = tk.StringVar()
        ttk_bs.Label(main_frame, text="Description:").pack(anchor=W)
        self.desc_text = tk.Text(main_frame, height=4, width=50)
        self.desc_text.pack(fill=X, pady=(0, 10))
        
        self.category_var = tk.StringVar()
        ttk_bs.Label(main_frame, text="Category:").pack(anchor=W)
        category_combo = ttk_bs.Combobox(
            main_frame, 
            textvariable=self.category_var,
            values=["Programming", "Language", "Business", "Science", "Art", "Other"]
        )
        category_combo.pack(fill=X, pady=(0, 10))
        
        self.difficulty_var = tk.IntVar(value=1)
        ttk_bs.Label(main_frame, text="Difficulty (1-5):").pack(anchor=W)
        difficulty_scale = ttk_bs.Scale(
            main_frame,
            from_=1,
            to=5,
            variable=self.difficulty_var,
            orient=HORIZONTAL
        )
        difficulty_scale.pack(fill=X, pady=(0, 10))
        
        self.hours_var = tk.IntVar()
        ttk_bs.Label(main_frame, text="Estimated Hours:").pack(anchor=W)
        ttk_bs.Entry(main_frame, textvariable=self.hours_var, width=20).pack(anchor=W, pady=(0, 20))
        
        # Buttons
        btn_frame = ttk_bs.Frame(main_frame)
        btn_frame.pack(fill=X)
        
        ttk_bs.Button(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            style='Secondary.TButton'
        ).pack(side=RIGHT, padx=(10, 0))
        
        ttk_bs.Button(
            btn_frame,
            text="Create Course",
            command=self.create_course,
            style='Success.TButton'
        ).pack(side=RIGHT)
        
    def create_course(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a course title.")
            return
            
        description = self.desc_text.get("1.0", tk.END).strip()
        category = self.category_var.get()
        difficulty = self.difficulty_var.get()
        hours = self.hours_var.get()
        
        course_id = self.db.create_course(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            estimated_hours=hours
        )
        
        self.result = course_id
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()


class QuickNoteDialog:
    def __init__(self, parent, db):
        self.db = db
        self.result = None
        
        # Create dialog window
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("Quick Note")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_form()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
        
    def create_form(self):
        main_frame = ttk_bs.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Title
        ttk_bs.Label(main_frame, text="Create Quick Note", style='Header.TLabel').pack(pady=(0, 20))
        
        # Form fields
        self.title_var = tk.StringVar()
        ttk_bs.Label(main_frame, text="Note Title:").pack(anchor=W)
        ttk_bs.Entry(main_frame, textvariable=self.title_var, width=50).pack(fill=X, pady=(0, 10))
        
        # Course selection
        ttk_bs.Label(main_frame, text="Course (optional):").pack(anchor=W)
        self.course_var = tk.StringVar()
        course_combo = ttk_bs.Combobox(main_frame, textvariable=self.course_var, state="readonly")
        courses = self.db.get_courses()
        course_combo['values'] = [""] + [course['title'] for course in courses]
        course_combo.pack(fill=X, pady=(0, 10))
        
        # Note content
        ttk_bs.Label(main_frame, text="Note Content:").pack(anchor=W)
        self.content_text = tk.Text(main_frame, height=8, width=50)
        self.content_text.pack(fill=BOTH, expand=True, pady=(0, 20))
        
        # Buttons
        btn_frame = ttk_bs.Frame(main_frame)
        btn_frame.pack(fill=X)
        
        ttk_bs.Button(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            style='Secondary.TButton'
        ).pack(side=RIGHT, padx=(10, 0))
        
        ttk_bs.Button(
            btn_frame,
            text="Save Note",
            command=self.save_note,
            style='Success.TButton'
        ).pack(side=RIGHT)
        
    def save_note(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a note title.")
            return
            
        content = self.content_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showerror("Error", "Please enter note content.")
            return
        
        # Get course ID
        course_id = None
        course_name = self.course_var.get()
        if course_name:
            courses = self.db.get_courses()
            course = next((c for c in courses if c['title'] == course_name), None)
            if course:
                course_id = course['id']
        
        # Create note
        note_id = self.db.create_note(
            course_id=course_id,
            title=title,
            content=content,
            note_type="quick",
            tags=["quick-note"]
        )
        
        self.result = note_id
        messagebox.showinfo("Success", "Quick note saved successfully!")
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()


def main():
    app = VisualLearningTracker()
    app.run()


if __name__ == "__main__":
    main()