import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the application."""
    # Secret key for session security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development-key-change-in-production'
    
    # MySQL Database configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'notesmart_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_password')
    DB_NAME = os.environ.get('DB_NAME', 'notesmart')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # Debug mode (should be False in production)
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', 't', '1')
    
    # Host and port settings for the development server
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))