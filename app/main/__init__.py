from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Section, Thread, Post, User, ThreadType, GroupType, Rating
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import markdown
import re
import os
import math
from collections import defaultdict


bp = Blueprint('main', __name__)

def truncate_html(html, length=200):
    text = re.sub(r'<[^>]+>', '', html)
    if len(text) > length:
        text = text[:length] + '...'
    return text

def thread_hot_score(U, M, L, A):
    """
    U - уникальные авторы за последние 24ч
    M - сообщения за последние 24ч
    L - апвоуты за последние 24ч
    A - часы с последнего сообщения
    """
    log_part = math.log1p(5*U + 3*M + 2*L)
    decay_part = 1 / (1 + A/24)
    return log_part + decay_part

def get_post_rating(post_id):
    """Возвращает количество голосов за пост"""
    return db.session.query(func.count(Rating.id)).filter(Rating.target_id == post_id).scalar() or 0

def get_thread_rating(thread_id):
    """Возвращает сумму голосов за все посты в треде"""
    return db.session.query(func.count(Rating.id)).join(Post, Post.id == Rating.target_id).filter(Post.thread_id == thread_id).scalar() or 0



@bp.route('/')
@bp.route('/index')
def index():
    sections = Section.query.filter_by(is_visible=True).all()
    
    sections_by_group = {
        'language': [],
        'DB': [],
        'AOB': []
    }
    
    for section in sections:
        group_name = section.group.name if hasattr(section.group, 'name') else str(section.group)
        if group_name in sections_by_group:
            sections_by_group[group_name].append(section)
    
    for group in sections_by_group:
        sections_by_group[group].sort(key=lambda x: x.title)

    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)
    
    # Посты за 24 часа
    posts_last_24h = Post.query.filter(Post.created_at >= day_ago).all()
    thread_stats = defaultdict(lambda: {'authors': set(), 'messages': 0, 'post_ids': []})
    for p in posts_last_24h:
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
    
    all_threads = Thread.query.all()
    hot_list = []
    
    for thread in all_threads:
        if thread.id in thread_stats:
            U = len(thread_stats[thread.id]['authors'])
            M = thread_stats[thread.id]['messages']
            L = upvotes_per_thread.get(thread.id, 0)
            last_post = Post.query.filter_by(thread_id=thread.id).order_by(Post.created_at.desc()).first()
            A = (now - last_post.created_at).total_seconds() / 3600 if last_post else (now - thread.created_at).total_seconds() / 3600
            posts_count = M  # или общее количество постов (не только за 24ч) – сделаем отдельно
            rating_sum = get_thread_rating(thread.id)  # общая сумма голосов за всё время
        else:
            last_post = Post.query.filter_by(thread_id=thread.id).order_by(Post.created_at.desc()).first()
            A = (now - last_post.created_at).total_seconds() / 3600 if last_post else (now - thread.created_at).total_seconds() / 3600
            U = M = L = 0
            posts_count = Post.query.filter_by(thread_id=thread.id).count()
            rating_sum = get_thread_rating(thread.id)
        
        score = thread_hot_score(U, M, L, A)
        hot_list.append((thread, posts_count, rating_sum, score))
    
    hot_list.sort(key=lambda x: x[3], reverse=True)
    hot_threads = hot_list[:5]   # каждый элемент: (thread, posts_count, rating_sum, score)
    
    return render_template('index.html', sections_by_group=sections_by_group, hot_threads=hot_threads)

