# app/models.py - COMPLETO CON MODULO PERCORRENZE

from app.extensions import db
from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# MODELLO PER GESTIONE NUCLEI DINAMICA
class Nucleo(db.Model):
    __tablename__ = 'nuclei'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descrizione = db.Column(db.String(200))
    indirizzo = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Nucleo {self.nome}>'

# MODELLO USER
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nucleo = db.Column(db.String(50), default='Via Capitel')
    ruolo = db.Column(db.String(20), default='user')  # admin, user
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        return self.ruolo == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

# 🆕 MODELLO LIMITI CHILOMETRICI - COMPATIBILE CON DB ESISTENTE
class LimiteChilometrico(db.Model):
    __tablename__ = 'limiti_chilometrici'
    
    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    
    # CAMPI OBBLIGATORI (da struttura DB reale)
    anno = db.Column(db.Integer, nullable=False)
    data_inizio = db.Column(db.Date, nullable=False)
    data_fine = db.Column(db.Date, nullable=False)
    limite_annuale = db.Column(db.Integer, nullable=False, default=30000)
    limite_mensile = db.Column(db.Integer, nullable=False, default=2500)
    limite_trimestrale = db.Column(db.Integer, nullable=False, default=7500)
    
    # CAMPI OPZIONALI (con DEFAULT dal DB)
    soglia_alert_percentuale = db.Column(db.Integer, default=80)
    giorni_preavviso_scadenza = db.Column(db.Integer, default=30)
    attivo = db.Column(db.Boolean, default=True)
    note = db.Column(db.Text)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow)
    
    # CAMPI AGGIUNTI (opzionali)
    costo_km_eccedenza = db.Column(db.Numeric(10, 3))
    societa_noleggio_id = db.Column(db.Integer, db.ForeignKey('fornitori.id'))
    numero_contratto = db.Column(db.String(50))
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    # Relazioni
    veicolo = db.relationship('Veicolo', backref='limiti_chilometrici')
    societa_noleggio = db.relationship('Fornitore', foreign_keys=[societa_noleggio_id])
    
    @property
    def limite_giornaliero(self):
        """Calcola limite km giornaliero (media mensile/30)"""
        return round(self.limite_mensile / 30, 1) if self.limite_mensile else None
    
    @property
    def is_attivo(self):
        """Verifica se il limite è attualmente attivo"""
        oggi = date.today()
        return (
            self.attivo and 
            self.data_inizio <= oggi <= self.data_fine and
            self.anno == oggi.year
        )
    
    @property
    def giorni_rimanenti(self):
        """Giorni rimanenti del contratto"""
        oggi = date.today()
        return max(0, (self.data_fine - oggi).days) if self.data_fine >= oggi else 0
    
    @property
    def percentuale_tempo_trascorso(self):
        """Percentuale del tempo di contratto trascorso"""
        oggi = date.today()
        if self.data_inizio >= oggi:
            return 0
        if oggi >= self.data_fine:
            return 100
        
        totale_giorni = (self.data_fine - self.data_inizio).days
        giorni_trascorsi = (oggi - self.data_inizio).days
        return round((giorni_trascorsi / totale_giorni) * 100, 1) if totale_giorni > 0 else 0
    
    def calcola_limite_per_mese(self, mese):
        """Calcola limite specifico per un mese (considerando giorni del mese)"""
        import calendar
        giorni_mese = calendar.monthrange(self.anno, mese)[1]
        return round((self.limite_mensile / 30) * giorni_mese)
    
    def __repr__(self):
        return f'<Limite {self.veicolo.targa if self.veicolo else "N/A"}: {self.limite_mensile}km/mese ({self.anno})>'

