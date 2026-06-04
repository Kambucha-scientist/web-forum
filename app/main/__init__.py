from flask import Blueprint, render_template
from app.models import Section, Thread
from sqlalchemy import func

bp = Blueprint('main', __name__)

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