from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, UserRole, Section
from app.decorators import roles_required
import re

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

@bp.route('/sections')
@login_required
@roles_required('admin')
def sections():
    """Список всех разделов с возможностью редактирования/удаления"""
    all_sections = Section.query.order_by(Section.name).all()
    return render_template('admin/sections.html', sections=all_sections)

@bp.route('/sections/new', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def new_section():
    """Создание нового раздела"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        codename = request.form.get('codename', '').strip().lower()
        description = request.form.get('description', '').strip()
        
        # Валидация
        errors = []
        if not name or len(name) < 3:
            errors.append('Название раздела должно содержать минимум 3 символа')
        
        if not codename or len(codename) < 2:
            errors.append('Кодовое имя должно содержать минимум 2 символа')
        elif not re.match(r'^[a-z0-9_-]+$', codename):
            errors.append('Кодовое имя может содержать только латиницу в нижнем регистре, цифры, _ и -')
        
        # Проверка уникальности codename
        if Section.query.filter_by(codename=codename).first():
            errors.append(f'Раздел с кодовым именем "{codename}" уже существует')
        
        if errors:
            for err in errors:
                flash(err, 'danger')
        else:
            section = Section(
                name=name,
                codename=codename,
                description=description
            )
            db.session.add(section)
            db.session.commit()
            flash(f'Раздел "{name}" успешно создан!', 'success')
            return redirect(url_for('admin.sections'))
    
    return render_template('admin/section_form.html', title='Создать раздел', section=None)

@bp.route('/sections/<uuid:section_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_section(section_id):
    """Редактирование существующего раздела"""
    section = Section.query.get_or_404(section_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        codename = request.form.get('codename', '').strip().lower()
        description = request.form.get('description', '').strip()
        
        errors = []
        if not name or len(name) < 3:
            errors.append('Название раздела должно содержать минимум 3 символа')
        
        if not codename or len(codename) < 2:
            errors.append('Кодовое имя должно содержать минимум 2 символа')
        elif not re.match(r'^[a-z0-9_-]+$', codename):
            errors.append('Кодовое имя может содержать только латиницу в нижнем регистре, цифры, _ и -')
        
        # Проверка уникальности codename (исключая текущий раздел)
        existing = Section.query.filter(Section.codename == codename, Section.id != section.id).first()
        if existing:
            errors.append(f'Раздел с кодовым именем "{codename}" уже существует')
        
        if errors:
            for err in errors:
                flash(err, 'danger')
        else:
            section.name = name
            section.codename = codename
            section.description = description
            db.session.commit()
            flash(f'Раздел "{name}" успешно обновлён!', 'success')
            return redirect(url_for('admin.sections'))
    
    return render_template('admin/section_form.html', title='Редактировать раздел', section=section)

@bp.route('/sections/<uuid:section_id>/delete', methods=['POST'])
@login_required
@roles_required('admin')
def delete_section(section_id):
    """Удаление раздела (вместе со всеми тредами и постами, благодаря CASCADE)"""
    section = Section.query.get_or_404(section_id)
    name = section.name
    
    # Проверяем, не пытается ли админ удалить последний раздел (опционально)
    if Section.query.count() == 1:
        flash('Нельзя удалить единственный раздел.', 'danger')
        return redirect(url_for('admin.sections'))
    
    db.session.delete(section)
    db.session.commit()
    flash(f'Раздел "{name}" и все его темы удалены.', 'success')
    return redirect(url_for('admin.sections'))

