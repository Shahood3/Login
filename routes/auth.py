from flask import Blueprint, request, jsonify, session
from flask import current_app
from models.user import User
import jwt
from datetime import datetime, timedelta
from functools import wraps
from bson import ObjectId

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # Get user from database
            from flask import g
            user_model = User(g.mongo.db)
            current_user = user_model.get_user_by_id(current_user_id)
            
            if not current_user or not current_user.get('is_active'):
                return jsonify({'error': 'Invalid or inactive user'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401
        except Exception as e:
            print(f"Token validation error: {str(e)}")
            return jsonify({'error': 'Token validation failed'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Debug: Print received data (remove passwords in production!)
        print(f"Registration attempt - Data received: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check for required fields
        required_fields = ['first_name', 'last_name', 'email', 'password', 'user_type']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Initialize user model
        from flask import g
        user_model = User(g.mongo.db)
        
        # Create user
        result, status_code = user_model.create_user(data)
        
        print(f"Registration result: {result}, Status: {status_code}")
        
        return jsonify(result), status_code
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        print(f"Login attempt - Data keys: {data.keys() if data else 'None'}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt for email: {email}")
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if SECRET_KEY is available
        if not current_app.config.get('SECRET_KEY'):
            print("ERROR: SECRET_KEY not found in app config")
            return jsonify({'error': 'Server configuration error'}), 500
        
        # Initialize user model
        from flask import g
        user_model = User(g.mongo.db)
        
        # Check if user exists first
        user = user_model.get_user_by_email(email)
        if not user:
            print(f"User not found for email: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        print(f"User found: {user.get('email')}, Active: {user.get('is_active')}")
        
        # Verify credentials
        if not user_model.verify_password(email, password):
            print(f"Password verification failed for: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        print(f"Password verified successfully for: {email}")
        
        if not user.get('is_active'):
            return jsonify({'error': 'Account is inactive'}), 401
        
        # Update last login
        user_model.update_last_login(user['_id'])
        
        # Convert ObjectId to string for JWT token
        user_id_str = str(user['_id']) if isinstance(user['_id'], ObjectId) else user['_id']
        
        # Generate JWT token with proper error handling
        token_payload = {
            'user_id': user_id_str,
            'email': user['email'],
            'user_type': user['user_type'],
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        
        try:
            token = jwt.encode(
                token_payload, 
                current_app.config['SECRET_KEY'], 
                algorithm='HS256'
            )
            
            # Handle both string and bytes return types
            if isinstance(token, bytes):
                token = token.decode('utf-8')
                
        except Exception as jwt_error:
            print(f"JWT encoding error: {str(jwt_error)}")
            return jsonify({'error': 'Token generation failed'}), 500
        
        # Remove sensitive data from user object
        user_response = dict(user)
        user_response.pop('password_hash', None)
        user_response['_id'] = user_id_str
        
        print(f"Login successful for: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user_response
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Logout user (client-side token removal)"""
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile"""
    return jsonify({
        'message': 'Profile retrieved successfully',
        'user': current_user
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update current user profile"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        from flask import g
        user_model = User(g.mongo.db)
        
        if user_model.update_user(current_user['_id'], data):
            updated_user = user_model.get_user_by_id(current_user['_id'])
            return jsonify({
                'message': 'Profile updated successfully',
                'user': updated_user
            }), 200
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
            
    except Exception as e:
        print(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Profile update failed'}), 500

@auth_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    """Get all users (manager only)"""
    try:
        if current_user.get('user_type') != 'manager':
            return jsonify({'error': 'Access denied. Manager role required.'}), 403
        
        user_type = request.args.get('user_type')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 50))
        
        from flask import g
        user_model = User(g.mongo.db)
        result = user_model.get_all_users(user_type, skip, limit)
        
        return jsonify({
            'message': 'Users retrieved successfully',
            **result
        }), 200
        
    except Exception as e:
        print(f"Get users error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve users'}), 500

@auth_bp.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user_by_id(current_user, user_id):
    """Get user by ID (manager only or own profile)"""
    try:
        if current_user.get('user_type') != 'manager' and str(current_user['_id']) != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        from flask import g
        user_model = User(g.mongo.db)
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'message': 'User retrieved successfully',
            'user': user
        }), 200
        
    except Exception as e:
        print(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve user'}), 500

@auth_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    """Delete user (manager only)"""
    try:
        if current_user.get('user_type') != 'manager':
            return jsonify({'error': 'Access denied. Manager role required.'}), 403
        
        if str(current_user['_id']) == user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        from flask import g
        user_model = User(g.mongo.db)
        
        if user_model.delete_user(user_id):
            return jsonify({'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete user'}), 500
            
    except Exception as e:
        print(f"Delete user error: {str(e)}")
        return jsonify({'error': 'Failed to delete user'}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify JWT token validity"""
    try:
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format', 'valid': False}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing', 'valid': False}), 401
        
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        
        from flask import g
        user_model = User(g.mongo.db)
        user = user_model.get_user_by_id(data['user_id'])
        
        if not user or not user.get('is_active'):
            return jsonify({'error': 'Invalid or inactive user', 'valid': False}), 401
        
        return jsonify({
            'message': 'Token is valid',
            'valid': True,
            'user': user
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired', 'valid': False}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token is invalid', 'valid': False}), 401
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return jsonify({'error': 'Token validation failed', 'valid': False}), 401