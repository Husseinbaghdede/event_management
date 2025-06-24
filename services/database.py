from app import db
from models.event import Event
from datetime import datetime
from sqlalchemy import or_, and_

class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    def create_event(title, description, date, location, status='upcoming'):
        """Create a new event"""
        try:
            event = Event(
                title=title,
                description=description,
                date=date,
                location=location,
                status=status
            )
            
            if not event.validate_status():
                raise ValueError(f"Invalid status: {status}")
            
            db.session.add(event)
            db.session.commit()
            return event
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_event_by_id(event_id):
        """Get event by ID"""
        return Event.query.get_or_404(event_id)
    
    @staticmethod
    def get_all_events(page=1, per_page=10):
        """Get all events with pagination"""
        return Event.query.order_by(Event.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_upcoming_events(limit=None):
        """Get upcoming events"""
        query = Event.query.filter(Event.date >= datetime.now()).order_by(Event.date.asc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def update_event(event_id, title=None, description=None, date=None, location=None, status=None):
        """Update an existing event"""
        try:
            event = Event.query.get_or_404(event_id)
            
            if title is not None:
                event.title = title
            if description is not None:
                event.description = description
            if date is not None:
                event.date = date
            if location is not None:
                event.location = location
            if status is not None:
                if status not in Event.VALID_STATUSES:
                    raise ValueError(f"Invalid status: {status}")
                event.status = status
            
            event.updated_at = datetime.utcnow()
            db.session.commit()
            return event
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_event(event_id):
        """Delete an event"""
        try:
            event = Event.query.get_or_404(event_id)
            db.session.delete(event)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def search_events(query, search_type='all'):
        """Search events by different criteria"""
        if not query:
            return []
        
        search_query = f"%{query}%"
        
        if search_type == 'title':
            return Event.query.filter(Event.title.like(search_query)).all()
        elif search_type == 'location':
            return Event.query.filter(Event.location.like(search_query)).all()
        elif search_type == 'description':
            return Event.query.filter(Event.description.like(search_query)).all()
        else:  # search all fields
            return Event.query.filter(
                or_(
                    Event.title.like(search_query),
                    Event.description.like(search_query),
                    Event.location.like(search_query)
                )
            ).all()
    
    @staticmethod
    def filter_events_by_status(status):
        """Filter events by status"""
        if status not in Event.VALID_STATUSES:
            return []
        return Event.query.filter(Event.status == status).all()
    
    @staticmethod
    def filter_events_by_date_range(start_date, end_date):
        """Filter events by date range"""
        return Event.query.filter(
            and_(Event.date >= start_date, Event.date <= end_date)
        ).order_by(Event.date.asc()).all()
    
    @staticmethod
    def get_event_stats():
        """Get event statistics"""
        total = Event.query.count()
        upcoming = Event.query.filter(Event.date >= datetime.now()).count()
        past = Event.query.filter(Event.date < datetime.now()).count()
        
        status_counts = {}
        for status in Event.VALID_STATUSES:
            status_counts[status] = Event.query.filter(Event.status == status).count()
        
        return {
            'total': total,
            'upcoming': upcoming,
            'past': past,
            'by_status': status_counts
        }