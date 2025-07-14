from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import Veicolo, Fornitore, Manutenzione, Scadenza, Nucleo
from app.extensions import db
from datetime import datetime, date
from sqlalchemy import func, and_, text

dashboard_bp = Blueprint('dashboard', __name__)

def get_stats_by_nucleo():
    """Calcola statistiche filtrate per nucleo utente o selezione admin"""
    from flask import session
    
    stats = {}
    
    if not current_user.is_authenticated:
        return stats
    
    # Determina filtro nucleo
    if current_user.ruolo == 'admin':
        # Admin può filtrare per nucleo specifico o vedere tutti
        filtro_admin = session.get('admin_nucleo_filter', 'tutti')
        
        if filtro_admin == 'tutti':
            # Admin vede tutto
            veicoli_query = Veicolo.query
            fornitori_query = Fornitore.query
            manutenzioni_query = Manutenzione.query
            scadenze_query = Scadenza.query
        else:
            # Admin con filtro specifico
            veicoli_query = Veicolo.query.filter_by(nucleo=filtro_admin)
            fornitori_query = Fornitore.query.filter_by(nucleo=filtro_admin)
            manutenzioni_query = Manutenzione.query.filter_by(nucleo=filtro_admin)
            scadenze_query = Scadenza.query.filter_by(nucleo=filtro_admin)
    else:
        # User normale vede solo il suo nucleo
        nucleo_filter = current_user.nucleo
        veicoli_query = Veicolo.query.filter_by(nucleo=nucleo_filter)
        fornitori_query = Fornitore.query.filter_by(nucleo=nucleo_filter)
        manutenzioni_query = Manutenzione.query.filter_by(nucleo=nucleo_filter)
        scadenze_query = Scadenza.query.filter_by(nucleo=nucleo_filter)
    
    # Calcola statistiche
    stats['totale_veicoli'] = veicoli_query.count()
    stats['veicoli_attivi'] = veicoli_query.filter_by(stato='Attivo').count()
    stats['totale_fornitori'] = fornitori_query.count()
    stats['fornitori_attivi'] = fornitori_query.filter_by(attivo=True).count()
    stats['totale_manutenzioni'] = manutenzioni_query.count()
    stats['manutenzioni_da_fare'] = manutenzioni_query.filter_by(stato='Da Fare').count()
    
    # Scadenze urgenti (prossimi 30 giorni)
    stats['scadenze_urgenti'] = scadenze_query.filter(
        and_(
            Scadenza.stato == 'Attiva',
            text("date(data_scadenza) <= date('now', '+30 days')")
        )
    ).count()
    
    return stats

def get_dashboard_data():
    """Restituisce tutti i dati dashboard filtrati per nucleo o selezione admin"""
    from flask import session
    
    # Determina filtro nucleo
    if current_user.ruolo == 'admin':
        filtro_admin = session.get('admin_nucleo_filter', 'tutti')
        
        if filtro_admin == 'tutti':
            # Admin vede tutto
            scadenze_query = Scadenza.query
            manutenzioni_query = Manutenzione.query
            nucleo_info = {
                'nome': 'AMMINISTRATORE',
                'is_admin': True,
                'username': current_user.username,
                'ruolo': 'admin',
                'visualizza': 'Tutti i nuclei',
                'filtro_attivo': 'tutti'
            }
        else:
            # Admin con filtro specifico
            scadenze_query = Scadenza.query.filter_by(nucleo=filtro_admin)
            manutenzioni_query = Manutenzione.query.filter_by(nucleo=filtro_admin)
            
            nucleo_obj = Nucleo.query.filter_by(nome=filtro_admin).first()
            nucleo_info = {
                'nome': filtro_admin,
                'is_admin': True,
                'username': current_user.username,
                'ruolo': 'admin',
                'visualizza': f'Solo nucleo {filtro_admin}',
                'descrizione': nucleo_obj.descrizione if nucleo_obj else '',
                'filtro_attivo': filtro_admin
            }
    else:
        # User normale vede solo il suo nucleo
        nucleo_filter = current_user.nucleo
        scadenze_query = Scadenza.query.filter_by(nucleo=nucleo_filter)
        manutenzioni_query = Manutenzione.query.filter_by(nucleo=nucleo_filter)
        
        nucleo_obj = Nucleo.query.filter_by(nome=current_user.nucleo).first()
        nucleo_info = {
            'nome': current_user.nucleo,
            'is_admin': False,
            'username': current_user.username,
            'ruolo': 'user',
            'visualizza': f'Nucleo {current_user.nucleo}',
            'descrizione': nucleo_obj.descrizione if nucleo_obj else '',
            'filtro_attivo': current_user.nucleo
        }
    
    # Scadenze urgenti (prossimi 30 giorni)
    scadenze_urgenti = scadenze_query.filter(
        and_(
            Scadenza.stato == 'Attiva',
            text("date(data_scadenza) <= date('now', '+30 days')")
        )
    ).order_by(Scadenza.data_scadenza).limit(5).all()
    
    # Manutenzioni da fare
    manutenzioni_da_fare = manutenzioni_query.filter_by(
        stato='Da Fare'
    ).order_by(Manutenzione.data_intervento.asc()).limit(8).all()
    
    # Ultime manutenzioni completate
    ultime_manutenzioni = manutenzioni_query.filter_by(
        stato='Fatto'
    ).order_by(Manutenzione.data_intervento.desc()).limit(5).all()
    
    return {
        'scadenze_urgenti': scadenze_urgenti,
        'manutenzioni_da_fare': manutenzioni_da_fare,
        'ultime_manutenzioni': ultime_manutenzioni,
        'nucleo_info': nucleo_info
    }

