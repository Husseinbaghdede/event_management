from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')

# Database file path
DATABASE = 'data/events.db'

def get_db_connection():
    """Get database connection"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with events table"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'upcoming',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def format_date(date_str):
    """Format date string for display"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return date_str

def short_date(date_str):
    """Short date format"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%m/%d/%Y %I:%M %p')
    except:
        return date_str

def is_past(date_str):
    """Check if date is in the past"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt < datetime.now()
    except:
        return False

def status_badge_class(status):
    """Get CSS class for status badge"""
    status_classes = {
        'upcoming': 'bg-primary',
        'attending': 'bg-success',
        'maybe': 'bg-warning',
        'declined': 'bg-danger'
    }
    return status_classes.get(status, 'bg-secondary')

# Add template filters
app.jinja_env.filters['format_date'] = format_date
app.jinja_env.filters['short_date'] = short_date
app.jinja_env.filters['is_past'] = is_past
app.jinja_env.filters['status_badge_class'] = status_badge_class

# Import routes after app setup
from routes.events import events_bp
from routes.search import search_bp

app.register_blueprint(events_bp, url_prefix='/events')
app.register_blueprint(search_bp, url_prefix='/search')

@app.route('/')
def index():
    """Dashboard home page"""
    conn = get_db_connection()
    
    # Get recent events
    recent_events = conn.execute('''
        SELECT * FROM events 
        ORDER BY date DESC 
        LIMIT 5
    ''').fetchall()
    
    # Get stats
    total_events = conn.execute('SELECT COUNT(*) as count FROM events').fetchone()['count']
    upcoming_events = conn.execute('''
        SELECT COUNT(*) as count FROM events 
        WHERE date >= datetime('now')
    ''').fetchone()['count']
    
    conn.close()
    
    return render_template('index.html', 
                         recent_events=recent_events,
                         total_events=total_events,
                         upcoming_events=upcoming_events)

if __name__ == '__main__':
    # Initialize database before running the app
    init_database()
    print("Database initialized successfully!")
    app.run(debug=True, host='0.0.0.0', port=5000)