import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
from datetime import datetime, timedelta
import random
from typing import List, Dict, Optional


class FlashcardWidget:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.current_cards = []
        self.current_card_index = 0
        self.show_answer = False
        self.setup_ui()

    def setup_ui(self):
        # Main frame
        self.main_frame = ttk_bs.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True)

        # Header
        header_frame = ttk_bs.Frame(self.main_frame)
        header_frame.pack(fill=X, padx=20, pady=20)

        ttk_bs.Label(
            header_frame, text="🃏 Flashcard Review", font=("Helvetica", 18, "bold")
        ).pack(side=LEFT)

        # Control buttons
        control_frame = ttk_bs.Frame(header_frame)
        control_frame.pack(side=RIGHT)

        ttk_bs.Button(
            control_frame,
            text="📚 Load Cards",
            command=self.load_cards_dialog,
            style="Info.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            control_frame,
            text="➕ Add Card",
            command=self.add_card_dialog,
            style="Success.TButton",
        ).pack(side=LEFT, padx=2)

        # Study area
        self.create_study_area()

        # Controls
        self.create_controls()

        # Statistics
        self.create_statistics()

        # Load initial cards
        self.load_review_cards()

    def create_study_area(self):
        # Study area frame
        study_frame = ttk_bs.LabelFrame(self.main_frame, text="Study Area", padding=20)
        study_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

        # Card counter
        self.counter_label = ttk_bs.Label(
            study_frame, text="No cards loaded", font=("Helvetica", 12)
        )
        self.counter_label.pack(pady=(0, 20))

        # Card display area
        self.card_frame = ttk_bs.Frame(study_frame)
        self.card_frame.pack(fill=BOTH, expand=True, pady=20)

        # Card content
        self.card_content = tk.Text(
            self.card_frame,
            height=8,
            font=("Helvetica", 14),
            wrap=tk.WORD,
            state="disabled",
            bg="white",
            relief="raised",
            borderwidth=2,
        )
        self.card_content.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # Show/Hide answer button
        self.toggle_answer_btn = ttk_bs.Button(
            study_frame,
            text="Show Answer",
            command=self.toggle_answer,
            style="Warning.TButton",
            state="disabled",
        )
        self.toggle_answer_btn.pack(pady=10)

    def create_controls(self):
        # Controls frame
        controls_frame = ttk_bs.LabelFrame(
            self.main_frame, text="Review Controls", padding=15
        )
        controls_frame.pack(fill=X, padx=20, pady=(0, 20))

        # Navigation buttons
        nav_frame = ttk_bs.Frame(controls_frame)
        nav_frame.pack(fill=X, pady=(0, 10))

        self.prev_btn = ttk_bs.Button(
            nav_frame,
            text="⬅️ Previous",
            command=self.previous_card,
            style="Secondary.TButton",
            state="disabled",
        )
        self.prev_btn.pack(side=LEFT)

        self.next_btn = ttk_bs.Button(
            nav_frame,
            text="Next ➡️",
            command=self.next_card,
            style="Secondary.TButton",
            state="disabled",
        )
        self.next_btn.pack(side=RIGHT)

        # Difficulty rating
        difficulty_frame = ttk_bs.Frame(controls_frame)
        difficulty_frame.pack(fill=X)

        ttk_bs.Label(difficulty_frame, text="Rate this card:").pack(side=LEFT)

        # Rating buttons
        rating_frame = ttk_bs.Frame(difficulty_frame)
        rating_frame.pack(side=RIGHT)

        rating_buttons = [
            ("😰 Hard", "hard", "Danger.TButton"),
            ("🤔 Medium", "medium", "Warning.TButton"),
            ("😊 Easy", "easy", "Success.TButton"),
        ]

        for text, rating, style in rating_buttons:
            btn = ttk_bs.Button(
                rating_frame,
                text=text,
                command=lambda r=rating: self.rate_card(r),
                style=style,
                state="disabled",
            )
            btn.pack(side=LEFT, padx=5)

        # Store rating buttons for enable/disable
        self.rating_buttons = rating_frame.winfo_children()

    def create_statistics(self):
        # Statistics frame
        stats_frame = ttk_bs.LabelFrame(
            self.main_frame, text="Session Statistics", padding=15
        )
        stats_frame.pack(fill=X, padx=20, pady=(0, 20))

        # Statistics labels
        stats_container = ttk_bs.Frame(stats_frame)
        stats_container.pack(fill=X)

        self.stats_labels = {}
        stats_items = [
            ("Cards Reviewed", "reviewed"),
            ("Correct Answers", "correct"),
            ("Accuracy", "accuracy"),
            ("Session Time", "time"),
        ]

        for i, (label_text, key) in enumerate(stats_items):
            stat_frame = ttk_bs.Frame(stats_container)
            stat_frame.pack(side=LEFT, fill=X, expand=True)

            ttk_bs.Label(stat_frame, text=label_text, font=("Helvetica", 10)).pack()

            value_label = ttk_bs.Label(
                stat_frame, text="0", font=("Helvetica", 16, "bold")
            )
            value_label.pack()
            self.stats_labels[key] = value_label

        # Session tracking
        self.session_start = datetime.now()
        self.cards_reviewed = 0
        self.correct_answers = 0

    def load_cards_dialog(self):
        # Get available courses
        courses = self.db.get_courses()
        if not courses:
            messagebox.showinfo("No Courses", "Create some courses first!")
            return

        # Simple course selection dialog
        dialog = CourseSelectionDialog(self.parent, courses)
        if dialog.result:
            course_id = dialog.result
            self.load_course_cards(course_id)

    def load_course_cards(self, course_id):
        """Load flashcards for a specific course"""
        cards = self.db.get_flashcards_for_review(course_id)
        if not cards:
            messagebox.showinfo("No Cards", "No flashcards found for this course.")
            return

        self.current_cards = cards
        self.current_card_index = 0
        self.show_answer = False

        # Shuffle cards for better learning
        random.shuffle(self.current_cards)

        # Enable controls
        self.enable_controls()

        # Show first card
        self.display_current_card()

    def load_review_cards(self):
        """Load cards that are due for review"""
        cards = self.db.get_flashcards_for_review(limit=20)
        if cards:
            self.current_cards = cards
            self.current_card_index = 0
            self.show_answer = False
            random.shuffle(self.current_cards)
            self.enable_controls()
            self.display_current_card()
        else:
            self.display_no_cards_message()

    def display_current_card(self):
        if not self.current_cards:
            self.display_no_cards_message()
            return

        card = self.current_cards[self.current_card_index]

        # Update counter
        self.counter_label.config(
            text=f"Card {self.current_card_index + 1} of {len(self.current_cards)}"
        )

        # Display question
        self.card_content.config(state="normal")
        self.card_content.delete(1.0, tk.END)

        if self.show_answer:
            # Show both question and answer
            self.card_content.insert(tk.END, "Question:\n", "question_header")
            self.card_content.insert(tk.END, card["question"] + "\n\n", "question")
            self.card_content.insert(tk.END, "Answer:\n", "answer_header")
            self.card_content.insert(tk.END, card["answer"], "answer")
            self.toggle_answer_btn.config(text="Hide Answer")
        else:
            # Show only question
            self.card_content.insert(tk.END, card["question"], "question")
            self.toggle_answer_btn.config(text="Show Answer")

        self.card_content.config(state="disabled")

        # Configure text tags
        self.card_content.tag_configure(
            "question_header", font=("Helvetica", 12, "bold"), foreground="blue"
        )
        self.card_content.tag_configure(
            "answer_header", font=("Helvetica", 12, "bold"), foreground="green"
        )
        self.card_content.tag_configure("question", font=("Helvetica", 14))
        self.card_content.tag_configure(
            "answer", font=("Helvetica", 14), foreground="dark green"
        )

        # Update navigation buttons
        self.prev_btn.config(
            state="normal" if self.current_card_index > 0 else "disabled"
        )
        self.next_btn.config(
            state="normal"
            if self.current_card_index < len(self.current_cards) - 1
            else "disabled"
        )

    def display_no_cards_message(self):
        self.counter_label.config(text="No cards loaded")
        self.card_content.config(state="normal")
        self.card_content.delete(1.0, tk.END)
        self.card_content.insert(
            tk.END,
            "No flashcards available.\n\nClick 'Load Cards' to select a course or 'Add Card' to create new flashcards.",
        )
        self.card_content.config(state="disabled")
        self.disable_controls()

    def toggle_answer(self):
        self.show_answer = not self.show_answer
        self.display_current_card()

        # Enable rating buttons when answer is shown
        if self.show_answer:
            for btn in self.rating_buttons:
                btn.config(state="normal")
        else:
            for btn in self.rating_buttons:
                btn.config(state="disabled")

    def previous_card(self):
        if self.current_card_index > 0:
            self.current_card_index -= 1
            self.show_answer = False
            self.display_current_card()
            for btn in self.rating_buttons:
                btn.config(state="disabled")

    def next_card(self):
        if self.current_card_index < len(self.current_cards) - 1:
            self.current_card_index += 1
            self.show_answer = False
            self.display_current_card()
            for btn in self.rating_buttons:
                btn.config(state="disabled")

    def rate_card(self, rating):
        if not self.current_cards or not self.show_answer:
            return

        # Track statistics
        self.cards_reviewed += 1
        if rating == "easy":
            self.correct_answers += 1

        # Update display
        self.update_statistics()

        # Move to next card automatically
        if self.current_card_index < len(self.current_cards) - 1:
            self.next_card()
        else:
            messagebox.showinfo(
                "Session Complete",
                f"Great job! You've reviewed all {len(self.current_cards)} cards.",
            )

    def update_statistics(self):
        # Calculate session time
        session_time = datetime.now() - self.session_start
        minutes = int(session_time.total_seconds() / 60)

        # Calculate accuracy
        accuracy = (
            (self.correct_answers / self.cards_reviewed * 100)
            if self.cards_reviewed > 0
            else 0
        )

        # Update labels
        self.stats_labels["reviewed"].config(text=str(self.cards_reviewed))
        self.stats_labels["correct"].config(text=str(self.correct_answers))
        self.stats_labels["accuracy"].config(text=f"{accuracy:.1f}%")
        self.stats_labels["time"].config(text=f"{minutes}m")

    def enable_controls(self):
        self.toggle_answer_btn.config(state="normal")
        self.prev_btn.config(state="normal")
        self.next_btn.config(state="normal")

    def disable_controls(self):
        self.toggle_answer_btn.config(state="disabled")
        self.prev_btn.config(state="disabled")
        self.next_btn.config(state="disabled")
        for btn in self.rating_buttons:
            btn.config(state="disabled")

    def add_card_dialog(self):
        # Get available courses
        courses = self.db.get_courses()
        if not courses:
            messagebox.showinfo("No Courses", "Create some courses first!")
            return

        dialog = AddCardDialog(self.parent, self.db, courses)
        if dialog.result:
            messagebox.showinfo("Success", "Flashcard added successfully!")
            # Reload cards if we're studying the same course
            if self.current_cards:
                self.load_review_cards()


