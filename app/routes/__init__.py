from .dashboard import dashboard_bp
from .veicoli import veicoli_bp
from .fornitori import fornitori_bp
from .manutenzioni import manutenzioni_bp
from .scadenze import scadenze_bp
from .auth import auth_bp
# Il modulo percorrenze è stato rimosso nella versione 1.24.2, pertanto non viene più importato

__all__ = ['dashboard_bp', 'veicoli_bp', 'fornitori_bp', 'manutenzioni_bp', 'scadenze_bp', 'auth_bp', 'scheda_km_bp']

from .scheda_km import scheda_km_bp