# 🆕 MODELLO PERCORRENZE CHILOMETRICHE
class PercorrenzaChilometrica(db.Model):
    __tablename__ = 'percorrenze_chilometriche'
    
    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    
    # Dati rilevazione
    anno = db.Column(db.Integer, nullable=False)
    mese = db.Column(db.Integer, nullable=False)  # 1-12
    km_iniziali = db.Column(db.Integer, nullable=False)
    km_finali = db.Column(db.Integer, nullable=False)
    
    # Data rilevazione
    data_rilevazione = db.Column(db.Date, nullable=False, default=date.today)
    rilevatore = db.Column(db.String(100))  # Chi ha fatto la rilevazione
    
    # Note e dettagli
    note = db.Column(db.Text)
    verificata = db.Column(db.Boolean, default=False)  # Flag verifica da responsabile
    
    # Gestione nuclei
    nucleo = db.Column(db.String(50), default='Via Capitel')
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    veicolo = db.relationship('Veicolo', backref='percorrenze')
    
    @property
    def km_percorsi(self):
        """Calcola km percorsi nel mese"""
        if self.km_finali and self.km_iniziali:
            return self.km_finali - self.km_iniziali
        return 0
    
    @property
    def periodo_completo(self):
        """Restituisce periodo in formato leggibile"""
        try:
            mesi = ['', 'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
                   'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
            return f"{mesi[self.mese]} {self.anno}"
        except:
            return f"{self.mese}/{self.anno}"
    
    @property
    def stato_verifica(self):
        """Stato della verifica"""
        return "Verificata" if self.verificata else "Da Verificare"
    
    def check_superamento_limite(self):
        """Verifica se ha superato i limiti del contratto noleggio"""
        # Trova limite attivo per il veicolo
        limite = LimiteChilometrico.query.filter_by(
            veicolo_id=self.veicolo_id,
            attivo=True,
            anno=self.anno
        ).first()
        
        if not limite:
            return None
        
        eccedenza = self.km_percorsi - limite.limite_mensile
        if eccedenza > 0:
            return {
                'eccedenza_km': eccedenza,
                'limite_mensile': limite.limite_mensile,
                'costo_stimato': float(eccedenza * (limite.costo_km_eccedenza or 0))
            }
        return None
    
    def __repr__(self):
        return f'<Percorrenza {self.veicolo.targa if self.veicolo else "N/A"} {self.mese}/{self.anno}: {self.km_percorsi}km>'

# MODELLO VEICOLO ESISTENTE - AGGIORNATO
class Veicolo(db.Model):
    # Use a single table name. The veicoli table is referenced by other models, so
    # define only one __tablename__. Defining multiple names can cause SQLAlchemy
    # to create multiple table mappings, leading to foreign key errors.  By
    # explicitly setting the table name here we ensure consistency across
    # references.
    __tablename__ = 'veicoli'
    
    id = db.Column(db.Integer, primary_key=True)
    targa = db.Column(db.String(10), nullable=False, unique=True)
    marca = db.Column(db.String(50), nullable=False)
    modello = db.Column(db.String(50), nullable=False)
    anno_immatricolazione = db.Column(db.Integer, nullable=False)
    data_immatricolazione = db.Column(db.Date, nullable=False)
    km_attuali = db.Column(db.Integer, default=0)
    carburante = db.Column(db.String(20), nullable=False)
    carburante_personalizzato = db.Column(db.String(50))
    cilindrata = db.Column(db.Integer)
    colore = db.Column(db.String(30))
    stato = db.Column(db.String(20), default='Attivo')
    note = db.Column(db.Text)
    
    # CAMPI PER CARTA CARBURANTE
    carta_carburante = db.Column(db.String(100))
    pin_carburante = db.Column(db.String(20))
    
    # CAMPO PER SOCIETÀ NOLEGGIO (FK a fornitori)
    societa_noleggio_id = db.Column(db.Integer, db.ForeignKey('fornitori.id'))
    
    # CAMPO NUCLEO
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    # CAMPO UNITÀ OPERATIVA
    unita_operativa = db.Column(db.String(100), default='Cure Primarie ADI Via del Capitel')
    unita_operativa_personalizzata = db.Column(db.String(100))
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni esistenti
    manutenzioni = db.relationship('Manutenzione', backref='veicolo', lazy=True, 
                                 order_by='desc(Manutenzione.data_intervento)')
    scadenze = db.relationship('Scadenza', backref='veicolo', lazy=True,
                              order_by='desc(Scadenza.data_scadenza)')
    
    # CORRETTO: Usa fornitori, non SocietaNoleggio
    societa_noleggio = db.relationship('Fornitore', foreign_keys=[societa_noleggio_id])
    
    @property
    def nome_completo(self):
        return f"{self.targa} - {self.marca} {self.modello}"
    
    @property
    def carburante_display(self):
        return self.carburante_personalizzato if self.carburante_personalizzato else self.carburante
    
    @property
    def unita_operativa_display(self):
        return self.unita_operativa_personalizzata if self.unita_operativa_personalizzata else self.unita_operativa
    
    @property
    def limite_attivo(self):
        """Restituisce il limite chilometrico attualmente attivo"""
        oggi = date.today()
        return LimiteChilometrico.query.filter_by(
            veicolo_id=self.id,
            attivo=True,
            anno=oggi.year
        ).filter(
            LimiteChilometrico.data_inizio <= oggi,
            LimiteChilometrico.data_fine >= oggi
        ).first()
    
    @property
    def ha_limite_chilometrico(self):
        """Verifica se il veicolo ha limiti chilometrici attivi"""
        return self.limite_attivo is not None
    
    def get_percorrenza_mese_corrente(self):
        """Ottiene percorrenza del mese corrente"""
        oggi = date.today()
        return PercorrenzaChilometrica.query.filter_by(
            veicolo_id=self.id,
            anno=oggi.year,
            mese=oggi.month
        ).first()
    
    def calcola_km_anno_corrente(self):
        """Calcola km totali percorsi nell'anno corrente"""
        anno_corrente = date.today().year
        percorrenze = PercorrenzaChilometrica.query.filter_by(
            veicolo_id=self.id,
            anno=anno_corrente
        ).all()
        return sum(p.km_percorsi for p in percorrenze)

    def __repr__(self):
        return f'<Veicolo {self.targa}>'

# MODELLO FORNITORE ESISTENTE
class Fornitore(db.Model):
    __tablename__ = 'fornitori'
    
    id = db.Column(db.Integer, primary_key=True)
    ragione_sociale = db.Column(db.String(200), nullable=False)
    partita_iva = db.Column(db.String(11), unique=True, nullable=True)
    codice_fiscale = db.Column(db.String(16))
    indirizzo = db.Column(db.String(200))
    citta = db.Column(db.String(100))
    cap = db.Column(db.String(5))
    provincia = db.Column(db.String(2))
    
    # TELEFONI MULTIPLI
    telefono = db.Column(db.String(20))
    telefono_2 = db.Column(db.String(20))
    telefono_3 = db.Column(db.String(20))
    
    # EMAIL MULTIPLE
    email = db.Column(db.String(100))
    email_2 = db.Column(db.String(100))
    email_3 = db.Column(db.String(100))
    
    referente = db.Column(db.String(100))
    
    # SETTORI MULTIPLI
    settore = db.Column(db.String(100))
    settore_2 = db.Column(db.String(100))
    settore_3 = db.Column(db.String(100))
    settore_personalizzato = db.Column(db.String(100))
    
    # CAMPO NUCLEO
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    note = db.Column(db.Text)
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    manutenzioni = db.relationship('Manutenzione', backref='fornitore', lazy=True)
    
    @property
    def telefoni_lista(self):
        telefoni = []
        if self.telefono: telefoni.append(self.telefono)
        if self.telefono_2: telefoni.append(self.telefono_2)
        if self.telefono_3: telefoni.append(self.telefono_3)
        return telefoni
    
    @property
    def email_lista(self):
        emails = []
        if self.email: emails.append(self.email)
        if self.email_2: emails.append(self.email_2)
        if self.email_3: emails.append(self.email_3)
        return emails
    
    @property
    def settori_lista(self):
        settori = []
        if self.settore: settori.append(self.settore)
        if self.settore_2: settori.append(self.settore_2)
        if self.settore_3: settori.append(self.settore_3)
        if self.settore_personalizzato: settori.append(self.settore_personalizzato)
        return settori
    
    @property
    def settori_display(self):
        return ' + '.join(self.settori_lista)
    
    @property
    def is_noleggio(self):
        """Verifica se è una società di noleggio"""
        settori = [s.lower() if s else '' for s in self.settori_lista]
        return any('noleggio' in s for s in settori)

    def __repr__(self):
        return f'<Fornitore {self.ragione_sociale}>'

# MODELLI ESISTENTI MANUTENZIONE E SCADENZA
class Manutenzione(db.Model):
    __tablename__ = 'manutenzioni'
    
    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    fornitore_id = db.Column(db.Integer, db.ForeignKey('fornitori.id'))
    data_intervento = db.Column(db.Date, nullable=False)
    km_intervento = db.Column(db.Integer, nullable=False)
    tipo_intervento = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    costo = db.Column(db.Numeric(10, 2))
    numero_documento = db.Column(db.String(50))
    data_fattura = db.Column(db.Date)
    garanzia_mesi = db.Column(db.Integer, default=0)
    prossima_scadenza_km = db.Column(db.Integer)
    note = db.Column(db.Text)
    stato = db.Column(db.String(20), default='Da Fare')
    nucleo = db.Column(db.String(50), default='Via Capitel')
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)

    # Relazioni
    allegati = db.relationship('AllegatoManutenzione', back_populates='manutenzione', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Manutenzione {self.id} - {self.tipo_intervento}>'

class Scadenza(db.Model):
    __tablename__ = 'scadenze'
    
    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    tipo_scadenza = db.Column(db.String(50), nullable=False)
    data_scadenza = db.Column(db.Date, nullable=False)
    stato = db.Column(db.String(20), default='Attiva')
    note = db.Column(db.Text)
    notifica_giorni = db.Column(db.Integer, default=30)
    nucleo = db.Column(db.String(50), default='Via Capitel')
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)

    # Relazioni
    allegati = db.relationship('AllegatoScadenza', back_populates='scadenza', cascade='all, delete-orphan')

    @property
    def giorni_scadenza(self):
        if self.data_scadenza:
            delta = self.data_scadenza - date.today()
            return delta.days
        return None
    
    @property
    def stato_urgenza(self):
        giorni = self.giorni_scadenza
        if giorni is None:
            return 'sconosciuto'
        elif giorni < 0:
            return 'scaduta'
        elif giorni <= 7:
            return 'critica'
        elif giorni <= 30:
            return 'urgente'
        else:
            return 'normale'

    def __repr__(self):
        return f'<Scadenza {self.tipo_scadenza} - {self.data_scadenza}>'



