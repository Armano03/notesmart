import os
from flask import Flask, g, session
import db
import auth
from routes import register_routes
from config import Config
from datetime import datetime

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Custom template filters
    @app.template_filter('datetime')
    def format_datetime(value):
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        
        if isinstance(value, datetime):
            return value.strftime('%b %d, %Y at %I:%M %p')
        return value
    
    @app.template_filter('nl2br')
    def nl2br(value):
        if value:
            return value.replace('\n', '<br>')
        return ''
    
    # Initialize database at application startup
    with app.app_context():
        try:
            db.init_db()
        except Exception as e:
            app.logger.error(f"Failed to initialize database: {str(e)}")
    
    # Register database close function
    @app.teardown_appcontext
    def close_connection(exception):
        db.close_db()
    
    # Register all routes
    register_routes(app)
    
    # Context processor to make current_user available in templates
    @app.context_processor
    def inject_user():
        return {'current_user': auth.current_user()}
    
    # This loads the user ID from session
    @app.before_request
    def load_user():
        if 'user_id' in session:
            g.user_id = session['user_id']
        else:
            g.user_id = None
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )