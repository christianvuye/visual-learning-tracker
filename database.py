import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import os


class DatabaseManager:
    def __init__(self, db_path: str = "learning_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Courses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    difficulty INTEGER DEFAULT 1,
                    estimated_hours INTEGER DEFAULT 0,
                    current_progress REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'active',
                    start_date DATE,
                    target_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cover_image TEXT,
                    tags TEXT,
                    priority INTEGER DEFAULT 3
                )
            ''')
            
            # Course modules/chapters
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS course_modules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    order_index INTEGER,
                    completed BOOLEAN DEFAULT FALSE,
                    completion_date TIMESTAMP,
                    estimated_minutes INTEGER DEFAULT 0,
                    actual_minutes INTEGER DEFAULT 0,
                    FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
                )
            ''')
            
            # Learning sessions (time tracking)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    module_id INTEGER,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_minutes INTEGER,
                    notes TEXT,
                    session_type TEXT DEFAULT 'study',
                    mood INTEGER DEFAULT 3,
                    energy_level INTEGER DEFAULT 3,
                    FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
                    FOREIGN KEY (module_id) REFERENCES course_modules (id) ON DELETE SET NULL
                )
            ''')
            
            # Notes system
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    module_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT,
                    note_type TEXT DEFAULT 'text',
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_favorite BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
                    FOREIGN KEY (module_id) REFERENCES course_modules (id) ON DELETE SET NULL
                )
            ''')
            
            # Mind maps
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mind_maps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    map_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_template BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE SET NULL
                )
            ''')
            
            # Knowledge graph nodes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    node_type TEXT DEFAULT 'concept',
                    mastery_level INTEGER DEFAULT 0,
                    position_x REAL DEFAULT 0,
                    position_y REAL DEFAULT 0,
                    color TEXT DEFAULT '#3498db',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
                )
            ''')
            
            # Knowledge graph connections
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_node_id INTEGER,
                    target_node_id INTEGER,
                    connection_type TEXT DEFAULT 'related',
                    strength REAL DEFAULT 1.0,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_node_id) REFERENCES knowledge_nodes (id) ON DELETE CASCADE,
                    FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes (id) ON DELETE CASCADE
                )
            ''')
            
            # Flashcards
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flashcards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    note_id INTEGER,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    difficulty INTEGER DEFAULT 3,
                    times_reviewed INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    last_reviewed TIMESTAMP,
                    next_review TIMESTAMP,
                    interval_days INTEGER DEFAULT 1,
                    ease_factor REAL DEFAULT 2.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
                    FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE SET NULL
                )
            ''')
            
            # Learning goals
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    goal_type TEXT DEFAULT 'skill',
                    target_date DATE,
                    progress REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'active',
                    course_ids TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            # Study streaks and achievements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    achievement_type TEXT,
                    badge_icon TEXT,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    course_id INTEGER,
                    FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE SET NULL
                )
            ''')
            
            # Settings/preferences
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    # Course management methods
    def create_course(self, title: str, description: str = "", category: str = "", 
                     difficulty: int = 1, estimated_hours: int = 0, 
                     target_date: str = None, tags: List[str] = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            tags_json = json.dumps(tags) if tags else "[]"
            cursor.execute('''
                INSERT INTO courses (title, description, category, difficulty, 
                                   estimated_hours, target_date, tags, start_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, category, difficulty, estimated_hours, 
                  target_date, tags_json, date.today().isoformat()))
            return cursor.lastrowid
    
    def get_courses(self, status: str = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute('SELECT * FROM courses WHERE status = ? ORDER BY updated_at DESC', (status,))
            else:
                cursor.execute('SELECT * FROM courses ORDER BY updated_at DESC')
            
            courses = []
            for row in cursor.fetchall():
                course = dict(row)
                course['tags'] = json.loads(course['tags']) if course['tags'] else []
                courses.append(course)
            return courses
    
    def update_course_progress(self, course_id: int, progress: float):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE courses 
                SET current_progress = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (progress, course_id))
            conn.commit()
    
    # Module management
    def add_course_module(self, course_id: int, title: str, description: str = "", 
                         estimated_minutes: int = 0, order_index: int = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if order_index is None:
                cursor.execute('SELECT MAX(order_index) FROM course_modules WHERE course_id = ?', (course_id,))
                max_order = cursor.fetchone()[0] or 0
                order_index = max_order + 1
            
            cursor.execute('''
                INSERT INTO course_modules (course_id, title, description, 
                                          estimated_minutes, order_index)
                VALUES (?, ?, ?, ?, ?)
            ''', (course_id, title, description, estimated_minutes, order_index))
            return cursor.lastrowid
    
    def get_course_modules(self, course_id: int) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM course_modules 
                WHERE course_id = ? 
                ORDER BY order_index
            ''', (course_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def complete_module(self, module_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE course_modules 
                SET completed = TRUE, completion_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (module_id,))
            conn.commit()
    
    # Learning session tracking
    def start_learning_session(self, course_id: int, module_id: int = None, 
                              session_type: str = 'study') -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO learning_sessions (course_id, module_id, start_time, session_type)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?)
            ''', (course_id, module_id, session_type))
            return cursor.lastrowid
    
    def end_learning_session(self, session_id: int, notes: str = "", 
                           mood: int = 3, energy_level: int = 3):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE learning_sessions 
                SET end_time = CURRENT_TIMESTAMP,
                    duration_minutes = (julianday(CURRENT_TIMESTAMP) - julianday(start_time)) * 24 * 60,
                    notes = ?, mood = ?, energy_level = ?
                WHERE id = ?
            ''', (notes, mood, energy_level, session_id))
            conn.commit()
    
    # Notes management
    def create_note(self, course_id: int, title: str, content: str = "", 
                   note_type: str = 'text', tags: List[str] = None, 
                   module_id: int = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            tags_json = json.dumps(tags) if tags else "[]"
            cursor.execute('''
                INSERT INTO notes (course_id, module_id, title, content, 
                                 note_type, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (course_id, module_id, title, content, note_type, tags_json))
            return cursor.lastrowid
    
    def get_notes(self, course_id: int = None, search_query: str = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = 'SELECT * FROM notes WHERE 1=1'
            params = []
            
            if course_id:
                query += ' AND course_id = ?'
                params.append(course_id)
            
            if search_query:
                query += ' AND (title LIKE ? OR content LIKE ?)'
                params.extend([f'%{search_query}%', f'%{search_query}%'])
            
            query += ' ORDER BY updated_at DESC'
            
            cursor.execute(query, params)
            notes = []
            for row in cursor.fetchall():
                note = dict(row)
                note['tags'] = json.loads(note['tags']) if note['tags'] else []
                notes.append(note)
            return notes
    
    # Mind map management
    def save_mind_map(self, course_id: int, title: str, map_data: Dict, 
                     description: str = "", mind_map_id: int = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            map_data_json = json.dumps(map_data)
            
            if mind_map_id:
                cursor.execute('''
                    UPDATE mind_maps 
                    SET title = ?, description = ?, map_data = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (title, description, map_data_json, mind_map_id))
                return mind_map_id
            else:
                cursor.execute('''
                    INSERT INTO mind_maps (course_id, title, description, map_data)
                    VALUES (?, ?, ?, ?)
                ''', (course_id, title, description, map_data_json))
                return cursor.lastrowid
    
    def get_mind_maps(self, course_id: int = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if course_id:
                cursor.execute('SELECT * FROM mind_maps WHERE course_id = ? ORDER BY updated_at DESC', (course_id,))
            else:
                cursor.execute('SELECT * FROM mind_maps ORDER BY updated_at DESC')
            
            mind_maps = []
            for row in cursor.fetchall():
                mind_map = dict(row)
                mind_map['map_data'] = json.loads(mind_map['map_data']) if mind_map['map_data'] else {}
                mind_maps.append(mind_map)
            return mind_maps
    
    # Analytics and statistics
    def get_learning_statistics(self, days: int = 30) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total study time
            cursor.execute('''
                SELECT SUM(duration_minutes) 
                FROM learning_sessions 
                WHERE start_time >= datetime('now', '-{} days')
            '''.format(days))
            total_minutes = cursor.fetchone()[0] or 0
            
            # Study sessions count
            cursor.execute('''
                SELECT COUNT(*) 
                FROM learning_sessions 
                WHERE start_time >= datetime('now', '-{} days')
            '''.format(days))
            session_count = cursor.fetchone()[0] or 0
            
            # Active courses
            cursor.execute("SELECT COUNT(*) FROM courses WHERE status = 'active'")
            active_courses = cursor.fetchone()[0] or 0
            
            # Completed modules
            cursor.execute('''
                SELECT COUNT(*) 
                FROM course_modules 
                WHERE completed = TRUE AND completion_date >= datetime('now', '-{} days')
            '''.format(days))
            completed_modules = cursor.fetchone()[0] or 0
            
            return {
                'total_study_hours': round(total_minutes / 60, 1),
                'study_sessions': session_count,
                'active_courses': active_courses,
                'completed_modules': completed_modules,
                'avg_session_length': round(total_minutes / session_count, 1) if session_count > 0 else 0
            }
    
    # Flashcard methods
    def create_flashcard(self, course_id: int, question: str, answer: str, 
                        note_id: int = None, difficulty: int = 3) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO flashcards (course_id, note_id, question, answer, difficulty)
                VALUES (?, ?, ?, ?, ?)
            ''', (course_id, note_id, question, answer, difficulty))
            return cursor.lastrowid
    
    def get_flashcards_for_review(self, course_id: int = None, limit: int = 20) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM flashcards 
                WHERE (next_review IS NULL OR next_review <= CURRENT_TIMESTAMP)
            '''
            params = []
            
            if course_id:
                query += ' AND course_id = ?'
                params.append(course_id)
            
            query += ' ORDER BY last_reviewed ASC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        pass