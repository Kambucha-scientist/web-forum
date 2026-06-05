from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, UserRole
from app.decorators import roles_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/users')
@login_required
@roles_required('admin')
def users():
    all_users = User.query.order_by(User.created_at).all()
    return render_template('admin/users.html', users=all_users, roles=UserRole)

@bp.route('/users/<uuid:user_id>/promote', methods=['POST'])
@login_required
@roles_required('admin')
def promote_user(user_id):
    user = User.query.get_or_404(user_id)
    new_role_name = request.form.get('role')
    
    try:
        new_role = UserRole[new_role_name.upper()]
    except KeyError:
        flash('Некорректная роль', 'danger')
        return redirect(url_for('admin.users'))
    
    if user.id == current_user.id:
        flash('Вы не можете изменить свою собственную роль.', 'warning')
        return redirect(url_for('admin.users'))
    
    user.role = new_role
    db.session.commit()
    
    flash(f'Роль пользователя {user.username} изменена на {new_role.value}', 'success')
    return redirect(url_for('admin.users'))