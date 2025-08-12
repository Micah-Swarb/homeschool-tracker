from src.models.user import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    grade_level = db.Column(db.String(20), nullable=False)
    student_id = db.Column(db.String(20), unique=True)  # Optional custom student ID
    profile_picture = db.Column(db.String(255))  # Path to profile image
    notes = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='student', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='student', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='student', lazy=True, cascade='all, delete-orphan')

    def get_age(self):
        """Calculate student's current age."""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def get_full_name(self):
        """Get student's full name."""
        return f"{self.first_name} {self.last_name}"

    def get_current_gpa(self):
        """Calculate current GPA based on graded assignments."""
        from src.models.assignment import Assignment
        from src.models.grade import Grade
        
        # Get all graded assignments for this student
        graded_assignments = db.session.query(Assignment, Grade).join(
            Grade, Assignment.id == Grade.assignment_id
        ).filter(Assignment.student_id == self.id).all()
        
        if not graded_assignments:
            return None
            
        total_percentage = sum(grade.percentage for _, grade in graded_assignments if grade.percentage is not None)
        count = len([grade for _, grade in graded_assignments if grade.percentage is not None])
        
        return round(total_percentage / count, 2) if count > 0 else None

    def get_attendance_rate(self, days=30):
        """Calculate attendance rate for the last N days."""
        from src.models.attendance import Attendance
        from datetime import date, timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        attendance_records = Attendance.query.filter(
            Attendance.student_id == self.id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
        
        if not attendance_records:
            return None
            
        present_days = sum(1 for record in attendance_records if record.status == 'present')
        total_days = len(attendance_records)
        
        return round((present_days / total_days) * 100, 1) if total_days > 0 else None

    def __repr__(self):
        return f'<Student {self.get_full_name()}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.get_age(),
            'grade_level': self.grade_level,
            'student_id': self.student_id,
            'profile_picture': self.profile_picture,
            'notes': self.notes,
            'active': self.active,
            'current_gpa': self.get_current_gpa(),
            'attendance_rate': self.get_attendance_rate(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

