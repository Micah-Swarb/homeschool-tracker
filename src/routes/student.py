from flask import Blueprint, jsonify, request
from src.models import db, Student
from src.routes.user import login_required, get_current_user
from datetime import datetime
from src.utils.request_utils import get_json_data

student_bp = Blueprint('student', __name__)

@student_bp.route('/students', methods=['GET'])
@login_required
def get_students():
    """Get all students for the current user."""
    current_user = get_current_user()
    students = Student.query.filter_by(user_id=current_user.id, active=True).all()
    return jsonify([student.to_dict() for student in students])

@student_bp.route('/students', methods=['POST'])
@login_required
def create_student():
    """Create a new student."""
    current_user = get_current_user()
    data, error, status = get_json_data(['first_name', 'last_name', 'date_of_birth', 'grade_level'])
    if error:
        return error, status
    
    # Parse date of birth
    try:
        dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Check if student_id is unique (if provided)
    if data.get('student_id'):
        existing_student = Student.query.filter_by(student_id=data['student_id']).first()
        if existing_student:
            return jsonify({'error': 'Student ID already exists'}), 400
    
    # Create new student
    student = Student(
        user_id=current_user.id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        date_of_birth=dob,
        grade_level=data['grade_level'],
        student_id=data.get('student_id'),
        profile_picture=data.get('profile_picture'),
        notes=data.get('notes')
    )
    
    db.session.add(student)
    db.session.commit()
    
    return jsonify({
        'message': 'Student created successfully',
        'student': student.to_dict()
    }), 201

@student_bp.route('/students/<int:student_id>', methods=['GET'])
@login_required
def get_student(student_id):
    """Get specific student by ID."""
    current_user = get_current_user()
    student = Student.query.filter_by(id=student_id, user_id=current_user.id).first_or_404()
    return jsonify(student.to_dict())

@student_bp.route('/students/<int:student_id>', methods=['PUT'])
@login_required
def update_student(student_id):
    """Update student information."""
    current_user = get_current_user()
    student = Student.query.filter_by(id=student_id, user_id=current_user.id).first_or_404()
    data, error, status = get_json_data()
    if error:
        return error, status
    
    # Update allowed fields
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'date_of_birth' in data:
        try:
            student.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    if 'grade_level' in data:
        student.grade_level = data['grade_level']
    if 'student_id' in data:
        # Check if student_id is unique
        if data['student_id'] != student.student_id:
            existing_student = Student.query.filter_by(student_id=data['student_id']).first()
            if existing_student:
                return jsonify({'error': 'Student ID already exists'}), 400
        student.student_id = data['student_id']
    if 'profile_picture' in data:
        student.profile_picture = data['profile_picture']
    if 'notes' in data:
        student.notes = data['notes']
    if 'active' in data:
        student.active = data['active']
    
    student.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(student.to_dict())

@student_bp.route('/students/<int:student_id>', methods=['DELETE'])
@login_required
def delete_student(student_id):
    """Delete (deactivate) student."""
    current_user = get_current_user()
    student = Student.query.filter_by(id=student_id, user_id=current_user.id).first_or_404()
    
    # Soft delete - just mark as inactive
    student.active = False
    student.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Student deactivated successfully'})

@student_bp.route('/students/<int:student_id>/dashboard', methods=['GET'])
@login_required
def get_student_dashboard(student_id):
    """Get dashboard data for a specific student."""
    current_user = get_current_user()
    student = Student.query.filter_by(id=student_id, user_id=current_user.id).first_or_404()
    
    # Get recent assignments
    from src.models import Assignment
    recent_assignments = Assignment.query.filter_by(student_id=student_id).order_by(
        Assignment.due_date.desc()
    ).limit(5).all()
    
    # Get attendance summary for last 30 days
    from src.models.attendance import Attendance
    attendance_summary = Attendance.get_attendance_summary(student_id)
    
    # Get current goals
    from src.models import Goal
    active_goals = Goal.query.filter_by(student_id=student_id, status='active').all()
    
    dashboard_data = {
        'student': student.to_dict(),
        'recent_assignments': [assignment.to_dict() for assignment in recent_assignments],
        'attendance_summary': attendance_summary,
        'active_goals': [goal.to_dict() for goal in active_goals],
        'current_gpa': student.get_current_gpa(),
        'attendance_rate': student.get_attendance_rate()
    }
    
    return jsonify(dashboard_data)

