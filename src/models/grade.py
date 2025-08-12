from src.models.user import db
from datetime import datetime
import json

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False, index=True)
    points_earned = db.Column(db.Numeric(5, 2))
    percentage = db.Column(db.Numeric(5, 2))
    grade_letter = db.Column(db.String(2))
    feedback = db.Column(db.Text)
    rubric_scores = db.Column(db.Text)  # JSON object for detailed rubric scoring
    graded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    graded_at = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grader = db.relationship('User', foreign_keys=[graded_by])

    def set_rubric_scores(self, rubric_dict):
        """Set rubric scores as JSON string."""
        self.rubric_scores = json.dumps(rubric_dict)

    def get_rubric_scores(self):
        """Get rubric scores as dictionary."""
        if self.rubric_scores:
            return json.loads(self.rubric_scores)
        return {}

    def calculate_percentage(self, points_total):
        """Calculate percentage based on points earned and total points."""
        if self.points_earned is not None and points_total > 0:
            self.percentage = round((float(self.points_earned) / points_total) * 100, 2)
            return self.percentage
        return None

    def calculate_letter_grade(self):
        """Calculate letter grade based on percentage."""
        if self.percentage is None:
            return None
            
        percentage = float(self.percentage)
        if percentage >= 97:
            self.grade_letter = 'A+'
        elif percentage >= 93:
            self.grade_letter = 'A'
        elif percentage >= 90:
            self.grade_letter = 'A-'
        elif percentage >= 87:
            self.grade_letter = 'B+'
        elif percentage >= 83:
            self.grade_letter = 'B'
        elif percentage >= 80:
            self.grade_letter = 'B-'
        elif percentage >= 77:
            self.grade_letter = 'C+'
        elif percentage >= 73:
            self.grade_letter = 'C'
        elif percentage >= 70:
            self.grade_letter = 'C-'
        elif percentage >= 67:
            self.grade_letter = 'D+'
        elif percentage >= 63:
            self.grade_letter = 'D'
        elif percentage >= 60:
            self.grade_letter = 'D-'
        else:
            self.grade_letter = 'F'
            
        return self.grade_letter

    def set_grade(self, points_earned, points_total, graded_by_id, feedback=None):
        """Set grade with automatic calculations."""
        self.points_earned = points_earned
        self.graded_by = graded_by_id
        self.graded_at = datetime.utcnow()
        self.feedback = feedback
        
        # Calculate percentage and letter grade
        self.calculate_percentage(points_total)
        self.calculate_letter_grade()

    def get_grade_color(self):
        """Get color code for grade display."""
        if not self.grade_letter:
            return '#666666'  # Gray for ungraded
            
        if self.grade_letter.startswith('A'):
            return '#4CAF50'  # Green
        elif self.grade_letter.startswith('B'):
            return '#8BC34A'  # Light Green
        elif self.grade_letter.startswith('C'):
            return '#FF9800'  # Orange
        elif self.grade_letter.startswith('D'):
            return '#FF5722'  # Deep Orange
        else:  # F
            return '#F44336'  # Red

    def __repr__(self):
        return f'<Grade {self.grade_letter} ({self.percentage}%)>'

    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'points_earned': float(self.points_earned) if self.points_earned else None,
            'percentage': float(self.percentage) if self.percentage else None,
            'grade_letter': self.grade_letter,
            'feedback': self.feedback,
            'rubric_scores': self.get_rubric_scores(),
            'graded_by': self.graded_by,
            'grader_name': f"{self.grader.first_name} {self.grader.last_name}" if self.grader else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'grade_color': self.get_grade_color(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

