from src.models.user import db
from datetime import datetime, date
from sqlalchemy import UniqueConstraint

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), default='present')  # present, absent, partial
    hours = db.Column(db.Numeric(3, 1), default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique attendance record per student per date
    __table_args__ = (UniqueConstraint('student_id', 'date', name='unique_student_date'),)

    def get_status_color(self):
        """Get color code for attendance status."""
        status_colors = {
            'present': '#4CAF50',    # Green
            'absent': '#F44336',     # Red
            'partial': '#FF9800'     # Orange
        }
        return status_colors.get(self.status, '#666666')

    def get_status_icon(self):
        """Get icon for attendance status."""
        status_icons = {
            'present': '✅',
            'absent': '❌',
            'partial': '⚠️'
        }
        return status_icons.get(self.status, '❓')

    def is_weekend(self):
        """Check if the attendance date is a weekend."""
        return self.date.weekday() >= 5  # Saturday = 5, Sunday = 6

    def is_today(self):
        """Check if the attendance date is today."""
        return self.date == date.today()

    def is_future(self):
        """Check if the attendance date is in the future."""
        return self.date > date.today()

    def get_hours_formatted(self):
        """Get formatted hours string."""
        if self.hours:
            hours = float(self.hours)
            if hours == int(hours):
                return f"{int(hours)} hour{'s' if hours != 1 else ''}"
            else:
                return f"{hours} hour{'s' if hours != 1 else ''}"
        return "0 hours"

    @staticmethod
    def get_attendance_summary(student_id, start_date=None, end_date=None):
        """Get attendance summary for a student within a date range."""
        query = Attendance.query.filter(Attendance.student_id == student_id)
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
            
        records = query.all()
        
        if not records:
            return {
                'total_days': 0,
                'present_days': 0,
                'absent_days': 0,
                'partial_days': 0,
                'total_hours': 0,
                'attendance_rate': 0
            }
        
        total_days = len(records)
        present_days = sum(1 for r in records if r.status == 'present')
        absent_days = sum(1 for r in records if r.status == 'absent')
        partial_days = sum(1 for r in records if r.status == 'partial')
        total_hours = sum(float(r.hours) for r in records if r.hours)
        attendance_rate = round((present_days / total_days) * 100, 1) if total_days > 0 else 0
        
        return {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'partial_days': partial_days,
            'total_hours': total_hours,
            'attendance_rate': attendance_rate
        }

    def __repr__(self):
        return f'<Attendance {self.date} - {self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'status_color': self.get_status_color(),
            'status_icon': self.get_status_icon(),
            'hours': float(self.hours) if self.hours else 0.0,
            'hours_formatted': self.get_hours_formatted(),
            'notes': self.notes,
            'is_weekend': self.is_weekend(),
            'is_today': self.is_today(),
            'is_future': self.is_future(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