class CourseSelectionDialog:
    def __init__(self, parent, courses):
        self.result = None

        # Create dialog
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("Select Course")
        self.dialog.geometry("300x400")
        self.dialog.resizable(False, False)

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Create content
        main_frame = ttk_bs.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        ttk_bs.Label(
            main_frame, text="Select a course to study:", font=("Helvetica", 12, "bold")
        ).pack(pady=(0, 15))

        # Course list
        self.course_listbox = tk.Listbox(main_frame, height=15)
        self.course_listbox.pack(fill=BOTH, expand=True, pady=(0, 15))

        for course in courses:
            self.course_listbox.insert(tk.END, course["title"])

        # Buttons
        btn_frame = ttk_bs.Frame(main_frame)
        btn_frame.pack(fill=X)

        ttk_bs.Button(
            btn_frame, text="Cancel", command=self.cancel, style="Secondary.TButton"
        ).pack(side=RIGHT, padx=(10, 0))

        ttk_bs.Button(
            btn_frame,
            text="Select",
            command=lambda: self.select(courses),
            style="Success.TButton",
        ).pack(side=RIGHT)

        # Bind double-click
        self.course_listbox.bind("<Double-1>", lambda e: self.select(courses))

        # Wait for dialog
        parent.wait_window(self.dialog)

    def select(self, courses):
        selection = self.course_listbox.curselection()
        if selection:
            self.result = courses[selection[0]]["id"]
            self.dialog.destroy()
        else:
            messagebox.showwarning("No Selection", "Please select a course.")

    def cancel(self):
        self.dialog.destroy()


