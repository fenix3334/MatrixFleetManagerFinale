# app/routes/dashboard.py - COMPLETO CON MODULO PERCORRENZE

from flask import Blueprint, render_template, jsonify, session
from flask_login import login_required, current_user
from app.models import (
    Veicolo, Fornitore, Manutenzione, Scadenza, Nucleo,
    PercorrenzaChilometrica, LimiteChilometrico
)
from app.extensions import db
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, text, desc
from app.utils.nuclei import filter_by_nucleo, get_nucleo_corrente_admin

dashboard_bp = Blueprint('dashboard', __name__)

def get_stats_by_nucleo():
    """Calcola statistiche filtrate per nucleo utente o selezione admin"""
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
            percorrenze_query = PercorrenzaChilometrica.query
            limiti_query = LimiteChilometrico.query
        else:
            # Admin con filtro specifico: veicoli e altre entità sono filtrate per nucleo,
            # tranne i fornitori che rimangono condivisi tra tutti i nuclei a partire da v1.7.
            veicoli_query = Veicolo.query.filter_by(nucleo=filtro_admin)
            # Anagrafica fornitori condivisa
            fornitori_query = Fornitore.query
            manutenzioni_query = Manutenzione.query.filter_by(nucleo=filtro_admin)
            scadenze_query = Scadenza.query.filter_by(nucleo=filtro_admin)
            percorrenze_query = PercorrenzaChilometrica.query.filter_by(nucleo=filtro_admin)
            limiti_query = LimiteChilometrico.query.filter_by(nucleo=filtro_admin)
    else:
        # User normale vede solo il suo nucleo
        nucleo_filter = current_user.nucleo
        veicoli_query = Veicolo.query.filter_by(nucleo=nucleo_filter)
        # A partire dalla versione v1.7 l'anagrafica fornitori è condivisa tra tutti i nuclei.
        # Pertanto le statistiche relative ai fornitori non devono essere filtrate per nucleo.
        fornitori_query = Fornitore.query
        manutenzioni_query = Manutenzione.query.filter_by(nucleo=nucleo_filter)
        scadenze_query = Scadenza.query.filter_by(nucleo=nucleo_filter)
        percorrenze_query = PercorrenzaChilometrica.query.filter_by(nucleo=nucleo_filter)
        limiti_query = LimiteChilometrico.query.filter_by(nucleo=nucleo_filter)
    
    # Calcola statistiche esistenti
    stats['totale_veicoli'] = veicoli_query.count()
    stats['veicoli_attivi'] = veicoli_query.filter_by(stato='Attivo').count()
    stats['totale_fornitori'] = fornitori_query.count()  # AGGIUNTO
    stats['fornitori_attivi'] = fornitori_query.filter_by(attivo=True).count()
    stats['societa_noleggio'] = fornitori_query.filter(
        (Fornitore.settore.like('%noleggio%')) |
        (Fornitore.settore_2.like('%noleggio%')) |
        (Fornitore.settore_3.like('%noleggio%'))
    ).count()
    
    # Manutenzioni
    stats['totale_manutenzioni'] = manutenzioni_query.count()  # AGGIUNTO
    stats['manutenzioni_totali'] = manutenzioni_query.count()
    stats['manutenzioni_da_fare'] = manutenzioni_query.filter_by(stato='Da Fare').count()
    stats['manutenzioni_fatto'] = manutenzioni_query.filter_by(stato='Fatto').count()
    
    # Scadenze
    oggi = date.today()
    stats['scadenze_totali'] = scadenze_query.count()
    stats['scadenze_scadute'] = scadenze_query.filter(Scadenza.data_scadenza < oggi).count()
    stats['scadenze_prossime'] = scadenze_query.filter(
        and_(
            Scadenza.data_scadenza >= oggi,
            Scadenza.data_scadenza <= oggi + timedelta(days=30)
        )
    ).count()
    stats['scadenze_urgenti'] = stats['scadenze_prossime']  # AGGIUNTO per template
    
    # NUOVE STATISTICHE PERCORRENZE CHILOMETRICHE
    mese_corrente = date.today().replace(day=1)
    anno_corrente = date.today().year
    
    # Percorrenze mese corrente
    percorrenze_mese = percorrenze_query.filter(
        PercorrenzaChilometrica.anno == anno_corrente,
        PercorrenzaChilometrica.mese == date.today().month
    )
    
    stats['percorrenze_mese_corrente'] = percorrenze_mese.count()
    
    # Km totali mese corrente
    km_mese = db.session.query(
        func.sum(PercorrenzaChilometrica.km_finali - PercorrenzaChilometrica.km_iniziali)
    ).filter(
        PercorrenzaChilometrica.anno == anno_corrente,
        PercorrenzaChilometrica.mese == date.today().month
    )
    
    if current_user.ruolo != 'admin' or session.get('admin_nucleo_filter', 'tutti') != 'tutti':
        nucleo_corrente = get_nucleo_corrente_admin() if current_user.ruolo == 'admin' else current_user.nucleo
        if nucleo_corrente:
            km_mese = km_mese.filter(PercorrenzaChilometrica.nucleo == nucleo_corrente)
    
    stats['km_totali_mese'] = km_mese.scalar() or 0
    
    # Limiti chilometrici attivi
    stats['limiti_attivi'] = limiti_query.filter_by(attivo=True).count()
    
    # Veicoli con limiti
    veicoli_con_limiti = db.session.query(LimiteChilometrico.veicolo_id).filter_by(attivo=True)
    if current_user.ruolo != 'admin' or session.get('admin_nucleo_filter', 'tutti') != 'tutti':
        nucleo_corrente = get_nucleo_corrente_admin() if current_user.ruolo == 'admin' else current_user.nucleo
        if nucleo_corrente:
            veicoli_con_limiti = veicoli_con_limiti.filter(LimiteChilometrico.nucleo == nucleo_corrente)
    
    stats['veicoli_con_limiti'] = veicoli_con_limiti.distinct().count()
    
    # ALERT SUPERAMENTI CHILOMETRICI
    stats['alert_superamenti'] = get_alert_superamenti_dashboard()
    
    return stats

