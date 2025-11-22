from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId
import re

class User:
    def __init__(self, db):
        self.collection = db.users
        
    def create_user(self, user_data):
        """Create a new user account"""
        try:
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'password', 'user_type']
            for field in required_fields:
                if field not in user_data or not user_data[field].strip():
                    return {'error': f'{field.replace("_", " ").title()} is required'}, 400
            
            # Validate email format
            if not self._is_valid_email(user_data['email']):
                return {'error': 'Invalid email format'}, 400
            
            # Check if email already exists
            if self.collection.find_one({'email': user_data['email'].lower()}):
                return {'error': 'Email already exists'}, 409
            
            # Validate password
            if len(user_data['password']) < 6:
                return {'error': 'Password must be at least 6 characters long'}, 400
            
            # Validate user type
            if user_data['user_type'] not in ['user', 'manager']:
                return {'error': 'Invalid user type. Must be "user" or "manager"'}, 400
            
            # Validate phone if provided
            if user_data.get('phone') and not self._is_valid_phone(user_data['phone']):
                return {'error': 'Invalid phone number format'}, 400
            
            # Create user document
            user_doc = {
                'first_name': user_data['first_name'].strip().title(),
                'last_name': user_data['last_name'].strip().title(),
                'email': user_data['email'].lower().strip(),
                'password_hash': generate_password_hash(user_data['password']),
                'user_type': user_data['user_type'],
                'phone': user_data.get('phone', '').strip(),
                'is_active': True,
                'email_verified': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'last_login': None,
                'profile': {
                    'avatar_url': None,
                    'bio': '',
                    'location': '',
                    'website': ''
                },
                'preferences': {
                    'email_notifications': True,
                    'sms_notifications': False,
                    'theme': 'light'
                }
            }
            
            # Add manager-specific fields
            if user_data['user_type'] == 'manager':
                user_doc['manager_info'] = {
                    'department': '',
                    'team_size': 0,
                    'permissions': ['read', 'write'],
                    'approval_level': 1
                }
            
            # Insert user into database
            result = self.collection.insert_one(user_doc)
            
            if result.inserted_id:
                # Return user data without password
                user_doc.pop('password_hash', None)
                user_doc['_id'] = str(result.inserted_id)
                return {
                    'message': 'User created successfully',
                    'user': user_doc
                }, 201
            else:
                return {'error': 'Failed to create user'}, 500
                
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return {'error': 'Internal server error'}, 500
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            user = self.collection.find_one({'email': email.lower()})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            print(f"Error getting user by email: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                user.pop('password_hash', None)  # Remove password hash from response
            return user
        except Exception as e:
            print(f"Error getting user by ID: {str(e)}")
            return None
    
    def verify_password(self, email, password):
        """Verify user password"""
        try:
            user = self.collection.find_one({'email': email.lower()})
            if user and check_password_hash(user['password_hash'], password):
                return True
            return False
        except Exception as e:
            print(f"Error verifying password: {str(e)}")
            return False
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        try:
            self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'last_login': datetime.utcnow(), 'updated_at': datetime.utcnow()}}
            )
        except Exception as e:
            print(f"Error updating last login: {str(e)}")
    
    def get_all_users(self, user_type=None, skip=0, limit=50):
        """Get all users with optional filtering"""
        try:
            query = {}
            if user_type:
                query['user_type'] = user_type
            
            users = list(self.collection.find(query, {'password_hash': 0}).skip(skip).limit(limit))
            for user in users:
                user['_id'] = str(user['_id'])
            
            total_count = self.collection.count_documents(query)
            
            return {
                'users': users,
                'total': total_count,
                'skip': skip,
                'limit': limit
            }
        except Exception as e:
            print(f"Error getting all users: {str(e)}")
            return {'users': [], 'total': 0, 'skip': skip, 'limit': limit}
    
    def update_user(self, user_id, update_data):
        """Update user information"""
        try:
            # Remove sensitive fields that shouldn't be updated directly
            update_data.pop('password_hash', None)
            update_data.pop('_id', None)
            update_data.pop('created_at', None)
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            return False
    
    def delete_user(self, user_id):
        """Soft delete user (set is_active to False)"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            return False
    
    def _is_valid_email(self, email):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.match(email_pattern, email) is not None
    
    def _is_valid_phone(self, phone):
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it's exactly 10 digits
        return len(digits_only) == 10
    
    # Add this method to your User model class in models/user.py

def get_user_by_id(self, user_id):
    """Get user by ID"""
    try:
        # Handle both string and ObjectId inputs
        if isinstance(user_id, str):
            object_id = ObjectId(user_id)
        else:
            object_id = user_id
            
        user = self.collection.find_one({'_id': object_id})
        if user:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
            user.pop('password_hash', None)  # Remove password hash from response
        return user
    except Exception as e:
        print(f"Error getting user by ID: {str(e)}")
        return None

def update_last_login(self, user_id):
    """Update user's last login timestamp"""
    try:
        # Handle both string and ObjectId inputs
        if isinstance(user_id, str):
            object_id = ObjectId(user_id)
        else:
            object_id = user_id
            
        self.collection.update_one(
            {'_id': object_id},
            {'$set': {'last_login': datetime.utcnow(), 'updated_at': datetime.utcnow()}}
        )
    except Exception as e:
        print(f"Error updating last login: {str(e)}")

def update_user(self, user_id, update_data):
    """Update user information"""
    try:
        # Handle both string and ObjectId inputs
        if isinstance(user_id, str):
            object_id = ObjectId(user_id)
        else:
            object_id = user_id
            
        # Remove sensitive fields that shouldn't be updated directly
        update_data.pop('password_hash', None)
        update_data.pop('_id', None)
        update_data.pop('created_at', None)
        
        update_data['updated_at'] = datetime.utcnow()
        
        result = self.collection.update_one(
            {'_id': object_id},
            {'$set': update_data}
        )
        
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating user: {str(e)}")
        return False

def delete_user(self, user_id):
    """Soft delete user (set is_active to False)"""
    try:
        # Handle both string and ObjectId inputs
        if isinstance(user_id, str):
            object_id = ObjectId(user_id)
        else:
            object_id = user_id
            
        result = self.collection.update_one(
            {'_id': object_id},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return False