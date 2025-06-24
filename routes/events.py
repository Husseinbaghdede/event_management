from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import sqlite3
import os

events_bp = Blueprint('events', __name__)

def get_db_connection():
    """Get database connection"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/events.db')
    conn.row_factory = sqlite3.Row
    return conn

@events_bp.route('/')
def list_events():
    """List all events with filtering"""
    status_filter = request.args.get('status', '')
    
    conn = get_db_connection()
    
    if status_filter:
        events = conn.execute('''
            SELECT * FROM events 
            WHERE status = ? 
            ORDER BY date DESC
        ''', (status_filter,)).fetchall()
    else:
        events = conn.execute('''
            SELECT * FROM events 
            ORDER BY date DESC
        ''').fetchall()
    
    conn.close()
    
    # Mock pagination object for template compatibility
    class MockPagination:
        def __init__(self, items):
            self.items = items
            self.has_prev = False
            self.has_next = False
            self.prev_num = None
            self.next_num = None
            self.page = 1
            self.pages = 1
    
    events_paginated = MockPagination(events)
    
    return render_template('events.html', 
                         events=events_paginated, 
                         current_status=status_filter)

@events_bp.route('/add', methods=['GET', 'POST'])
def add_event():
    """Add new event"""
    if request.method == 'POST':
        # Check if this is AI-powered input
        ai_input = request.form.get('ai_input', '').strip()
        
        if ai_input:
            # Simple AI simulation (you can add OpenAI integration later)
            try:
                # Import AI service
                from services.ai_service import AIService
                ai_service = AIService()
                ai_result = ai_service.parse_natural_language_event(ai_input)
                
                if ai_result['success']:
                    event_data = ai_result['event_data']
                    
                    if event_data.get('needs_clarification'):
                        flash(f"Need clarification: {event_data.get('clarification_message')}", 'warning')
                        return render_template('add_event.html', ai_input=ai_input)
                    
                    # Create event from AI-parsed data
                    conn = get_db_connection()
                    conn.execute('''
                        INSERT INTO events (title, description, date, location, status)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        event_data['title'],
                        event_data.get('description'),
                        event_data['date'].isoformat() if isinstance(event_data['date'], datetime) else event_data['date'],
                        event_data.get('location'),
                        event_data.get('status', 'upcoming')
                    ))
                    conn.commit()
                    conn.close()
                    
                    flash(f'Event "{event_data["title"]}" created successfully using AI!', 'success')
                    return redirect(url_for('events.list_events'))
                else:
                    flash(f'AI parsing failed: {ai_result.get("error", "Unknown error")}', 'error')
                    return render_template('add_event.html', ai_input=ai_input)
            except Exception as e:
                flash(f'AI service error: {str(e)}', 'warning')
                # Fall back to manual form
                pass
        
        # Traditional form input
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '').strip()
        location = request.form.get('location', '').strip()
        status = request.form.get('status', 'upcoming')
        
        # Validate required fields
        if not title:
            flash('Event title is required', 'error')
            return render_template('add_event.html')
        
        if not date_str:
            flash('Event date is required', 'error')
            return render_template('add_event.html')
        
        # Parse date
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('add_event.html')
        
        # Create event
        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO events (title, description, date, location, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description or None, event_date.isoformat(), location or None, status))
            conn.commit()
            conn.close()
            
            flash(f'Event "{title}" created successfully!', 'success')
            return redirect(url_for('events.list_events'))
            
        except Exception as e:
            flash(f'Error creating event: {str(e)}', 'error')
    
    return render_template('add_event.html')

@events_bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    """Edit existing event"""
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
    
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('events.list_events'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '').strip()
        location = request.form.get('location', '').strip()
        status = request.form.get('status', 'upcoming')
        
        # Validate required fields
        if not title:
            flash('Event title is required', 'error')
            return render_template('add_event.html', event=event, edit_mode=True)
        
        if not date_str:
            flash('Event date is required', 'error')
            return render_template('add_event.html', event=event, edit_mode=True)
        
        # Parse date
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('add_event.html', event=event, edit_mode=True)
        
        # Update event
        try:
            conn.execute('''
                UPDATE events 
                SET title = ?, description = ?, date = ?, location = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (title, description or None, event_date.isoformat(), location or None, status, event_id))
            conn.commit()
            conn.close()
            
            flash(f'Event "{title}" updated successfully!', 'success')
            return redirect(url_for('events.list_events'))
            
        except Exception as e:
            flash(f'Error updating event: {str(e)}', 'error')
    
    conn.close()
    return render_template('add_event.html', event=event, edit_mode=True)

@events_bp.route('/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    """Delete event"""
    try:
        conn = get_db_connection()
        event = conn.execute('SELECT title FROM events WHERE id = ?', (event_id,)).fetchone()
        
        if event:
            event_title = event['title']
            conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
            conn.commit()
            flash(f'Event "{event_title}" deleted successfully!', 'success')
        else:
            flash('Event not found', 'error')
        
        conn.close()
    except Exception as e:
        flash(f'Error deleting event: {str(e)}', 'error')
    
    return redirect(url_for('events.list_events'))

@events_bp.route('/api/<int:event_id>')
def get_event_api(event_id):
    """API endpoint to get single event"""
    try:
        conn = get_db_connection()
        event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
        conn.close()
        
        if event:
            return jsonify({
                'success': True,
                'event': dict(event)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@events_bp.route('/api/enhance-description', methods=['POST'])
def enhance_description_api():
    """API endpoint to enhance event description using AI"""
    data = request.get_json()
    title = data.get('title', '')
    location = data.get('location', '')
    
    if not title:
        return jsonify({
            'success': False,
            'error': 'Title is required'
        }), 400
    
    try:
        from services.ai_service import AIService
        ai_service = AIService()
        enhanced_description = ai_service.enhance_event_description(title, location)
        return jsonify({
            'success': True,
            'description': enhanced_description
        })
    except Exception as e:
        # Fallback to simple description
        description = f"Event: {title}"
        if location:
            description += f" at {location}"
        
        return jsonify({
            'success': True,
            'description': description
        })