class SchedaKilometrica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mese = db.Column(db.Integer, nullable=False)
    anno = db.Column(db.Integer, nullable=False)
    # The foreign key must reference the correct table name for the Veicolo model.
    # Since Veicolo.__tablename__ is 'veicoli', use 'veicoli.id' here.  This
    # prevents errors when creating the schema and ensures the relationship is
    # properly defined.
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    km_iniziali = db.Column(db.Integer, nullable=True)
    km_finali = db.Column(db.Integer, nullable=True)
    sede = db.Column(db.String(64), nullable=True)
    centro_costo = db.Column(db.String(64), nullable=True)

    veicolo = db.relationship('Veicolo', backref='schede_km')

    @property
    def km_percorsi(self):
        if self.km_iniziali is not None and self.km_finali is not None:
            return self.km_finali - self.km_iniziali
        return None

# =============================================================
# Modelli aggiuntivi per v1.22
#
# Per mantenere il database esistente compatibile e al tempo stesso
# introdurre nuove funzionalità, i seguenti modelli vivono in
# tabelle dedicate.  Essi non modificano le strutture esistenti,
# ma si collegano tramite chiavi esterne.  In questo modo il
# progetto resta modulare e ogni nuovo modulo può essere
# disattivato senza impattare sulle altre parti dell'applicazione.

