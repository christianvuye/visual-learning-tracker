import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import json
from datetime import datetime
from typing import List, Dict, Optional


class NotesEditor:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.current_note_id = None
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        self.main_frame = ttk_bs.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Create paned window for split view
        self.paned_window = ttk_bs.PanedWindow(self.main_frame, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=True)
        
        # Left panel - Notes list
        self.create_notes_list()
        
        # Right panel - Editor
        self.create_editor()
        
        # Load initial notes
        self.refresh_notes_list()
        
    def create_notes_list(self):
        # Notes list frame
        list_frame = ttk_bs.Frame(self.paned_window, width=300)
        self.paned_window.add(list_frame, weight=1)
        
        # Header
        header_frame = ttk_bs.Frame(list_frame)
        header_frame.pack(fill=X, padx=10, pady=10)
        
        ttk_bs.Label(
            header_frame,
            text="📝 Notes",
            font=('Helvetica', 14, 'bold')
        ).pack(side=LEFT)
        
        ttk_bs.Button(
            header_frame,
            text="+ New",
            command=self.new_note,
            style='Success.Outline.TButton'
        ).pack(side=RIGHT)
        
        # Search bar
        search_frame = ttk_bs.Frame(list_frame)
        search_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        
        # Add a label for search hint
        ttk_bs.Label(search_frame, text="Search notes:", font=('Helvetica', 9)).pack(anchor=W)
        
        search_entry = ttk_bs.Entry(
            search_frame,
            textvariable=self.search_var
        )
        search_entry.pack(fill=X)
        
        # Filter buttons
        filter_frame = ttk_bs.Frame(list_frame)
        filter_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        self.filter_var = tk.StringVar(value="all")
        
        filter_buttons = [
            ("All", "all"),
            ("Recent", "recent"),
            ("Favorites", "favorites")
        ]
        
        for text, value in filter_buttons:
            btn = ttk_bs.Radiobutton(
                filter_frame,
                text=text,
                value=value,
                variable=self.filter_var,
                command=self.refresh_notes_list
            )
            btn.pack(side=LEFT, padx=2)
        
        # Notes listbox with scrollbar
        list_container = ttk_bs.Frame(list_frame)
        list_container.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create Treeview for better formatting
        columns = ("title", "date", "course")
        self.notes_tree = ttk_bs.Treeview(
            list_container,
            columns=columns,
            show="tree headings",
            height=15
        )
        
        # Configure columns
        self.notes_tree.heading("#0", text="📝")
        self.notes_tree.heading("title", text="Title")
        self.notes_tree.heading("date", text="Date")
        self.notes_tree.heading("course", text="Course")
        
        self.notes_tree.column("#0", width=30, minwidth=30)
        self.notes_tree.column("title", width=150, minwidth=100)
        self.notes_tree.column("date", width=80, minwidth=80)
        self.notes_tree.column("course", width=100, minwidth=80)
        
        # Scrollbar
        scrollbar = ttk_bs.Scrollbar(list_container, orient=VERTICAL, command=self.notes_tree.yview)
        self.notes_tree.configure(yscrollcommand=scrollbar.set)
        
        self.notes_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Bind selection event
        self.notes_tree.bind("<<TreeviewSelect>>", self.on_note_select)
        self.notes_tree.bind("<Double-1>", self.on_note_double_click)
        
    def create_editor(self):
        # Editor frame
        editor_frame = ttk_bs.Frame(self.paned_window)
        self.paned_window.add(editor_frame, weight=3)
        
        # Toolbar
        self.create_editor_toolbar(editor_frame)
        
        # Note metadata
        self.create_note_metadata(editor_frame)
        
        # Text editor
        self.create_text_editor(editor_frame)
        
        # Tags and actions
        self.create_note_actions(editor_frame)
        
    def create_editor_toolbar(self, parent):
        toolbar_frame = ttk_bs.Frame(parent)
        toolbar_frame.pack(fill=X, padx=10, pady=10)
        
        # File operations
        ttk_bs.Button(
            toolbar_frame,
            text="💾 Save",
            command=self.save_note,
            style='Success.Outline.TButton'
        ).pack(side=LEFT, padx=2)
        
        ttk_bs.Button(
            toolbar_frame,
            text="🗑️ Delete",
            command=self.delete_note,
            style='Danger.Outline.TButton'
        ).pack(side=LEFT, padx=2)
        
        ttk_bs.Separator(toolbar_frame, orient=VERTICAL).pack(side=LEFT, padx=10, fill=Y)
        
        # Text formatting
        ttk_bs.Button(
            toolbar_frame,
            text="B",
            command=lambda: self.format_text("bold"),
            style='Secondary.Outline.TButton',
            width=3
        ).pack(side=LEFT, padx=1)
        
        ttk_bs.Button(
            toolbar_frame,
            text="I",
            command=lambda: self.format_text("italic"),
            style='Secondary.Outline.TButton',
            width=3
        ).pack(side=LEFT, padx=1)
        
        ttk_bs.Button(
            toolbar_frame,
            text="U",
            command=lambda: self.format_text("underline"),
            style='Secondary.Outline.TButton',
            width=3
        ).pack(side=LEFT, padx=1)
        
        ttk_bs.Separator(toolbar_frame, orient=VERTICAL).pack(side=LEFT, padx=10, fill=Y)
        
        # Font size
        ttk_bs.Label(toolbar_frame, text="Size:").pack(side=LEFT, padx=(0, 5))
        
        self.font_size_var = tk.StringVar(value="12")
        font_size_combo = ttk_bs.Combobox(
            toolbar_frame,
            textvariable=self.font_size_var,
            values=["8", "10", "12", "14", "16", "18", "20", "24"],
            width=5
        )
        font_size_combo.pack(side=LEFT, padx=2)
        font_size_combo.bind("<<ComboboxSelected>>", self.change_font_size)
        
        # Export options
        ttk_bs.Separator(toolbar_frame, orient=VERTICAL).pack(side=LEFT, padx=10, fill=Y)
        
        ttk_bs.Button(
            toolbar_frame,
            text="📤 Export",
            command=self.export_note,
            style='Info.Outline.TButton'
        ).pack(side=RIGHT, padx=2)
        
    def create_note_metadata(self, parent):
        metadata_frame = ttk_bs.LabelFrame(parent, text="Note Information", padding=10)
        metadata_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Title
        title_frame = ttk_bs.Frame(metadata_frame)
        title_frame.pack(fill=X, pady=(0, 5))
        
        ttk_bs.Label(title_frame, text="Title:", width=10).pack(side=LEFT)
        self.title_var = tk.StringVar()
        self.title_entry = ttk_bs.Entry(title_frame, textvariable=self.title_var, font=('Helvetica', 12, 'bold'))
        self.title_entry.pack(side=LEFT, fill=X, expand=True)
        
        # Course selection
        course_frame = ttk_bs.Frame(metadata_frame)
        course_frame.pack(fill=X, pady=(0, 5))
        
        ttk_bs.Label(course_frame, text="Course:", width=10).pack(side=LEFT)
        self.course_var = tk.StringVar()
        self.course_combo = ttk_bs.Combobox(course_frame, textvariable=self.course_var, state="readonly")
        self.course_combo.pack(side=LEFT, fill=X, expand=True)
        self.refresh_course_list()
        
        # Note type
        type_frame = ttk_bs.Frame(metadata_frame)
        type_frame.pack(fill=X)
        
        ttk_bs.Label(type_frame, text="Type:", width=10).pack(side=LEFT)
        self.note_type_var = tk.StringVar(value="text")
        type_combo = ttk_bs.Combobox(
            type_frame,
            textvariable=self.note_type_var,
            values=["text", "summary", "concept", "example", "question"],
            state="readonly"
        )
        type_combo.pack(side=LEFT, padx=(0, 10))
        
        # Favorite checkbox
        self.favorite_var = tk.BooleanVar()
        ttk_bs.Checkbutton(
            type_frame,
            text="⭐ Favorite",
            variable=self.favorite_var
        ).pack(side=LEFT)
        
    def create_text_editor(self, parent):
        # Text editor with scrollbar
        editor_frame = ttk_bs.Frame(parent)
        editor_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create text widget
        self.text_editor = tk.Text(
            editor_frame,
            wrap=tk.WORD,
            font=('Helvetica', 12),
            undo=True,
            maxundo=50
        )
        
        # Scrollbar
        scrollbar = ttk_bs.Scrollbar(editor_frame, orient=VERTICAL, command=self.text_editor.yview)
        self.text_editor.configure(yscrollcommand=scrollbar.set)
        
        self.text_editor.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Configure text tags for formatting
        self.setup_text_tags()
        
        # Bind events
        self.text_editor.bind("<KeyRelease>", self.on_text_changed)
        self.text_editor.bind("<Control-s>", lambda e: self.save_note())
        
    def create_note_actions(self, parent):
        actions_frame = ttk_bs.LabelFrame(parent, text="Tags & Actions", padding=10)
        actions_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Tags
        tags_frame = ttk_bs.Frame(actions_frame)
        tags_frame.pack(fill=X, pady=(0, 10))
        
        ttk_bs.Label(tags_frame, text="Tags:", width=10).pack(side=LEFT)
        self.tags_var = tk.StringVar()
        
        # Tags container with hint
        tags_container = ttk_bs.Frame(tags_frame)
        tags_container.pack(side=LEFT, fill=X, expand=True)
        
        ttk_bs.Label(tags_container, text="(comma separated)", font=('Helvetica', 8), foreground="gray").pack(anchor=W)
        
        tags_entry = ttk_bs.Entry(
            tags_container,
            textvariable=self.tags_var
        )
        tags_entry.pack(fill=X)
        
        # Quick actions
        quick_frame = ttk_bs.Frame(actions_frame)
        quick_frame.pack(fill=X)
        
        ttk_bs.Button(
            quick_frame,
            text="🃏 Create Flashcard",
            command=self.create_flashcard_from_selection,
            style='Info.Outline.TButton'
        ).pack(side=LEFT, padx=2)
        
        ttk_bs.Button(
            quick_frame,
            text="🧠 Add to Mind Map",
            command=self.add_to_mind_map,
            style='Warning.Outline.TButton'
        ).pack(side=LEFT, padx=2)
        
        ttk_bs.Button(
            quick_frame,
            text="📊 Word Count",
            command=self.show_word_count,
            style='Secondary.Outline.TButton'
        ).pack(side=RIGHT, padx=2)
        
    def setup_text_tags(self):
        # Configure text formatting tags
        self.text_editor.tag_configure("bold", font=('Helvetica', 12, 'bold'))
        self.text_editor.tag_configure("italic", font=('Helvetica', 12, 'italic'))
        self.text_editor.tag_configure("underline", underline=True)
        self.text_editor.tag_configure("heading1", font=('Helvetica', 18, 'bold'))
        self.text_editor.tag_configure("heading2", font=('Helvetica', 16, 'bold'))
        self.text_editor.tag_configure("code", font=('Courier', 11), background='#f8f8f8')
        
    def refresh_course_list(self):
        courses = self.db.get_courses()
        course_names = [""] + [course['title'] for course in courses]
        self.course_combo['values'] = course_names
        
    def refresh_notes_list(self):
        # Clear existing items
        for item in self.notes_tree.get_children():
            self.notes_tree.delete(item)
        
        # Get notes based on filter
        filter_type = self.filter_var.get()
        search_query = self.search_var.get()
        
        if filter_type == "favorites":
            # Would need to add favorites filter to database
            notes = self.db.get_notes(search_query=search_query)
            notes = [note for note in notes if note.get('is_favorite', False)]
        elif filter_type == "recent":
            notes = self.db.get_notes(search_query=search_query)
            # Sort by date and take recent ones
            notes = sorted(notes, key=lambda x: x['updated_at'], reverse=True)[:20]
        else:
            notes = self.db.get_notes(search_query=search_query)
        
        # Get course names for display
        courses = {course['id']: course['title'] for course in self.db.get_courses()}
        
        # Populate tree
        for note in notes:
            course_name = courses.get(note['course_id'], 'No Course')
            created_date = note['created_at'][:10] if note['created_at'] else ''
            
            icon = "⭐" if note.get('is_favorite', False) else "📝"
            
            self.notes_tree.insert(
                "",
                "end",
                text=icon,
                values=(note['title'], created_date, course_name),
                tags=(str(note['id']),)
            )
    
    def on_search_changed(self, *args):
        # Refresh list when search changes
        self.refresh_notes_list()
        
    def on_note_select(self, event):
        selection = self.notes_tree.selection()
        if selection:
            item = selection[0]
            note_id = int(self.notes_tree.item(item)['tags'][0])
            self.load_note(note_id)
            
    def on_note_double_click(self, event):
        # Double-click focuses on editor
        self.text_editor.focus_set()
        
    def new_note(self):
        # Clear editor for new note
        self.current_note_id = None
        self.title_var.set("New Note")
        self.course_var.set("")
        self.note_type_var.set("text")
        self.tags_var.set("")
        self.favorite_var.set(False)
        self.text_editor.delete(1.0, tk.END)
        self.title_entry.focus_set()
        
    def load_note(self, note_id: int):
        notes = self.db.get_notes()
        note = next((n for n in notes if n['id'] == note_id), None)
        
        if not note:
            messagebox.showerror("Error", "Note not found!")
            return
        
        self.current_note_id = note_id
        self.title_var.set(note['title'])
        self.note_type_var.set(note['note_type'])
        self.favorite_var.set(note.get('is_favorite', False))
        
        # Set course
        if note['course_id']:
            courses = self.db.get_courses()
            course = next((c for c in courses if c['id'] == note['course_id']), None)
            if course:
                self.course_var.set(course['title'])
        
        # Set tags
        tags = json.loads(note['tags']) if note['tags'] else []
        self.tags_var.set(", ".join(tags))
        
        # Set content
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, note['content'] or "")
        
    def save_note(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a note title.")
            return
        
        content = self.text_editor.get(1.0, tk.END).strip()
        
        # Get course ID
        course_id = None
        course_name = self.course_var.get()
        if course_name:
            courses = self.db.get_courses()
            course = next((c for c in courses if c['title'] == course_name), None)
            if course:
                course_id = course['id']
        
        # Parse tags
        tags_text = self.tags_var.get().strip()
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()] if tags_text else []
        
        if self.current_note_id:
            # Update existing note
            # This would require an update method in the database
            messagebox.showinfo("Info", "Note update functionality to be implemented")
        else:
            # Create new note
            note_id = self.db.create_note(
                course_id=course_id,
                title=title,
                content=content,
                note_type=self.note_type_var.get(),
                tags=tags
            )
            self.current_note_id = note_id
            messagebox.showinfo("Success", "Note saved successfully!")
        
        self.refresh_notes_list()
        
    def delete_note(self):
        if not self.current_note_id:
            messagebox.showwarning("Warning", "No note selected to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?"):
            # Delete functionality would need to be added to database
            messagebox.showinfo("Info", "Note deletion functionality to be implemented")
            self.refresh_notes_list()
            
    def format_text(self, format_type: str):
        try:
            # Get selected text
            if self.text_editor.tag_ranges(tk.SEL):
                current_tags = self.text_editor.tag_names(tk.SEL_FIRST)
                
                if format_type in current_tags:
                    # Remove formatting
                    self.text_editor.tag_remove(format_type, tk.SEL_FIRST, tk.SEL_LAST)
                else:
                    # Add formatting
                    self.text_editor.tag_add(format_type, tk.SEL_FIRST, tk.SEL_LAST)
            else:
                messagebox.showinfo("Info", "Please select text to format.")
        except tk.TclError:
            messagebox.showinfo("Info", "Please select text to format.")
            
    def change_font_size(self, event=None):
        try:
            size = int(self.font_size_var.get())
            font_config = ('Helvetica', size)
            self.text_editor.configure(font=font_config)
            
            # Update tag fonts
            self.text_editor.tag_configure("bold", font=font_config + ('bold',))
            self.text_editor.tag_configure("italic", font=font_config + ('italic',))
        except ValueError:
            pass
            
    def on_text_changed(self, event=None):
        # Auto-save functionality could be implemented here
        pass
        
    def export_note(self):
        if not self.current_note_id:
            messagebox.showwarning("Warning", "No note selected to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                content = self.text_editor.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# {self.title_var.get()}\n\n")
                    f.write(content)
                messagebox.showinfo("Success", f"Note exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export note: {str(e)}")
                
    def create_flashcard_from_selection(self):
        try:
            selected_text = self.text_editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                # Open flashcard creation dialog
                dialog = FlashcardDialog(self.parent, selected_text)
                if dialog.result:
                    question, answer = dialog.result
                    
                    # Get course ID
                    course_id = None
                    course_name = self.course_var.get()
                    if course_name:
                        courses = self.db.get_courses()
                        course = next((c for c in courses if c['title'] == course_name), None)
                        if course:
                            course_id = course['id']
                    
                    if course_id:
                        self.db.create_flashcard(course_id, question, answer, self.current_note_id)
                        messagebox.showinfo("Success", "Flashcard created!")
                    else:
                        messagebox.showwarning("Warning", "Please select a course for this note.")
            else:
                messagebox.showinfo("Info", "Please select text to create a flashcard.")
        except tk.TclError:
            messagebox.showinfo("Info", "Please select text to create a flashcard.")
            
    def add_to_mind_map(self):
        selected_text = ""
        try:
            selected_text = self.text_editor.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass
        
        if not selected_text:
            selected_text = self.title_var.get()
        
        messagebox.showinfo("Mind Map", f"Mind map integration coming soon!\nSelected text: {selected_text[:50]}...")
        
    def show_word_count(self):
        content = self.text_editor.get(1.0, tk.END)
        words = len(content.split())
        chars = len(content)
        chars_no_spaces = len(content.replace(" ", "").replace("\n", ""))
        
        messagebox.showinfo(
            "Word Count",
            f"Words: {words}\nCharacters: {chars}\nCharacters (no spaces): {chars_no_spaces}"
        )


