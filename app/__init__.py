# app/__init__.py - COMPLETO CON MODULO PERCORRENZE

from flask import Flask
from app.extensions import db, migrate, login_manager
from app.routes.dashboard import dashboard_bp
from app.routes.veicoli import veicoli_bp
from app.routes.fornitori import fornitori_bp  
from app.routes.manutenzioni import manutenzioni_bp
from app.routes.scadenze import scadenze_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
# from app.routes.percorrenze import percorrenze_bp  # Il modulo percorrenze è stato rimosso
from app.routes.theme import theme_bp  # Blueprint per cambio tema
from app.routes.report import report_bp  # Blueprint per report veicoli
from app.routes.manutenzioni_preventive import manutenzioni_preventive_bp  # Nuovo blueprint per manutenzioni preventive
from app.routes.policy import policy_bp  # Blueprint per policy e documentazione
from app.routes.allegati import allegati_bp  # Blueprint per allegati manutenzioni
from app.routes.allegati_scadenze import allegati_scadenze_bp  # Blueprint per allegati scadenze
from app.routes.sinistri import sinistri_bp  # Nuovo modulo sinistri
from app.routes.allegati_sinistri import allegati_sinistri_bp  # Blueprint allegati sinistri
from app.routes.versioni import versioni_bp  # Blueprint visualizzazione versioni/CHANGELOG
from app.routes.scheda_km import scheda_km_bp  # Blueprint per schede chilometriche

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Inizializza estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configura Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Effettua il login per accedere a questa pagina.'
    login_manager.login_message_category = 'info'
    
    # User loader per Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # FILTRI CUSTOM PER TEMPLATE
    @app.template_filter('format_number')
    def format_number(value):
        """Formatta un numero con separatori di migliaia"""
        if value is None:
            return '0'
        try:
            return f"{int(value):,}".replace(',', '.')
        except (ValueError, TypeError):
            return str(value)
    
    # IMPORTANTE: Importa i modelli DOPO aver inizializzato db
    from app import models
    
    # Registra blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(veicoli_bp, url_prefix='/veicoli')
    app.register_blueprint(fornitori_bp, url_prefix='/fornitori')
    app.register_blueprint(manutenzioni_bp, url_prefix='/manutenzioni')
    app.register_blueprint(scadenze_bp, url_prefix='/scadenze')
    # app.register_blueprint(percorrenze_bp, url_prefix='/percorrenze')  # Rimosso: modulo percorrenze deprecato
    app.register_blueprint(theme_bp)  # Registrazione blueprint tema
    app.register_blueprint(report_bp)  # Registrazione blueprint report veicoli
    # Registrazione nuovi blueprint per moduli aggiuntivi
    app.register_blueprint(manutenzioni_preventive_bp)
    app.register_blueprint(policy_bp)
    app.register_blueprint(allegati_bp)
    app.register_blueprint(allegati_scadenze_bp)
    app.register_blueprint(sinistri_bp, url_prefix='/sinistri')
    app.register_blueprint(allegati_sinistri_bp)
    app.register_blueprint(versioni_bp)  # Visualizzazione changelog
    app.register_blueprint(scheda_km_bp)  # Schede chilometriche trimestrali
    
    # Crea tabelle e inizializza database
    with app.app_context():
        db.create_all()

        # INIZIALIZZAZIONE AUTOMATICA: Crea utente admin se non esiste
        from app.models import User, Nucleo

        # Crea nuclei predefiniti
        nuclei_default = [
            {'nome': 'Via Capitel', 'descrizione': 'Cure Primarie ADI Via del Capitel'},
            {'nome': 'Campania', 'descrizione': 'Cure Primarie ADI Via Campania'}
        ]
        for nucleo_data in nuclei_default:
            if not Nucleo.query.filter_by(nome=nucleo_data['nome']).first():
                db.session.add(Nucleo(**nucleo_data))

        # Crea utente admin se non esiste
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', nucleo='Via Capitel', ruolo='admin', attivo=True)
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Utente admin creato")

        db.session.commit()

    # Context processor per notifiche dinamiche
    @app.context_processor
    def inject_notifications():
        """
        Calcola notifiche per l'utente corrente.

        Le notifiche includono scadenze imminenti (entro 30 giorni)
        e manutenzioni preventive prossime.  Viene applicato il filtro
        nucleo come per le altre entità.
        """
        from datetime import date, timedelta
        from flask import url_for
        from app.models import Scadenza, ManutenzionePreventiva
        from app.utils.nuclei import filter_by_nucleo
        # Importa current_user da Flask-Login per verificare l'autenticazione
        from flask_login import current_user

        # Utente non autenticato non ha notifiche
        if not current_user.is_authenticated:
            return dict(notifications_count=0, notifications_list=[])

        notifs = []
        oggi = date.today()

        # Scadenze imminenti
        scadenze_query = Scadenza.query.filter(Scadenza.stato == 'Attiva')
        scadenze_query = filter_by_nucleo(scadenze_query, Scadenza)
        scadenze_imminenti = scadenze_query.filter(
            Scadenza.data_scadenza <= oggi + timedelta(days=30)
        ).order_by(Scadenza.data_scadenza).all()
        for sc in scadenze_imminenti:
            try:
                titolo = f"Scadenza {sc.tipo_scadenza} - {sc.veicolo.targa}"
            except Exception:
                titolo = f"Scadenza {sc.tipo_scadenza}"
            messaggio = sc.data_scadenza.strftime('%d/%m/%Y') if sc.data_scadenza else ''
            link = url_for('scadenze.dettaglio_scadenza', id=sc.id)
            notifs.append({'title': titolo, 'message': messaggio, 'url': link})

        # Manutenzioni preventive imminenti
        preventiva_query = filter_by_nucleo(ManutenzionePreventiva.query, ManutenzionePreventiva)
        preventive = preventiva_query.all()
        for p in preventive:
            next_date = p.calcola_prossima_data()
            due = False
            message_parts = []
            if next_date:
                giorni = (next_date - oggi).days
                if giorni <= 30:
                    due = True
                    message_parts.append(next_date.strftime('%d/%m/%Y'))
            # Non disponiamo dei km attuali del veicolo per confrontare con intervallo_km,
            # pertanto non generiamo notifiche basate sui chilometri rimanenti.
            if due:
                try:
                    titolo_p = f"Preventiva {p.tipo_intervento} - {p.veicolo.targa}"
                except Exception:
                    titolo_p = f"Preventiva {p.tipo_intervento}"
                messaggio_p = ' / '.join(message_parts)
                link_p = url_for('manutenzioni_preventive.modifica_preventiva', id=p.id)
                notifs.append({'title': titolo_p, 'message': messaggio_p, 'url': link_p})

        count = len(notifs)
        return dict(notifications_count=count, notifications_list=notifs[:10])

    return app
