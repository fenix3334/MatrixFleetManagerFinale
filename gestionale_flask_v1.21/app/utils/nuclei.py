"""
Utility per gestione separazione nuclei
Matrix Fleet Manager
"""

from flask_login import current_user
from app.models import Nucleo, Veicolo, Fornitore, Manutenzione, Scadenza
from sqlalchemy import and_

def get_nuclei_disponibili():
    """Restituisce lista nuclei disponibili per l'utente corrente"""
    if not current_user.is_authenticated:
        return []
    
    if current_user.is_admin:
        # Admin vede tutti i nuclei attivi
        return Nucleo.query.filter_by(attivo=True).order_by(Nucleo.nome).all()
    else:
        # User normale vede solo il suo nucleo
        return Nucleo.query.filter_by(nome=current_user.nucleo, attivo=True).all()

def get_nucleo_corrente():
    """Restituisce il nucleo dell'utente corrente"""
    if not current_user.is_authenticated:
        return None
    return current_user.nucleo

def is_admin_user():
    """Verifica se l'utente corrente è admin"""
    if not current_user.is_authenticated:
        return False
    return current_user.is_admin

def get_nucleo_corrente_admin():
    """
    Restituisce il nucleo che l'admin sta visualizzando attualmente
    """
    from flask import session
    
    if current_user.ruolo == 'admin':
        filtro = session.get('admin_nucleo_filter', 'tutti')
        return None if filtro == 'tutti' else filtro
    else:
        return current_user.nucleo

def should_filter_by_nucleo():
    """Determina se applicare filtro nucleo alle query"""
    from flask import session
    
    if current_user.ruolo == 'admin':
        # Admin applica filtro solo se ha selezionato un nucleo specifico
        return session.get('admin_nucleo_filter', 'tutti') != 'tutti'
    else:
        # User normale sempre con filtro
        return True

def filter_by_nucleo(query, model_class):
    """
    Applica filtro nucleo automatico alla query
    - Se utente non autenticato: nessun risultato
    - Se admin con "tutti": nessun filtro
    - Se admin con nucleo specifico: filtra per quel nucleo
    - Se user normale: filtra per suo nucleo
    """
    if not current_user.is_authenticated:
        return query.filter(False)  # Nessun risultato per utenti non autenticati
    
    if not should_filter_by_nucleo():
        # Admin che visualizza tutti i nuclei
        return query
    else:
        # Admin con filtro specifico o user normale
        nucleo_target = get_nucleo_corrente_admin()
        return query.filter(model_class.nucleo == nucleo_target)

def get_veicoli_by_nucleo():
    """Restituisce veicoli filtrati per nucleo utente"""
    query = Veicolo.query
    return filter_by_nucleo(query, Veicolo)

def get_fornitori_by_nucleo():
    """Restituisce fornitori filtrati per nucleo utente"""
    query = Fornitore.query
    return filter_by_nucleo(query, Fornitore)

def get_manutenzioni_by_nucleo():
    """Restituisce manutenzioni filtrate per nucleo utente"""
    query = Manutenzione.query
    return filter_by_nucleo(query, Manutenzione)

def get_scadenze_by_nucleo():
    """Restituisce scadenze filtrate per nucleo utente"""
    query = Scadenza.query
    return filter_by_nucleo(query, Scadenza)

def can_access_record(record):
    """
    Verifica se l'utente può accedere a un record specifico
    Controlla il nucleo del record vs nucleo utente
    """
    if not current_user.is_authenticated:
        return False
    
    if current_user.is_admin:
        return True
    
    # Verifica che il record abbia il campo nucleo e corrisponda
    if hasattr(record, 'nucleo'):
        return record.nucleo == current_user.nucleo
    
    return False

def get_veicoli_for_choices():
    """Restituisce veicoli per dropdown nelle form (filtrati per nucleo)"""
    veicoli = get_veicoli_by_nucleo().filter_by(stato='Attivo').order_by(Veicolo.targa).all()
    return [(v.id, f"{v.targa} - {v.marca} {v.modello}") for v in veicoli]

def get_fornitori_for_choices():
    """Restituisce fornitori per dropdown nelle form (filtrati per nucleo)"""
    fornitori = get_fornitori_by_nucleo().filter_by(attivo=True).order_by(Fornitore.ragione_sociale).all()
    return [(f.id, f.ragione_sociale) for f in fornitori]

def get_societa_noleggio_for_choices():
    """Restituisce società noleggio per dropdown (filtrati per nucleo)"""
    # Le società noleggio sono nell'anagrafica fornitori
    fornitori = get_fornitori_by_nucleo().filter(
        and_(
            Fornitore.attivo == True,
            Fornitore.settore.contains('Noleggio')
        )
    ).order_by(Fornitore.ragione_sociale).all()
    
    choices = [('', 'Proprietà aziendale')]  # Opzione default
    choices.extend([(f.id, f.ragione_sociale) for f in fornitori])
    return choices