def get_alert_superamenti_dashboard():
    """Calcola alert superamenti per dashboard"""
    oggi = date.today()
    
    # Query percorrenze mese corrente
    query = PercorrenzaChilometrica.query.filter(
        PercorrenzaChilometrica.anno == oggi.year,
        PercorrenzaChilometrica.mese == oggi.month
    )
    
    # Applica filtro nucleo
    if current_user.ruolo != 'admin' or session.get('admin_nucleo_filter', 'tutti') != 'tutti':
        nucleo_corrente = get_nucleo_corrente_admin() if current_user.ruolo == 'admin' else current_user.nucleo
        if nucleo_corrente:
            query = query.filter(PercorrenzaChilometrica.nucleo == nucleo_corrente)
    
    superamenti = []
    costo_totale = 0
    
    for percorrenza in query.all():
        superamento = percorrenza.check_superamento_limite()
        if superamento:
            # Calcola percentuale utilizzo e livello alert
            limite_mensile = superamento['limite_mensile']
            km_percorsi = percorrenza.km_percorsi
            percentuale_utilizzo = round((km_percorsi / limite_mensile) * 100, 1) if limite_mensile > 0 else 0
            
            # Determina livello alert
            if percentuale_utilizzo >= 150:
                livello_alert = "CRITICO"
            elif percentuale_utilizzo >= 120:
                livello_alert = "ALTO"
            elif percentuale_utilizzo >= 100:
                livello_alert = "MEDIO"
            else:
                livello_alert = "BASSO"
            
            # Calcola km residui (negativi se superato)
            km_residui = limite_mensile - km_percorsi
            
            superamenti.append({
                'veicolo': percorrenza.veicolo,
                'veicolo_id': percorrenza.veicolo_id,
                'km_eccedenza': superamento['eccedenza_km'],
                'costo': superamento['costo_stimato'],
                'livello_alert': livello_alert,
                'percentuale_utilizzo': percentuale_utilizzo,
                'km_residui': km_residui
            })
            costo_totale += superamento['costo_stimato']
    
    return {
        'count': len(superamenti),
        'dettagli': superamenti[:5],  # Primi 5 per dashboard
        'costo_totale': costo_totale
    }

def get_attivita_recenti():
    """Ottieni attività recenti per dashboard"""
    attivita = []
    
    # Determina filtro nucleo
    base_filter = {}
    if current_user.ruolo != 'admin' or session.get('admin_nucleo_filter', 'tutti') != 'tutti':
        nucleo_corrente = get_nucleo_corrente_admin() if current_user.ruolo == 'admin' else current_user.nucleo
        if nucleo_corrente:
            base_filter['nucleo'] = nucleo_corrente
    
    # Manutenzioni recenti (ultime 5)
    manutenzioni = Manutenzione.query.filter_by(**base_filter).order_by(
        desc(Manutenzione.data_creazione)
    ).limit(5).all()
    
    for m in manutenzioni:
        attivita.append({
            'tipo': 'manutenzione',
            'icona': 'wrench',
            'titolo': f'Manutenzione {m.veicolo.targa}',
            'descrizione': m.tipo_intervento,
            'data': m.data_creazione,
            'url': f'/manutenzioni/{m.id}'
        })
    
    # Scadenze recenti (ultime 5)
    scadenze = Scadenza.query.filter_by(**base_filter).order_by(
        desc(Scadenza.data_creazione)
    ).limit(5).all()
    
    for s in scadenze:
        attivita.append({
            'tipo': 'scadenza',
            'icona': 'calendar-x',
            'titolo': f'Scadenza {s.veicolo.targa}',
            'descrizione': s.tipo_scadenza,
            'data': s.data_creazione,
            'url': f'/scadenze/{s.id}'
        })
    
    # Nota: il modulo "percorrenze" è stato deprecato e le relative pagine sono state rimosse.
    # Pertanto non aggiungiamo più le percorrenze alle attività recenti.
    
    # Ordina per data decrescente e prendi le prime 10
    attivita.sort(key=lambda x: x['data'], reverse=True)
    return attivita[:10]

