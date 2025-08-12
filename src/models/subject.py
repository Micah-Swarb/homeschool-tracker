from src.models.user import db
from datetime import datetime

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7))  # Hex color code for UI
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='subject', lazy=True)
    goals = db.relationship('Goal', backref='subject', lazy=True)

    def get_assignment_count(self):
        """Get total number of assignments for this subject."""
        return len(self.assignments)

    def get_average_grade(self):
        """Calculate average grade for all assignments in this subject."""
        from src.models.grade import Grade
        from src.models.assignment import Assignment
        
        grades = db.session.query(Grade).join(
            Assignment, Grade.assignment_id == Assignment.id
        ).filter(Assignment.subject_id == self.id).all()
        
        if not grades:
            return None
            
        valid_grades = [grade.percentage for grade in grades if grade.percentage is not None]
        return round(sum(valid_grades) / len(valid_grades), 2) if valid_grades else None

    def __repr__(self):
        return f'<Subject {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'active': self.active,
            'assignment_count': self.get_assignment_count(),
            'average_grade': self.get_average_grade(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