@student_bp.route('/students/<int:student_id>/assignments', methods=['GET'])
@login_required
def get_student_assignments(student_id):
    """Get all assignments for a specific student."""
    current_user = get_current_user()
    student = Student.query.filter_by(id=student_id, user_id=current_user.id).first_or_404()
    
    # Get query parameters for filtering
    status = request.args.get('status')
    subject_id = request.args.get('subject_id')
    limit = request.args.get('limit', type=int)
    
    from src.models import Assignment
    query = Assignment.query.filter_by(student_id=student_id)
    
    if status:
        query = query.filter_by(status=status)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    
    query = query.order_by(Assignment.due_date.desc())
    
    if limit:
        query = query.limit(limit)
    
    assignments = query.all()
    return jsonify([assignment.to_dict() for assignment in assignments])

@student_bp.route('/students/<int:student_id>/grades', methods=['GET'])
@login_required
def get_student_grades(student_id):
    """Get all grades for a specific student."""
    current_user = get_current_user()
    student = Student.query.filter_by(id=student_id, user_id=current_user.id).first_or_404()
    
    from src.models import Assignment, Grade
    
    # Get all graded assignments for this student
    graded_assignments = db.session.query(Assignment, Grade).join(
        Grade, Assignment.id == Grade.assignment_id
    ).filter(Assignment.student_id == student_id).order_by(
        Grade.graded_at.desc()
    ).all()
    
    grades_data = []
    for assignment, grade in graded_assignments:
        grade_dict = grade.to_dict()
        grade_dict['assignment'] = {
            'id': assignment.id,
            'title': assignment.title,
            'subject_id': assignment.subject_id,
            'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
            'points_total': assignment.points_total
        }
        grades_data.append(grade_dict)
    
    return jsonify(grades_data)

@student_bp.route('/students/<int:student_id>/progress', methods=['GET'])
@login_required
def get_student_progress(student_id):
    """Get progress analytics for a specific student."""
    current_user = get_current_user()
    student = Student.query.filter_by(id=student_id, user_id=current_user.id).first_or_404()
    
    from src.models import Assignment, Grade, Subject
    
    # Get grade trends over time
    grade_trends = db.session.query(Grade, Assignment).join(
        Assignment, Grade.assignment_id == Assignment.id
    ).filter(Assignment.student_id == student_id).order_by(
        Grade.graded_at.asc()
    ).all()
    
    # Get subject averages
    subject_averages = db.session.query(
        Subject.name,
        Subject.color,
        db.func.avg(Grade.percentage).label('average')
    ).join(Assignment, Subject.id == Assignment.subject_id).join(
        Grade, Assignment.id == Grade.assignment_id
    ).filter(Assignment.student_id == student_id).group_by(Subject.id).all()
    
    progress_data = {
        'student': student.to_dict(),
        'grade_trends': [
            {
                'date': grade.graded_at.isoformat() if grade.graded_at else None,
                'percentage': float(grade.percentage) if grade.percentage else None,
                'assignment_title': assignment.title
            }
            for grade, assignment in grade_trends
        ],
        'subject_averages': [
            {
                'subject': name,
                'color': color,
                'average': round(float(average), 2) if average else 0
            }
            for name, color, average in subject_averages
        ],
        'overall_gpa': student.get_current_gpa(),
        'total_assignments': len(student.assignments),
        'completed_assignments': len([a for a in student.assignments if a.status == 'graded'])
    }
    
    return jsonify(progress_data)