def get_scadenze_urgenti():
    """Ottieni scadenze urgenti per dashboard"""
    oggi = date.today()
    limite_urgenza = oggi + timedelta(days=30)
    
    # Query base
    query = Scadenza.query.filter(
        Scadenza.data_scadenza <= limite_urgenza,
        Scadenza.stato == 'Attiva'
    )
    
    # Applica filtro nucleo
    if current_user.ruolo != 'admin' or session.get('admin_nucleo_filter', 'tutti') != 'tutti':
        nucleo_corrente = get_nucleo_corrente_admin() if current_user.ruolo == 'admin' else current_user.nucleo
        if nucleo_corrente:
            query = query.filter(Scadenza.nucleo == nucleo_corrente)
    
    scadenze = query.order_by(Scadenza.data_scadenza).limit(10).all()
    
    return scadenze  # Restituisce direttamente le scadenze

def get_manutenzioni_da_fare():
    """Ottieni manutenzioni da fare per dashboard"""
    # Query base
    query = Manutenzione.query.filter(Manutenzione.stato == 'Da Fare')
    
    # Applica filtro nucleo
    if current_user.ruolo != 'admin' or session.get('admin_nucleo_filter', 'tutti') != 'tutti':
        nucleo_corrente = get_nucleo_corrente_admin() if current_user.ruolo == 'admin' else current_user.nucleo
        if nucleo_corrente:
            query = query.filter(Manutenzione.nucleo == nucleo_corrente)
    
    manutenzioni = query.order_by(Manutenzione.data_intervento).limit(10).all()
    
    return manutenzioni  # Restituisce direttamente le manutenzioni

def get_nuclei_info():
    """Ottieni informazioni sui nuclei per dashboard admin"""
    if current_user.ruolo != 'admin':
        return []
    
    try:
        # Query per ottenere informazioni sui nuclei
        nuclei = Nucleo.query.filter_by(attivo=True).all()
        
        nuclei_info = []
        for nucleo in nuclei:
            # Conta veicoli per nucleo
            veicoli_count = Veicolo.query.filter_by(nucleo=nucleo.nome).count()
            
            # Conta manutenzioni da fare per nucleo
            manutenzioni_da_fare = Manutenzione.query.filter_by(
                nucleo=nucleo.nome, 
                stato='Da Fare'
            ).count()
            
            nuclei_info.append({
                'nome': nucleo.nome,
                'descrizione': nucleo.descrizione,
                'veicoli': veicoli_count,
                'manutenzioni_da_fare': manutenzioni_da_fare
            })
        
        return nuclei_info
    except Exception as e:
        # Se la tabella nuclei non esiste, restituisce info di base
        return [
            {
                'nome': 'Via Capitel',
                'descrizione': 'Nucleo principale',
                'veicoli': Veicolo.query.filter_by(nucleo='Via Capitel').count(),
                'manutenzioni_da_fare': Manutenzione.query.filter_by(nucleo='Via Capitel', stato='Da Fare').count()
            },
            {
                'nome': 'Campania',
                'descrizione': 'Nucleo Campania',
                'veicoli': Veicolo.query.filter_by(nucleo='Campania').count(),
                'manutenzioni_da_fare': Manutenzione.query.filter_by(nucleo='Campania', stato='Da Fare').count()
            }
        ]

