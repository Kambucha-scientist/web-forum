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

class UserRole(enum.Enum):
    GUEST = 'guest'
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

class ThreadType(enum.Enum):
    QANDA = 'Q&A'
    DISCUSSION = 'discussion'
    ARTICLE = 'article'

class RatingTargetType(enum.Enum):
    USER = 'user'
    SECTION = 'section'
    THREAD = 'thread'
    POST = 'post'

class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    avatar_url = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    threads = db.relationship('Thread', back_populates='author', cascade='all, delete-orphan')
    posts = db.relationship('Post', back_populates='author', cascade='all, delete-orphan')
    ratings_given = db.relationship('Rating', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_moderator(self):
        return self.role == UserRole.MODERATOR or self.is_admin()
    
    def __repr__(self):
        return f'<User {self.username}>'

class Section(Base):
    __tablename__ = 'sections'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    codename = db.Column(db.String(5), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    threads = db.relationship('Thread', back_populates='section', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Section {self.name}>'

class Thread(Base):
    __tablename__ = 'threads'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('sections.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    thread_type = db.Column(db.Enum(ThreadType), default=ThreadType.DISCUSSION, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    thread = db.relationship('Thread', back_populates='posts')
    author = db.relationship('User', back_populates='posts')
    
    def __repr__(self):
        return f'<Post {self.id} in thread {self.thread_id}>'

class Rating(Base):
    __tablename__ = 'ratings'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_type', 'target_id', name='unique_user_target'),
        db.Index('idx_target', 'target_type', 'target_id'),
    )
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_type = db.Column(db.Enum(RatingTargetType), nullable=False)
    target_id = db.Column(db.UUID(as_uuid=True), nullable=False)
    value = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', back_populates='ratings_given')
    
    def __repr__(self):
        return f'<Rating +1 from {self.user_id} to {self.target_type}:{self.target_id}>'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(uuid.UUID(user_id))
    except (ValueError, TypeError):
        return None
