from flask import Blueprint, jsonify, request
from src.models import db, Subject
from src.routes.user import login_required, get_current_user
from src.utils.request_utils import get_json_data

subject_bp = Blueprint('subject', __name__)

@subject_bp.route('/subjects', methods=['GET'])
@login_required
def get_subjects():
    """Get all subjects for the current user."""
    current_user = get_current_user()
    subjects = Subject.query.filter_by(user_id=current_user.id, active=True).all()
    return jsonify([subject.to_dict() for subject in subjects])

@subject_bp.route('/subjects', methods=['POST'])
@login_required
def create_subject():
    """Create a new subject."""
    current_user = get_current_user()
    data, error, status = get_json_data(['name'])
    if error:
        return error, status
    
    # Check if subject name already exists for this user
    existing_subject = Subject.query.filter_by(
        user_id=current_user.id,
        name=data['name']
    ).first()
    if existing_subject:
        return jsonify({'error': 'Subject name already exists'}), 400
    
    # Create new subject
    subject = Subject(
        user_id=current_user.id,
        name=data['name'],
        description=data.get('description'),
        color=data.get('color', '#2196F3')  # Default blue color
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify({
        'message': 'Subject created successfully',
        'subject': subject.to_dict()
    }), 201

@subject_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@login_required
def get_subject(subject_id):
    """Get specific subject by ID."""
    current_user = get_current_user()
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    return jsonify(subject.to_dict())

@subject_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@login_required
def update_subject(subject_id):
    """Update subject information."""
    current_user = get_current_user()
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    data, error, status = get_json_data()
    if error:
        return error, status
    
    # Update allowed fields
    if 'name' in data:
        # Check if new name already exists for this user
        if data['name'] != subject.name:
            existing_subject = Subject.query.filter_by(
                user_id=current_user.id,
                name=data['name']
            ).first()
            if existing_subject:
                return jsonify({'error': 'Subject name already exists'}), 400
        subject.name = data['name']
    
    if 'description' in data:
        subject.description = data['description']
    if 'color' in data:
        subject.color = data['color']
    if 'active' in data:
        subject.active = data['active']
    
    db.session.commit()
    
    return jsonify(subject.to_dict())

@subject_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@login_required
def delete_subject(subject_id):
    """Delete (deactivate) subject."""
    current_user = get_current_user()
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    
    # Check if subject has assignments
    if subject.assignments:
        # Soft delete - just mark as inactive
        subject.active = False
        db.session.commit()
        return jsonify({'message': 'Subject deactivated successfully (has existing assignments)'})
    else:
        # Hard delete if no assignments
        db.session.delete(subject)
        db.session.commit()
        return jsonify({'message': 'Subject deleted successfully'})

@subject_bp.route('/subjects/<int:subject_id>/assignments', methods=['GET'])
@login_required
def get_subject_assignments(subject_id):
    """Get all assignments for a specific subject."""
    current_user = get_current_user()
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    
    # Get query parameters for filtering
    student_id = request.args.get('student_id', type=int)
    status = request.args.get('status')
    limit = request.args.get('limit', type=int)
    
    from src.models import Assignment, Student
    query = Assignment.query.join(Student).filter(
        Assignment.subject_id == subject_id,
        Student.user_id == current_user.id
    )
    
    if student_id:
        query = query.filter(Assignment.student_id == student_id)
    if status:
        query = query.filter(Assignment.status == status)
    
    query = query.order_by(Assignment.due_date.desc())
    
    if limit:
        query = query.limit(limit)
    
    assignments = query.all()
    return jsonify([assignment.to_dict() for assignment in assignments])

@subject_bp.route('/subjects/<int:subject_id>/analytics', methods=['GET'])
@login_required
def get_subject_analytics(subject_id):
    """Get analytics for a specific subject."""
    current_user = get_current_user()
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    
    from src.models import Assignment, Grade, Student
    
    # Get all assignments for this subject
    assignments = db.session.query(Assignment).join(Student).filter(
        Assignment.subject_id == subject_id,
        Student.user_id == current_user.id
    ).all()
    
    # Get all grades for this subject
    grades = db.session.query(Grade, Assignment).join(
        Assignment, Grade.assignment_id == Assignment.id
    ).join(Student, Assignment.student_id == Student.id).filter(
        Assignment.subject_id == subject_id,
        Student.user_id == current_user.id
    ).all()
    
    # Calculate analytics
    total_assignments = len(assignments)
    graded_assignments = len(grades)
    
    if grades:
        average_grade = sum(float(grade.percentage) for grade, _ in grades if grade.percentage) / len(grades)
        grade_distribution = {}
        for grade, _ in grades:
            letter = grade.grade_letter
            if letter:
                grade_distribution[letter] = grade_distribution.get(letter, 0) + 1
    else:
        average_grade = 0
        grade_distribution = {}
    
    # Assignment status distribution
    status_distribution = {}
    for assignment in assignments:
        status = assignment.status
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    analytics_data = {
        'subject': subject.to_dict(),
        'total_assignments': total_assignments,
        'graded_assignments': graded_assignments,
        'average_grade': round(average_grade, 2) if average_grade else 0,
        'grade_distribution': grade_distribution,
        'status_distribution': status_distribution,
        'completion_rate': round((graded_assignments / total_assignments) * 100, 1) if total_assignments > 0 else 0
    }
    
    return jsonify(analytics_data)

