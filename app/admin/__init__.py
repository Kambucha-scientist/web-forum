from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.main import thread_hot_score, get_thread_rating
from app.models import User, UserRole, Section, GroupType, Post, Thread, Rating
from app.decorators import admin_required, moderator_required, post_owner_or_moderator
from sqlalchemy import func
import re
import csv
from io import StringIO
from flask import Response
from datetime import datetime, timedelta
from collections import defaultdict

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at).all()
    return render_template('admin/users.html', users=all_users, roles=UserRole)

@bp.route('/users/<uuid:user_id>/promote', methods=['POST'])
@login_required
@admin_required
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
@admin_required
def sections():
    all_sections = Section.query.order_by(Section.title).all()
    return render_template('admin/sections.html', sections=all_sections)

@bp.route('/sections/new', methods=['GET', 'POST'])
@login_required
@admin_required
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
        if not codename or not re.match(r'^[a-z0-9_-]+$', codename):
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
@admin_required
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
@admin_required
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

@bp.route('/<string:codename>/<uuid:thread_id>/pin', methods=['POST'])
@login_required
@moderator_required
def toggle_pin(codename, thread_id):
    """Закрепить/открепить тему"""
    section = Section.query.filter_by(codename=codename).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, section_id=section.id).first_or_404()
    thread.is_pinned = not thread.is_pinned
    db.session.commit()
    flash('Статус закрепления изменён.', 'success')
    return redirect(url_for('main.section_by_codename', codename=section.codename))

@bp.route('/<string:codename>/<uuid:thread_id>/close', methods=['POST'])
@login_required
@moderator_required
def toggle_close(codename, thread_id):
    """Закрыть/открыть тему (в закрытую нельзя отвечать)"""
    section = Section.query.filter_by(codename=codename).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, section_id=section.id).first_or_404()
    thread.is_closed = not thread.is_closed
    db.session.commit()
    flash('Статус темы изменён.', 'success')
    return redirect(url_for('main.section_by_codename', codename=section.codename))

@bp.route('/<string:codename>/<uuid:thread_id>/delete', methods=['POST'])
@login_required
@moderator_required
def delete_thread(codename, thread_id):
    """Удалить тему со всеми постами"""
    section = Section.query.filter_by(codename=codename).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, section_id=section.id).first_or_404()
    db.session.delete(thread)
    db.session.commit()
    flash('Тема удалена.', 'success')
    return redirect(url_for('main.section_by_codename', codename=section.codename))

@bp.route('/<string:codename>/<uuid:thread_id>/edit_post/<uuid:post_id>', methods=['GET', 'POST'])
@login_required
@post_owner_or_moderator
def edit_post(codename, thread_id, post_id):
    """Редактирование поста (для модератора/админа)"""
    section = Section.query.filter_by(codename=codename).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, section_id=section.id).first_or_404()
    post = Post.query.filter_by(id=post_id, thread_id=thread.id).first_or_404()
    
    if request.method == 'POST':
        new_content = request.form.get('content', '').strip()
        if not new_content or len(new_content) < 3:
            flash('Содержание поста не может быть пустым.', 'danger')
            return render_template('edit_post.html', post=post, thread=thread, section=section)
        post.content = new_content
        db.session.commit()
        flash('Пост отредактирован.', 'success')
        return redirect(url_for('main.view_thread', codename=section.codename, thread_id=thread.id))
    
    return render_template('edit_post.html', post=post, thread=thread, section=section)

@bp.route('/<string:codename>/<uuid:thread_id>/delete_post/<uuid:post_id>', methods=['POST'])
@login_required
@post_owner_or_moderator
def delete_post(codename, thread_id, post_id):
    """Удаление поста"""
    section = Section.query.filter_by(codename=codename).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, section_id=section.id).first_or_404()
    post = Post.query.filter_by(id=post_id, thread_id=thread.id).first_or_404()
    
    first_post = Post.query.filter_by(thread_id=thread.id).order_by(Post.created_at).first()

    if post.id == first_post.id:
        db.session.delete(thread)
        db.session.commit()
        flash('Удалён первый пост, поэтому тема удалена целиком.', 'warning')
        return redirect(url_for('main.section_by_codename', codename=section.codename))
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Пост удалён.', 'success')
        return redirect(url_for('main.view_thread', codename=section.codename, thread_id=thread.id))
 