class ManutenzionePreventiva(db.Model):
    """
    Definisce una manutenzione programmata per un veicolo.

    L'utente può impostare un intervallo in chilometri o mesi e
    opzionalmente registrare l'ultimo intervento effettuato.  Il
    prossimo intervento viene calcolato a partire da questi dati.
    """
    __tablename__ = 'manutenzioni_preventive'

    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    tipo_intervento = db.Column(db.String(100), nullable=False)
    intervallo_km = db.Column(db.Integer)
    intervallo_mesi = db.Column(db.Integer)
    ultimo_km = db.Column(db.Integer)
    ultima_data = db.Column(db.Date)
    note = db.Column(db.Text)
    nucleo = db.Column(db.String(50), default='Via Capitel')
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)

    # relazioni
    veicolo = db.relationship('Veicolo', backref='manutenzioni_preventive')
    log_entries = db.relationship('LogPreventiva', back_populates='preventiva', cascade='all, delete-orphan')
    allegati = db.relationship('AllegatoPreventiva', back_populates='preventiva', cascade='all, delete-orphan')

    def calcola_prossimo_km(self):
        """Calcola il chilometraggio previsto per il prossimo intervento."""
        if self.ultimo_km is not None and self.intervallo_km:
            return self.ultimo_km + self.intervallo_km
        return None

    def calcola_prossima_data(self):
        """Calcola la prossima data di intervento aggiungendo mesi a ultima_data."""
        from datetime import timedelta

        if self.ultima_data and self.intervallo_mesi:
            # Calcolo manuale del mese successivo senza usare librerie esterne
            anno = self.ultima_data.year
            mese = self.ultima_data.month + self.intervallo_mesi
            giorno = self.ultima_data.day
            # Gestione overflow mesi
            while mese > 12:
                mese -= 12
                anno += 1
            # Se il giorno non esiste nel nuovo mese (es. 31 feb), riducilo
            try:
                return date(anno, mese, giorno)
            except ValueError:
                # Setta l'ultimo giorno valido del mese
                from calendar import monthrange
                ultimo_giorno = monthrange(anno, mese)[1]
                return date(anno, mese, ultimo_giorno)
        return None

    def __repr__(self):
        return f"<Preventiva {self.veicolo.targa if self.veicolo else ''} - {self.tipo_intervento}>"


