from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
import sqlite3
import os

search_bp = Blueprint('search', __name__)

def get_db_connection():
    """Get database connection"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/events.db')
    conn.row_factory = sqlite3.Row
    return conn

@search_bp.route('/')
def search_page():
    """Main search page"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    status_filter = request.args.get('status', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    results = []
    total_results = 0
    
    if query or status_filter or (date_from and date_to):
        conn = get_db_connection()
        
        # Build SQL query based on criteria
        sql_parts = []
        params = []
        
        if query:
            if search_type == 'title':
                sql_parts.append("title LIKE ?")
                params.append(f"%{query}%")
            elif search_type == 'location':
                sql_parts.append("location LIKE ?")
                params.append(f"%{query}%")
            elif search_type == 'description':
                sql_parts.append("description LIKE ?")
                params.append(f"%{query}%")
            else:  # search all fields
                sql_parts.append("(title LIKE ? OR description LIKE ? OR location LIKE ?)")
                params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        if status_filter:
            sql_parts.append("status = ?")
            params.append(status_filter)
        
        if date_from and date_to:
            try:
                start_date = datetime.strptime(date_from, '%Y-%m-%d').isoformat()
                end_date = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59).isoformat()
                sql_parts.append("date BETWEEN ? AND ?")
                params.extend([start_date, end_date])
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        if sql_parts:
            sql = f"SELECT * FROM events WHERE {' AND '.join(sql_parts)} ORDER BY date DESC"
            results = conn.execute(sql, params).fetchall()
        
        conn.close()
        total_results = len(results)
    
    return render_template('search.html',
                         results=results,
                         query=query,
                         search_type=search_type,
                         status_filter=status_filter,
                         date_from=date_from,
                         date_to=date_to,
                         total_results=total_results)

@search_bp.route('/api/quick-search')
def quick_search_api():
    """API endpoint for quick search (AJAX)"""
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 5, type=int)
    
    if not query:
        return jsonify({
            'success': True,
            'results': []
        })
    
    try:
        conn = get_db_connection()
        
        # Quick search across all fields
        results = conn.execute('''
            SELECT * FROM events 
            WHERE title LIKE ? OR description LIKE ? OR location LIKE ?
            ORDER BY date DESC
            LIMIT ?
        ''', (f"%{query}%", f"%{query}%", f"%{query}%", limit)).fetchall()
        
        conn.close()
        
        # Convert to dict
        results_data = [dict(row) for row in results]
        
        return jsonify({
            'success': True,
            'results': results_data,
            'total': len(results_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@search_bp.route('/api/suggestions')
def search_suggestions_api():
    """API endpoint for search suggestions"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({
            'success': True,
            'suggestions': []
        })
    
    try:
        conn = get_db_connection()
        
        # Get events that match the query
        events = conn.execute('''
            SELECT title, location FROM events 
            WHERE title LIKE ? OR location LIKE ?
            LIMIT 10
        ''', (f"%{query}%", f"%{query}%")).fetchall()
        
        conn.close()
        
        # Extract unique suggestions
        suggestions = set()
        
        for event in events:
            # Add title words that contain the query
            if event['title']:
                title_words = event['title'].lower().split()
                for word in title_words:
                    if query.lower() in word and len(word) > 2:
                        suggestions.add(word.title())
            
            # Add location if it contains the query
            if event['location'] and query.lower() in event['location'].lower():
                suggestions.add(event['location'])
        
        return jsonify({
            'success': True,
            'suggestions': list(suggestions)[:8]  # Limit to 8 suggestions
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500