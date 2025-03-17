from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for, flash, request
from functools import wraps
import db
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Simple user class
class User:
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email
        self.is_authenticated = True

# Core authentication functions
def login_required(f):
    """Decorator to require login for a view."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def current_user():
    """Get the current logged-in user or None."""
    if 'user_id' in session:
        user_data = db.get_user_by_id(session['user_id'])
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['email'])
    return None

def is_authenticated():
    """Check if the user is authenticated."""
    is_auth = 'user_id' in session
    user_id = session.get('user_id')
    print(f"is_authenticated check: {is_auth}, user_id: {user_id}")
    
    if is_auth and user_id:
        # Verify this user actually exists
        user = db.get_user_by_id(user_id)
        if not user:
            print(f"User ID {user_id} not found in database")
            return False
    return is_auth

def login_user(username, password):
    """Authenticate and log in a user."""
    user = db.get_user_by_username(username)
    
    if not user:
        logger.debug(f"Login failed: User {username} not found")
        return False, "Invalid username or password"
    
    if not check_password_hash(user['password_hash'], password):
        logger.debug(f"Login failed: Invalid password for {username}")
        return False, "Invalid username or password"
    
    # Store user info in session
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    
    logger.debug(f"User logged in: {username} (ID: {user['id']})")
    return True, User(user['id'], user['username'], user['email'])

def logout_user():
    """Log out the current user."""
    logger.debug(f"User logged out: {session.get('username', 'Unknown')}")
    session.clear()

def register_user(username, email, password):
    """Register a new user."""
    # Check if username already exists
    if db.get_user_by_username(username):
        logger.debug(f"Registration failed: Username {username} already exists")
        return False, "Username already exists"
    
    # Check if email already exists
    if db.get_user_by_email(email):
        logger.debug(f"Registration failed: Email {email} already exists")
        return False, "Email already exists"
    
    # Hash the password and create user
    password_hash = generate_password_hash(password)
    
    try:
        # Create the user
        user_id = db.create_user(username, email, password_hash)
        logger.debug(f"User registered: {username} (ID: {user_id})")
        
        # Create default categories
        db.create_category("Work", user_id)
        db.create_category("Personal", user_id)
        logger.debug(f"Created default categories for user {user_id}")
        
        return True, user_id
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return False, "An error occurred during registration"