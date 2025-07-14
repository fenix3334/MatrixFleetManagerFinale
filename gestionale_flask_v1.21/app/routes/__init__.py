from .dashboard import dashboard_bp
from .veicoli import veicoli_bp
from .fornitori import fornitori_bp
from .manutenzioni import manutenzioni_bp
from .scadenze import scadenze_bp
from .auth import auth_bp

__all__ = ['dashboard_bp', 'veicoli_bp', 'fornitori_bp', 'manutenzioni_bp', 'scadenze_bp', 'auth_bp']
