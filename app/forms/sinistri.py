"""
Modulo contenente i form per la gestione dei sinistri.

Il ``SinistroForm`` permette di creare o modificare un evento di sinistro
associato a un veicolo.  Comprende campi per data, luogo, veicoli
coinvolti, tipo di sinistro e descrizione.  Il ``AllegatoSinistroForm``
fornisce un campo file per caricare documenti legati al sinistro, come
CID, fotografie, documenti d'identità o denunce.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SelectField, DateField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.models import Veicolo


class SinistroForm(FlaskForm):
    """
    Form per la creazione e la modifica di un sinistro.

    Le scelte del campo ``veicolo_id`` sono popolate dinamicamente nel
    costruttore in base ai veicoli presenti nel database.  Si visualizza
    la targa seguita da marca e modello.
    """

    veicolo_id = SelectField('Veicolo', coerce=int, validators=[DataRequired()])
    data_sinistro = DateField('Data sinistro', validators=[DataRequired()])
    luogo = StringField('Luogo', validators=[Optional()])
    veicoli_coinvolti = StringField('Veicoli coinvolti (opzionale)', validators=[Optional()])
    tipo = SelectField(
        'Tipo sinistro',
        choices=[
            ('Con controparte', 'Con controparte'),
            ('Vandalico', 'Vandalico'),
            ('Sconosciuto', 'Sconosciuto'),
        ],
        validators=[DataRequired()],
    )
    descrizione = TextAreaField('Descrizione', validators=[Optional()])

    # Campi aggiuntivi per la gestione completa del sinistro
    numero_sinistro = StringField('Numero sinistro', validators=[Optional()])
    cellulare_controparte = StringField('Cellulare controparte', validators=[Optional()])
    cellulare_autista = StringField('Cellulare nostro autista', validators=[Optional()])
    numero_patente_autista = StringField('Numero patente autista', validators=[Optional()])
    numero_patente_controparte = StringField('Numero patente controparte', validators=[Optional()])
    comune_patente_autista = StringField('Comune emissione patente autista', validators=[Optional()])
    comune_patente_controparte = StringField('Comune emissione patente controparte', validators=[Optional()])
    data_emissione_patente_autista = DateField('Data emissione patente autista', validators=[Optional()])
    data_scadenza_patente_autista = DateField('Data scadenza patente autista', validators=[Optional()])
    data_emissione_patente_controparte = DateField('Data emissione patente controparte', validators=[Optional()])
    data_scadenza_patente_controparte = DateField('Data scadenza patente controparte', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        """
        Costruttore del form. Lascia l'inizializzazione delle scelte del
        campo ``veicolo_id`` ai chiamanti (le route), così da poter
        applicare correttamente il filtro sul nucleo.  In questo modo il
        form non popola automaticamente la lista con tutti i veicoli,
        evitando che un utente admin visualizzi veicoli di altri nuclei
        quando crea un nuovo sinistro.  Le scelte vengono impostate nel
        ``@sinistri_bp.route('/nuovo')`` e ``modifica_sinistro``.
        """
        super(SinistroForm, self).__init__(*args, **kwargs)
        # Le scelte saranno impostate nelle route ``aggiungi_sinistro``
        # e ``modifica_sinistro`` tramite ``get_veicoli_by_nucleo()``.
        self.veicolo_id.choices = []


class AllegatoSinistroForm(FlaskForm):
    """
    Form per il caricamento di allegati per un sinistro.

    Utilizza ``FileField`` con validatore ``FileRequired`` per assicurare
    che l'utente selezioni un file prima dell'invio.
    """

    file = FileField('Seleziona file', validators=[FileRequired()])