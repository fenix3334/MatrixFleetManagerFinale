"""
Modulo Autenticazione JWT
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User


def admin_required():
    """Decorator per verificare che l'utente sia admin"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or not user.is_admin:
                return jsonify({
                    'success': False,
                    'message': 'Accesso negato: richiesti privilegi di amministratore'
                }), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper


def get_current_user():
    """Ottiene l'utente corrente dal JWT"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)
