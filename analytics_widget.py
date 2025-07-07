import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta, date
import json
from typing import List, Dict, Optional


class AnalyticsWidget:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
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
            text="📊 Learning Analytics",
            font=('Helvetica', 18, 'bold')
        ).pack(side=LEFT)
        
        # Time period selector
        period_frame = ttk_bs.Frame(header_frame)
        period_frame.pack(side=RIGHT)
        
        ttk_bs.Label(period_frame, text="Period:").pack(side=LEFT, padx=(0, 5))
        
        self.period_var = tk.StringVar(value="30")
        period_combo = ttk_bs.Combobox(
            period_frame,
            textvariable=self.period_var,
            values=["7", "30", "90", "365"],
            width=10,
            state="readonly"
        )
        period_combo.pack(side=LEFT)
        period_combo.bind("<<ComboboxSelected>>", self.refresh_analytics)
        
        # Create main content area
        self.create_content_area()
        
        # Load initial data
        self.refresh_analytics()
        
    def create_content_area(self):
        # Create notebook for different analytics views
        self.analytics_notebook = ttk_bs.Notebook(self.main_frame)
        self.analytics_notebook.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Overview tab
        self.create_overview_tab()
        
        # Progress tab
        self.create_progress_tab()
        
        # Time analysis tab
        self.create_time_analysis_tab()
        
    def create_overview_tab(self):
        overview_frame = ttk_bs.Frame(self.analytics_notebook)
        self.analytics_notebook.add(overview_frame, text="📈 Overview")
        
        # Statistics cards
        self.create_stats_cards(overview_frame)
        
        # Quick insights
        self.create_insights_section(overview_frame)
        
    def create_stats_cards(self, parent):
        cards_frame = ttk_bs.Frame(parent)
        cards_frame.pack(fill=X, padx=20, pady=20)
        
        # Get statistics
        stats = self.db.get_learning_statistics(int(self.period_var.get()))
        
        # Create cards
        cards_data = [
            ("📚 Active Courses", str(stats['active_courses']), "primary", "courses"),
            ("⏱️ Study Hours", f"{stats['total_study_hours']:.1f}h", "success", "hours"),
            ("🎯 Study Sessions", str(stats['study_sessions']), "info", "sessions"),
            ("✅ Modules Done", str(stats['completed_modules']), "warning", "modules"),
            ("📝 Notes Created", "0", "secondary", "notes"),  # Would need to implement
            ("🃏 Cards Reviewed", "0", "dark", "flashcards")  # Would need to implement
        ]
        
        # Create two rows of cards
        for row in range(2):
            row_frame = ttk_bs.Frame(cards_frame)
            row_frame.pack(fill=X, pady=5)
            
            for col in range(3):
                card_index = row * 3 + col
                if card_index < len(cards_data):
                    title, value, style, key = cards_data[card_index]
                    self.create_stat_card(row_frame, title, value, style)
                    
    def create_stat_card(self, parent, title, value, style):
        card = ttk_bs.Frame(parent, style='Card.TFrame', padding=15)
        card.pack(side=LEFT, fill=BOTH, expand=True, padx=5)
        
        # Icon and title
        ttk_bs.Label(
            card,
            text=title,
            font=('Helvetica', 10),
            foreground="gray"
        ).pack()
        
        # Value
        ttk_bs.Label(
            card,
            text=value,
            font=('Helvetica', 20, 'bold')
        ).pack(pady=(5, 0))
        
    def create_insights_section(self, parent):
        insights_frame = ttk_bs.LabelFrame(parent, text="📋 Quick Insights", padding=15)
        insights_frame.pack(fill=X, padx=20, pady=(0, 20))
        
        # Generate insights based on data
        insights = self.generate_insights()
        
        if insights:
            for insight in insights:
                insight_item = ttk_bs.Frame(insights_frame)
                insight_item.pack(fill=X, pady=2)
                
                ttk_bs.Label(
                    insight_item,
                    text="•",
                    font=('Helvetica', 12, 'bold'),
                    foreground="blue"
                ).pack(side=LEFT, padx=(0, 10))
                
                ttk_bs.Label(
                    insight_item,
                    text=insight,
                    font=('Helvetica', 10),
                    wraplength=600
                ).pack(side=LEFT, fill=X, expand=True)
        else:
            ttk_bs.Label(
                insights_frame,
                text="Start learning to see personalized insights!",
                foreground="gray"
            ).pack()
            
    def create_progress_tab(self):
        progress_frame = ttk_bs.Frame(self.analytics_notebook)
        self.analytics_notebook.add(progress_frame, text="📈 Progress")
        
        # Course progress section
        progress_section = ttk_bs.LabelFrame(progress_frame, text="Course Progress", padding=15)
        progress_section.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Get courses for progress display
        courses = self.db.get_courses(status='active')
        
        if courses:
            # Create scrollable frame
            canvas = tk.Canvas(progress_section)
            scrollbar = ttk_bs.Scrollbar(progress_section, orient=VERTICAL, command=canvas.yview)
            scrollable_frame = ttk_bs.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Create progress bars for each course
            for course in courses:
                self.create_course_progress_item(scrollable_frame, course)
            
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar.pack(side=RIGHT, fill=Y)
        else:
            ttk_bs.Label(
                progress_section,
                text="No active courses found. Create some courses to track progress!",
                foreground="gray"
            ).pack(expand=True)
            
    def create_course_progress_item(self, parent, course):
        item_frame = ttk_bs.Frame(parent, padding=10)
        item_frame.pack(fill=X, pady=5)
        
        # Course title and category
        header_frame = ttk_bs.Frame(item_frame)
        header_frame.pack(fill=X)
        
        ttk_bs.Label(
            header_frame,
            text=course['title'],
            font=('Helvetica', 12, 'bold')
        ).pack(side=LEFT)
        
        if course['category']:
            ttk_bs.Label(
                header_frame,
                text=f"📂 {course['category']}",
                foreground="gray"
            ).pack(side=RIGHT)
        
        # Progress bar
        progress_frame = ttk_bs.Frame(item_frame)
        progress_frame.pack(fill=X, pady=(5, 0))
        
        progress_bar = ttk_bs.Progressbar(
            progress_frame,
            value=course['current_progress'],
            style='Success.Horizontal.TProgressbar'
        )
        progress_bar.pack(fill=X, side=LEFT, expand=True)
        
        progress_label = ttk_bs.Label(
            progress_frame,
            text=f"{course['current_progress']:.1f}%"
        )
        progress_label.pack(side=RIGHT, padx=(10, 0))
        
        # Course stats
        stats_frame = ttk_bs.Frame(item_frame)
        stats_frame.pack(fill=X, pady=(5, 0))
        
        # Get modules for this course
        modules = self.db.get_course_modules(course['id'])
        completed_modules = sum(1 for m in modules if m['completed'])
        
        stats_text = f"{completed_modules}/{len(modules)} modules completed"
        if course['estimated_hours']:
            stats_text += f" • {course['estimated_hours']}h estimated"
            
        ttk_bs.Label(
            stats_frame,
            text=stats_text,
            foreground="gray",
            font=('Helvetica', 9)
        ).pack(side=LEFT)
        
    def create_time_analysis_tab(self):
        time_frame = ttk_bs.Frame(self.analytics_notebook)
        self.analytics_notebook.add(time_frame, text="⏰ Time Analysis")
        
        # Create matplotlib figure
        self.create_time_chart(time_frame)
        
    def create_time_chart(self, parent):
        # Create figure and axis
        fig = Figure(figsize=(10, 6), dpi=100)
        fig.patch.set_facecolor('#2c3e50')  # Dark background to match theme
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#34495e')
        
        # Sample data (in a real app, this would come from the database)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = [2.5, 1.8, 3.2, 2.1, 2.8, 1.5, 3.5]  # Sample study hours
        
        # Create bar chart
        bars = ax.bar(days, hours, color='#3498db', alpha=0.8)
        
        # Styling
        ax.set_title('Study Hours This Week', color='white', fontsize=14, fontweight='bold')
        ax.set_xlabel('Day of Week', color='white')
        ax.set_ylabel('Hours Studied', color='white')
        ax.tick_params(colors='white')
        
        # Add value labels on bars
        for bar, hour in zip(bars, hours):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                   f'{hour}h', ha='center', va='bottom', color='white')
        
        # Set grid
        ax.grid(True, alpha=0.3, color='white')
        ax.set_ylim(0, max(hours) * 1.2)
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=20, pady=20)
        
    def generate_insights(self):
        """Generate personalized insights based on user data"""
        insights = []
        
        # Get statistics
        stats = self.db.get_learning_statistics(int(self.period_var.get()))
        period_text = f"last {self.period_var.get()} days"
        
        # Study time insights
        if stats['total_study_hours'] > 0:
            avg_daily = stats['total_study_hours'] / int(self.period_var.get())
            insights.append(f"You've studied {stats['total_study_hours']:.1f} hours in the {period_text} (avg: {avg_daily:.1f}h/day)")
            
            if avg_daily >= 2:
                insights.append("🎉 Excellent! You're maintaining a great study routine.")
            elif avg_daily >= 1:
                insights.append("👍 Good progress! Consider increasing study time for faster progress.")
            else:
                insights.append("💡 Try to aim for at least 1 hour of study per day for consistent progress.")
        
        # Session insights
        if stats['study_sessions'] > 0:
            if stats['avg_session_length'] > 0:
                insights.append(f"Your average study session is {stats['avg_session_length']:.1f} minutes")
                
                if stats['avg_session_length'] > 60:
                    insights.append("⚡ Great focus! Long study sessions show deep engagement.")
                elif stats['avg_session_length'] > 30:
                    insights.append("📚 Good session length! This is optimal for retention.")
                else:
                    insights.append("🔥 Consider longer sessions for deeper learning (30-60 minutes ideal).")
        
        # Course insights
        if stats['active_courses'] > 3:
            insights.append("📚 You're learning multiple topics! Consider focusing on 2-3 courses for better progress.")
        elif stats['active_courses'] == 0:
            insights.append("🚀 Ready to start learning? Create your first course to begin!")
        
        # Module completion insights
        if stats['completed_modules'] > 0:
            insights.append(f"🎯 You've completed {stats['completed_modules']} modules in the {period_text}")
        
        return insights
        
    def refresh_analytics(self, event=None):
        """Refresh all analytics data"""
        # Clear and recreate content
        for tab in self.analytics_notebook.tabs():
            self.analytics_notebook.forget(tab)
            
        # Recreate tabs with fresh data
        self.create_overview_tab()
        self.create_progress_tab()
        self.create_time_analysis_tab()


# Example usage
if __name__ == "__main__":
    from database import DatabaseManager
    
    root = ttk_bs.Window(themename="superhero")
    root.title("Analytics Demo")
    root.geometry("1000x700")
    
    db = DatabaseManager("test_analytics.db")
    widget = AnalyticsWidget(root, db)
    
    root.mainloop()