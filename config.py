import os
from dotenv import load_dotenv
HOUR=3600
DAY=24
MONTH=30
SIZE=16

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH_IN_BYTES = SIZE * 1024 * 1024 #1MB = 1024KB = 1024*1024B
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'txt', 'pdf', 'zip'} 
    REMEMBER_COOKIE_DURATION = MONTH * DAY * HOUR
