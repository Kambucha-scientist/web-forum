from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user
from app.models import Post

def admin_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Необходимо войти в систему.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role.name != 'ADMIN':
            flash('Доступ только для администратора.', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrapped

def moderator_required(func):
    
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Необходимо войти в систему.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role.name not in ('MODERATOR', 'ADMIN'):
            flash('Недостаточно прав для выполнения этого действия.', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrapped

def post_owner_or_moderator(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        post_id=kwargs.get('post_id')
        post = Post.query.get_or_404(post_id)
        if current_user.id == post.user_id or current_user.role.name in ('MODERATOR', 'ADMIN'):
            return func(*args, **kwargs)
        flash('Вы не можете редактировать этот пост.', 'danger')
        return redirect(request.referrer or url_for('main.index'))
    return wrapped

def account_active_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if current_user.is_banned:
            flash('Ваш аккаунт заблокирован. Вы не можете выполнять это действие.', 'danger')
            return redirect(request.referrer or url_for('main.index'))
            
        return func(*args, **kwargs)
    return wrapped