def get_nuclei_per_admin_selector():
    """Restituisce lista nuclei per il selettore admin"""
    nuclei = []
    nuclei.append(('tutti', 'Tutti i nuclei'))
    
    nuclei_attivi = Nucleo.query.filter_by(attivo=True).order_by(Nucleo.nome).all()
    for nucleo in nuclei_attivi:
        nuclei.append((nucleo.nome, f'Solo {nucleo.nome}'))
    
    return nuclei

@dashboard_bp.route('/')
@login_required
def index():
    # Statistiche filtrate per nucleo o selezione admin
    stats = get_stats_by_nucleo()
    
    # Dati dashboard filtrati
    dashboard_data = get_dashboard_data()
    
    # Informazioni nuclei (per admin che visualizza tutti)
    nuclei_info = []
    admin_selector = []
    
    if current_user.ruolo == 'admin':
        # Opzioni selettore nucleo per admin
        admin_selector = get_nuclei_per_admin_selector()
        
        # Se admin visualizza "tutti", mostra panoramica nuclei
        from flask import session
        if session.get('admin_nucleo_filter', 'tutti') == 'tutti':
            nuclei = Nucleo.query.filter_by(attivo=True).all()
            for nucleo in nuclei:
                nucleo_stats = {
                    'nome': nucleo.nome,
                    'descrizione': nucleo.descrizione,
                    'veicoli': Veicolo.query.filter_by(nucleo=nucleo.nome).count(),
                    'fornitori': Fornitore.query.filter_by(nucleo=nucleo.nome).count(),
                    'manutenzioni_da_fare': Manutenzione.query.filter_by(
                        nucleo=nucleo.nome, stato='Da Fare'
                    ).count(),
                    'scadenze_urgenti': Scadenza.query.filter(
                        and_(
                            Scadenza.nucleo == nucleo.nome,
                            Scadenza.stato == 'Attiva',
                            text("date(data_scadenza) <= date('now', '+30 days')")
                        )
                    ).count()
                }
                nuclei_info.append(nucleo_stats)
    
    return render_template('dashboard.html', 
                         stats=stats,
                         scadenze_urgenti=dashboard_data['scadenze_urgenti'],
                         manutenzioni_da_fare=dashboard_data['manutenzioni_da_fare'],
                         ultime_manutenzioni=dashboard_data['ultime_manutenzioni'],
                         nucleo_info=dashboard_data['nucleo_info'],
                         nuclei_info=nuclei_info,
                         admin_selector=admin_selector)

@dashboard_bp.route('/api/statistiche')
@login_required
def api_statistiche():
    """API per statistiche in tempo reale (nome diverso per evitare conflitti)"""
    stats = get_stats_by_nucleo()
    return jsonify(stats)

@dashboard_bp.route('/api/nuclei-panoramica')
@login_required
def api_nuclei_panoramica():
    """API per statistiche per tutti i nuclei (solo admin)"""
    if current_user.ruolo != 'admin':
        return jsonify({'error': 'Accesso negato'}), 403
    
    nuclei_stats = []
    nuclei = Nucleo.query.filter_by(attivo=True).all()
    
    for nucleo in nuclei:
        stats = {
            'nome': nucleo.nome,
            'veicoli_attivi': Veicolo.query.filter_by(nucleo=nucleo.nome, stato='Attivo').count(),
            'manutenzioni_da_fare': Manutenzione.query.filter_by(nucleo=nucleo.nome, stato='Da Fare').count(),
            'scadenze_urgenti': Scadenza.query.filter(
                and_(
                    Scadenza.nucleo == nucleo.nome,
                    Scadenza.stato == 'Attiva',
                    text("date(data_scadenza) <= date('now', '+30 days')")
                )
            ).count()
        }
        nuclei_stats.append(stats)
    
    return jsonify(nuclei_stats)