@bp.route('/<string:codename>')
def section_by_codename(codename):
    section = Section.query.filter_by(codename=codename, is_visible=True).first_or_404()
    threads = Thread.query.filter_by(section_id=section.id)\
                         .order_by(Thread.is_pinned.desc(), Thread.created_at.desc()).all()

    thread_ids = [t.id for t in threads]

    posts_with_ratings = db.session.query(
        Post.id, Post.thread_id, Post.user_id, Post.content, Post.created_at, Post.attachment,
        func.count(Rating.id).label('rating_count')
    ).outerjoin(Rating, Rating.target_id == Post.id)\
     .filter(Post.thread_id.in_(thread_ids))\
     .group_by(Post.id)\
     .order_by(Post.created_at)\
     .all()

    thread_posts = defaultdict(list)
    for p in posts_with_ratings:
        thread_posts[p.thread_id].append({
            'id': p.id,
            'user_id': p.user_id,
            'content': p.content,
            'created_at': p.created_at,
            'attachment': p.attachment,
            'rating_count': p.rating_count or 0
        })

    users_ids = set(p.user_id for p in posts_with_ratings) | set(t.user_id for t in threads)
    users = User.query.filter(User.id.in_(users_ids)).all()
    user_map = {u.id: u for u in users}

    threads_data = []
    for thread in threads:
        posts = thread_posts.get(thread.id, [])
        first_post = posts[0] if posts else None
        
        preview = ''
        first_post_attachment = None
        first_post_author = None
        first_post_rating = 0
        
        if first_post:
            html_content = markdown.markdown(first_post['content'], extensions=['fenced_code', 'codehilite'])
            preview = truncate_html(html_content, 150)
            first_post_author = user_map.get(first_post['user_id'])
            first_post_attachment = first_post['attachment']
            first_post_rating = first_post['rating_count']

        posts_count = len(posts)
        rating_sum = sum(p['rating_count'] for p in posts)

        last_replies = posts[1:][-3:] if len(posts) > 1 else []
        replies_html = []
        for reply in last_replies:
            reply_html = markdown.markdown(reply['content'], extensions=['fenced_code', 'codehilite'])
            replies_html.append({
                'id': reply['id'],
                'author': user_map.get(reply['user_id']),
                'content': truncate_html(reply_html, 100),
                'full_content_html': reply_html,
                'created_at': reply['created_at'],
                'attachment': reply['attachment'],
                'rating_count': reply['rating_count']
            })

        threads_data.append({
            'thread': thread,
            'preview': preview,
            'posts_count': posts_count,
            'rating_sum': rating_sum,
            'last_replies': replies_html,
            'replies_count': len(last_replies),
            'first_post_author': first_post_author,
            'first_post_attachment': first_post_attachment,
            'first_post_rating': first_post_rating,
        })

    user_post_ratings = defaultdict(list)
    for p in posts_with_ratings:
        user_post_ratings[p.user_id].append(p.rating_count or 0)

    def h_index(ratings):
        ratings.sort(reverse=True)
        h = 0
        for i, r in enumerate(ratings, 1):
            if r >= i:
                h = i
            else:
                break
        return h

    top_users = []
    for user_id, ratings in user_post_ratings.items():
        h = h_index(ratings)
        top_users.append((user_map.get(user_id), h))
    top_users.sort(key=lambda x: x[1], reverse=True)
    top_users = top_users[:3]

    return render_template('section.html', section=section, threads=threads_data, top_users=top_users)

@bp.route('/<string:codename>/new', methods=['GET', 'POST'])
@login_required
def new_thread(codename):
    section = Section.query.filter_by(codename=codename, is_visible=True).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        thread_type_str = request.form.get('thread_type', 'question')
        
        
        if not title or len(title) < 5:
            flash('Заголовок минимум 5 символов', 'danger')
            return render_template('new_thread.html', section=section)
        if not content or len(content) < 10:
            flash('Содержание минимум 10 символов', 'danger')
            return render_template('new_thread.html', section=section)
        
        attachment_path = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                # Проверка расширения
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    # Генерируем уникальное имя
                    import uuid
                    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                    attachments_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attachments')
                    os.makedirs(attachments_dir, exist_ok=True)
                    filepath = os.path.join(attachments_dir, filename)
                    file.save(filepath)
                    attachment_path = f"/uploads/attachments/{filename}"
                else:
                    flash('Недопустимый формат вложения', 'danger')
                    return render_template('new_thread.html', section=section)
        
        try:
            thread_type = ThreadType(thread_type_str)
        except ValueError:
            thread_type = ThreadType.question
        
        
        thread = Thread(
            title=title,
            thread_type=thread_type,
            section_id=section.id,
            user_id=current_user.id,
            views=0,
            is_pinned=False,
            is_closed=False
        )
        db.session.add(thread)
        db.session.flush()
        
        post = Post(content=content, thread_id=thread.id, user_id=current_user.id, attachment=attachment_path, is_solution=False)
        db.session.add(post)
        db.session.commit()
        
        flash('Тема создана', 'success')
        return redirect(url_for('main.view_thread', codename=section.codename, thread_id=thread.id))
    
    return render_template('new_thread.html', section=section)

