from flask import Blueprint, jsonify, request
from src.models import db, Assignment, Grade, Student, Subject, Submission
from src.routes.user import login_required, get_current_user
from datetime import datetime, date
from src.utils.request_utils import get_json_data

assignment_bp = Blueprint('assignment', __name__)

@assignment_bp.route('/assignments', methods=['GET'])
@login_required
def get_assignments():
    """Get all assignments for the current user's students."""
    current_user = get_current_user()
    
    # Get query parameters for filtering
    student_id = request.args.get('student_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    status = request.args.get('status')
    limit = request.args.get('limit', type=int)
    
    # Base query - only assignments for current user's students
    query = db.session.query(Assignment).join(Student).filter(Student.user_id == current_user.id)
    
    # Apply filters
    if student_id:
        query = query.filter(Assignment.student_id == student_id)
    if subject_id:
        query = query.filter(Assignment.subject_id == subject_id)
    if status:
        query = query.filter(Assignment.status == status)
    
    # Order by due date
    query = query.order_by(Assignment.due_date.desc())
    
    if limit:
        query = query.limit(limit)
    
    assignments = query.all()
    return jsonify([assignment.to_dict() for assignment in assignments])

@assignment_bp.route('/assignments', methods=['POST'])
@login_required
def create_assignment():
    """Create a new assignment."""
    current_user = get_current_user()
    data, error, status = get_json_data(['student_id', 'title'])
    if error:
        return error, status
    
    # Verify student belongs to current user
    student = Student.query.filter_by(id=data['student_id'], user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student not found or access denied'}), 404
    
    # Verify subject belongs to current user (if provided)
    if data.get('subject_id'):
        subject = Subject.query.filter_by(id=data['subject_id'], user_id=current_user.id).first()
        if not subject:
            return jsonify({'error': 'Subject not found or access denied'}), 404
    
    # Parse due date if provided
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Create new assignment
    assignment = Assignment(
        student_id=data['student_id'],
        subject_id=data.get('subject_id'),
        title=data['title'],
        description=data.get('description'),
        instructions=data.get('instructions'),
        due_date=due_date,
        estimated_duration=data.get('estimated_duration'),
        points_total=data.get('points_total', 100),
        assignment_type=data.get('assignment_type', 'homework'),
        difficulty_level=data.get('difficulty_level', 'medium'),
        priority=data.get('priority', 'normal')
    )
    
    # Set tags and resources if provided
    if data.get('tags'):
        assignment.set_tags(data['tags'])
    if data.get('resources'):
        assignment.set_resources(data['resources'])
    
    db.session.add(assignment)
    db.session.commit()
    
    return jsonify({
        'message': 'Assignment created successfully',
        'assignment': assignment.to_dict()
    }), 201

@assignment_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@login_required
def get_assignment(assignment_id):
    """Get specific assignment by ID."""
    current_user = get_current_user()
    
    # Verify assignment belongs to current user's student
    assignment = db.session.query(Assignment).join(Student).filter(
        Assignment.id == assignment_id,
        Student.user_id == current_user.id
    ).first_or_404()
    
    return jsonify(assignment.to_dict())

@assignment_bp.route('/assignments/<int:assignment_id>', methods=['PUT'])
@login_required
def update_assignment(assignment_id):
    """Update assignment information."""
    current_user = get_current_user()
    
    # Verify assignment belongs to current user's student
    assignment = db.session.query(Assignment).join(Student).filter(
        Assignment.id == assignment_id,
        Student.user_id == current_user.id
    ).first_or_404()
    
    data, error, status = get_json_data()
    if error:
        return error, status
    
    # Update allowed fields
    if 'title' in data:
        assignment.title = data['title']
    if 'description' in data:
        assignment.description = data['description']
    if 'instructions' in data:
        assignment.instructions = data['instructions']
    if 'due_date' in data:
        if data['due_date']:
            try:
                assignment.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        else:
            assignment.due_date = None
    if 'estimated_duration' in data:
        assignment.estimated_duration = data['estimated_duration']
    if 'points_total' in data:
        assignment.points_total = data['points_total']
    if 'assignment_type' in data:
        assignment.assignment_type = data['assignment_type']
    if 'difficulty_level' in data:
        assignment.difficulty_level = data['difficulty_level']
    if 'status' in data:
        assignment.status = data['status']
    if 'priority' in data:
        assignment.priority = data['priority']
    if 'tags' in data:
        assignment.set_tags(data['tags'])
    if 'resources' in data:
        assignment.set_resources(data['resources'])
    
    assignment.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(assignment.to_dict())

@assignment_bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
@login_required
def delete_assignment(assignment_id):
    """Delete assignment."""
    current_user = get_current_user()
    
    # Verify assignment belongs to current user's student
    assignment = db.session.query(Assignment).join(Student).filter(
        Assignment.id == assignment_id,
        Student.user_id == current_user.id
    ).first_or_404()
    
    db.session.delete(assignment)
    db.session.commit()
    
    return jsonify({'message': 'Assignment deleted successfully'})

# Grade management routes
@assignment_bp.route('/assignments/<int:assignment_id>/grade', methods=['POST'])
@login_required
def grade_assignment(assignment_id):
    """Grade an assignment."""
    current_user = get_current_user()
    
    # Verify assignment belongs to current user's student
    assignment = db.session.query(Assignment).join(Student).filter(
        Assignment.id == assignment_id,
        Student.user_id == current_user.id
    ).first_or_404()
    
    data, error, status = get_json_data(['points_earned'])
    if error:
        return error, status
    
    points_earned = data['points_earned']
    if points_earned < 0 or points_earned > assignment.points_total:
        return jsonify({'error': f'Points earned must be between 0 and {assignment.points_total}'}), 400
    
    # Check if assignment is already graded
    if assignment.grade:
        # Update existing grade
        grade = assignment.grade
        grade.set_grade(points_earned, assignment.points_total, current_user.id, data.get('feedback'))
        if data.get('rubric_scores'):
            grade.set_rubric_scores(data['rubric_scores'])
    else:
        # Create new grade
        grade = Grade()
        grade.assignment_id = assignment_id
        grade.set_grade(points_earned, assignment.points_total, current_user.id, data.get('feedback'))
        if data.get('rubric_scores'):
            grade.set_rubric_scores(data['rubric_scores'])
        db.session.add(grade)
    
    # Update assignment status
    assignment.status = 'graded'
    assignment.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Assignment graded successfully',
        'grade': grade.to_dict(),
        'assignment': assignment.to_dict()
    })

