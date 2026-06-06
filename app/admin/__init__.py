from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, UserRole, Section, GroupType
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
        flash('Нельзя менять свою роль', 'warning')
        return redirect(url_for('admin.users'))
    user.role = new_role
    db.session.commit()
    flash(f'Роль {user.username} изменена на {new_role.value}', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/sections')
@login_required
@roles_required('admin')
def sections():
    all_sections = Section.query.order_by(Section.title).all()
    return render_template('admin/sections.html', sections=all_sections)

@bp.route('/sections/new', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def new_section():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        codename = request.form.get('codename', '').strip().lower()
        description = request.form.get('description', '').strip()
        group_str = request.form.get('group', 'language')
        is_visible = request.form.get('is_visible') == 'on'
        
        errors = []
        if not title or len(title) < 3:
            errors.append('Название минимум 3 символа')
        if not codename or len(codename) < 2 or not re.match(r'^[a-z0-9_-]+$', codename):
            errors.append('Кодовое имя (латиница, цифры, _, -)')
        if Section.query.filter_by(codename=codename).first():
            errors.append(f'Кодовое имя "{codename}" уже занято')
        
        try:
            group = GroupType(group_str)
        except ValueError:
            errors.append('Неверная группа')
        
        if errors:
            for err in errors:
                flash(err, 'danger')
        else:
            section = Section(
                title=title,
                codename=codename,
                description=description,
                group=group,
                is_visible=is_visible
            )
            db.session.add(section)
            db.session.commit()
            flash(f'Раздел "{title}" создан', 'success')
            return redirect(url_for('admin.sections'))
    
    return render_template('admin/section_form.html', title='Создать раздел', section=None)

@bp.route('/sections/<uuid:section_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_section(section_id):
    section = Section.query.get_or_404(section_id)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        codename = request.form.get('codename', '').strip().lower()
        description = request.form.get('description', '').strip()
        group_str = request.form.get('group', 'language')
        is_visible = request.form.get('is_visible') == 'on'
        
        errors = []
        if not title or len(title) < 3:
            errors.append('Название минимум 3 символа')
        if not codename or len(codename) < 2 or not re.match(r'^[a-z0-9_-]+$', codename):
            errors.append('Кодовое имя (латиница, цифры, _, -)')
        existing = Section.query.filter(Section.codename == codename, Section.id != section.id).first()
        if existing:
            errors.append(f'Кодовое имя "{codename}" уже занято')
        try:
            group = GroupType(group_str)
        except ValueError:
            errors.append('Неверная группа')
        
        if errors:
            for err in errors:
                flash(err, 'danger')
        else:
            section.title = title
            section.codename = codename
            section.description = description
            section.group = group
            section.is_visible = is_visible
            db.session.commit()
            flash('Раздел обновлён', 'success')
            return redirect(url_for('admin.sections'))
    return render_template('admin/section_form.html', title='Редактировать раздел', section=section)

@bp.route('/sections/<uuid:section_id>/delete', methods=['POST'])
@login_required
@roles_required('admin')
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    name = section.title
    if Section.query.count() == 1:
        flash('Нельзя удалить единственный раздел', 'danger')
        return redirect(url_for('admin.sections'))
    db.session.delete(section)
    db.session.commit()
    flash(f'Раздел "{name}" удалён', 'success')
    return redirect(url_for('admin.sections'))

