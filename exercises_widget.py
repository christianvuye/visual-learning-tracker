import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import json
import webbrowser
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ExercisesWidget:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.current_exercise_id = None
        self.setup_ui()
        self.refresh_exercises_list()

    def setup_ui(self):
        # Main container
        self.main_frame = ttk_bs.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True)

        # Create paned window for split view
        self.paned_window = ttk_bs.PanedWindow(self.main_frame, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=True)

        # Left panel - Exercises list
        self.create_exercises_list()

        # Right panel - Exercise details
        self.create_exercise_details()

    def create_exercises_list(self):
        # Exercises list frame
        list_frame = ttk_bs.Frame(self.paned_window, width=350)
        self.paned_window.add(list_frame, weight=1)

        # Header
        header_frame = ttk_bs.Frame(list_frame)
        header_frame.pack(fill=X, padx=10, pady=10)

        ttk_bs.Label(
            header_frame, text="🏋️ LLM Exercises", font=("Helvetica", 14, "bold")
        ).pack(side=LEFT)

        ttk_bs.Button(
            header_frame,
            text="+ New Exercise",
            command=self.new_exercise_dialog,
            style="Success.Outline.TButton",
        ).pack(side=RIGHT)

        # Filter buttons
        filter_frame = ttk_bs.Frame(list_frame)
        filter_frame.pack(fill=X, padx=10, pady=(0, 10))

        self.status_filter_var = tk.StringVar(value="all")

        filter_buttons = [
            ("All", "all"),
            ("Active", "in_progress"),
            ("Completed", "completed"),
            ("Paused", "paused"),
        ]

        for text, value in filter_buttons:
            btn = ttk_bs.Radiobutton(
                filter_frame,
                text=text,
                value=value,
                variable=self.status_filter_var,
                command=self.refresh_exercises_list,
            )
            btn.pack(side=LEFT, padx=2)

        # Category filter
        category_frame = ttk_bs.Frame(list_frame)
        category_frame.pack(fill=X, padx=10, pady=(0, 10))

        ttk_bs.Label(category_frame, text="Category:").pack(side=LEFT)
        self.category_filter_var = tk.StringVar(value="all")
        category_combo = ttk_bs.Combobox(
            category_frame,
            textvariable=self.category_filter_var,
            values=[
                "all",
                "coding",
                "algorithms",
                "system_design",
                "debugging",
                "refactoring",
                "testing",
            ],
            state="readonly",
            width=15,
        )
        category_combo.pack(side=LEFT, padx=(5, 0))
        category_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.refresh_exercises_list()
        )

        # Exercises listbox with scrollbar
        list_container = ttk_bs.Frame(list_frame)
        list_container.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        # Create Treeview for better formatting
        columns = ("title", "progress", "time", "status")
        self.exercises_tree = ttk_bs.Treeview(
            list_container, columns=columns, show="tree headings", height=15
        )

        # Configure columns
        self.exercises_tree.heading("#0", text="💪")
        self.exercises_tree.heading("title", text="Title")
        self.exercises_tree.heading("progress", text="Progress")
        self.exercises_tree.heading("time", text="Time (min)")
        self.exercises_tree.heading("status", text="Status")

        self.exercises_tree.column("#0", width=30, minwidth=30)
        self.exercises_tree.column("title", width=180, minwidth=120)
        self.exercises_tree.column("progress", width=70, minwidth=70)
        self.exercises_tree.column("time", width=80, minwidth=80)
        self.exercises_tree.column("status", width=80, minwidth=80)

        # Scrollbar
        scrollbar = ttk_bs.Scrollbar(
            list_container, orient=VERTICAL, command=self.exercises_tree.yview
        )
        self.exercises_tree.configure(yscrollcommand=scrollbar.set)

        self.exercises_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Bind selection event
        self.exercises_tree.bind("<<TreeviewSelect>>", self.on_exercise_select)
        self.exercises_tree.bind("<Double-1>", self.on_exercise_double_click)

    def create_exercise_details(self):
        # Details frame
        details_frame = ttk_bs.Frame(self.paned_window)
        self.paned_window.add(details_frame, weight=2)

        # Header
        header_frame = ttk_bs.Frame(details_frame)
        header_frame.pack(fill=X, padx=20, pady=20)

        self.exercise_title_label = ttk_bs.Label(
            header_frame,
            text="Select an exercise to view details",
            font=("Helvetica", 16, "bold"),
        )
        self.exercise_title_label.pack(side=LEFT)

        # Action buttons
        actions_frame = ttk_bs.Frame(header_frame)
        actions_frame.pack(side=RIGHT)

        ttk_bs.Button(
            actions_frame,
            text="🔗 Open Link",
            command=self.open_conversation_link,
            style="Info.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            actions_frame,
            text="✏️ Edit",
            command=self.edit_exercise,
            style="Warning.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            actions_frame,
            text="🗑️ Delete",
            command=self.delete_exercise,
            style="Danger.TButton",
        ).pack(side=LEFT, padx=2)

        # Exercise information
        self.create_exercise_info(details_frame)

        # Progress tracking
        self.create_progress_section(details_frame)

        # Notes section
        self.create_notes_section(details_frame)

    def create_exercise_info(self, parent):
        info_frame = ttk_bs.LabelFrame(parent, text="Exercise Information", padding=15)
        info_frame.pack(fill=X, padx=20, pady=(0, 10))

        # Create grid layout
        info_grid = ttk_bs.Frame(info_frame)
        info_grid.pack(fill=X)

        # Left column
        left_col = ttk_bs.Frame(info_grid)
        left_col.pack(side=LEFT, fill=BOTH, expand=True)

        self.info_labels = {}
        info_items = [
            ("Category:", "category"),
            ("Type:", "exercise_type"),
            ("Difficulty:", "difficulty"),
            ("Platform:", "platform"),
            ("Course:", "course"),
        ]

        for i, (label_text, key) in enumerate(info_items):
            item_frame = ttk_bs.Frame(left_col)
            item_frame.pack(fill=X, pady=2)

            ttk_bs.Label(item_frame, text=label_text, width=12).pack(side=LEFT)
            value_label = ttk_bs.Label(item_frame, text="-", font=("Helvetica", 10))
            value_label.pack(side=LEFT)
            self.info_labels[key] = value_label

        # Right column
        right_col = ttk_bs.Frame(info_grid)
        right_col.pack(side=RIGHT, fill=BOTH, expand=True)

        time_items = [
            ("Estimated:", "estimated_time"),
            ("Actual:", "actual_time"),
            ("Created:", "created_at"),
            ("Updated:", "updated_at"),
            ("Status:", "status"),
        ]

        for label_text, key in time_items:
            item_frame = ttk_bs.Frame(right_col)
            item_frame.pack(fill=X, pady=2)

            ttk_bs.Label(item_frame, text=label_text, width=12).pack(side=LEFT)
            value_label = ttk_bs.Label(item_frame, text="-", font=("Helvetica", 10))
            value_label.pack(side=LEFT)
            self.info_labels[key] = value_label

        # Description
        desc_frame = ttk_bs.Frame(info_frame)
        desc_frame.pack(fill=X, pady=(10, 0))

        ttk_bs.Label(
            desc_frame, text="Description:", font=("Helvetica", 10, "bold")
        ).pack(anchor=W)
        self.description_text = tk.Text(
            desc_frame, height=3, font=("Helvetica", 9), state="disabled"
        )
        self.description_text.pack(fill=X, pady=(5, 0))

    def create_progress_section(self, parent):
        progress_frame = ttk_bs.LabelFrame(parent, text="Progress Tracking", padding=15)
        progress_frame.pack(fill=X, padx=20, pady=(0, 10))

        # Progress bar
        progress_container = ttk_bs.Frame(progress_frame)
        progress_container.pack(fill=X, pady=(0, 10))

        ttk_bs.Label(progress_container, text="Progress:").pack(side=LEFT)
        self.progress_bar = ttk_bs.Progressbar(
            progress_container, style="Success.Horizontal.TProgressbar", length=200
        )
        self.progress_bar.pack(side=LEFT, padx=(10, 10), fill=X, expand=True)

        self.progress_label = ttk_bs.Label(progress_container, text="0%")
        self.progress_label.pack(side=RIGHT)

        # Progress controls
        controls_frame = ttk_bs.Frame(progress_frame)
        controls_frame.pack(fill=X)

        ttk_bs.Label(controls_frame, text="Update Progress:").pack(side=LEFT)

        self.progress_var = tk.DoubleVar()
        progress_scale = ttk_bs.Scale(
            controls_frame,
            from_=0,
            to=100,
            variable=self.progress_var,
            orient=HORIZONTAL,
            length=150,
            command=self.on_progress_change,
        )
        progress_scale.pack(side=LEFT, padx=(10, 10))

        # Status controls
        status_frame = ttk_bs.Frame(controls_frame)
        status_frame.pack(side=RIGHT)

        ttk_bs.Button(
            status_frame,
            text="Mark Complete",
            command=self.mark_complete,
            style="Success.Outline.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            status_frame,
            text="Pause",
            command=self.pause_exercise,
            style="Warning.Outline.TButton",
        ).pack(side=LEFT, padx=2)

    def create_notes_section(self, parent):
        notes_frame = ttk_bs.LabelFrame(parent, text="Exercise Notes", padding=15)
        notes_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

        # Notes text area
        self.notes_text = tk.Text(
            notes_frame, height=8, font=("Helvetica", 10), wrap=tk.WORD
        )

        notes_scrollbar = ttk_bs.Scrollbar(
            notes_frame, orient=VERTICAL, command=self.notes_text.yview
        )
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)

        self.notes_text.pack(side=LEFT, fill=BOTH, expand=True)
        notes_scrollbar.pack(side=RIGHT, fill=Y)

        # Save notes button
        save_notes_frame = ttk_bs.Frame(notes_frame)
        save_notes_frame.pack(fill=X, pady=(10, 0))

        ttk_bs.Button(
            save_notes_frame,
            text="💾 Save Notes",
            command=self.save_notes,
            style="Info.Outline.TButton",
        ).pack(side=RIGHT)

    def refresh_exercises_list(self):
        # Clear existing items
        for item in self.exercises_tree.get_children():
            self.exercises_tree.delete(item)

        # Get exercises based on filters
        status_filter = self.status_filter_var.get()
        category_filter = self.category_filter_var.get()

        exercises = self.db.get_exercises(
            status=None if status_filter == "all" else status_filter
        )

        # Filter by category
        if category_filter != "all":
            exercises = [ex for ex in exercises if ex["category"] == category_filter]

        # Get course names for display
        courses = {course["id"]: course["title"] for course in self.db.get_courses()}

        # Populate tree
        for exercise in exercises:
            course_name = courses.get(exercise["course_id"], "")

            # Status icons
            status_icons = {
                "in_progress": "🔄",
                "completed": "✅",
                "paused": "⏸️",
                "not_started": "⭕",
            }

            icon = status_icons.get(exercise["status"], "💪")
            progress = f"{exercise['progress']:.0f}%"
            time_spent = f"{exercise['actual_time'] or 0}/{exercise['estimated_time']}"

            self.exercises_tree.insert(
                "",
                "end",
                text=icon,
                values=(exercise["title"], progress, time_spent, exercise["status"]),
                tags=(str(exercise["id"]),),
            )

    def on_exercise_select(self, event):
        selection = self.exercises_tree.selection()
        if selection:
            item = selection[0]
            exercise_id = int(self.exercises_tree.item(item)["tags"][0])
            self.load_exercise_details(exercise_id)

    def on_exercise_double_click(self, event):
        # Double-click opens conversation link
        self.open_conversation_link()

    def load_exercise_details(self, exercise_id: int):
        exercises = self.db.get_exercises()
        exercise = next((ex for ex in exercises if ex["id"] == exercise_id), None)

        if not exercise:
            return

        self.current_exercise_id = exercise_id

        # Update title
        self.exercise_title_label.config(text=exercise["title"])

        # Update info labels
        courses = {course["id"]: course["title"] for course in self.db.get_courses()}
        course_name = courses.get(exercise["course_id"], "No Course")

        self.info_labels["category"].config(text=exercise["category"])
        self.info_labels["exercise_type"].config(text=exercise["exercise_type"])
        self.info_labels["difficulty"].config(text=f"{exercise['difficulty']}/5")
        self.info_labels["platform"].config(text=exercise["platform"])
        self.info_labels["course"].config(text=course_name)
        self.info_labels["estimated_time"].config(
            text=f"{exercise['estimated_time']} min"
        )
        self.info_labels["actual_time"].config(
            text=f"{exercise['actual_time'] or 0} min"
        )
        self.info_labels["status"].config(
            text=exercise["status"].replace("_", " ").title()
        )

        # Format dates
        created_date = exercise["created_at"][:10] if exercise["created_at"] else ""
        updated_date = exercise["updated_at"][:10] if exercise["updated_at"] else ""
        self.info_labels["created_at"].config(text=created_date)
        self.info_labels["updated_at"].config(text=updated_date)

        # Update description
        self.description_text.config(state="normal")
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(
            1.0, exercise["description"] or "No description available."
        )
        self.description_text.config(state="disabled")

        # Update progress
        progress = exercise["progress"] or 0
        self.progress_bar["value"] = progress
        self.progress_label.config(text=f"{progress:.0f}%")
        self.progress_var.set(progress)

        # Update notes
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(1.0, exercise["notes"] or "")

    def on_progress_change(self, value):
        progress = float(value)
        self.progress_bar["value"] = progress
        self.progress_label.config(text=f"{progress:.0f}%")

        if self.current_exercise_id:
            self.db.update_exercise_progress(self.current_exercise_id, progress)

    def mark_complete(self):
        if not self.current_exercise_id:
            return

        self.db.update_exercise_progress(
            self.current_exercise_id, 100.0, status="completed"
        )
        self.refresh_exercises_list()
        self.load_exercise_details(self.current_exercise_id)
        messagebox.showinfo("Success", "Exercise marked as completed!")

    def pause_exercise(self):
        if not self.current_exercise_id:
            return

        current_progress = self.progress_var.get()
        self.db.update_exercise_progress(
            self.current_exercise_id, current_progress, status="paused"
        )
        self.refresh_exercises_list()
        self.load_exercise_details(self.current_exercise_id)
        messagebox.showinfo("Success", "Exercise paused.")

    def save_notes(self):
        if not self.current_exercise_id:
            return

        notes = self.notes_text.get(1.0, tk.END).strip()
        # This would require an update_exercise_notes method in the database
        messagebox.showinfo(
            "Info", "Note saving functionality to be implemented in database layer."
        )

    def open_conversation_link(self):
        if not self.current_exercise_id:
            return

        exercises = self.db.get_exercises()
        exercise = next(
            (ex for ex in exercises if ex["id"] == self.current_exercise_id), None
        )

        if exercise and exercise["conversation_link"]:
            try:
                webbrowser.open(exercise["conversation_link"])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open link: {str(e)}")
        else:
            messagebox.showwarning(
                "No Link", "No conversation link available for this exercise."
            )

    def new_exercise_dialog(self):
        dialog = ExerciseDialog(self.parent, self.db)
        if dialog.result:
            self.refresh_exercises_list()

    def edit_exercise(self):
        if not self.current_exercise_id:
            messagebox.showwarning("No Selection", "Please select an exercise to edit.")
            return
        messagebox.showinfo("Edit", "Exercise editing dialog to be implemented.")

    def delete_exercise(self):
        if not self.current_exercise_id:
            messagebox.showwarning(
                "No Selection", "Please select an exercise to delete."
            )
            return

        if messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this exercise?"
        ):
            messagebox.showinfo(
                "Delete", "Exercise deletion functionality to be implemented."
            )


