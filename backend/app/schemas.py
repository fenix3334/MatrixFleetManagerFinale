"""
Marshmallow Schemas per serializzazione/deserializzazione
"""
from marshmallow import Schema, fields, validate


# ==================== USER SCHEMAS ====================
class UserSchema(Schema):
    """Schema per utente"""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    nucleo = fields.Str()
    ruolo = fields.Str(validate=validate.OneOf(['user', 'admin']))
    attivo = fields.Bool()
    data_creazione = fields.DateTime(dump_only=True)


class UserLoginSchema(Schema):
    """Schema per login"""
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserRegisterSchema(Schema):
    """Schema per registrazione"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=6), load_only=True)
    nucleo = fields.Str()
    ruolo = fields.Str(validate=validate.OneOf(['user', 'admin']), missing='user')


# ==================== VEICOLO SCHEMAS ====================
class VeicoloSchema(Schema):
    """Schema per veicolo"""
    id = fields.Int(dump_only=True)
    targa = fields.Str(required=True, validate=validate.Length(max=10))
    marca = fields.Str(required=True, validate=validate.Length(max=50))
    modello = fields.Str(required=True, validate=validate.Length(max=50))
    anno_immatricolazione = fields.Int(required=True)
    data_immatricolazione = fields.Date(required=True)
    km_attuali = fields.Int()
    carburante = fields.Str(required=True)
    carburante_personalizzato = fields.Str()
    cilindrata = fields.Int()
    colore = fields.Str()
    stato = fields.Str()
    note = fields.Str()
    carta_carburante = fields.Str()
    pin_carburante = fields.Str()
    societa_noleggio_id = fields.Int()
    nucleo = fields.Str()
    unita_operativa = fields.Str()
    unita_operativa_personalizzata = fields.Str()
    data_creazione = fields.DateTime(dump_only=True)

    # Campi calcolati
    nome_completo = fields.Str(dump_only=True)
    carburante_display = fields.Str(dump_only=True)
    unita_operativa_display = fields.Str(dump_only=True)


class VeicoloListSchema(Schema):
    """Schema semplificato per lista veicoli"""
    id = fields.Int()
    targa = fields.Str()
    marca = fields.Str()
    modello = fields.Str()
    anno_immatricolazione = fields.Int()
    km_attuali = fields.Int()
    carburante = fields.Str()
    stato = fields.Str()
    nucleo = fields.Str()
    nome_completo = fields.Str(dump_only=True)


# ==================== FORNITORE SCHEMAS ====================
class FornitoreSchema(Schema):
    """Schema per fornitore"""
    id = fields.Int(dump_only=True)
    ragione_sociale = fields.Str(required=True)
    partita_iva = fields.Str()
    codice_fiscale = fields.Str()
    indirizzo = fields.Str()
    citta = fields.Str()
    cap = fields.Str()
    provincia = fields.Str()
    telefono = fields.Str()
    telefono_2 = fields.Str()
    telefono_3 = fields.Str()
    email = fields.Email()
    email_2 = fields.Email()
    email_3 = fields.Email()
    referente = fields.Str()
    settore = fields.Str()
    settore_2 = fields.Str()
    settore_3 = fields.Str()
    settore_personalizzato = fields.Str()
    nucleo = fields.Str()
    note = fields.Str()
    attivo = fields.Bool()
    data_creazione = fields.DateTime(dump_only=True)
    settori_display = fields.Str(dump_only=True)


# ==================== MANUTENZIONE SCHEMAS ====================
class ManutenzioneSchema(Schema):
    """Schema per manutenzione"""
    id = fields.Int(dump_only=True)
    veicolo_id = fields.Int(required=True)
    fornitore_id = fields.Int()
    data_intervento = fields.Date(required=True)
    km_intervento = fields.Int(required=True)
    tipo_intervento = fields.Str(required=True)
    descrizione = fields.Str()
    costo = fields.Decimal(as_string=True)
    numero_documento = fields.Str()
    data_fattura = fields.Date()
    garanzia_mesi = fields.Int()
    prossima_scadenza_km = fields.Int()
    note = fields.Str()
    stato = fields.Str()
    nucleo = fields.Str()
    data_creazione = fields.DateTime(dump_only=True)


# ==================== SCADENZA SCHEMAS ====================
class ScadenzaSchema(Schema):
    """Schema per scadenza"""
    id = fields.Int(dump_only=True)
    veicolo_id = fields.Int(required=True)
    tipo_scadenza = fields.Str(required=True)
    data_scadenza = fields.Date(required=True)
    stato = fields.Str()
    note = fields.Str()
    notifica_giorni = fields.Int()
    nucleo = fields.Str()
    data_creazione = fields.DateTime(dump_only=True)
    giorni_scadenza = fields.Int(dump_only=True)
    stato_urgenza = fields.Str(dump_only=True)


# ==================== SINISTRO SCHEMAS ====================
class SinistroSchema(Schema):
    """Schema per sinistro"""
    id = fields.Int(dump_only=True)
    veicolo_id = fields.Int(required=True)
    data_sinistro = fields.Date(required=True)
    luogo = fields.Str()
    veicoli_coinvolti = fields.Str()
    tipo = fields.Str()
    descrizione = fields.Str()
    numero_sinistro = fields.Str()
    cellulare_controparte = fields.Str()
    numero_patente_controparte = fields.Str()
    comune_patente_controparte = fields.Str()
    data_emissione_patente_controparte = fields.Date()
    data_scadenza_patente_controparte = fields.Date()
    cellulare_autista = fields.Str()
    numero_patente_autista = fields.Str()
    comune_patente_autista = fields.Str()
    data_emissione_patente_autista = fields.Date()
    data_scadenza_patente_autista = fields.Date()
    nucleo = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# ==================== STATS SCHEMAS ====================
class DashboardStatsSchema(Schema):
    """Schema per statistiche dashboard"""
    totale_veicoli = fields.Int()
    veicoli_attivi = fields.Int()
    veicoli_manutenzione = fields.Int()
    scadenze_imminenti = fields.Int()
    km_totali = fields.Int()
    costo_manutenzioni_anno = fields.Decimal(as_string=True)