class AddCardDialog:
    def __init__(self, parent, db, courses):
        self.db = db
        self.result = None

        # Create dialog
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("Add Flashcard")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_form(courses)

        # Wait for dialog
        parent.wait_window(self.dialog)

    def create_form(self, courses):
        main_frame = ttk_bs.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        ttk_bs.Label(
            main_frame, text="Create New Flashcard", font=("Helvetica", 14, "bold")
        ).pack(pady=(0, 20))

        # Course selection
        ttk_bs.Label(main_frame, text="Course:").pack(anchor=W)
        self.course_var = tk.StringVar()
        course_combo = ttk_bs.Combobox(
            main_frame, textvariable=self.course_var, state="readonly"
        )
        course_combo["values"] = [course["title"] for course in courses]
        course_combo.pack(fill=X, pady=(5, 15))

        # Question
        ttk_bs.Label(main_frame, text="Question:").pack(anchor=W)
        self.question_text = tk.Text(main_frame, height=4, width=50)
        self.question_text.pack(fill=X, pady=(5, 15))

        # Answer
        ttk_bs.Label(main_frame, text="Answer:").pack(anchor=W)
        self.answer_text = tk.Text(main_frame, height=4, width=50)
        self.answer_text.pack(fill=X, pady=(5, 20))

        # Buttons
        btn_frame = ttk_bs.Frame(main_frame)
        btn_frame.pack(fill=X)

        ttk_bs.Button(
            btn_frame, text="Cancel", command=self.cancel, style="Secondary.TButton"
        ).pack(side=RIGHT, padx=(10, 0))

        ttk_bs.Button(
            btn_frame,
            text="Create",
            command=lambda: self.create(courses),
            style="Success.TButton",
        ).pack(side=RIGHT)

    def create(self, courses):
        course_title = self.course_var.get()
        if not course_title:
            messagebox.showerror("Error", "Please select a course.")
            return

        question = self.question_text.get(1.0, tk.END).strip()
        answer = self.answer_text.get(1.0, tk.END).strip()

        if not question or not answer:
            messagebox.showerror("Error", "Please enter both question and answer.")
            return

        # Find course ID
        course = next((c for c in courses if c["title"] == course_title), None)
        if not course:
            messagebox.showerror("Error", "Course not found.")
            return

        # Create flashcard
        card_id = self.db.create_flashcard(course["id"], question, answer)
        self.result = card_id
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()


# Example usage
if __name__ == "__main__":
    from database import DatabaseManager

    root = ttk_bs.Window(themename="superhero")
    root.title("Flashcard Demo")
    root.geometry("800x700")

    db = DatabaseManager("test_flashcards.db")
    widget = FlashcardWidget(root, db)

    root.mainloop()