@bp.route('/<string:codename>/<uuid:thread_id>')
def view_thread(codename, thread_id):
    section = Section.query.filter_by(codename=codename, is_visible=True).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, section_id=section.id).first_or_404()
    
    posts = (Post.query
             .filter_by(thread_id=thread.id)
             .order_by(Post.created_at)
             .all())

    user_votes = set()
    if current_user.is_authenticated:
        user_votes = set(
            r.target_id for r in Rating.query.filter_by(user_id=current_user.id).all()
        )

    for post in posts:
        post.rating_count = get_post_rating(post.id)
        post.html_content = markdown.markdown(post.content, extensions=['fenced_code', 'codehilite'])
        post.user_voted = post.id in user_votes
        post.is_edited = post.updated_at is not None and post.updated_at > post.created_at

    thread_rating = get_thread_rating(thread.id)

    return render_template('thread.html',
                           section=section,
                           thread=thread,
                           posts=posts,
                           thread_rating=thread_rating)

@bp.route('/<string:codename>/<uuid:thread_id>/reply', methods=['POST'])
@login_required
def reply_to_thread(codename, thread_id):
    section = Section.query.filter_by(codename=codename, is_visible=True).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, section_id=section.id).first_or_404()

    if thread.is_closed and current_user.role.name not in ('MODERATOR', 'ADMIN'):
        flash('Тема закрыта. Только модераторы могут отвечать.', 'danger')
        return redirect(url_for('main.view_thread', codename=section.codename, thread_id=thread.id))
    
    content = request.form.get('content', '').strip()
    if not content or len(content) < 3:
        flash('Ответ минимум 3 символа', 'danger')
        return redirect(url_for('main.view_thread', codename=section.codename, thread_id=thread.id))
    
    attachment_path = None
    if 'attachment' in request.files:
        file = request.files['attachment']
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if ext in current_app.config['ALLOWED_EXTENSIONS']:
                import uuid
                filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                attachments_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attachments')
                os.makedirs(attachments_dir, exist_ok=True)
                filepath = os.path.join(attachments_dir, filename)
                file.save(filepath)
                attachment_path = f"/uploads/attachments/{filename}"
            else:
                flash('Недопустимый формат вложения', 'danger')
                return redirect(url_for('main.view_thread', codename=section.codename, thread_id=thread.id))
    
    post = Post(content=content, thread_id=thread.id, user_id=current_user.id, attachment=attachment_path, is_solution=False)
    db.session.add(post)
    db.session.commit()
    flash('Ответ добавлен', 'success')
    return redirect(url_for('main.view_thread', codename=section.codename, thread_id=thread.id))

@bp.route('/vote', methods=['POST'])
@login_required
def vote():
    post_id = request.form.get('post_id')
    if not post_id:
        return jsonify({'error': 'Не указан пост'}), 400
    
    post = Post.query.get_or_404(post_id)

    existing = Rating.query.filter_by(user_id=current_user.id, target_id=post.id).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        new_count = get_post_rating(post.id)
        return jsonify({'success': True, 'new_rating': new_count, 'voted': False})
    else:
        # Добавляем голос
        rating = Rating(user_id=current_user.id, target_id=post.id)
        db.session.add(rating)
        db.session.commit()
        new_count = get_post_rating(post.id)
        return jsonify({'success': True, 'new_rating': new_count, 'voted': True})