import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import json
import os
from datetime import datetime
from typing import Dict, Any


class SettingsWidget:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.settings = self.load_settings()
        self.setup_ui()

    def setup_ui(self):
        # Main frame
        self.main_frame = ttk_bs.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True)

        # Header
        header_frame = ttk_bs.Frame(self.main_frame)
        header_frame.pack(fill=X, padx=20, pady=20)

        ttk_bs.Label(
            header_frame,
            text="⚙️ Settings & Preferences",
            font=("Helvetica", 18, "bold"),
        ).pack(side=LEFT)

        # Save button
        ttk_bs.Button(
            header_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            style="Success.TButton",
        ).pack(side=RIGHT)

        # Create notebook for different setting categories
        self.settings_notebook = ttk_bs.Notebook(self.main_frame)
        self.settings_notebook.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

        # Create setting categories
        self.create_general_settings()
        self.create_appearance_settings()
        self.create_study_settings()
        self.create_data_settings()
        self.create_about_tab()

    def create_general_settings(self):
        general_frame = ttk_bs.Frame(self.settings_notebook)
        self.settings_notebook.add(general_frame, text="🏠 General")

        # Create scrollable frame
        canvas = tk.Canvas(general_frame)
        scrollbar = ttk_bs.Scrollbar(
            general_frame, orient=VERTICAL, command=canvas.yview
        )
        scrollable_frame = ttk_bs.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # User preferences section
        user_section = ttk_bs.LabelFrame(
            scrollable_frame, text="User Preferences", padding=15
        )
        user_section.pack(fill=X, padx=20, pady=20)

        # Username
        user_frame = ttk_bs.Frame(user_section)
        user_frame.pack(fill=X, pady=5)

        ttk_bs.Label(user_frame, text="Display Name:", width=20).pack(side=LEFT)
        self.username_var = tk.StringVar(
            value=self.settings.get("username", "Learning Enthusiast")
        )
        ttk_bs.Entry(user_frame, textvariable=self.username_var, width=30).pack(
            side=LEFT, padx=(10, 0)
        )

        # Default course category
        category_frame = ttk_bs.Frame(user_section)
        category_frame.pack(fill=X, pady=5)

        ttk_bs.Label(category_frame, text="Default Category:", width=20).pack(side=LEFT)
        self.default_category_var = tk.StringVar(
            value=self.settings.get("default_category", "General")
        )
        category_combo = ttk_bs.Combobox(
            category_frame,
            textvariable=self.default_category_var,
            values=["Programming", "Language", "Business", "Science", "Art", "General"],
            width=27,
        )
        category_combo.pack(side=LEFT, padx=(10, 0))

        # Auto-save interval
        autosave_frame = ttk_bs.Frame(user_section)
        autosave_frame.pack(fill=X, pady=5)

        ttk_bs.Label(autosave_frame, text="Auto-save (minutes):", width=20).pack(
            side=LEFT
        )
        self.autosave_var = tk.IntVar(value=self.settings.get("autosave_interval", 5))
        autosave_spin = ttk_bs.Spinbox(
            autosave_frame, from_=1, to=60, textvariable=self.autosave_var, width=28
        )
        autosave_spin.pack(side=LEFT, padx=(10, 0))

        # Language preference
        language_frame = ttk_bs.Frame(user_section)
        language_frame.pack(fill=X, pady=5)

        ttk_bs.Label(language_frame, text="Language:", width=20).pack(side=LEFT)
        self.language_var = tk.StringVar(value=self.settings.get("language", "English"))
        language_combo = ttk_bs.Combobox(
            language_frame,
            textvariable=self.language_var,
            values=["English", "Spanish", "French", "German", "Chinese", "Japanese"],
            width=27,
            state="readonly",
        )
        language_combo.pack(side=LEFT, padx=(10, 0))

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def create_appearance_settings(self):
        appearance_frame = ttk_bs.Frame(self.settings_notebook)
        self.settings_notebook.add(appearance_frame, text="🎨 Appearance")

        # Theme section
        theme_section = ttk_bs.LabelFrame(
            appearance_frame, text="Theme & Colors", padding=15
        )
        theme_section.pack(fill=X, padx=20, pady=20)

        # Theme selection
        theme_frame = ttk_bs.Frame(theme_section)
        theme_frame.pack(fill=X, pady=5)

        ttk_bs.Label(theme_frame, text="Theme:", width=20).pack(side=LEFT)
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "superhero"))
        theme_combo = ttk_bs.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=[
                "superhero",
                "darkly",
                "cyborg",
                "vapor",
                "cosmo",
                "flatly",
                "litera",
                "minty",
            ],
            width=27,
            state="readonly",
        )
        theme_combo.pack(side=LEFT, padx=(10, 0))
        theme_combo.bind("<<ComboboxSelected>>", self.preview_theme)

        # Font size
        font_frame = ttk_bs.Frame(theme_section)
        font_frame.pack(fill=X, pady=5)

        ttk_bs.Label(font_frame, text="Font Size:", width=20).pack(side=LEFT)
        self.font_size_var = tk.IntVar(value=self.settings.get("font_size", 12))
        font_scale = ttk_bs.Scale(
            font_frame,
            from_=8,
            to=20,
            variable=self.font_size_var,
            orient=HORIZONTAL,
            length=200,
        )
        font_scale.pack(side=LEFT, padx=(10, 0))

        # Window settings section
        window_section = ttk_bs.LabelFrame(
            appearance_frame, text="Window Settings", padding=15
        )
        window_section.pack(fill=X, padx=20, pady=(0, 20))

        # Start maximized
        self.start_maximized_var = tk.BooleanVar(
            value=self.settings.get("start_maximized", False)
        )
        ttk_bs.Checkbutton(
            window_section,
            text="Start application maximized",
            variable=self.start_maximized_var,
        ).pack(anchor=W, pady=2)

        # Remember window position
        self.remember_position_var = tk.BooleanVar(
            value=self.settings.get("remember_position", True)
        )
        ttk_bs.Checkbutton(
            window_section,
            text="Remember window position",
            variable=self.remember_position_var,
        ).pack(anchor=W, pady=2)

        # Show sidebar by default
        self.show_sidebar_var = tk.BooleanVar(
            value=self.settings.get("show_sidebar", True)
        )
        ttk_bs.Checkbutton(
            window_section,
            text="Show sidebar by default",
            variable=self.show_sidebar_var,
        ).pack(anchor=W, pady=2)

    def create_study_settings(self):
        study_frame = ttk_bs.Frame(self.settings_notebook)
        self.settings_notebook.add(study_frame, text="📚 Study")

        # Study preferences section
        study_section = ttk_bs.LabelFrame(
            study_frame, text="Study Preferences", padding=15
        )
        study_section.pack(fill=X, padx=20, pady=20)

        # Default study duration
        duration_frame = ttk_bs.Frame(study_section)
        duration_frame.pack(fill=X, pady=5)

        ttk_bs.Label(duration_frame, text="Default Session (min):", width=20).pack(
            side=LEFT
        )
        self.study_duration_var = tk.IntVar(
            value=self.settings.get("default_study_duration", 25)
        )
        duration_spin = ttk_bs.Spinbox(
            duration_frame,
            from_=5,
            to=120,
            textvariable=self.study_duration_var,
            width=28,
        )
        duration_spin.pack(side=LEFT, padx=(10, 0))

        # Break duration
        break_frame = ttk_bs.Frame(study_section)
        break_frame.pack(fill=X, pady=5)

        ttk_bs.Label(break_frame, text="Break Duration (min):", width=20).pack(
            side=LEFT
        )
        self.break_duration_var = tk.IntVar(
            value=self.settings.get("break_duration", 5)
        )
        break_spin = ttk_bs.Spinbox(
            break_frame, from_=1, to=30, textvariable=self.break_duration_var, width=28
        )
        break_spin.pack(side=LEFT, padx=(10, 0))

        # Notification settings section
        notification_section = ttk_bs.LabelFrame(
            study_frame, text="Notifications", padding=15
        )
        notification_section.pack(fill=X, padx=20, pady=(0, 20))

        # Enable notifications
        self.enable_notifications_var = tk.BooleanVar(
            value=self.settings.get("enable_notifications", True)
        )
        ttk_bs.Checkbutton(
            notification_section,
            text="Enable study session notifications",
            variable=self.enable_notifications_var,
        ).pack(anchor=W, pady=2)

        # Sound notifications
        self.sound_notifications_var = tk.BooleanVar(
            value=self.settings.get("sound_notifications", False)
        )
        ttk_bs.Checkbutton(
            notification_section,
            text="Play sound with notifications",
            variable=self.sound_notifications_var,
        ).pack(anchor=W, pady=2)

        # Daily goal reminders
        self.daily_reminders_var = tk.BooleanVar(
            value=self.settings.get("daily_reminders", True)
        )
        ttk_bs.Checkbutton(
            notification_section,
            text="Daily study goal reminders",
            variable=self.daily_reminders_var,
        ).pack(anchor=W, pady=2)

        # Learning analytics section
        analytics_section = ttk_bs.LabelFrame(
            study_frame, text="Analytics & Tracking", padding=15
        )
        analytics_section.pack(fill=X, padx=20, pady=(0, 20))

        # Track mood and energy
        self.track_mood_var = tk.BooleanVar(value=self.settings.get("track_mood", True))
        ttk_bs.Checkbutton(
            analytics_section,
            text="Track mood and energy levels",
            variable=self.track_mood_var,
        ).pack(anchor=W, pady=2)

        # Auto-complete modules
        self.auto_complete_var = tk.BooleanVar(
            value=self.settings.get("auto_complete_modules", False)
        )
        ttk_bs.Checkbutton(
            analytics_section,
            text="Auto-complete modules when all sessions done",
            variable=self.auto_complete_var,
        ).pack(anchor=W, pady=2)

    def create_data_settings(self):
        data_frame = ttk_bs.Frame(self.settings_notebook)
        self.settings_notebook.add(data_frame, text="🗄️ Data")

        # Backup section
        backup_section = ttk_bs.LabelFrame(
            data_frame, text="Backup & Export", padding=15
        )
        backup_section.pack(fill=X, padx=20, pady=20)

        # Auto-backup
        self.auto_backup_var = tk.BooleanVar(
            value=self.settings.get("auto_backup", True)
        )
        ttk_bs.Checkbutton(
            backup_section,
            text="Enable automatic daily backups",
            variable=self.auto_backup_var,
        ).pack(anchor=W, pady=5)

        # Backup location
        backup_location_frame = ttk_bs.Frame(backup_section)
        backup_location_frame.pack(fill=X, pady=5)

        ttk_bs.Label(backup_location_frame, text="Backup Folder:").pack(anchor=W)

        location_frame = ttk_bs.Frame(backup_location_frame)
        location_frame.pack(fill=X, pady=(5, 0))

        self.backup_location_var = tk.StringVar(
            value=self.settings.get(
                "backup_location", "~/Documents/LearningTracker_Backups"
            )
        )
        location_entry = ttk_bs.Entry(
            location_frame, textvariable=self.backup_location_var
        )
        location_entry.pack(side=LEFT, fill=X, expand=True)

        ttk_bs.Button(
            location_frame,
            text="Browse",
            command=self.browse_backup_location,
            style="Secondary.Outline.TButton",
        ).pack(side=RIGHT, padx=(10, 0))

        # Action buttons
        action_frame = ttk_bs.Frame(backup_section)
        action_frame.pack(fill=X, pady=(15, 0))

        ttk_bs.Button(
            action_frame,
            text="💾 Create Backup Now",
            command=self.create_backup,
            style="Info.TButton",
        ).pack(side=LEFT, padx=(0, 10))

        ttk_bs.Button(
            action_frame,
            text="📤 Export Data",
            command=self.export_data,
            style="Warning.TButton",
        ).pack(side=LEFT, padx=(0, 10))

        ttk_bs.Button(
            action_frame,
            text="📥 Import Data",
            command=self.import_data,
            style="Success.TButton",
        ).pack(side=LEFT)

        # Database section
        database_section = ttk_bs.LabelFrame(
            data_frame, text="Database Management", padding=15
        )
        database_section.pack(fill=X, padx=20, pady=(0, 20))

        # Database info
        info_frame = ttk_bs.Frame(database_section)
        info_frame.pack(fill=X, pady=(0, 10))

        db_path = getattr(self.db, "db_path", "learning_tracker.db")
        db_size = self.get_database_size(db_path)

        ttk_bs.Label(info_frame, text=f"Database: {os.path.basename(db_path)}").pack(
            anchor=W
        )
        ttk_bs.Label(info_frame, text=f"Size: {db_size}").pack(anchor=W)
        ttk_bs.Label(
            info_frame, text=f"Location: {os.path.dirname(os.path.abspath(db_path))}"
        ).pack(anchor=W)

        # Database actions
        db_action_frame = ttk_bs.Frame(database_section)
        db_action_frame.pack(fill=X, pady=(10, 0))

        ttk_bs.Button(
            db_action_frame,
            text="🧹 Optimize Database",
            command=self.optimize_database,
            style="Info.Outline.TButton",
        ).pack(side=LEFT, padx=(0, 10))

        ttk_bs.Button(
            db_action_frame,
            text="⚠️ Reset All Data",
            command=self.reset_database,
            style="Danger.TButton",
        ).pack(side=LEFT)

    def create_about_tab(self):
        about_frame = ttk_bs.Frame(self.settings_notebook)
        self.settings_notebook.add(about_frame, text="ℹ️ About")

        # About section
        about_section = ttk_bs.LabelFrame(
            about_frame, text="Application Information", padding=20
        )
        about_section.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # App info
        app_info = [
            ("Visual Learning Tracker", "Title", 16, "bold"),
            ("Version 1.0.0", "Version", 12, "normal"),
            ("", "", 8, "normal"),
            (
                "A comprehensive learning management application",
                "Description",
                11,
                "normal",
            ),
            ("designed specifically for visual learners.", "", 11, "normal"),
            ("", "", 8, "normal"),
            ("Created with Python, tkinter, and ttkbootstrap", "Tech", 10, "italic"),
            ("", "", 8, "normal"),
            (f"Last updated: {datetime.now().strftime('%B %Y')}", "Date", 9, "normal"),
        ]

        for text, _, size, weight in app_info:
            if text:
                label = ttk_bs.Label(
                    about_section,
                    text=text,
                    font=("Helvetica", size, weight),
                    justify=CENTER,
                )
                label.pack(pady=2)
            else:
                ttk_bs.Label(about_section, text="").pack()

        # Features list
        features_frame = ttk_bs.LabelFrame(about_frame, text="Key Features", padding=15)
        features_frame.pack(fill=X, padx=20, pady=(0, 20))

        features = [
            "📚 Course Management with Progress Tracking",
            "📝 Rich Text Note-Taking with Tags",
            "🧠 Interactive Mind Mapping",
            "🔗 Knowledge Graph Visualization",
            "🃏 Spaced Repetition Flashcards",
            "📊 Learning Analytics Dashboard",
            "⏱️ Study Session Timer",
            "💾 Data Export and Backup",
        ]

        for feature in features:
            ttk_bs.Label(features_frame, text=feature, font=("Helvetica", 10)).pack(
                anchor=W, pady=1
            )

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults"""
        settings_file = "settings.json"
        default_settings = {
            "username": "Learning Enthusiast",
            "default_category": "General",
            "autosave_interval": 5,
            "language": "English",
            "theme": "superhero",
            "font_size": 12,
            "start_maximized": False,
            "remember_position": True,
            "show_sidebar": True,
            "default_study_duration": 25,
            "break_duration": 5,
            "enable_notifications": True,
            "sound_notifications": False,
            "daily_reminders": True,
            "track_mood": True,
            "auto_complete_modules": False,
            "auto_backup": True,
            "backup_location": "~/Documents/LearningTracker_Backups",
        }

        try:
            if os.path.exists(settings_file):
                with open(settings_file, "r") as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                default_settings.update(loaded_settings)
            return default_settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings

    def save_settings(self):
        """Save current settings to file"""
        settings = {
            "username": self.username_var.get(),
            "default_category": self.default_category_var.get(),
            "autosave_interval": self.autosave_var.get(),
            "language": self.language_var.get(),
            "theme": self.theme_var.get(),
            "font_size": self.font_size_var.get(),
            "start_maximized": self.start_maximized_var.get(),
            "remember_position": self.remember_position_var.get(),
            "show_sidebar": self.show_sidebar_var.get(),
            "default_study_duration": self.study_duration_var.get(),
            "break_duration": self.break_duration_var.get(),
            "enable_notifications": self.enable_notifications_var.get(),
            "sound_notifications": self.sound_notifications_var.get(),
            "daily_reminders": self.daily_reminders_var.get(),
            "track_mood": self.track_mood_var.get(),
            "auto_complete_modules": self.auto_complete_var.get(),
            "auto_backup": self.auto_backup_var.get(),
            "backup_location": self.backup_location_var.get(),
        }

        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def preview_theme(self, event=None):
        """Preview theme change (would need app restart for full effect)"""
        messagebox.showinfo(
            "Theme Change", "Theme will be applied when you restart the application."
        )

    def browse_backup_location(self):
        """Browse for backup folder location"""
        folder = filedialog.askdirectory(title="Select Backup Location")
        if folder:
            self.backup_location_var.set(folder)

    def create_backup(self):
        """Create a backup of the database"""
        messagebox.showinfo(
            "Backup",
            "Backup functionality would copy the database to the specified location.",
        )

    def export_data(self):
        """Export data to various formats"""
        messagebox.showinfo(
            "Export",
            "Data export functionality would allow exporting to JSON, CSV, etc.",
        )

    def import_data(self):
        """Import data from file"""
        messagebox.showinfo(
            "Import",
            "Data import functionality would allow importing from backup files.",
        )

    def get_database_size(self, db_path: str) -> str:
        """Get human-readable database size"""
        try:
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                if size_bytes < 1024:
                    return f"{size_bytes} bytes"
                elif size_bytes < 1024**2:
                    return f"{size_bytes/1024:.1f} KB"
                elif size_bytes < 1024**3:
                    return f"{size_bytes/(1024**2):.1f} MB"
                else:
                    return f"{size_bytes/(1024**3):.1f} GB"
            return "Unknown"
        except Exception:
            return "Unknown"

    def optimize_database(self):
        """Optimize database performance"""
        messagebox.showinfo(
            "Optimize", "Database optimization would run VACUUM and ANALYZE commands."
        )

    def reset_database(self):
        """Reset all data (with confirmation)"""
        if messagebox.askyesno(
            "Reset Database",
            "⚠️ This will permanently delete ALL your learning data!\n\nThis action cannot be undone. Are you sure you want to continue?",
            icon="warning",
        ):
            if messagebox.askyesno(
                "Final Confirmation",
                "Last chance! This will delete:\n• All courses and modules\n• All notes and mind maps\n• All flashcards and progress\n• All study sessions\n\nProceed with reset?",
                icon="warning",
            ):
                messagebox.showinfo(
                    "Reset",
                    "Database reset functionality would reinitialize the database.",
                )


# Example usage
if __name__ == "__main__":
    from database import DatabaseManager

    root = ttk_bs.Window(themename="superhero")
    root.title("Settings Demo")
    root.geometry("900x700")

    db = DatabaseManager("test_settings.db")
    widget = SettingsWidget(root, db)

    root.mainloop()
