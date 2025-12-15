"""Blueprint per la gestione del cambio tema.

Questo modulo definisce una rotta per cambiare il tema grafico dell'applicazione.
Il tema scelto viene salvato nella sessione dell'utente così da applicarsi solo
alla sessione corrente (non influisce sugli altri utenti).
"""

from flask import Blueprint, redirect, request, session, url_for
from flask_login import login_required

theme_bp = Blueprint('theme', __name__)

@theme_bp.route('/change-theme/<theme>')
@login_required
def change_theme(theme):
    """Cambia il tema grafico salvando la scelta nella sessione utente.

    Parametri:
        theme (str): nome del tema, deve essere 'matrix' o 'professional'.

    Ritorna:
        redirect alla pagina precedente o alla dashboard se la pagina
        precedente non è disponibile.
    """
    if theme in ('matrix', 'professional'):
        session['theme'] = theme
    # Ritorna alla pagina da cui è stato invocato il cambio tema o alla dashboard.
    return redirect(request.referrer or url_for('dashboard.index'))