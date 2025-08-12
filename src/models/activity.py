from src.models.user import db
from datetime import datetime, date
import json

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    activity_type = db.Column(db.String(50))  # sports, music, art, volunteer, etc.
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    hours_total = db.Column(db.Numeric(5, 1))
    achievements = db.Column(db.Text)  # JSON array of achievements
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_achievements(self, achievements_list):
        """Set achievements as JSON string."""
        self.achievements = json.dumps(achievements_list)

    def get_achievements(self):
        """Get achievements as list."""
        if self.achievements:
            return json.loads(self.achievements)
        return []

    def add_achievement(self, achievement):
        """Add a new achievement to the list."""
        current_achievements = self.get_achievements()
        current_achievements.append({
            'title': achievement,
            'date': date.today().isoformat()
        })
        self.set_achievements(current_achievements)

    def is_ongoing(self):
        """Check if activity is currently ongoing."""
        today = date.today()
        if not self.start_date:
            return False
        if not self.end_date:
            return self.start_date <= today
        return self.start_date <= today <= self.end_date

    def is_completed(self):
        """Check if activity is completed."""
        if not self.end_date:
            return False
        return self.end_date < date.today()

    def is_future(self):
        """Check if activity is in the future."""
        if not self.start_date:
            return False
        return self.start_date > date.today()

    def get_duration_days(self):
        """Get the duration of the activity in days."""
        if not self.start_date or not self.end_date:
            return None
        return (self.end_date - self.start_date).days + 1

    def get_type_icon(self):
        """Get icon for activity type."""
        type_icons = {
            'sports': '⚽',
            'music': '🎵',
            'art': '🎨',
            'volunteer': '🤝',
            'academic': '📚',
            'technology': '💻',
            'outdoor': '🌲',
            'social': '👥',
            'leadership': '👑',
            'community': '🏘️'
        }
        return type_icons.get(self.activity_type, '🎯')

    def get_status(self):
        """Get current status of the activity."""
        if self.is_completed():
            return 'completed'
        elif self.is_ongoing():
            return 'ongoing'
        elif self.is_future():
            return 'upcoming'
        else:
            return 'planned'

    def get_status_color(self):
        """Get color code for activity status."""
        status = self.get_status()
        status_colors = {
            'completed': '#4CAF50',   # Green
            'ongoing': '#2196F3',     # Blue
            'upcoming': '#FF9800',    # Orange
            'planned': '#9E9E9E'      # Gray
        }
        return status_colors.get(status, '#666666')

    def get_hours_formatted(self):
        """Get formatted hours string."""
        if self.hours_total:
            hours = float(self.hours_total)
            if hours == int(hours):
                return f"{int(hours)} hour{'s' if hours != 1 else ''}"
            else:
                return f"{hours} hour{'s' if hours != 1 else ''}"
        return "No hours recorded"

    def __repr__(self):
        return f'<Activity {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'description': self.description,
            'activity_type': self.activity_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'hours_total': float(self.hours_total) if self.hours_total else None,
            'hours_formatted': self.get_hours_formatted(),
            'achievements': self.get_achievements(),
            'notes': self.notes,
            'status': self.get_status(),
            'status_color': self.get_status_color(),
            'type_icon': self.get_type_icon(),
            'is_ongoing': self.is_ongoing(),
            'is_completed': self.is_completed(),
            'is_future': self.is_future(),
            'duration_days': self.get_duration_days(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

