from src.models.user import db
from datetime import datetime, date
import json

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    due_date = db.Column(db.Date, index=True)
    estimated_duration = db.Column(db.Integer)  # Minutes
    points_total = db.Column(db.Integer, default=100)
    assignment_type = db.Column(db.String(50), default='homework')  # homework, quiz, test, project
    difficulty_level = db.Column(db.String(20), default='medium')  # easy, medium, hard
    status = db.Column(db.String(20), default='assigned', index=True)  # assigned, in_progress, submitted, graded
    priority = db.Column(db.String(20), default='normal')  # low, normal, high
    tags = db.Column(db.Text)  # JSON array of tags
    resources = db.Column(db.Text)  # JSON array of resource links
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grade = db.relationship('Grade', backref='assignment', uselist=False, cascade='all, delete-orphan')
    submissions = db.relationship('Submission', backref='assignment', lazy=True, cascade='all, delete-orphan')

    def set_tags(self, tags_list):
        """Set tags as JSON string."""
        self.tags = json.dumps(tags_list)

    def get_tags(self):
        """Get tags as list."""
        if self.tags:
            return json.loads(self.tags)
        return []

    def set_resources(self, resources_list):
        """Set resources as JSON string."""
        self.resources = json.dumps(resources_list)

    def get_resources(self):
        """Get resources as list."""
        if self.resources:
            return json.loads(self.resources)
        return []

    def is_overdue(self):
        """Check if assignment is overdue."""
        if not self.due_date:
            return False
        return self.due_date < date.today() and self.status not in ['submitted', 'graded']

    def days_until_due(self):
        """Calculate days until due date."""
        if not self.due_date:
            return None
        delta = self.due_date - date.today()
        return delta.days

    def get_grade_percentage(self):
        """Get grade percentage if graded."""
        if self.grade:
            return self.grade.percentage
        return None

    def get_grade_letter(self):
        """Get letter grade if graded."""
        if self.grade:
            return self.grade.grade_letter
        return None

    def is_graded(self):
        """Check if assignment has been graded."""
        return self.grade is not None

    def get_submission_count(self):
        """Get number of submissions for this assignment."""
        return len(self.submissions)

    def get_latest_submission(self):
        """Get the most recent submission."""
        if self.submissions:
            return max(self.submissions, key=lambda s: s.submitted_at)
        return None

    def __repr__(self):
        return f'<Assignment {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'estimated_duration': self.estimated_duration,
            'points_total': self.points_total,
            'assignment_type': self.assignment_type,
            'difficulty_level': self.difficulty_level,
            'status': self.status,
            'priority': self.priority,
            'tags': self.get_tags(),
            'resources': self.get_resources(),
            'is_overdue': self.is_overdue(),
            'days_until_due': self.days_until_due(),
            'grade_percentage': self.get_grade_percentage(),
            'grade_letter': self.get_grade_letter(),
            'is_graded': self.is_graded(),
            'submission_count': self.get_submission_count(),
            'latest_submission': self.get_latest_submission().to_dict() if self.get_latest_submission() else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