def validate_nucleo_access(record_id, model_class):
    """
    Valida che l'utente possa accedere a un record specifico
    Utilizzato nei decorator per route di dettaglio/modifica
    """
    if not current_user.is_authenticated:
        return False
    
    record = model_class.query.get(record_id)
    if not record:
        return False
    
    return can_access_record(record)

def get_stats_by_nucleo():
    """Calcola statistiche filtrate per nucleo utente o selezione admin"""
    stats = {}
    
    if not current_user.is_authenticated:
        return stats
    
    # Veicoli
    veicoli_query = get_veicoli_by_nucleo()
    stats['totale_veicoli'] = veicoli_query.count()
    stats['veicoli_attivi'] = veicoli_query.filter_by(stato='Attivo').count()
    
    # Fornitori
    fornitori_query = get_fornitori_by_nucleo()
    stats['totale_fornitori'] = fornitori_query.count()
    stats['fornitori_attivi'] = fornitori_query.filter_by(attivo=True).count()
    
    # Manutenzioni
    manutenzioni_query = get_manutenzioni_by_nucleo()
    stats['totale_manutenzioni'] = manutenzioni_query.count()
    stats['manutenzioni_da_fare'] = manutenzioni_query.filter_by(stato='Da Fare').count()
    
    # Scadenze
    from sqlalchemy import func, text
    scadenze_query = get_scadenze_by_nucleo()
    stats['totale_scadenze'] = scadenze_query.count()
    stats['scadenze_urgenti'] = scadenze_query.filter(
        and_(
            Scadenza.stato == 'Attiva',
            text("date(data_scadenza) <= date('now', '+30 days')")
        )
    ).count()
    
    return stats

def get_nucleo_info():
    """Restituisce informazioni sul nucleo correntemente visualizzato"""
    from flask import session
    
    if not current_user.is_authenticated:
        return None
    
    if current_user.ruolo == 'admin':
        filtro_admin = session.get('admin_nucleo_filter', 'tutti')
        
        if filtro_admin == 'tutti':
            return {
                'nome': 'AMMINISTRATORE',
                'is_admin': True,
                'username': current_user.username,
                'ruolo': 'admin',
                'visualizza': 'Tutti i nuclei',
                'filtro_attivo': 'tutti'
            }
        else:
            nucleo_obj = Nucleo.query.filter_by(nome=filtro_admin).first()
            return {
                'nome': filtro_admin,
                'is_admin': True,
                'username': current_user.username,
                'ruolo': 'admin',
                'visualizza': f'Solo nucleo {filtro_admin}',
                'descrizione': nucleo_obj.descrizione if nucleo_obj else '',
                'filtro_attivo': filtro_admin
            }
    else:
        nucleo_obj = Nucleo.query.filter_by(nome=current_user.nucleo).first()
        return {
            'nome': current_user.nucleo,
            'is_admin': False,
            'username': current_user.username,
            'ruolo': 'user',
            'visualizza': f'Nucleo {current_user.nucleo}',
            'descrizione': nucleo_obj.descrizione if nucleo_obj else '',
            'filtro_attivo': current_user.nucleo
        }

def set_nucleo_on_create(form_data):
    """
    Imposta automaticamente il nucleo sui nuovi record
    Da chiamare prima del salvataggio
    """
    if current_user.is_authenticated and not current_user.is_admin:
        form_data['nucleo'] = current_user.nucleo
    return form_data

def get_dashboard_data():
    """Restituisce tutti i dati necessari per la dashboard filtrati per nucleo o selezione admin"""
    from datetime import date
    from sqlalchemy import func, text
    
    if not current_user.is_authenticated:
        return {}
    
    # Statistiche
    stats = get_stats_by_nucleo()
    
    # Scadenze urgenti (prossimi 30 giorni)
    scadenze_urgenti = get_scadenze_by_nucleo().filter(
        and_(
            Scadenza.stato == 'Attiva',
            text("date(data_scadenza) <= date('now', '+30 days')")
        )
    ).order_by(Scadenza.data_scadenza).limit(5).all()
    
    # Manutenzioni da fare
    manutenzioni_da_fare = get_manutenzioni_by_nucleo().filter_by(
        stato='Da Fare'
    ).order_by(Manutenzione.data_intervento.asc()).limit(8).all()
    
    # Ultime manutenzioni completate
    ultime_manutenzioni = get_manutenzioni_by_nucleo().filter_by(
        stato='Fatto'
    ).order_by(Manutenzione.data_intervento.desc()).limit(5).all()
    
    return {
        'stats': stats,
        'scadenze_urgenti': scadenze_urgenti,
        'manutenzioni_da_fare': manutenzioni_da_fare,
        'ultime_manutenzioni': ultime_manutenzioni,
        'nucleo_info': get_nucleo_info()
    }

def get_nuclei_per_admin_selector():
    """Restituisce lista nuclei per il selettore admin"""
    nuclei = []
    nuclei.append(('tutti', 'Tutti i nuclei'))
    
    nuclei_attivi = Nucleo.query.filter_by(attivo=True).order_by(Nucleo.nome).all()
    for nucleo in nuclei_attivi:
        nuclei.append((nucleo.nome, f'Solo {nucleo.nome}'))
    
    return nuclei
