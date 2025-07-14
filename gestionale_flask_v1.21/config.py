import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'matrix-fleet-manager-supersecret-key-2025'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///matrix_fleet.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # True per vedere le query SQL
    
    # Configurazioni avanzate
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Upload files
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = 'uploads'
    
    # Paginazione
    ITEMS_PER_PAGE = 10
    
    # Timezone
    TIMEZONE = 'Europe/Rome'
