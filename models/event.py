from app import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='upcoming', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status options: upcoming, attending, maybe, declined
    VALID_STATUSES = ['upcoming', 'attending', 'maybe', 'declined']
    
    def __repr__(self):
        return f'<Event {self.title}>'
    
    def to_dict(self):
        """Convert event to dictionary for JSON responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'location': self.location,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def formatted_date(self):
        """Return human-readable date format"""
        if self.date:
            return self.date.strftime('%B %d, %Y at %I:%M %p')
        return 'No date set'
    
    @property
    def short_date(self):
        """Return short date format"""
        if self.date:
            return self.date.strftime('%m/%d/%Y %I:%M %p')
        return 'No date'
    
    @property
    def is_past(self):
        """Check if event is in the past"""
        if self.date:
            return self.date < datetime.now()
        return False
    
    @property
    def status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'upcoming': 'badge-primary',
            'attending': 'badge-success',
            'maybe': 'badge-warning',
            'declined': 'badge-danger'
        }
        return status_classes.get(self.status, 'badge-secondary')
    
    def validate_status(self):
        """Validate if status is valid"""
        return self.status in self.VALID_STATUSES