from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash
from src.models import db, User
from functools import wraps

user_bp = Blueprint('user', __name__)

def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the current logged-in user."""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@user_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.json
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        timezone=data.get('timezone', 'UTC')
    )
    user.set_password(data['password'])
    
    if data.get('preferences'):
        user.set_preferences(data['preferences'])
    
    db.session.add(user)
    db.session.commit()
    
    # Log in the user
    session['user_id'] = user.id
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@user_bp.route('/auth/login', methods=['POST'])
def login():
    """Login user."""
    data = request.json
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Log in the user
    session['user_id'] = user.id
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    })

@user_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user."""
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

@user_bp.route('/auth/me', methods=['GET'])
@login_required
def get_current_user_info():
    """Get current user information."""
    user = get_current_user()
    return jsonify(user.to_dict())

@user_bp.route('/auth/me', methods=['PUT'])
@login_required
def update_current_user():
    """Update current user information."""
    user = get_current_user()
    data = request.json
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        # Check if email is already taken by another user
        existing_user = User.query.filter(User.email == data['email'], User.id != user.id).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']
    if 'timezone' in data:
        user.timezone = data['timezone']
    if 'preferences' in data:
        user.set_preferences(data['preferences'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    user = get_current_user()
    data = request.json
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    if len(data['new_password']) < 6:
        return jsonify({'error': 'New password must be at least 6 characters long'}), 400
    
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'})

# Admin routes (for development/testing)
@user_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    """Get all users (admin only)."""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get specific user by ID."""
    current_user = get_current_user()
    
    # Users can only view their own profile
    if current_user.id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Delete user account."""
    current_user = get_current_user()
    
    # Users can only delete their own account
    if current_user.id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    # Clear session
    session.pop('user_id', None)
    
    return jsonify({'message': 'Account deleted successfully'})
