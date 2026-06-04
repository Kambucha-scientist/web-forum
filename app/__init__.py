
from flask import Flask, render_template
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

    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.utcnow().year}
    
    return app