@bp.route('/export/users/<string:codename>')
@login_required
@admin_required
def export_users_ratings(codename):
    section = Section.query.filter_by(codename=codename).first_or_404()
    
    # Получаем все посты раздела с рейтингами каждого поста (как в section_by_codename)
    posts_data = db.session.query(
        Post.id, Post.user_id, func.count(Rating.id).label('rating_count')
    ).outerjoin(Rating, Rating.target_id == Post.id)\
     .join(Thread, Thread.id == Post.thread_id)\
     .filter(Thread.section_id == section.id)\
     .group_by(Post.id)\
     .all()
    
    # Группируем по пользователям: список rating_count каждого поста
    user_ratings = defaultdict(list)
    for post in posts_data:
        user_ratings[post.user_id].append(post.rating_count or 0)
    
    # Получаем имена пользователей
    users = User.query.filter(User.id.in_(user_ratings.keys())).all()
    user_map = {u.id: u for u in users}
    
    # Функция h-index
    def h_index(ratings):
        ratings.sort(reverse=True)
        h = 0
        for i, r in enumerate(ratings, 1):
            if r >= i:
                h = i
            else:
                break
        return h
    
    # Формируем список для CSV
    data = []
    for user_id, ratings in user_ratings.items():
        user = user_map.get(user_id)
        if not user:
            continue
        total_votes = sum(ratings)
        post_count = len(ratings)
        h = h_index(ratings)
        data.append([user.username, post_count, total_votes, h])
    
    # Сортируем по h-index (убывание)
    data.sort(key=lambda x: x[3], reverse=True)
    
    # Создаём CSV
    output = StringIO()
    output.write('\ufeff')  # BOM для корректного открытия в Excel
    writer = csv.writer(output, delimiter=';')  # разделитель точка с запятой
    writer.writerow(['Имя пользователя', 'Количество постов', 'Всего голосов (апвоутов)', 'h-index'])
    writer.writerows(data)
    output.seek(0)
    
    filename = f"users_ratings_{section.codename}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={"Content-Disposition": f"attachment;filename={filename}"})

@bp.route('/export/threads/<string:codename>')
@login_required
@admin_required
def export_threads_ratings(codename):
    section = Section.query.filter_by(codename=codename).first_or_404()
    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)
    
    # Получаем все треды раздела
    threads = Thread.query.filter_by(section_id=section.id, is_closed=False).all()
    
    # Посты за последние 24 часа для Hot-формулы
    posts_last_24h = Post.query.filter(Post.created_at >= day_ago).all()
    thread_stats = defaultdict(lambda: {'authors': set(), 'messages': 0, 'post_ids': []})
    for p in posts_last_24h:
        if p.thread.section_id == section.id:  # только треды этого раздела
            thread_stats[p.thread_id]['authors'].add(p.user_id)
            thread_stats[p.thread_id]['messages'] += 1
            thread_stats[p.thread_id]['post_ids'].append(p.id)
    
    all_post_ids = [pid for stats in thread_stats.values() for pid in stats['post_ids']]
    ratings_last_24h = []
    if all_post_ids:
        ratings_last_24h = Rating.query.filter(
            Rating.target_id.in_(all_post_ids),
            Rating.created_at >= day_ago
        ).all()
    
    post_to_thread = {}
    for tid, stats in thread_stats.items():
        for pid in stats['post_ids']:
            post_to_thread[pid] = tid
    
    upvotes_per_thread = defaultdict(int)
    for r in ratings_last_24h:
        tid = post_to_thread.get(r.target_id)
        if tid:
            upvotes_per_thread[tid] += 1
    
    # Готовим данные для CSV
    data = []
    for thread in threads:
        # Общая сумма голосов (за всё время)
        total_votes = get_thread_rating(thread.id)
        total_posts = Post.query.filter_by(thread_id=thread.id).count()
        
        # Данные за 24 часа
        if thread.id in thread_stats:
            U = len(thread_stats[thread.id]['authors'])
            M = thread_stats[thread.id]['messages']
            L = upvotes_per_thread.get(thread.id, 0)
            last_post = Post.query.filter_by(thread_id=thread.id).order_by(Post.created_at.desc()).first()
            A = (now - last_post.created_at).total_seconds() / 3600 if last_post else (now - thread.created_at).total_seconds() / 3600
        else:
            U = M = L = 0
            last_post = Post.query.filter_by(thread_id=thread.id).order_by(Post.created_at.desc()).first()
            A = (now - last_post.created_at).total_seconds() / 3600 if last_post else (now - thread.created_at).total_seconds() / 3600
        
        hot_score = thread_hot_score(U, M, L, A)
        
        data.append([
            thread.title,
            thread.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            total_posts,
            total_votes,
            f"{hot_score:.4f}"
        ])
    
    # Сортируем по убыванию Hot
    data.sort(key=lambda x: float(x[4]), reverse=True)
    
    output = StringIO()
    output.write('\ufeff')  # BOM для корректного открытия в Excel
    writer = csv.writer(output, delimiter=';')  # разделитель точка с запятой
    writer.writerow(['Заголовок', 'Дата создания', 'Количество постов', 'Всего голосов (апвоутов)', 'Hot-рейтинг'])
    writer.writerows(data)
    output.seek(0)
    
    filename = f"threads_ratings_{section.codename}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={"Content-Disposition": f"attachment;filename={filename}"})

@bp.route('/user/<uuid:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    # Нельзя удалить самого себя
    if user_id == current_user.id:
        flash('Нельзя удалить собственный аккаунт', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Пользователь {user.username} удалён', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))

@bp.route('/user/<uuid:user_id>/toggle_ban', methods=['POST'])
@login_required
@moderator_required
def toggle_ban(user_id):
    if user_id == current_user.id:
        flash('Нельзя заблокировать собственный аккаунт', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    
    user.is_banned = not user.is_banned
    db.session.commit()
    status = 'заблокирован' if user.is_banned else 'разблокирован'
    flash(f'Пользователь {user.username} {status}', 'success')
    
    return redirect(request.referrer)