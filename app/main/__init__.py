from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Section, Thread, Post, User
from app import db
from sqlalchemy import func, desc
import markdown
import re
 
bp = Blueprint('main', __name__)

def truncate_html(html, length=200):
    text = re.sub(r'<[^>]+>', '', html)
    if len(text) > length:
        text = text[:length] + '...'
    return text

@bp.route('/')
@bp.route('/index')
def index():
    sections = Section.query.order_by(Section.name).all()
    hot_threads = (Thread.query
                   .outerjoin(Thread.posts)
                   .group_by(Thread.id)
                   .order_by(func.count(Thread.posts).desc())
                   .limit(5)
                   .all())
    return render_template('index.html', sections=sections, hot_threads=hot_threads)

@bp.route('/<string:codename>')
def section_by_codename(codename):
    """Страница раздела (по codename: /py, /cpp, /js)"""
    section = Section.query.filter_by(codename=codename).first_or_404()
    
    # Получаем все треды раздела с авторами и количеством постов
    threads = (Thread.query
               .filter_by(section_id=section.id)
               .outerjoin(Post)
               .group_by(Thread.id)
               .order_by(Thread.created_at.desc())
               .all())
    
    # Для каждого треда получаем превью первого поста и количество постов
    threads_data = []
    for thread in threads:
        first_post = Post.query.filter_by(thread_id=thread.id).order_by(Post.created_at).first()
        preview = ''
        if first_post:
            # Преобразуем markdown в HTML и обрезаем
            html_content = markdown.markdown(first_post.content)
            preview = truncate_html(html_content, 150)
        
        posts_count = Post.query.filter_by(thread_id=thread.id).count()
        rating_count = db.session.query(func.count(Post.id)).filter(
            Post.thread_id == thread.id
        ).scalar()  # пока заглушка для рейтинга

        last_replies = (Post.query
                        .filter(Post.thread_id == thread.id)
                        .filter(Post.id != first_post.id if first_post else True)
                        .order_by(Post.created_at.desc())
                        .limit(3)
                        .all())
        
        # Преобразуем ответы в HTML (обрезанные)
        replies_html = []
        for reply in last_replies:
            reply_html = markdown.markdown(reply.content)
            replies_html.append({
                'author': reply.author,
                'content': truncate_html(reply_html, 100),
                'created_at': reply.created_at
            })
        
        threads_data.append({
            'thread': thread,
            'preview': preview,
            'posts_count': posts_count,
            'rating_count': rating_count or 0,
            'last_replies': replies_html,      
            'replies_count': len(last_replies)  
        })
    
    # Топ-3 активных участника в этом разделе
    top_users = (db.session.query(User, func.count(Post.id).label('post_count'))
                 .join(Post, Post.user_id == User.id)
                 .join(Thread, Thread.id == Post.thread_id)
                 .filter(Thread.section_id == section.id)
                 .group_by(User.id)
                 .order_by(desc('post_count'))
                 .limit(3)
                 .all())
    
    return render_template('section.html', 
                         section=section, 
                         threads=threads_data,
                         top_users=top_users)

@bp.route('/<string:codename>/<uuid:thread_id>/reply', methods=['POST'])
@login_required
def reply_to_thread(codename, thread_id):
    """Ответ на существующий тред"""
    section = Section.query.filter_by(codename=codename).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, section_id=section.id).first_or_404()
    
    content = request.form.get('content', '').strip()
    
    if not content or len(content) < 3:
        flash('Содержание ответа должно быть минимум 3 символа', 'danger')
        return redirect(url_for('main.view_thread', codename=section.codename, thread_id=thread.id))
    
    post = Post(content=content, thread_id=thread.id, user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    
    flash('Ответ успешно добавлен!', 'success')
    return redirect(url_for('main.view_thread', codename=section.codename, thread_id=thread.id))

@bp.route('/<string:codename>/new', methods=['GET', 'POST'])
@login_required
def new_thread(codename):
    """Создание нового треда в разделе"""
    section = Section.query.filter_by(codename=codename).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        thread_type_str = request.form.get('thread_type', 'discussion')
        
        # Валидация
        if not title or len(title) < 5:
            flash('Заголовок должен содержать минимум 5 символов', 'danger')
            return render_template('new_thread.html', section=section)
        
        if not content or len(content) < 10:
            flash('Содержание поста должно быть минимум 10 символов', 'danger')
            return render_template('new_thread.html', section=section)
        
        # Преобразуем строку в Enum
        from app.models import ThreadType
        try:
            thread_type = ThreadType(thread_type_str)
        except ValueError:
            thread_type = ThreadType.DISCUSSION
        
        # Создаём тред
        thread = Thread(
            title=title,
            thread_type=thread_type,
            section_id=section.id,
            user_id=current_user.id
        )
        db.session.add(thread)
        db.session.flush()  # Получаем thread.id
        
        # Создаём первый пост
        post = Post(
            content=content,
            thread_id=thread.id,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        
        flash('Тема успешно создана!', 'success')
        return redirect(url_for('main.view_thread', codename=section.codename, thread_id=thread.id))
    
    return render_template('new_thread.html', section=section)


@bp.route('/<string:codename>/<uuid:thread_id>')
def view_thread(codename, thread_id):
    """Просмотр конкретного треда со всеми постами"""
    section = Section.query.filter_by(codename=codename).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, section_id=section.id).first_or_404()
    
    # Получаем все посты треда с авторами
    posts = (Post.query
             .filter_by(thread_id=thread.id)
             .order_by(Post.created_at)
             .all())
    
    # Преобразуем markdown в HTML для каждого поста
    for post in posts:
        post.html_content = markdown.markdown(post.content, extensions=['fenced_code', 'codehilite'])
    
    # Считаем рейтинг треда (пока заглушка)
    rating_count = 0
    
    return render_template('thread.html', 
                         section=section, 
                         thread=thread, 
                         posts=posts, 
                         rating_count=rating_count)
