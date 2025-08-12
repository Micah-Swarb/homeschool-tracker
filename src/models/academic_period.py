from src.models.user import db
from datetime import datetime, date

class AcademicPeriod(db.Model):
    __tablename__ = 'academic_periods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(20), default='semester')  # year, semester, quarter, term
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_current(self):
        """Check if this period is currently active."""
        today = date.today()
        return self.start_date <= today <= self.end_date

    def is_future(self):
        """Check if this period is in the future."""
        return self.start_date > date.today()

    def is_past(self):
        """Check if this period is in the past."""
        return self.end_date < date.today()

    def get_duration_days(self):
        """Get the duration of the period in days."""
        return (self.end_date - self.start_date).days + 1

    def get_progress_percentage(self):
        """Get the progress percentage of the current period."""
        if not self.is_current():
            return 100 if self.is_past() else 0
            
        total_days = self.get_duration_days()
        elapsed_days = (date.today() - self.start_date).days + 1
        return min(round((elapsed_days / total_days) * 100, 1), 100)

    def get_remaining_days(self):
        """Get remaining days in the period."""
        if self.is_past():
            return 0
        elif self.is_future():
            return self.get_duration_days()
        else:
            return (self.end_date - date.today()).days

    def __repr__(self):
        return f'<AcademicPeriod {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'period_type': self.period_type,
            'active': self.active,
            'is_current': self.is_current(),
            'is_future': self.is_future(),
            'is_past': self.is_past(),
            'duration_days': self.get_duration_days(),
            'progress_percentage': self.get_progress_percentage(),
            'remaining_days': self.get_remaining_days(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