# == Nuovi modelli per v1.24 ==
#
# Per tracciare le modifiche alle manutenzioni preventive e gestire file
# allegati su queste programmazioni, introduciamo due nuove tabelle.
# "LogPreventiva" registra ogni azione eseguita su una manutenzione
# preventiva (creazione, modifica, eliminazione) insieme all'utente e
# al timestamp. "AllegatoPreventiva" memorizza i file collegati a
# ciascuna manutenzione preventiva, consentendo di caricare documenti
# (es. fatture, certificati) direttamente dalla schermata di dettaglio.

class LogPreventiva(db.Model):
    """
    Traccia le operazioni eseguite su una manutenzione preventiva.

    Ogni volta che un utente crea, modifica o elimina una manutenzione
    preventiva viene creato un record in questa tabella.  I campi
    "azione" descrivono l'operazione (es. "creazione", "modifica",
    "eliminazione"), mentre "dettagli" può contenere una descrizione
    più estesa dell'intervento (ad esempio quali campi sono stati
    modificati).
    """

    __tablename__ = 'log_preventive'

    id = db.Column(db.Integer, primary_key=True)
    preventiva_id = db.Column(db.Integer, db.ForeignKey('manutenzioni_preventive.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    azione = db.Column(db.String(50), nullable=False)
    dettagli = db.Column(db.Text)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)

    # relazioni
    preventiva = db.relationship('ManutenzionePreventiva', back_populates='log_entries')
    user = db.relationship('User')

    def __repr__(self):
        return f"<LogPreventiva {self.azione} per preventiva {self.preventiva_id}>"


class AllegatoPreventiva(db.Model):
    """
    File allegati a una manutenzione preventiva.

    Ogni record rappresenta un singolo file caricato per una
    manutenzione preventiva specifica.  Il campo "filepath" contiene
    il percorso relativo all'interno della cartella static/uploads.
    """

    __tablename__ = 'allegati_preventive'

    id = db.Column(db.Integer, primary_key=True)
    preventiva_id = db.Column(db.Integer, db.ForeignKey('manutenzioni_preventive.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    preventiva = db.relationship('ManutenzionePreventiva', back_populates='allegati')

    def __repr__(self):
        return f"<AllegatoPreventiva {self.filename}>"


class AllegatoManutenzione(db.Model):
    """
    Allegati associati a una manutenzione ordinaria.

    Conserva sia il nome originale del file sia il percorso sul disco
    (relativo alla cartella static/uploads).  Gli allegati non vengono
    caricati se la tabella non viene utilizzata.
    """
    __tablename__ = 'allegati_manutenzioni'

    id = db.Column(db.Integer, primary_key=True)
    manutenzione_id = db.Column(db.Integer, db.ForeignKey('manutenzioni.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    manutenzione = db.relationship('Manutenzione', back_populates='allegati')

    def __repr__(self):
        return f"<Allegato {self.filename}>"


class AllegatoScadenza(db.Model):
    """
    File allegati a una scadenza.

    Ogni record rappresenta un singolo file caricato per una
    scadenza specifica.  Il campo "filepath" contiene
    il percorso relativo all'interno della cartella static/uploads.
    """

    __tablename__ = 'allegati_scadenze'

    id = db.Column(db.Integer, primary_key=True)
    scadenza_id = db.Column(db.Integer, db.ForeignKey('scadenze.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relazione verso la scadenza
    scadenza = db.relationship('Scadenza', back_populates='allegati')

    def __repr__(self):
        return f"<AllegatoScadenza {self.filename}>"


# ------------------------------- SINISTRI -------------------------------
# Il modulo Sinistri consente di registrare eventi di sinistro (incidenti) per
# i veicoli del parco auto. Ogni sinistro è associato a un veicolo
# principale, può indicare altri veicoli coinvolti, specificare la tipologia
# dell'evento (ad esempio con controparte, vandalico, sconosciuto) e
# memorizzare una descrizione dettagliata.  Gli allegati relativi al
# sinistro (CID, documenti d'identità, denunce, ecc.) sono gestiti nel
# modello AllegatoSinistro e memorizzati nella directory static/uploads/sinistri.

class Sinistro(db.Model):
    """
    Registro dei sinistri occorsi ai veicoli.  Ogni sinistro è legato a un
    veicolo principale tramite la chiave esterna ``veicolo_id`` e memorizza
    informazioni di base quali la data, il luogo, i veicoli coinvolti, il
    tipo di sinistro e una descrizione.  Il campo ``nucleo`` consente di
    filtrare gli eventi per nucleo (sede) in modo simile ad altri moduli.
    """

    __tablename__ = 'sinistri'

    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    data_sinistro = db.Column(db.Date, nullable=False)
    luogo = db.Column(db.String(120))
    veicoli_coinvolti = db.Column(db.String(255))
    tipo = db.Column(db.String(50))  # con controparte, vandalico, sconosciuto
    descrizione = db.Column(db.Text)

    # Campi aggiuntivi per informazioni dettagliate sul sinistro
    # Numero identificativo del sinistro fornito dall'assicurazione o dalle autorità
    numero_sinistro = db.Column(db.String(50))
    # Contatti telefonici delle parti coinvolte (controparte e nostro autista)
    cellulare_controparte = db.Column(db.String(30))
    cellulare_autista = db.Column(db.String(30))
    # Numero patente di guida per il nostro autista e per la controparte
    numero_patente_autista = db.Column(db.String(50))
    numero_patente_controparte = db.Column(db.String(50))
    # Comune che ha emesso le patenti
    comune_patente_autista = db.Column(db.String(100))
    comune_patente_controparte = db.Column(db.String(100))
    # Date di emissione e scadenza delle patenti
    data_emissione_patente_autista = db.Column(db.Date)
    data_scadenza_patente_autista = db.Column(db.Date)
    data_emissione_patente_controparte = db.Column(db.Date)
    data_scadenza_patente_controparte = db.Column(db.Date)
    nucleo = db.Column(db.String(50), default='Via Capitel')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relazioni
    veicolo = db.relationship('Veicolo', backref='sinistri', lazy=True)
    allegati = db.relationship('AllegatoSinistro', backref='sinistro', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sinistro {self.id} veicolo={self.veicolo.targa if self.veicolo else 'N/A'}>"


class AllegatoSinistro(db.Model):
    """
    File allegati a un sinistro.  Ogni record rappresenta un singolo file
    caricato per un sinistro specifico.  Il campo ``filepath`` contiene
    il percorso relativo all'interno della cartella static/uploads/sinistri.
    """

    __tablename__ = 'allegati_sinistri'

    id = db.Column(db.Integer, primary_key=True)
    sinistro_id = db.Column(db.Integer, db.ForeignKey('sinistri.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AllegatoSinistro {self.filename}>"


class Notifica(db.Model):
    """
    Modello di base per notifiche in-app.  Ogni record rappresenta
    un promemoria per l'utente relativo a scadenze o manutenzioni
    preventive imminenti.  Le notifiche possono essere marcate come
    lette quando l'utente le visualizza.
    """
    __tablename__ = 'notifiche'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    titolo = db.Column(db.String(100))
    messaggio = db.Column(db.String(255))
    tipo = db.Column(db.String(50))
    riferimenti = db.Column(db.String(255))
    letto = db.Column(db.Boolean, default=False)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    nucleo = db.Column(db.String(50), default='Via Capitel')

    user = db.relationship('User', backref='notifiche')

    def __repr__(self):
        return f"<Notifica {self.titolo}>"