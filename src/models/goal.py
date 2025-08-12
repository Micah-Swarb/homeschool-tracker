from src.models.user import db
from datetime import datetime, date

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    goal_type = db.Column(db.String(50), default='academic')  # academic, behavioral, skill
    status = db.Column(db.String(20), default='active')  # active, completed, paused, cancelled
    progress_percentage = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_overdue(self):
        """Check if goal is overdue."""
        if not self.target_date or self.status in ['completed', 'cancelled']:
            return False
        return self.target_date < date.today()

    def days_until_target(self):
        """Calculate days until target date."""
        if not self.target_date:
            return None
        delta = self.target_date - date.today()
        return delta.days

    def get_status_color(self):
        """Get color code for goal status."""
        status_colors = {
            'active': '#2196F3',      # Blue
            'completed': '#4CAF50',   # Green
            'paused': '#FF9800',      # Orange
            'cancelled': '#F44336'    # Red
        }
        return status_colors.get(self.status, '#666666')

    def get_status_icon(self):
        """Get icon for goal status."""
        status_icons = {
            'active': '🎯',
            'completed': '✅',
            'paused': '⏸️',
            'cancelled': '❌'
        }
        return status_icons.get(self.status, '❓')

    def get_type_icon(self):
        """Get icon for goal type."""
        type_icons = {
            'academic': '📚',
            'behavioral': '🎭',
            'skill': '🛠️'
        }
        return type_icons.get(self.goal_type, '🎯')

    def get_progress_color(self):
        """Get color for progress bar based on percentage."""
        if self.progress_percentage >= 80:
            return '#4CAF50'  # Green
        elif self.progress_percentage >= 60:
            return '#8BC34A'  # Light Green
        elif self.progress_percentage >= 40:
            return '#FF9800'  # Orange
        elif self.progress_percentage >= 20:
            return '#FF5722'  # Deep Orange
        else:
            return '#F44336'  # Red

    def update_progress(self, percentage):
        """Update goal progress and automatically complete if 100%."""
        self.progress_percentage = max(0, min(100, percentage))
        if self.progress_percentage >= 100 and self.status == 'active':
            self.status = 'completed'
        self.updated_at = datetime.utcnow()

    def complete_goal(self):
        """Mark goal as completed."""
        self.status = 'completed'
        self.progress_percentage = 100
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<Goal {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'title': self.title,
            'description': self.description,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'goal_type': self.goal_type,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'notes': self.notes,
            'is_overdue': self.is_overdue(),
            'days_until_target': self.days_until_target(),
            'status_color': self.get_status_color(),
            'status_icon': self.get_status_icon(),
            'type_icon': self.get_type_icon(),
            'progress_color': self.get_progress_color(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