class FlashcardDialog:
    def __init__(self, parent, initial_text: str = ""):
        self.result = None
        
        # Create dialog
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("Create Flashcard")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create form
        self.create_form(initial_text)
        
        # Wait for dialog
        parent.wait_window(self.dialog)
        
    def create_form(self, initial_text: str):
        main_frame = ttk_bs.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        ttk_bs.Label(main_frame, text="Create Flashcard", font=('Helvetica', 14, 'bold')).pack(pady=(0, 20))
        
        # Question
        ttk_bs.Label(main_frame, text="Question:").pack(anchor=W)
        self.question_text = tk.Text(main_frame, height=4, width=40)
        self.question_text.pack(fill=X, pady=(5, 10))
        
        # Answer
        ttk_bs.Label(main_frame, text="Answer:").pack(anchor=W)
        self.answer_text = tk.Text(main_frame, height=4, width=40)
        self.answer_text.pack(fill=X, pady=(5, 20))
        self.answer_text.insert(1.0, initial_text)
        
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
            text="Create",
            command=self.create,
            style='Success.TButton'
        ).pack(side=RIGHT)
        
    def create(self):
        question = self.question_text.get(1.0, tk.END).strip()
        answer = self.answer_text.get(1.0, tk.END).strip()
        
        if not question or not answer:
            messagebox.showerror("Error", "Please enter both question and answer.")
            return
        
        self.result = (question, answer)
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()


class NotesWidget:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        self.main_frame = ttk_bs.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Create notes editor
        self.notes_editor = NotesEditor(self.main_frame, self.db)


# Example usage
if __name__ == "__main__":
    from database import DatabaseManager
    
    root = ttk_bs.Window(themename="superhero")
    root.title("Notes Editor Demo")
    root.geometry("1200x800")
    
    db = DatabaseManager("test_notes.db")
    widget = NotesWidget(root, db)
    
    root.mainloop()