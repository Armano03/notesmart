from flask import render_template, redirect, url_for, request, flash, jsonify, session
from datetime import datetime
import db
import auth
import logging

# Setup logging
logger = logging.getLogger(__name__)

def register_routes(app):
    """Register all application routes."""
    
    @app.route('/')
    def index():
        if auth.is_authenticated():
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if auth.is_authenticated():
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not username or not email or not password:
                flash('Please fill all required fields', 'danger')
                return render_template('register.html')
            
            success, result = auth.register_user(username, email, password)
            
            if not success:
                flash(result, 'danger')
                return render_template('register.html')
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if auth.is_authenticated():
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please provide both username and password', 'danger')
                return render_template('login.html')
            
            success, result = auth.login_user(username, password)
            
            if not success:
                flash(result, 'danger')
                return render_template('login.html')
            
            return redirect(url_for('dashboard'))
            
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        auth.logout_user()
        flash('You have been logged out successfully', 'info')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @auth.login_required
    def dashboard():
        if 'user_id' not in session:
            flash('Please log in to access your dashboard', 'danger')
            return redirect(url_for('login'))
            
        user_id = session['user_id']
        categories = db.get_categories_by_user(user_id)
        search_query = request.args.get('search', '')
        category_id = request.args.get('category')
        
        if category_id and category_id.isdigit():
            category_id = int(category_id)
        else:
            category_id = None
            
        notes = db.get_notes_by_user(user_id, category_id, search_query)
        
        return render_template('dashboard.html', 
                               notes=notes, 
                               categories=categories,
                               search_query=search_query,
                               current_category=category_id)

    @app.route('/todos')
    @auth.login_required
    def todos():
        if 'user_id' not in session:
            flash('Please log in to access your to-dos', 'danger')
            return redirect(url_for('login'))
            
        user_id = session['user_id']
        categories = db.get_categories_by_user(user_id)
        
        filter_completed = request.args.get('completed')
        completed = None
        if filter_completed is not None:
            completed = filter_completed.lower() == 'true'
            
        todos = db.get_todos_by_user(user_id, completed)
        
        return render_template('todos.html', 
                               todos=todos, 
                               categories=categories,
                               filter_completed=filter_completed)

    @app.route('/note/<int:note_id>')
    @auth.login_required
    def view_note(note_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        user_id = session['user_id']
        note = db.get_note_by_id(note_id, user_id)
        
        if not note:
            flash('Note not found', 'danger')
            return redirect(url_for('dashboard'))
            
        categories = db.get_categories_by_user(user_id)
        
        return render_template('note.html', 
                               note=note, 
                               categories=categories)

    @app.route('/note/new', methods=['GET', 'POST'])
    @auth.login_required
    def new_note():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        user_id = session['user_id']
        categories = db.get_categories_by_user(user_id)
        
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content', '')
            category_name = request.form.get('category')
            is_todo = request.form.get('is_todo') == 'true'
            importance = request.form.get('importance', 'normal')
            color = request.form.get('color', 'blue')
            
            if not title:
                flash('Title is required', 'danger')
                return render_template('edit_note.html', 
                                      categories=categories,
                                      note=None)
            
            # Get or create category
            category_id = None
            if category_name:
                category = db.get_category_by_name(category_name, user_id)
                if category:
                    category_id = category['id']
                else:
                    category_id = db.create_category(category_name, user_id)
            
            note_id = db.create_note(title, content, category_id, is_todo, importance, color, user_id)
            flash('Note created successfully', 'success')
            
            if is_todo:
                return redirect(url_for('todos'))
            else:
                return redirect(url_for('dashboard'))
        
        return render_template('edit_note.html', 
                              categories=categories,
                              note=None)

    @app.route('/note/<int:note_id>/edit', methods=['GET', 'POST'])
    @auth.login_required
    def edit_note(note_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        user_id = session['user_id']
        note = db.get_note_by_id(note_id, user_id)
        
        if not note:
            flash('Note not found', 'danger')
            return redirect(url_for('dashboard'))
            
        categories = db.get_categories_by_user(user_id)
        
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content', '')
            category_name = request.form.get('category')
            is_todo = request.form.get('is_todo') == 'true'
            importance = request.form.get('importance', 'normal')
            color = request.form.get('color', 'blue')
            
            if not title:
                flash('Title is required', 'danger')
                return render_template('edit_note.html', 
                                      categories=categories,
                                      note=note)
            
            # Get or create category
            category_id = None
            if category_name:
                category = db.get_category_by_name(category_name, user_id)
                if category:
                    category_id = category['id']
                else:
                    category_id = db.create_category(category_name, user_id)
            
            updates = {
                'title': title,
                'content': content,
                'category_id': category_id,
                'is_todo': 1 if is_todo else 0,
                'importance': importance,
                'color': color
            }
            
            db.update_note(note_id, user_id, updates)
            flash('Note updated successfully', 'success')
            
            return redirect(url_for('view_note', note_id=note_id))
        
        return render_template('edit_note.html', 
                              categories=categories,
                              note=note)

    @app.route('/note/<int:note_id>/delete', methods=['POST'])
    @auth.login_required
    def delete_note(note_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        user_id = session['user_id']
        result = db.delete_note(note_id, user_id)
        
        if result > 0:
            flash('Note deleted successfully', 'success')
        else:
            flash('Note not found', 'danger')
        
        redirect_to = request.form.get('redirect_to', 'dashboard')
        return redirect(url_for(redirect_to))

    @app.route('/category/new', methods=['POST'])
    @auth.login_required
    def new_category():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        user_id = session['user_id']
        name = request.form.get('name')
        
        if not name:
            flash('Category name is required', 'danger')
            return redirect(url_for('dashboard'))
            
        db.create_category(name, user_id)
        flash('Category created successfully', 'success')
        
        return redirect(url_for('dashboard'))

    @app.route('/category/<int:category_id>/delete', methods=['POST'])
    @auth.login_required
    def delete_category(category_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        user_id = session['user_id']
        category = db.get_category_by_id(category_id, user_id)
        
        if not category:
            flash('Category not found', 'danger')
            return redirect(url_for('dashboard'))
            
        db.delete_category(category_id, user_id)
        flash('Category deleted successfully', 'success')
        
        return redirect(url_for('dashboard'))

    # API Routes
    @app.route('/api/notes', methods=['GET'])
    @auth.login_required
    def api_get_notes():
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user_id = session['user_id']
        category_id = request.args.get('category')
        search = request.args.get('search')
        
        if category_id and category_id.isdigit():
            category_id = int(category_id)
        else:
            category_id = None
            
        notes = db.get_notes_by_user(user_id, category_id, search)
        return jsonify(notes)

    @app.route('/api/notes', methods=['POST'])
    @auth.login_required
    def api_create_note():
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user_id = session['user_id']
        data = request.json
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        title = data.get('title')
        content = data.get('content', '')
        category_name = data.get('category')
        is_todo = data.get('is_todo', False)
        importance = data.get('importance', 'normal')
        color = data.get('color', 'blue')
        
        # Get or create category
        category_id = None
        if category_name:
            category = db.get_category_by_name(category_name, user_id)
            if category:
                category_id = category['id']
            else:
                category_id = db.create_category(category_name, user_id)
        
        note_id = db.create_note(title, content, category_id, is_todo, importance, color, user_id)
        note = db.get_note_by_id(note_id, user_id)
        
        return jsonify(note), 201

    @app.route('/api/notes/<int:note_id>', methods=['GET'])
    @auth.login_required
    def api_get_note(note_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user_id = session['user_id']
        note = db.get_note_by_id(note_id, user_id)
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
            
        return jsonify(note)

    @app.route('/api/notes/<int:note_id>', methods=['PUT'])
    @auth.login_required
    def api_update_note(note_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user_id = session['user_id']
        note = db.get_note_by_id(note_id, user_id)
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
            
        data = request.json
        updates = {}
        
        if 'title' in data:
            updates['title'] = data['title']
        if 'content' in data:
            updates['content'] = data['content']
        if 'is_todo' in data:
            updates['is_todo'] = 1 if data['is_todo'] else 0
        if 'completed' in data:
            updates['completed'] = 1 if data['completed'] else 0
        if 'importance' in data:
            updates['importance'] = data['importance']
        if 'color' in data:
            updates['color'] = data['color']
        
        if 'category' in data:
            category_name = data['category']
            if category_name:
                category = db.get_category_by_name(category_name, user_id)
                if category:
                    updates['category_id'] = category['id']
                else:
                    updates['category_id'] = db.create_category(category_name, user_id)
            else:
                updates['category_id'] = None
        
        db.update_note(note_id, user_id, updates)
        updated_note = db.get_note_by_id(note_id, user_id)
        
        return jsonify(updated_note)

    @app.route('/api/notes/<int:note_id>', methods=['DELETE'])
    @auth.login_required
    def api_delete_note(note_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user_id = session['user_id']
        note = db.get_note_by_id(note_id, user_id)
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
            
        db.delete_note(note_id, user_id)
        
        return '', 204

    @app.route('/api/categories', methods=['GET'])
    @auth.login_required
    def api_get_categories():
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user_id = session['user_id']
        categories = db.get_categories_by_user(user_id)
        return jsonify(categories)

    @app.route('/api/categories', methods=['POST'])
    @auth.login_required
    def api_create_category():
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user_id = session['user_id']
        data = request.json
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Category name is required'}), 400
            
        name = data['name']
        
        # Check if category already exists
        existing = db.get_category_by_name(name, user_id)
        if existing:
            return jsonify(existing), 200
            
        category_id = db.create_category(name, user_id)
        category = db.get_category_by_id(category_id, user_id)
        
        return jsonify(category), 201

    @app.route('/api/categories/<int:category_id>', methods=['DELETE'])
    @auth.login_required
    def api_delete_category(category_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user_id = session['user_id']
        category = db.get_category_by_id(category_id, user_id)
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
            
        db.delete_category(category_id, user_id)
        
        return '', 204