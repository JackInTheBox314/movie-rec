from flask_login import login_user, logout_user, current_user, login_required, UserMixin
from flask import Flask, render_template, request, redirect, url_for, flash

class User(UserMixin):
    def __init__(self, user_json):
        self.user_json = user_json

    def get_id(self):
        object_id = self.user_json.get('_id')
        return str(object_id)
    
    def __repr__(self):
        return f'<User: {self.user_json.get('username')}>'


def register_routes(app, db, bcrypt):
    
    users_collection = db['users']
    
    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            # Check if the username already exists
            if users_collection.find_one({'username': username}):
                flash('Username already exists. Choose a different one.', 'danger')
            else:
                users_collection.insert_one({'username': username, 'password': password})
                flash('Registration successful. You can now log in.', 'success')
                return redirect(url_for('login'))

        return render_template('register.html')
            
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Check if the username and password match
            user_json = users_collection.find_one({'username': username, 'password': password})
            if user_json:
                flash('Login successful.', 'success')
                # Add any additional logic, such as session management
                user = User(user_json)
                login_user(user)
                print(user)
            else:
                flash('Invalid username or password. Please try again.', 'danger')

        return render_template('login.html')
    