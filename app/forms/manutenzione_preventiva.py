"""
Form per gestire la creazione e modifica delle manutenzioni preventive.

Permette di definire l'intervallo chilometrico e/o temporale per un
intervento periodico su un veicolo. I campi facoltativi consentono di
registrare l'ultimo intervento eseguito per calcolare la prossima scadenza.
"""

from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, DateField, StringField, TextAreaField
from wtforms.validators import DataRequired, Optional, NumberRange
from app.models import Veicolo


class ManutenzionePreventivaForm(FlaskForm):
    veicolo_id = SelectField('Veicolo', coerce=int, validators=[DataRequired()])
    tipo_intervento = StringField('Tipo Intervento', validators=[DataRequired()])
    intervallo_km = IntegerField('Intervallo KM', validators=[Optional(), NumberRange(min=1)])
    intervallo_mesi = IntegerField('Intervallo Mesi', validators=[Optional(), NumberRange(min=1)])
    ultimo_km = IntegerField('Ultimo KM', validators=[Optional(), NumberRange(min=0)])
    ultima_data = DateField('Data Ultimo Intervento', validators=[Optional()])
    note = TextAreaField('Note', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Popola la lista dei veicoli attivi per il dropdown
        self.veicolo_id.choices = [
            (v.id, f"{v.targa} - {v.marca} {v.modello}")
            for v in Veicolo.query.filter_by(stato='Attivo').order_by(Veicolo.targa).all()
        ]