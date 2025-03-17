import pymysql
from datetime import datetime
from flask import g, current_app
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_db():
    """Get a database connection."""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with the required tables."""
    try:
        # First connect without database to check if it exists
        conn = pymysql.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            charset='utf8mb4'
        )
        with conn.cursor() as cursor:
            # Check if database exists, create if not
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {current_app.config['DB_NAME']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()
        
        # Now connect with the database and initialize tables
        db = get_db()
        with db.cursor() as cursor:
            # Create User table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(64) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                )
            """)
            
            # Create Category table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS category (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(64) NOT NULL,
                    user_id INT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                    UNIQUE (user_id, name)
                )
            """)
            
            # Create Note table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS note (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    content TEXT,
                    created_date DATETIME NOT NULL,
                    updated_date DATETIME NOT NULL,
                    is_todo TINYINT(1) NOT NULL DEFAULT 0,
                    completed TINYINT(1) NOT NULL DEFAULT 0,
                    importance VARCHAR(20) DEFAULT 'normal',
                    color VARCHAR(20) DEFAULT 'blue',
                    category_id INT,
                    user_id INT NOT NULL,
                    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL,
                    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for performance (safely)
            try:
                cursor.execute("CREATE INDEX idx_note_user_id ON note(user_id)")
            except Exception as e:
                if "Duplicate key name" not in str(e):
                    logger.warning(f"Could not create index idx_note_user_id: {str(e)}")
                    
            try:
                cursor.execute("CREATE INDEX idx_note_category_id ON note(category_id)")
            except Exception as e:
                if "Duplicate key name" not in str(e):
                    logger.warning(f"Could not create index idx_note_category_id: {str(e)}")
                    
            try:
                cursor.execute("CREATE INDEX idx_note_is_todo ON note(is_todo)")
            except Exception as e:
                if "Duplicate key name" not in str(e):
                    logger.warning(f"Could not create index idx_note_is_todo: {str(e)}")
            
        db.commit()
        logger.debug("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

# User-related functions
def get_user_by_id(user_id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM user WHERE id = %s', (user_id,))
        user = cursor.fetchone()
    return user

def get_user_by_username(username):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        user = cursor.fetchone()
    return user

def get_user_by_email(email):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cursor.fetchone()
    return user

def create_user(username, email, password_hash):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'INSERT INTO user (username, email, password_hash) VALUES (%s, %s, %s)',
                (username, email, password_hash)
            )
            user_id = cursor.lastrowid
        db.commit()
        return user_id
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise

# Category-related functions
def get_categories_by_user(user_id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM category WHERE user_id = %s ORDER BY name', (user_id,))
        categories = cursor.fetchall()
    return categories

def get_category_by_id(category_id, user_id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            'SELECT * FROM category WHERE id = %s AND user_id = %s', 
            (category_id, user_id)
        )
        category = cursor.fetchone()
    return category

def get_category_by_name(name, user_id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            'SELECT * FROM category WHERE name = %s AND user_id = %s', 
            (name, user_id)
        )
        category = cursor.fetchone()
    return category

def create_category(name, user_id):
    # Check if category already exists
    existing = get_category_by_name(name, user_id)
    if existing:
        return existing['id']
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'INSERT INTO category (name, user_id) VALUES (%s, %s)',
                (name, user_id)
            )
            category_id = cursor.lastrowid
        db.commit()
        return category_id
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating category: {str(e)}")
        raise

def delete_category(category_id, user_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute('DELETE FROM category WHERE id = %s AND user_id = %s', (category_id, user_id))
            affected_rows = cursor.rowcount
        db.commit()
        return affected_rows
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting category: {str(e)}")
        raise

# Note-related functions
def get_notes_by_user(user_id, category_id=None, search=None):
    db = get_db()
    query = '''
        SELECT n.*, c.name as category_name 
        FROM note n 
        LEFT JOIN category c ON n.category_id = c.id 
        WHERE n.user_id = %s
    '''
    params = [user_id]
    
    if category_id:
        query += ' AND n.category_id = %s'
        params.append(category_id)
    
    if search:
        query += ' AND (n.title LIKE %s OR n.content LIKE %s)'
        search_param = f'%{search}%'
        params.append(search_param)
        params.append(search_param)
    
    query += ' ORDER BY n.updated_date DESC'
    
    with db.cursor() as cursor:
        cursor.execute(query, params)
        notes = cursor.fetchall()
    
    return notes

def get_todos_by_user(user_id, completed=None):
    db = get_db()
    query = '''
        SELECT n.*, c.name as category_name 
        FROM note n 
        LEFT JOIN category c ON n.category_id = c.id 
        WHERE n.user_id = %s AND n.is_todo = 1
    '''
    params = [user_id]
    
    if completed is not None:
        query += ' AND n.completed = %s'
        params.append(1 if completed else 0)
    
    query += ' ORDER BY n.importance DESC, n.updated_date DESC'
    
    with db.cursor() as cursor:
        cursor.execute(query, params)
        todos = cursor.fetchall()
    
    return todos

def get_note_by_id(note_id, user_id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            '''SELECT n.*, c.name as category_name 
               FROM note n 
               LEFT JOIN category c ON n.category_id = c.id 
               WHERE n.id = %s AND n.user_id = %s''', 
            (note_id, user_id)
        )
        note = cursor.fetchone()
    return note

def create_note(title, content, category_id, is_todo, importance, color, user_id):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO note 
                   (title, content, created_date, updated_date, is_todo, completed, importance, color, category_id, user_id) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (title, content, now, now, 1 if is_todo else 0, 0, importance, color, category_id, user_id)
            )
            note_id = cursor.lastrowid
        db.commit()
        return note_id
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating note: {str(e)}")
        raise

def update_note(note_id, user_id, updates):
    if not updates:
        return 0
    
    # Add updated_date
    updates['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Build the SET clause and parameters
    set_clauses = []
    params = []
    
    for key, value in updates.items():
        set_clauses.append(f"{key} = %s")
        params.append(value)
    
    # Add WHERE clause parameters
    params.extend([note_id, user_id])
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            query = f'''UPDATE note 
                      SET {", ".join(set_clauses)} 
                      WHERE id = %s AND user_id = %s'''
            cursor.execute(query, params)
            affected_rows = cursor.rowcount
        db.commit()
        return affected_rows
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating note: {str(e)}")
        raise

def delete_note(note_id, user_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute('DELETE FROM note WHERE id = %s AND user_id = %s', (note_id, user_id))
            affected_rows = cursor.rowcount
        db.commit()
        return affected_rows
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting note: {str(e)}")
        raise