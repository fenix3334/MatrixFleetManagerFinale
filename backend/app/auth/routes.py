"""
Route Autenticazione - Login/Register/Refresh
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from app import db
from app.models import User
from app.schemas import UserSchema, UserLoginSchema, UserRegisterSchema
from marshmallow import ValidationError

# Namespace API
api = Namespace('auth', description='Autenticazione utenti')

# Modelli Flask-RESTX per Swagger
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Nome utente'),
    'password': fields.String(required=True, description='Password')
})

register_model = api.model('Register', {
    'username': fields.String(required=True, description='Nome utente'),
    'password': fields.String(required=True, description='Password'),
    'nucleo': fields.String(description='Nucleo di appartenenza'),
    'ruolo': fields.String(description='Ruolo (user/admin)', default='user')
})

token_response = api.model('TokenResponse', {
    'access_token': fields.String(description='JWT Access Token'),
    'refresh_token': fields.String(description='JWT Refresh Token'),
    'user': fields.Raw(description='Dati utente')
})


@api.route('/login')
class Login(Resource):
    """Login utente"""

    @api.doc('login_user')
    @api.expect(login_model)
    @api.response(200, 'Login effettuato', token_response)
    @api.response(401, 'Credenziali non valide')
    def post(self):
        """
        Login utente con username e password
        Restituisce access_token e refresh_token
        """
        try:
            # Valida input
            schema = UserLoginSchema()
            data = schema.load(request.json)

            # Cerca utente
            user = User.query.filter_by(username=data['username']).first()

            # Verifica password
            if not user or not user.check_password(data['password']):
                return {
                    'success': False,
                    'message': 'Credenziali non valide'
                }, 401

            # Verifica se attivo
            if not user.attivo:
                return {
                    'success': False,
                    'message': 'Account disattivato'
                }, 401

            # Genera token JWT
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            # Serializza utente
            user_schema = UserSchema()
            user_data = user_schema.dump(user)

            return {
                'success': True,
                'message': 'Login effettuato con successo',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_data
            }, 200

        except ValidationError as e:
            return {
                'success': False,
                'message': 'Dati non validi',
                'errors': e.messages
            }, 400
        except Exception as e:
            return {
                'success': False,
                'message': f'Errore durante il login: {str(e)}'
            }, 500


@api.route('/register')
class Register(Resource):
    """Registrazione nuovo utente"""

    @api.doc('register_user')
    @api.expect(register_model)
    @api.response(201, 'Utente registrato', token_response)
    @api.response(400, 'Dati non validi')
    def post(self):
        """
        Registrazione nuovo utente
        Restituisce access_token e refresh_token
        """
        try:
            # Valida input
            schema = UserRegisterSchema()
            data = schema.load(request.json)

            # Verifica se username già esiste
            if User.query.filter_by(username=data['username']).first():
                return {
                    'success': False,
                    'message': 'Username già in uso'
                }, 400

            # Crea nuovo utente
            user = User(
                username=data['username'],
                nucleo=data.get('nucleo', 'Via Capitel'),
                ruolo=data.get('ruolo', 'user'),
                attivo=True
            )
            user.set_password(data['password'])

            # Salva nel database
            db.session.add(user)
            db.session.commit()

            # Genera token JWT
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            # Serializza utente
            user_schema = UserSchema()
            user_data = user_schema.dump(user)

            return {
                'success': True,
                'message': 'Registrazione completata con successo',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_data
            }, 201

        except ValidationError as e:
            return {
                'success': False,
                'message': 'Dati non validi',
                'errors': e.messages
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Errore durante la registrazione: {str(e)}'
            }, 500


@api.route('/me')
class Me(Resource):
    """Informazioni utente corrente"""

    @api.doc('get_current_user', security='Bearer')
    @jwt_required()
    @api.response(200, 'Utente corrente')
    @api.response(401, 'Non autenticato')
    def get(self):
        """
        Ottiene informazioni sull'utente corrente
        Richiede JWT token valido
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return {
                    'success': False,
                    'message': 'Utente non trovato'
                }, 404

            # Serializza utente
            user_schema = UserSchema()
            user_data = user_schema.dump(user)

            return {
                'success': True,
                'user': user_data
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Errore: {str(e)}'
            }, 500


@api.route('/refresh')
class Refresh(Resource):
    """Refresh token"""

    @api.doc('refresh_token', security='Bearer')
    @jwt_required(refresh=True)
    @api.response(200, 'Token aggiornato')
    def post(self):
        """
        Ottiene un nuovo access_token usando il refresh_token
        """
        try:
            user_id = get_jwt_identity()
            access_token = create_access_token(identity=user_id)

            return {
                'success': True,
                'access_token': access_token
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Errore: {str(e)}'
            }, 500
