"""
Модели данных SQLAlchemy.
Все таблицы соответствуют техническому заданию.
"""
import uuid
import enum
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class Base(db.Model):
    __abstract__=True
    pass

# ========== ENUM (строго по диаграмме) ==========
class ThreadType(enum.Enum):
    article = "article"       # Статья или туториал
    question = "question"     # Вопрос или задача
    discussion = "discussion" # Открытое обсуждение
    showcase = "showcase"     # Проект или портфолио
    resource = "resource"     # Полезный материал или подборка

class GroupType(enum.Enum):
    language = "language"     # Язык программирования
    DB = "DB"                 # База данных
    AOB = "AOB"               # Разное

class UserRole(enum.Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"

# ========== ТАБЛИЦЫ ==========
class User(Base, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(50), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_banned = db.Column(db.Boolean, default=False, nullable=True)

    # Связи (обратные ссылки)
    threads = db.relationship('Thread', back_populates='author', cascade='all, delete-orphan')
    posts = db.relationship('Post', back_populates='author', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == UserRole.ADMIN

    def is_moderator(self):
        return self.role in (UserRole.MODERATOR, UserRole.ADMIN)

    def __repr__(self):
        return f'<User {self.username}>'


class Section(Base):
    __tablename__ = 'sections'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    codename = db.Column(db.String(5), nullable=False, unique=True, index=True)
    group = db.Column(db.Enum(GroupType), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)

    # Связи
    threads = db.relationship('Thread', back_populates='section', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Section {self.title} ({self.codename})>'


class Thread(Base):
    __tablename__ = 'threads'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('sections.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    thread_type = db.Column(db.Enum(ThreadType), nullable=False, default=ThreadType.question)
    views = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    is_closed = db.Column(db.Boolean, default=False, nullable=False)

    # Связи
    section = db.relationship('Section', back_populates='threads')
    author = db.relationship('User', back_populates='threads')
    posts = db.relationship('Post', back_populates='thread', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Thread {self.title}>'


class Post(Base):
    __tablename__ = 'posts'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('threads.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    attachment = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_solution = db.Column(db.Boolean, default=False, nullable=False)

    # 
    thread = db.relationship('Thread', back_populates='posts')
    author = db.relationship('User', back_populates='posts')
    ratings = db.relationship('Rating', back_populates='target_post', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Post {self.id} in thread {self.thread_id}>'


class Rating(Base):
    __tablename__ = 'ratings'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_id', name='unique_user_post_vote'),
        db.Index('idx_target_post', 'target_id'),
    )

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    user = db.relationship('User', back_populates='ratings')
    target_post = db.relationship('Post', back_populates='ratings')

    def __repr__(self):
        return f'<Rating +1 from {self.user_id} to post {self.target_id}>'


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(uuid.UUID(user_id))
    except (ValueError, TypeError):
        return None
