from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User
import os
import re
from PIL import Image   

bp = Blueprint('profile', __name__, url_prefix='/profile')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@login_required
def save_avatar(user_id, file):
    avatars_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(avatars_dir, exist_ok=True)
    
    img = Image.open(file)
    img = img.convert('RGB')
    filepath = os.path.join(avatars_dir, f'{user_id}.png')
    img.save(filepath, 'PNG')
    return f'/uploads/avatars/{user_id}.png'

@login_required
def delete_avatar(user_id):
    avatars_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    filepath = os.path.join(avatars_dir, f'{user_id}.png')
    if os.path.exists(filepath):
        os.remove(filepath)

@bp.route('/<uuid:user_id>')
@login_required
def view(user_id):
    user = User.query.get_or_404(user_id)
    avatar_path = f'/uploads/avatars/{user.id}.png'
    avatar_exists = os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', f'{user.id}.png'))
    return render_template('profile/view.html', user=user, avatar_exists=avatar_exists, avatar_path=avatar_path)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Редактирование профиля текущего пользователя"""
    if request.method == 'POST':
        if 'delete_avatar' in request.form:
            delete_avatar(current_user.id)
            flash('Аватарка удалена!', 'success')
            return redirect(url_for('profile.edit'))
        
        username = request.form.get('username', '').strip()
        
        
        errors = []
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
            current_user.username = username
            
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

    avatar_exists = os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', f'{current_user.id}.png'))
    avatar_path = f'/uploads/avatars/{current_user.id}.png'
    
    return render_template('profile/edit.html', user=current_user, avatar_exists=avatar_exists, avatar_path=avatar_path)
    