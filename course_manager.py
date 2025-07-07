import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
from datetime import datetime, date
import json
from typing import List, Dict, Optional


class CourseManagerWidget:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        self.main_frame = ttk_bs.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Create paned window for split view
        self.paned_window = ttk_bs.PanedWindow(self.main_frame, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=True)
        
        # Left panel - Course list
        self.create_course_list()
        
        # Right panel - Course details
        self.create_course_details()
        
        # Load initial courses
        self.refresh_course_list()
        
    def create_course_list(self):
        # Course list frame
        list_frame = ttk_bs.Frame(self.paned_window, width=400)
        self.paned_window.add(list_frame, weight=1)
        
        # Header
        header_frame = ttk_bs.Frame(list_frame)
        header_frame.pack(fill=X, padx=10, pady=10)
        
        ttk_bs.Label(
            header_frame,
            text="📚 My Courses",
            font=('Helvetica', 16, 'bold')
        ).pack(side=LEFT)
        
        ttk_bs.Button(
            header_frame,
            text="+ New Course",
            command=self.new_course_dialog,
            style='Success.TButton'
        ).pack(side=RIGHT)
        
        # Filter buttons
        filter_frame = ttk_bs.Frame(list_frame)
        filter_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        self.filter_var = tk.StringVar(value="all")
        
        filter_buttons = [
            ("All", "all"),
            ("Active", "active"),
            ("Completed", "completed"),
            ("Paused", "paused")
        ]
        
        for text, value in filter_buttons:
            btn = ttk_bs.Radiobutton(
                filter_frame,
                text=text,
                value=value,
                variable=self.filter_var,
                command=self.refresh_course_list
            )
            btn.pack(side=LEFT, padx=5)
        
        # Course cards container
        self.courses_container = ttk_bs.Frame(list_frame)
        self.courses_container.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create scrollable area
        canvas = tk.Canvas(self.courses_container)
        scrollbar = ttk_bs.Scrollbar(self.courses_container, orient=VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk_bs.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.canvas = canvas
        
    def create_course_details(self):
        # Course details frame
        details_frame = ttk_bs.Frame(self.paned_window)
        self.paned_window.add(details_frame, weight=2)
        
        # Header
        header_frame = ttk_bs.Frame(details_frame)
        header_frame.pack(fill=X, padx=20, pady=20)
        
        self.course_title_label = ttk_bs.Label(
            header_frame,
            text="Select a course to view details",
            font=('Helvetica', 18, 'bold')
        )
        self.course_title_label.pack(side=LEFT)
        
        # Action buttons
        self.action_frame = ttk_bs.Frame(header_frame)
        self.action_frame.pack(side=RIGHT)
        
        ttk_bs.Button(
            self.action_frame,
            text="📖 Study",
            command=self.start_study_session,
            style='Success.TButton'
        ).pack(side=LEFT, padx=2)
        
        ttk_bs.Button(
            self.action_frame,
            text="✏️ Edit",
            command=self.edit_current_course,
            style='Info.TButton'
        ).pack(side=LEFT, padx=2)
        
        ttk_bs.Button(
            self.action_frame,
            text="🗑️ Delete",
            command=self.delete_current_course,
            style='Danger.TButton'
        ).pack(side=LEFT, padx=2)
        
        # Course information
        self.create_course_info_section(details_frame)
        
        # Modules section
        self.create_modules_section(details_frame)
        
        # Progress section
        self.create_progress_section(details_frame)
        
        self.current_course_id = None
        
    def create_course_info_section(self, parent):
        info_frame = ttk_bs.LabelFrame(parent, text="Course Information", padding=15)
        info_frame.pack(fill=X, padx=20, pady=(0, 20))
        
        # Create info labels
        self.info_labels = {}
        
        info_items = [
            ("Category", "category"),
            ("Difficulty", "difficulty"),
            ("Estimated Hours", "estimated_hours"),
            ("Current Progress", "current_progress"),
            ("Status", "status"),
            ("Start Date", "start_date"),
            ("Target Date", "target_date")
        ]
        
        row = 0
        for label_text, key in info_items:
            # Label
            ttk_bs.Label(
                info_frame,
                text=f"{label_text}:",
                font=('Helvetica', 10, 'bold')
            ).grid(row=row, column=0, sticky=W, padx=(0, 10), pady=2)
            
            # Value
            value_label = ttk_bs.Label(info_frame, text="")
            value_label.grid(row=row, column=1, sticky=W, pady=2)
            self.info_labels[key] = value_label
            
            row += 1
        
        # Description
        ttk_bs.Label(
            info_frame,
            text="Description:",
            font=('Helvetica', 10, 'bold')
        ).grid(row=row, column=0, sticky=NW, padx=(0, 10), pady=(10, 0))
        
        self.description_text = tk.Text(
            info_frame,
            height=3,
            width=50,
            font=('Helvetica', 10),
            state='disabled'
        )
        self.description_text.grid(row=row, column=1, sticky=EW, pady=(10, 0))
        
        info_frame.grid_columnconfigure(1, weight=1)
        
    def create_modules_section(self, parent):
        modules_frame = ttk_bs.LabelFrame(parent, text="Course Modules", padding=15)
        modules_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Modules header
        modules_header = ttk_bs.Frame(modules_frame)
        modules_header.pack(fill=X, pady=(0, 10))
        
        ttk_bs.Label(
            modules_header,
            text="📋 Learning Modules",
            font=('Helvetica', 12, 'bold')
        ).pack(side=LEFT)
        
        ttk_bs.Button(
            modules_header,
            text="+ Add Module",
            command=self.add_module_dialog,
            style='Info.Outline.TButton'
        ).pack(side=RIGHT)
        
        # Modules list
        columns = ("title", "status", "estimated", "actual")
        self.modules_tree = ttk_bs.Treeview(
            modules_frame,
            columns=columns,
            show="tree headings",
            height=8
        )
        
        # Configure columns
        self.modules_tree.heading("#0", text="📚")
        self.modules_tree.heading("title", text="Module Title")
        self.modules_tree.heading("status", text="Status")
        self.modules_tree.heading("estimated", text="Est. Time")
        self.modules_tree.heading("actual", text="Actual Time")
        
        self.modules_tree.column("#0", width=30)
        self.modules_tree.column("title", width=250)
        self.modules_tree.column("status", width=100)
        self.modules_tree.column("estimated", width=80)
        self.modules_tree.column("actual", width=80)
        
        # Scrollbar for modules
        modules_scrollbar = ttk_bs.Scrollbar(modules_frame, orient=VERTICAL, command=self.modules_tree.yview)
        self.modules_tree.configure(yscrollcommand=modules_scrollbar.set)
        
        self.modules_tree.pack(side=LEFT, fill=BOTH, expand=True)
        modules_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Bind events
        self.modules_tree.bind("<Double-1>", self.toggle_module_completion)
        
    def create_progress_section(self, parent):
        progress_frame = ttk_bs.LabelFrame(parent, text="Progress Overview", padding=15)
        progress_frame.pack(fill=X, padx=20, pady=(0, 20))
        
        # Progress bar
        progress_container = ttk_bs.Frame(progress_frame)
        progress_container.pack(fill=X, pady=(0, 10))
        
        ttk_bs.Label(progress_container, text="Overall Progress:").pack(anchor=W)
        
        self.progress_bar = ttk_bs.Progressbar(
            progress_container,
            style='Success.Horizontal.TProgressbar',
            length=400
        )
        self.progress_bar.pack(fill=X, pady=(5, 0))
        
        self.progress_label = ttk_bs.Label(progress_container, text="0%")
        self.progress_label.pack(anchor=E)
        
        # Statistics
        stats_frame = ttk_bs.Frame(progress_frame)
        stats_frame.pack(fill=X)
        
        self.stats_labels = {}
        stats_items = [
            ("Total Modules", "total_modules"),
            ("Completed", "completed_modules"),
            ("Study Time", "study_time"),
            ("Last Session", "last_session")
        ]
        
        for i, (label_text, key) in enumerate(stats_items):
            stat_frame = ttk_bs.Frame(stats_frame)
            stat_frame.pack(side=LEFT, fill=X, expand=True, padx=5)
            
            ttk_bs.Label(
                stat_frame,
                text=label_text,
                font=('Helvetica', 9)
            ).pack()
            
            value_label = ttk_bs.Label(
                stat_frame,
                text="0",
                font=('Helvetica', 14, 'bold')
            )
            value_label.pack()
            self.stats_labels[key] = value_label
            
    def refresh_course_list(self):
        # Clear existing course cards
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get courses based on filter
        filter_status = self.filter_var.get()
        if filter_status == "all":
            courses = self.db.get_courses()
        else:
            courses = self.db.get_courses(status=filter_status)
        
        # Create course cards
        for course in courses:
            self.create_course_card(course)
            
    def create_course_card(self, course):
        card_frame = ttk_bs.Frame(self.scrollable_frame, style='Card.TFrame')
        card_frame.pack(fill=X, pady=5, padx=5)
        
        # Make card clickable
        card_frame.bind("<Button-1>", lambda e, c=course: self.select_course(c))
        
        # Course content
        content_frame = ttk_bs.Frame(card_frame)
        content_frame.pack(fill=X, padx=15, pady=15)
        content_frame.bind("<Button-1>", lambda e, c=course: self.select_course(c))
        
        # Title and category
        title_frame = ttk_bs.Frame(content_frame)
        title_frame.pack(fill=X)
        title_frame.bind("<Button-1>", lambda e, c=course: self.select_course(c))
        
        title_label = ttk_bs.Label(
            title_frame,
            text=course['title'],
            font=('Helvetica', 12, 'bold')
        )
        title_label.pack(side=LEFT)
        title_label.bind("<Button-1>", lambda e, c=course: self.select_course(c))
        
        if course['category']:
            category_label = ttk_bs.Label(
                title_frame,
                text=f"📂 {course['category']}",
                foreground="gray"
            )
            category_label.pack(side=RIGHT)
            category_label.bind("<Button-1>", lambda e, c=course: self.select_course(c))
        
        # Progress
        progress_frame = ttk_bs.Frame(content_frame)
        progress_frame.pack(fill=X, pady=(5, 0))
        progress_frame.bind("<Button-1>", lambda e, c=course: self.select_course(c))
        
        progress_bar = ttk_bs.Progressbar(
            progress_frame,
            value=course['current_progress'],
            style='Success.Horizontal.TProgressbar'
        )
        progress_bar.pack(fill=X, side=LEFT, expand=True)
        
        progress_text = ttk_bs.Label(
            progress_frame,
            text=f"{course['current_progress']:.0f}%"
        )
        progress_text.pack(side=RIGHT, padx=(10, 0))
        progress_text.bind("<Button-1>", lambda e, c=course: self.select_course(c))
        
    def select_course(self, course):
        self.current_course_id = course['id']
        self.load_course_details(course)
        
    def load_course_details(self, course):
        # Update course title
        self.course_title_label.config(text=course['title'])
        
        # Update info labels
        self.info_labels['category'].config(text=course['category'] or "None")
        self.info_labels['difficulty'].config(text=f"{course['difficulty']}/5")
        self.info_labels['estimated_hours'].config(text=f"{course['estimated_hours']} hours")
        self.info_labels['current_progress'].config(text=f"{course['current_progress']:.1f}%")
        self.info_labels['status'].config(text=course['status'].title())
        self.info_labels['start_date'].config(text=course['start_date'] or "Not set")
        self.info_labels['target_date'].config(text=course['target_date'] or "Not set")
        
        # Update description
        self.description_text.config(state='normal')
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(1.0, course['description'] or "No description available.")
        self.description_text.config(state='disabled')
        
        # Update progress bar
        self.progress_bar['value'] = course['current_progress']
        self.progress_label.config(text=f"{course['current_progress']:.1f}%")
        
        # Load modules
        self.load_course_modules(course['id'])
        
    def load_course_modules(self, course_id):
        # Clear existing modules
        for item in self.modules_tree.get_children():
            self.modules_tree.delete(item)
        
        # Get modules
        modules = self.db.get_course_modules(course_id)
        
        for module in modules:
            status = "✅ Completed" if module['completed'] else "⏳ Pending"
            estimated = f"{module['estimated_minutes']}m" if module['estimated_minutes'] else "N/A"
            actual = f"{module['actual_minutes']}m" if module['actual_minutes'] else "N/A"
            
            self.modules_tree.insert(
                "",
                "end",
                text="📚",
                values=(module['title'], status, estimated, actual),
                tags=(str(module['id']),)
            )
        
        # Update statistics
        total_modules = len(modules)
        completed_modules = sum(1 for m in modules if m['completed'])
        
        self.stats_labels['total_modules'].config(text=str(total_modules))
        self.stats_labels['completed_modules'].config(text=str(completed_modules))
        self.stats_labels['study_time'].config(text="0h")  # Would need session data
        self.stats_labels['last_session'].config(text="Never")  # Would need session data
        
    def new_course_dialog(self):
        dialog = CourseDialog(self.parent, self.db)
        if dialog.result:
            self.refresh_course_list()
            
    def add_module_dialog(self):
        if not self.current_course_id:
            messagebox.showwarning("No Course Selected", "Please select a course first.")
            return
            
        dialog = ModuleDialog(self.parent, self.db, self.current_course_id)
        if dialog.result:
            self.load_course_modules(self.current_course_id)
            
    def toggle_module_completion(self, event):
        selection = self.modules_tree.selection()
        if selection:
            item = selection[0]
            module_id = int(self.modules_tree.item(item)['tags'][0])
            self.db.complete_module(module_id)
            self.load_course_modules(self.current_course_id)
            
    def start_study_session(self):
        if not self.current_course_id:
            messagebox.showwarning("No Course Selected", "Please select a course first.")
            return
        messagebox.showinfo("Study Session", "Study session feature integrated with main app timer!")
        
    def edit_current_course(self):
        if not self.current_course_id:
            messagebox.showwarning("No Course Selected", "Please select a course first.")
            return
        messagebox.showinfo("Edit Course", "Course editing feature coming soon!")
        
    def delete_current_course(self):
        if not self.current_course_id:
            messagebox.showwarning("No Course Selected", "Please select a course first.")
            return
        messagebox.showinfo("Delete Course", "Course deletion feature coming soon!")


class ModuleDialog:
    def __init__(self, parent, db, course_id):
        self.db = db
        self.course_id = course_id
        self.result = None
        
        # Create dialog window
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("Add Module")
        self.dialog.geometry("400x300")
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
        ttk_bs.Label(main_frame, text="Add New Module", style='Header.TLabel').pack(pady=(0, 20))
        
        # Form fields
        self.title_var = tk.StringVar()
        ttk_bs.Label(main_frame, text="Module Title:").pack(anchor=W)
        ttk_bs.Entry(main_frame, textvariable=self.title_var, width=40).pack(fill=X, pady=(0, 10))
        
        self.desc_var = tk.StringVar()
        ttk_bs.Label(main_frame, text="Description:").pack(anchor=W)
        desc_text = tk.Text(main_frame, height=4, width=40)
        desc_text.pack(fill=X, pady=(0, 10))
        
        self.minutes_var = tk.IntVar()
        ttk_bs.Label(main_frame, text="Estimated Minutes:").pack(anchor=W)
        ttk_bs.Entry(main_frame, textvariable=self.minutes_var, width=20).pack(anchor=W, pady=(0, 20))
        
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
            text="Add Module",
            command=self.add_module,
            style='Success.TButton'
        ).pack(side=RIGHT)
        
        self.desc_text = desc_text
        
    def add_module(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a module title.")
            return
            
        description = self.desc_text.get("1.0", tk.END).strip()
        minutes = self.minutes_var.get()
        
        module_id = self.db.add_course_module(
            course_id=self.course_id,
            title=title,
            description=description,
            estimated_minutes=minutes
        )
        
        self.result = module_id
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()


# Use the existing CourseDialog from main.py
class CourseDialog:
    def __init__(self, parent, db):
        self.db = db
        self.result = None
        
        # Create dialog window
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("New Course")
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
        ttk_bs.Label(main_frame, text="Create New Course", style='Header.TLabel').pack(pady=(0, 20))
        
        # Form fields
        self.title_var = tk.StringVar()
        ttk_bs.Label(main_frame, text="Course Title:").pack(anchor=W)
        ttk_bs.Entry(main_frame, textvariable=self.title_var, width=50).pack(fill=X, pady=(0, 10))
        
        self.desc_var = tk.StringVar()
        ttk_bs.Label(main_frame, text="Description:").pack(anchor=W)
        desc_text = tk.Text(main_frame, height=4, width=50)
        desc_text.pack(fill=X, pady=(0, 10))
        
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
        
        self.desc_text = desc_text
        
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


# Example usage
if __name__ == "__main__":
    from database import DatabaseManager
    
    root = ttk_bs.Window(themename="superhero")
    root.title("Course Manager Demo")
    root.geometry("1200x800")
    
    db = DatabaseManager("test_courses.db")
    widget = CourseManagerWidget(root, db)
    
    root.mainloop()