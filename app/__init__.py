from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config



db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите, чтобы получить доступ к этой странице'
    login_manager.login_message_category = 'info'
    
    from app import models
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.profile import bp as profile_bp
    app.register_blueprint(profile_bp)

    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.route('/uploads/avatars/<path:filename>')
    def uploaded_avatar(filename):
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), filename)
    
    @app.route('/uploads/attachments/<path:filename>')
    def uploaded_attachment(filename):
        return send_from_directory(
            os.path.join(app.config['UPLOAD_FOLDER'], 'attachments'), 
            filename, 
            as_attachment=True, 
            download_name=filename
        )
    
    return app
