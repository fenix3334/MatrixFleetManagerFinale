from flask import Flask
from app.extensions import db, migrate, login_manager
from app.routes.dashboard import dashboard_bp
from app.routes.veicoli import veicoli_bp
from app.routes.fornitori import fornitori_bp  
from app.routes.manutenzioni import manutenzioni_bp
from app.routes.scadenze import scadenze_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Inizializza estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configura Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Effettua il login per accedere a questa pagina.'
    login_manager.login_message_category = 'info'
    
    # User loader per Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # IMPORTANTE: Importa i modelli DOPO aver inizializzato db
    from app import models
    
    # Registra blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')  # NUOVO BLUEPRINT
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(veicoli_bp, url_prefix='/veicoli')
    app.register_blueprint(fornitori_bp, url_prefix='/fornitori')
    app.register_blueprint(manutenzioni_bp, url_prefix='/manutenzioni')
    app.register_blueprint(scadenze_bp, url_prefix='/scadenze')
    
    # Crea tabelle
    with app.app_context():
        db.create_all()
    
    return app
