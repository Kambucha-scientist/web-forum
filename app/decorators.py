# app/decorators.py
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def roles_required(*roles):
    """
    Декоратор для ограничения доступа по ролям.
    Пример: @roles_required('admin', 'moderator')
    """
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Необходимо войти в систему.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role.name not in roles and 'admin' not in roles:
                flash('У вас недостаточно прав для доступа к этой странице.', 'danger')
                return redirect(url_for('main.index'))
            return func(*args, **kwargs)
        return wrapped
    return decorator