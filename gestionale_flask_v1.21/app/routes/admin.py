from flask import Blueprint, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from app.models import Nucleo

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/cambia-nucleo', methods=['POST'])
@login_required
def cambia_nucleo():
    """Permette all'admin di cambiare il nucleo visualizzato"""
    
    if current_user.ruolo != 'admin':
        flash('Accesso negato: solo gli amministratori possono cambiare nucleo', 'error')
        return redirect(url_for('dashboard.index'))
    
    nucleo_selezionato = request.form.get('nucleo_admin')
    
    # Valida la scelta
    if nucleo_selezionato == 'tutti':
        session['admin_nucleo_filter'] = 'tutti'
        flash('Visualizzazione impostata: Tutti i nuclei', 'info')
    else:
        # Verifica che il nucleo esista
        nucleo = Nucleo.query.filter_by(nome=nucleo_selezionato, attivo=True).first()
        if nucleo:
            session['admin_nucleo_filter'] = nucleo_selezionato
            flash(f'Visualizzazione impostata: Solo nucleo {nucleo_selezionato}', 'info')
        else:
            flash('Nucleo non valido', 'error')
            return redirect(url_for('dashboard.index'))
    
    # Redirect alla pagina precedente o dashboard
    next_page = request.form.get('next') or request.referrer or url_for('dashboard.index')
    return redirect(next_page)

@admin_bp.route('/reset-nucleo')
@login_required 
def reset_nucleo():
    """Reset visualizzazione admin a tutti i nuclei"""
    
    if current_user.ruolo != 'admin':
        return redirect(url_for('dashboard.index'))
    
    session.pop('admin_nucleo_filter', None)
    flash('Visualizzazione ripristinata: Tutti i nuclei', 'info')
    return redirect(url_for('dashboard.index'))