class ExerciseDialog:
    def __init__(self, parent, db):
        self.db = db
        self.result = None

        # Create dialog window
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("New Exercise")
        self.dialog.geometry("600x700")
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
        ttk_bs.Label(
            main_frame, text="Create New Exercise", style="Header.TLabel"
        ).pack(pady=(0, 20))

        # Basic info
        basic_frame = ttk_bs.LabelFrame(
            main_frame, text="Basic Information", padding=10
        )
        basic_frame.pack(fill=X, pady=(0, 10))

        # Exercise title
        self.title_var = tk.StringVar()
        ttk_bs.Label(basic_frame, text="Exercise Title:").pack(anchor=W)
        ttk_bs.Entry(basic_frame, textvariable=self.title_var, width=60).pack(
            fill=X, pady=(0, 10)
        )

        # Description
        ttk_bs.Label(basic_frame, text="Description:").pack(anchor=W)
        self.description_text = tk.Text(basic_frame, height=4, width=60)
        self.description_text.pack(fill=X, pady=(0, 10))

        # Category and type
        cat_frame = ttk_bs.Frame(basic_frame)
        cat_frame.pack(fill=X, pady=(0, 10))

        ttk_bs.Label(cat_frame, text="Category:").pack(side=LEFT)
        self.category_var = tk.StringVar(value="coding")
        category_combo = ttk_bs.Combobox(
            cat_frame,
            textvariable=self.category_var,
            values=[
                "coding",
                "algorithms",
                "system_design",
                "debugging",
                "refactoring",
                "testing",
            ],
            width=20,
        )
        category_combo.pack(side=LEFT, padx=(5, 20))

        ttk_bs.Label(cat_frame, text="Type:").pack(side=LEFT)
        self.type_var = tk.StringVar(value="coding")
        type_combo = ttk_bs.Combobox(
            cat_frame,
            textvariable=self.type_var,
            values=["coding", "theory", "problem_solving", "code_review", "debugging"],
            width=20,
        )
        type_combo.pack(side=LEFT, padx=(5, 0))

        # Technical details
        tech_frame = ttk_bs.LabelFrame(main_frame, text="Technical Details", padding=10)
        tech_frame.pack(fill=X, pady=(0, 10))

        # Difficulty and time
        diff_frame = ttk_bs.Frame(tech_frame)
        diff_frame.pack(fill=X, pady=(0, 10))

        ttk_bs.Label(diff_frame, text="Difficulty (1-5):").pack(side=LEFT)
        self.difficulty_var = tk.IntVar(value=3)
        difficulty_scale = ttk_bs.Scale(
            diff_frame,
            from_=1,
            to=5,
            variable=self.difficulty_var,
            orient=HORIZONTAL,
            length=100,
        )
        difficulty_scale.pack(side=LEFT, padx=(10, 20))

        ttk_bs.Label(diff_frame, text="Estimated Time (min):").pack(side=LEFT)
        self.time_var = tk.IntVar(value=60)
        ttk_bs.Entry(diff_frame, textvariable=self.time_var, width=10).pack(
            side=LEFT, padx=(5, 0)
        )

        # Platform and course
        platform_frame = ttk_bs.Frame(tech_frame)
        platform_frame.pack(fill=X, pady=(0, 10))

        ttk_bs.Label(platform_frame, text="Platform:").pack(side=LEFT)
        self.platform_var = tk.StringVar(value="LLM")
        platform_combo = ttk_bs.Combobox(
            platform_frame,
            textvariable=self.platform_var,
            values=["LLM", "ChatGPT", "Claude", "Copilot", "Other"],
            width=15,
        )
        platform_combo.pack(side=LEFT, padx=(5, 20))

        ttk_bs.Label(platform_frame, text="Related Course:").pack(side=LEFT)
        self.course_var = tk.StringVar()
        course_combo = ttk_bs.Combobox(
            platform_frame, textvariable=self.course_var, state="readonly", width=25
        )
        courses = self.db.get_courses()
        course_combo["values"] = [""] + [course["title"] for course in courses]
        course_combo.pack(side=LEFT, padx=(5, 0))

        # Conversation link
        link_frame = ttk_bs.LabelFrame(main_frame, text="Conversation Link", padding=10)
        link_frame.pack(fill=X, pady=(0, 10))

        ttk_bs.Label(link_frame, text="Link to LLM Conversation:").pack(anchor=W)
        self.link_var = tk.StringVar()
        ttk_bs.Entry(link_frame, textvariable=self.link_var, width=70).pack(
            fill=X, pady=(5, 0)
        )

        # Tags and concepts
        tags_frame = ttk_bs.LabelFrame(main_frame, text="Tags & Concepts", padding=10)
        tags_frame.pack(fill=X, pady=(0, 20))

        ttk_bs.Label(tags_frame, text="Tags (comma separated):").pack(anchor=W)
        self.tags_var = tk.StringVar()
        ttk_bs.Entry(tags_frame, textvariable=self.tags_var, width=70).pack(
            fill=X, pady=(5, 10)
        )

        ttk_bs.Label(tags_frame, text="Concepts (comma separated):").pack(anchor=W)
        self.concepts_var = tk.StringVar()
        ttk_bs.Entry(tags_frame, textvariable=self.concepts_var, width=70).pack(
            fill=X, pady=(5, 0)
        )

        # Buttons
        btn_frame = ttk_bs.Frame(main_frame)
        btn_frame.pack(fill=X)

        ttk_bs.Button(
            btn_frame, text="Cancel", command=self.cancel, style="Secondary.TButton"
        ).pack(side=RIGHT, padx=(10, 0))

        ttk_bs.Button(
            btn_frame,
            text="Create Exercise",
            command=self.create_exercise,
            style="Success.TButton",
        ).pack(side=RIGHT)

    def create_exercise(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter an exercise title.")
            return

        description = self.description_text.get("1.0", tk.END).strip()

        # Get course ID
        course_id = None
        course_name = self.course_var.get()
        if course_name:
            courses = self.db.get_courses()
            course = next((c for c in courses if c["title"] == course_name), None)
            if course:
                course_id = course["id"]

        # Parse tags and concepts
        tags_text = self.tags_var.get().strip()
        tags = (
            [tag.strip() for tag in tags_text.split(",") if tag.strip()]
            if tags_text
            else []
        )

        concepts_text = self.concepts_var.get().strip()
        concepts = (
            [concept.strip() for concept in concepts_text.split(",") if concept.strip()]
            if concepts_text
            else []
        )

        # Create exercise
        exercise_id = self.db.create_exercise(
            title=title,
            description=description,
            category=self.category_var.get(),
            difficulty=self.difficulty_var.get(),
            exercise_type=self.type_var.get(),
            conversation_link=self.link_var.get().strip(),
            platform=self.platform_var.get(),
            estimated_time=self.time_var.get(),
            course_id=course_id,
            concepts=concepts,
            tags=tags,
        )

        self.result = exercise_id
        messagebox.showinfo("Success", "Exercise created successfully!")
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()


# Example usage
if __name__ == "__main__":
    from database import DatabaseManager

    root = ttk_bs.Window(themename="superhero")
    root.title("Exercises Demo")
    root.geometry("1200x800")

    db = DatabaseManager("test_exercises.db")
    widget = ExercisesWidget(root, db)

    root.mainloop()
