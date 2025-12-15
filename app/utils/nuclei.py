"""
Utility per gestione separazione nuclei
Matrix Fleet Manager
"""

from flask_login import current_user
from app.models import (
    Nucleo,
    Veicolo,
    Fornitore,
    Manutenzione,
    Scadenza,
    ManutenzionePreventiva,
    Notifica,
    Sinistro,
)
from sqlalchemy import and_

def get_nuclei_disponibili():
    """Restituisce lista nuclei disponibili per l'utente corrente"""
    if not current_user.is_authenticated:
        return []
    
    if current_user.ruolo == 'admin':
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

def get_manutenzioni_preventive_by_nucleo():
    """
    Restituisce le manutenzioni preventive filtrate per nucleo utente.

    Questo metodo sfrutta il medesimo meccanismo di filtro delle altre entità,
    utilizzando il campo `nucleo` del record per determinare l'accesso.
    """
    query = ManutenzionePreventiva.query
    return filter_by_nucleo(query, ManutenzionePreventiva)


def get_sinistri_by_nucleo():
    """
    Restituisce i sinistri filtrati per nucleo utente.

    Come per gli altri moduli, l'accesso è limitato ai record del nucleo
    dell'utente normale, mentre l'admin può filtrare tramite la selezione
    del nucleo nella barra in alto.
    """
    query = Sinistro.query
    return filter_by_nucleo(query, Sinistro)

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
    
    if current_user.ruolo == 'admin':
        # Admin può accedere a tutto se non ha filtro
        from flask import session
        filtro_admin = session.get('admin_nucleo_filter', 'tutti')
        if filtro_admin == 'tutti':
            return True
        # Se ha filtro, deve corrispondere
        return hasattr(record, 'nucleo') and record.nucleo == filtro_admin
    
    # Verifica che il record abbia il campo nucleo e corrisponda
    if hasattr(record, 'nucleo'):
        return record.nucleo == current_user.nucleo
    
    return False

def get_veicoli_for_choices():
    """Restituisce veicoli per dropdown nelle form (filtrati per nucleo)"""
    veicoli = get_veicoli_by_nucleo().filter_by(stato='Attivo').order_by(Veicolo.targa).all()
    return [(v.id, f"{v.targa} - {v.marca} {v.modello}") for v in veicoli]

def get_fornitori_for_choices():
    """Restituisce fornitori per dropdown nelle form.

    Dalla versione v1.7 l'anagrafica fornitori è condivisa fra tutti i nuclei,
    pertanto questa funzione non applica filtri sul campo `nucleo`.  Viene
    restituito l'elenco di tutti i fornitori attivi, ordinati per ragione
    sociale."""
    fornitori = Fornitore.query.filter_by(attivo=True).order_by(Fornitore.ragione_sociale).all()
    return [(f.id, f.ragione_sociale) for f in fornitori]

def get_stats_by_nucleo():
    """Calcola statistiche filtrate per nucleo utente o selezione admin"""
    stats = {}
    
    if not current_user.is_authenticated:
        return stats
    
    # Determina filtro nucleo
    if current_user.ruolo == 'admin':
        from flask import session
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
    from sqlalchemy import text
    stats['scadenze_urgenti'] = scadenze_query.filter(
        and_(
            Scadenza.stato == 'Attiva',
            text("date(data_scadenza) <= date('now', '+30 days')")
        )
    ).count()
    
    return stats

def get_nucleo_info():
    """Restituisce informazioni sul nucleo corrente per l'interfaccia"""
    from flask import session
    
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
