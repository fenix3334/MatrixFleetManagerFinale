from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, IntegerField, StringField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from app.models import Veicolo, Fornitore

class ManutenzioneForm(FlaskForm):
    veicolo_id = SelectField('Veicolo', coerce=int, validators=[DataRequired()])
    fornitore_id = SelectField('Fornitore', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    data_intervento = DateField('Data Intervento', validators=[DataRequired()])
    km_intervento = IntegerField('KM Intervento', validators=[DataRequired(), NumberRange(min=0)])
    tipo_intervento = SelectField('Tipo Intervento',
                                choices=[('Tagliando', 'Tagliando'), ('Revisione', 'Revisione'),
                                       ('Riparazione', 'Riparazione'), ('Sostituzione pneumatici', 'Sostituzione pneumatici'),
                                       ('Cambio olio', 'Cambio olio'), ('Freni', 'Freni'),
                                       ('Altro', 'Altro')],
                                validators=[DataRequired()])
    
    # NUOVO CAMPO STATO
    stato = SelectField('Stato',
                       choices=[('Da Fare', 'Da Fare'), ('Fatto', 'Fatto')],
                       default='Da Fare',
                       validators=[DataRequired()])
    
    descrizione = TextAreaField('Descrizione')
    costo = DecimalField('Costo (€)', validators=[Optional(), NumberRange(min=0)], places=2)
    numero_documento = StringField('Numero Fattura', validators=[Length(max=50)])
    data_fattura = DateField('Data Fattura', validators=[Optional()])
    garanzia_mesi = IntegerField('Garanzia (mesi)', validators=[NumberRange(min=0, max=120)], default=0)
    prossima_scadenza_km = IntegerField('Prossima Scadenza KM', validators=[Optional(), NumberRange(min=0)])
    note = TextAreaField('Note')
    
    def __init__(self, *args, **kwargs):
        super(ManutenzioneForm, self).__init__(*args, **kwargs)
        self.veicolo_id.choices = [(v.id, f"{v.targa} - {v.marca} {v.modello}") 
                                  for v in Veicolo.query.filter_by(stato='Attivo').all()]
        self.fornitore_id.choices = [('', 'Seleziona fornitore')] + \
                                   [(f.id, f.ragione_sociale) 
                                    for f in Fornitore.query.filter_by(attivo=True).all()]