@dashboard_bp.route('/')
@login_required  
def index():
    """Dashboard principale"""
    stats = get_stats_by_nucleo()
    attivita_recenti = get_attivita_recenti()
    scadenze_urgenti = get_scadenze_urgenti()
    
    # Dati per grafici percorrenze
    grafico_percorrenze = get_dati_grafico_percorrenze()
    
    # AGGIUNGIAMO TUTTE LE VARIABILI CHE IL TEMPLATE SI ASPETTA
    from app.utils.nuclei import get_nuclei_disponibili, get_nucleo_corrente_admin
    
    # Info nucleo per template esistente
    nucleo_corrente = get_nucleo_corrente_admin() if current_user.ruolo == 'admin' else current_user.nucleo
    
    nucleo_info = {
        'is_admin': current_user.ruolo == 'admin',
        'nucleo_corrente': current_user.nucleo,
        'nucleo_filter': nucleo_corrente,
        'nuclei_disponibili': get_nuclei_disponibili(),
        'nome': nucleo_corrente or current_user.nucleo,
        'username': current_user.username,
        'visualizza': nucleo_corrente or current_user.nucleo,
        'filtro_attivo': session.get('admin_nucleo_filter', 'tutti') if current_user.ruolo == 'admin' else current_user.nucleo
    }
    
    # Admin selector per template
    admin_selector = None
    if current_user.ruolo == 'admin':
        admin_selector = [
            ('tutti', 'Tutti i Nuclei'),
            ('Via Capitel', 'Via Capitel'),
            ('Campania', 'Campania')
        ]
    
    # STATISTICHE PERCORRENZE PER TEMPLATE
    alert_superamenti = get_alert_superamenti_dashboard()
    stats_percorrenze = {
        'totale_alert': alert_superamenti['count'],
        'alert_critico': len([d for d in alert_superamenti['dettagli'] if d['km_eccedenza'] > 500]),
        'alert_alto': len([d for d in alert_superamenti['dettagli'] if 200 < d['km_eccedenza'] <= 500]),
        'alert_medio': len([d for d in alert_superamenti['dettagli'] if 50 < d['km_eccedenza'] <= 200]),
        'alert_scadenza': 0  # Placeholder per alert scadenze limiti
    }
    
    # Ottieni altre informazioni per dashboard
    manutenzioni_da_fare = get_manutenzioni_da_fare()
    nuclei_info = get_nuclei_info()
    
    # AGGIUNGIAMO ANCHE ALTRE VARIABILI CHE POTREBBERO SERVIRE
    context = {
        'stats': stats,
        'stats_percorrenze': stats_percorrenze,  # VARIABILE MANCANTE AGGIUNTA
        'alert_percorrenze': alert_superamenti['dettagli'],  # Per il pannello dettagli
        'attivita_recenti': attivita_recenti,
        'scadenze_urgenti': scadenze_urgenti,
        'manutenzioni_da_fare': manutenzioni_da_fare,
        'nuclei_info': nuclei_info,
        'grafico_percorrenze': grafico_percorrenze,
        'nucleo_info': nucleo_info,
        'admin_selector': admin_selector,  # AGGIUNTO
        'current_user': current_user,
        'page_title': 'Dashboard Matrix Fleet Manager'
    }
    
    return render_template('dashboard.html', **context)

def get_dati_grafico_percorrenze():
    """Dati per grafico percorrenze ultimi 6 mesi"""
    oggi = date.today()
    dati = []
    
    for i in range(5, -1, -1):  # Ultimi 6 mesi
        if oggi.month - i > 0:
            mese = oggi.month - i
            anno = oggi.year
        else:
            mese = 12 + (oggi.month - i)
            anno = oggi.year - 1
        
        # Query percorrenze per il mese
        query = PercorrenzaChilometrica.query.filter(
            PercorrenzaChilometrica.anno == anno,
            PercorrenzaChilometrica.mese == mese
        )
        
        # Applica filtro nucleo
        if current_user.ruolo != 'admin' or session.get('admin_nucleo_filter', 'tutti') != 'tutti':
            nucleo_corrente = get_nucleo_corrente_admin() if current_user.ruolo == 'admin' else current_user.nucleo
            if nucleo_corrente:
                query = query.filter(PercorrenzaChilometrica.nucleo == nucleo_corrente)
        
        percorrenze = query.all()
        km_totali = sum(p.km_percorsi for p in percorrenze)
        
        # Conta superamenti
        superamenti = 0
        for p in percorrenze:
            if p.check_superamento_limite():
                superamenti += 1
        
        dati.append({
            'mese': f"{mese:02d}/{anno}",
            'km_totali': km_totali,
            'rilevazioni': len(percorrenze),
            'superamenti': superamenti
        })
    
    return dati

@dashboard_bp.route('/api/statistiche')
@login_required
def api_statistiche():
    """API per statistiche real-time dashboard"""
    stats = get_stats_by_nucleo()
    return jsonify(stats)

@dashboard_bp.route('/api/alert-superamenti')
@login_required
def api_alert_superamenti():
    """API per alert superamenti chilometrici"""
    alert = get_alert_superamenti_dashboard()
    return jsonify(alert)

@dashboard_bp.route('/api/grafico-percorrenze')
@login_required
def api_grafico_percorrenze():
    """API per dati grafico percorrenze"""
    dati = get_dati_grafico_percorrenze()
    return jsonify(dati)