@assignment_bp.route('/assignments/<int:assignment_id>/grade', methods=['GET'])
@login_required
def get_assignment_grade(assignment_id):
    """Get grade for an assignment."""
    current_user = get_current_user()
    
    # Verify assignment belongs to current user's student
    assignment = db.session.query(Assignment).join(Student).filter(
        Assignment.id == assignment_id,
        Student.user_id == current_user.id
    ).first_or_404()
    
    if not assignment.grade:
        return jsonify({'error': 'Assignment not graded yet'}), 404
    
    return jsonify(assignment.grade.to_dict())

@assignment_bp.route('/assignments/<int:assignment_id>/grade', methods=['PUT'])
@login_required
def update_assignment_grade(assignment_id):
    """Update grade for an assignment."""
    current_user = get_current_user()
    
    # Verify assignment belongs to current user's student
    assignment = db.session.query(Assignment).join(Student).filter(
        Assignment.id == assignment_id,
        Student.user_id == current_user.id
    ).first_or_404()
    
    if not assignment.grade:
        return jsonify({'error': 'Assignment not graded yet'}), 404
    
    data, error, status = get_json_data()
    if error:
        return error, status
    grade = assignment.grade
    
    # Update grade fields
    if 'points_earned' in data:
        points_earned = data['points_earned']
        if points_earned < 0 or points_earned > assignment.points_total:
            return jsonify({'error': f'Points earned must be between 0 and {assignment.points_total}'}), 400
        grade.set_grade(points_earned, assignment.points_total, current_user.id, grade.feedback)
    
    if 'feedback' in data:
        grade.feedback = data['feedback']
    
    if 'rubric_scores' in data:
        grade.set_rubric_scores(data['rubric_scores'])
    
    grade.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(grade.to_dict())

@assignment_bp.route('/assignments/<int:assignment_id>/grade', methods=['DELETE'])
@login_required
def delete_assignment_grade(assignment_id):
    """Delete grade for an assignment."""
    current_user = get_current_user()
    
    # Verify assignment belongs to current user's student
    assignment = db.session.query(Assignment).join(Student).filter(
        Assignment.id == assignment_id,
        Student.user_id == current_user.id
    ).first_or_404()
    
    if not assignment.grade:
        return jsonify({'error': 'Assignment not graded yet'}), 404
    
    db.session.delete(assignment.grade)
    assignment.status = 'submitted' if assignment.submissions else 'assigned'
    assignment.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Grade deleted successfully'})

# Submission routes
@assignment_bp.route('/assignments/<int:assignment_id>/submissions', methods=['GET'])
@login_required
def get_assignment_submissions(assignment_id):
    """Get all submissions for an assignment."""
    current_user = get_current_user()
    
    # Verify assignment belongs to current user's student
    assignment = db.session.query(Assignment).join(Student).filter(
        Assignment.id == assignment_id,
        Student.user_id == current_user.id
    ).first_or_404()
    
    submissions = Submission.query.filter_by(assignment_id=assignment_id).order_by(
        Submission.submitted_at.desc()
    ).all()
    
    return jsonify([submission.to_dict() for submission in submissions])

# Dashboard and analytics routes
@assignment_bp.route('/assignments/dashboard', methods=['GET'])
@login_required
def get_assignments_dashboard():
    """Get assignment dashboard data."""
    current_user = get_current_user()
    
    # Get assignments that need attention
    overdue_assignments = db.session.query(Assignment).join(Student).filter(
        Student.user_id == current_user.id,
        Assignment.due_date < date.today(),
        Assignment.status.in_(['assigned', 'in_progress'])
    ).all()
    
    # Get assignments due soon (next 7 days)
    from datetime import timedelta
    due_soon = db.session.query(Assignment).join(Student).filter(
        Student.user_id == current_user.id,
        Assignment.due_date >= date.today(),
        Assignment.due_date <= date.today() + timedelta(days=7),
        Assignment.status.in_(['assigned', 'in_progress'])
    ).all()
    
    # Get assignments needing grading
    need_grading = db.session.query(Assignment).join(Student).filter(
        Student.user_id == current_user.id,
        Assignment.status == 'submitted'
    ).all()
    
    # Get recent activity
    recent_assignments = db.session.query(Assignment).join(Student).filter(
        Student.user_id == current_user.id
    ).order_by(Assignment.updated_at.desc()).limit(10).all()
    
    dashboard_data = {
        'overdue_assignments': [assignment.to_dict() for assignment in overdue_assignments],
        'due_soon': [assignment.to_dict() for assignment in due_soon],
        'need_grading': [assignment.to_dict() for assignment in need_grading],
        'recent_activity': [assignment.to_dict() for assignment in recent_assignments],
        'stats': {
            'total_assignments': len(current_user.students[0].assignments) if current_user.students else 0,
            'overdue_count': len(overdue_assignments),
            'due_soon_count': len(due_soon),
            'need_grading_count': len(need_grading)
        }
    }
    
    return jsonify(dashboard_data)

