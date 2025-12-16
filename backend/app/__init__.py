"""
Factory Application - Backend API REST
Matrix Fleet Manager
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restx import Api

# Inizializza estensioni
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name='default'):
    """
    Factory pattern per creare l'applicazione Flask

    Args:
        config_name: Nome della configurazione da usare (development/production)

    Returns:
        app: Applicazione Flask configurata
    """
    app = Flask(__name__)

    # Carica configurazione
    from config import config
    app.config.from_object(config[config_name])

    # Inizializza estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configura CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Crea API con Flask-RESTX
    api = Api(
        app,
        version='1.0',
        title='Matrix Fleet Manager API',
        description='API REST per gestione parco auto aziendale',
        doc='/api/docs',
        prefix='/api'
    )

    # Importa modelli (DOPO db.init_app)
    from app import models

    # Registra namespace API
    from app.api.veicoli import api as veicoli_ns
    from app.auth.routes import api as auth_ns

    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(veicoli_ns, path='/veicoli')

    # Crea tabelle database
    with app.app_context():
        db.create_all()

    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Matrix Fleet Manager API is running'}

    return app
