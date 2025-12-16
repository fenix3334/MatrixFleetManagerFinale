"""
Modelli Database - Backend API
Riutilizzo dei modelli esistenti da app/models.py
"""
from app import db
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash


# ==================== MODELLO USER ====================
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nucleo = db.Column(db.String(50), default='Via Capitel')
    ruolo = db.Column(db.String(20), default='user')  # admin, user
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash della password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica password"""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.ruolo == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


# ==================== MODELLO VEICOLO ====================
class Veicolo(db.Model):
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

    # Carta carburante
    carta_carburante = db.Column(db.String(100))
    pin_carburante = db.Column(db.String(20))

    # Società noleggio
    societa_noleggio_id = db.Column(db.Integer, db.ForeignKey('fornitori.id'))

    # Nucleo e unità operativa
    nucleo = db.Column(db.String(50), default='Via Capitel')
    unita_operativa = db.Column(db.String(100), default='Cure Primarie ADI Via del Capitel')
    unita_operativa_personalizzata = db.Column(db.String(100))

    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)

    # Relazioni
    manutenzioni = db.relationship('Manutenzione', backref='veicolo', lazy='dynamic')
    scadenze = db.relationship('Scadenza', backref='veicolo', lazy='dynamic')
    sinistri = db.relationship('Sinistro', backref='veicolo', lazy='dynamic')
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

    def __repr__(self):
        return f'<Veicolo {self.targa}>'


# ==================== MODELLO FORNITORE ====================
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

    # Telefoni multipli
    telefono = db.Column(db.String(20))
    telefono_2 = db.Column(db.String(20))
    telefono_3 = db.Column(db.String(20))

    # Email multiple
    email = db.Column(db.String(100))
    email_2 = db.Column(db.String(100))
    email_3 = db.Column(db.String(100))

    referente = db.Column(db.String(100))

    # Settori multipli
    settore = db.Column(db.String(100))
    settore_2 = db.Column(db.String(100))
    settore_3 = db.Column(db.String(100))
    settore_personalizzato = db.Column(db.String(100))

    nucleo = db.Column(db.String(50), default='Via Capitel')
    note = db.Column(db.Text)
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)

    # Relazioni
    manutenzioni = db.relationship('Manutenzione', backref='fornitore', lazy='dynamic')

    @property
    def settori_display(self):
        settori = []
        if self.settore: settori.append(self.settore)
        if self.settore_2: settori.append(self.settore_2)
        if self.settore_3: settori.append(self.settore_3)
        if self.settore_personalizzato: settori.append(self.settore_personalizzato)
        return ' + '.join(settori)

    def __repr__(self):
        return f'<Fornitore {self.ragione_sociale}>'


# ==================== MODELLO MANUTENZIONE ====================
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

    def __repr__(self):
        return f'<Manutenzione {self.tipo_intervento}>'


# ==================== MODELLO SCADENZA ====================
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
        return f'<Scadenza {self.tipo_scadenza}>'


# ==================== MODELLO SINISTRO ====================
class Sinistro(db.Model):
    __tablename__ = 'sinistri'

    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    data_sinistro = db.Column(db.Date, nullable=False)
    luogo = db.Column(db.String(120))
    veicoli_coinvolti = db.Column(db.String(255))
    tipo = db.Column(db.String(50))
    descrizione = db.Column(db.Text)
    numero_sinistro = db.Column(db.String(50))

    # Dati controparte
    cellulare_controparte = db.Column(db.String(30))
    numero_patente_controparte = db.Column(db.String(50))
    comune_patente_controparte = db.Column(db.String(100))
    data_emissione_patente_controparte = db.Column(db.Date)
    data_scadenza_patente_controparte = db.Column(db.Date)

    # Dati autista
    cellulare_autista = db.Column(db.String(30))
    numero_patente_autista = db.Column(db.String(50))
    comune_patente_autista = db.Column(db.String(100))
    data_emissione_patente_autista = db.Column(db.Date)
    data_scadenza_patente_autista = db.Column(db.Date)

    nucleo = db.Column(db.String(50), default='Via Capitel')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Sinistro {self.id}>'
