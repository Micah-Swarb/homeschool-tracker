from src.models.user import db
from datetime import datetime
import os

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False, index=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    file_path = db.Column(db.String(500))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='submitted')  # submitted, reviewed, returned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_file_size_formatted(self):
        """Get formatted file size string."""
        if not self.file_size:
            return None
            
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def get_file_extension(self):
        """Get file extension from filename."""
        if self.file_name:
            return os.path.splitext(self.file_name)[1].lower()
        return None

    def is_image(self):
        """Check if submitted file is an image."""
        if self.mime_type:
            return self.mime_type.startswith('image/')
        
        ext = self.get_file_extension()
        return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

    def is_document(self):
        """Check if submitted file is a document."""
        if self.mime_type:
            return self.mime_type in [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain'
            ]
        
        ext = self.get_file_extension()
        return ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']

    def get_file_icon(self):
        """Get appropriate icon for file type."""
        if self.is_image():
            return '🖼️'
        elif self.is_document():
            return '📄'
        elif self.get_file_extension() in ['.mp4', '.avi', '.mov', '.wmv']:
            return '🎥'
        elif self.get_file_extension() in ['.mp3', '.wav', '.m4a']:
            return '🎵'
        elif self.get_file_extension() in ['.zip', '.rar', '.7z']:
            return '📦'
        else:
            return '📎'

    def file_exists(self):
        """Check if the submitted file still exists on disk."""
        if self.file_path:
            return os.path.exists(self.file_path)
        return False

    def __repr__(self):
        return f'<Submission {self.file_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_size_formatted': self.get_file_size_formatted(),
            'mime_type': self.mime_type,
            'file_extension': self.get_file_extension(),
            'file_icon': self.get_file_icon(),
            'is_image': self.is_image(),
            'is_document': self.is_document(),
            'file_exists': self.file_exists(),
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

