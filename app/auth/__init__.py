from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, UserRole
import re

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        login_input = request.form.get('login')      
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        
        user = User.query.filter(
            (User.username == login_input) | (User.email == login_input)
        ).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Добро пожаловать, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Неверное имя пользователя/email или пароль', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm = request.form.get('password_confirm')
        
        # Валидация
        errors = []
        if not username or len(username) < 3:
            errors.append('Имя пользователя должно содержать минимум 3 символа')
        elif not re.match(r'^[a-zA-Z0-9_-]+$', username):
            errors.append('Имя пользователя может содержать только латиницу, цифры, _ и -')
        
        if not email or '@' not in email:
            errors.append('Введите корректный email')
        
        if not password or len(password) < 6:
            errors.append('Пароль должен быть минимум 6 символов')
        elif password != confirm:
            errors.append('Пароли не совпадают')
        
        # Проверка уникальности
        if User.query.filter_by(username=username).first():
            errors.append('Пользователь с таким именем уже существует')
        if User.query.filter_by(email=email).first():
            errors.append('Пользователь с таким email уже существует')
        
        if errors:
            for err in errors:
                flash(err, 'danger')
        else:
            user = User(username=username, email=email, role=UserRole.USER, is_banned=False)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('До скорой встречи!', 'info')
    return redirect(url_for('main.index'))