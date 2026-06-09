from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User
import os
import re
from werkzeug.utils import secure_filename
from PIL import Image   # если не установлен, нужно: pip install Pillow

bp = Blueprint('profile', __name__, url_prefix='/profile')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def save_avatar(user_id, file):
    """Сохраняет аватарку пользователя, конвертирует в PNG"""
    avatars_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(avatars_dir, exist_ok=True)
    
    # Конвертируем в PNG и сохраняем как {user_id}.png
    img = Image.open(file)
    img = img.convert('RGB')
    filepath = os.path.join(avatars_dir, f'{user_id}.png')
    img.save(filepath, 'PNG')
    return f'/uploads/avatars/{user_id}.png'

def delete_avatar(user_id):
    """Удаляет старую аватарку, если есть"""
    avatars_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    filepath = os.path.join(avatars_dir, f'{user_id}.png')
    if os.path.exists(filepath):
        os.remove(filepath)

@bp.route('/<uuid:user_id>')
def view(user_id):
    """Просмотр профиля пользователя"""
    user = User.query.get_or_404(user_id)
    # Проверяем, есть ли аватарка
    avatar_path = f'/uploads/avatars/{user.id}.png'
    avatar_exists = os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', f'{user.id}.png'))
    return render_template('profile/view.html', user=user, avatar_exists=avatar_exists, avatar_path=avatar_path)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Редактирование профиля текущего пользователя"""
    if request.method == 'POST':
        # 1. Если нажата кнопка удаления аватарки, пропускаем валидацию и сразу удаляем
        if 'delete_avatar' in request.form:
            delete_avatar(current_user.id)
            flash('Аватарка удалена!', 'success')
            return redirect(url_for('profile.edit'))
        
        # 2. Обычное сохранение профиля
        username = request.form.get('username', '').strip()
        
        
        errors = []
        # Валидация имени
        if not username or len(username) < 3:
            errors.append('Имя пользователя должно содержать минимум 3 символа')
        elif not re.match(r'^[a-zA-Z0-9_-]+$', username):
            errors.append('Имя пользователя может содержать только латиницу, цифры, _ и -')
        elif username != current_user.username and User.query.filter_by(username=username).first():
            errors.append('Пользователь с таким именем уже существует')
        
        
        if errors:
            for err in errors:
                flash(err, 'danger')
        else:
            # Обновляем данные
            current_user.username = username
            
            # Обработка загрузки новой аватарки
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and file.filename and allowed_file(file.filename):
                    delete_avatar(current_user.id) # Удаляем старую перед сохранением новой
                    save_avatar(current_user.id, file)
                    flash('Аватарка обновлена!', 'success')
                elif file and file.filename:
                    flash('Недопустимый формат файла. Разрешены: PNG, JPG, JPEG, GIF', 'danger')
            
            db.session.commit()
            flash('Профиль успешно обновлён!', 'success')
            return redirect(url_for('profile.view', user_id=current_user.id))

    # Передаем avatar_path в шаблон для отображения
    avatar_exists = os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', f'{current_user.id}.png'))
    avatar_path = f'/uploads/avatars/{current_user.id}.png'
    
    return render_template('profile/edit.html', user=current_user, avatar_exists=avatar_exists, avatar_path=avatar_path)
    