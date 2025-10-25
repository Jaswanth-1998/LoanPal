from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User
from sqlalchemy.exc import IntegrityError

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        flash('Please check your login details and try again.', 'danger')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    flash('✅ User logged in successfully', 'success')
    return redirect(url_for('main.dashboard'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password')
        
        # ✅ Validate form inputs
        if not username or not email or not password:
            flash('Please fill all required fields.', 'danger')
            return redirect(url_for('auth.register'))

        # ✅ Check for duplicates
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
            
        # ✅ Create user and handle database integrity errors    
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('An account with that username or email already exists.', 'danger')
            return redirect(url_for('auth.register'))

        flash('✅ User registered successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    # ✅ Always return something for GET request (important)
    return render_template('register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
