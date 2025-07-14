from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Optional, Length
from app.models import Veicolo

class ScadenzaForm(FlaskForm):
    veicolo_id = SelectField('Veicolo', coerce=int, validators=[DataRequired()])
    tipo_scadenza = SelectField('Tipo Scadenza',
                              choices=[('Revisione', 'Revisione'), ('Assicurazione', 'Assicurazione'),
                                     ('Bollo', 'Bollo'), ('Tagliando', 'Tagliando'),
                                     ('Controllo gas di scarico', 'Controllo gas di scarico'),
                                     ('Consegna auto a noleggio', 'Consegna auto a noleggio'),
                                     ('Riconsegna auto da noleggio', 'Riconsegna auto da noleggio'),
                                     ('Altro', 'Altro')],
                              validators=[DataRequired()])
    
    # CAMPO PER SCADENZA PERSONALIZZATA
    tipo_scadenza_personalizzato = StringField('Tipo Scadenza Personalizzato', 
                                             validators=[Optional(), Length(max=100)])
    
    data_scadenza = DateField('Data Scadenza', validators=[DataRequired()])
    
    # ❌ RIMOSSO: campo costo
    
    stato = SelectField('Stato',
                       choices=[('Attiva', 'Attiva'), ('Scaduta', 'Scaduta'), ('Rinnovata', 'Rinnovata')],
                       default='Attiva')
    notifica_giorni = IntegerField('Notifica (giorni prima)', validators=[Optional(), NumberRange(min=1, max=365)], default=30)
    note = TextAreaField('Note')
    
    def __init__(self, *args, **kwargs):
        super(ScadenzaForm, self).__init__(*args, **kwargs)
        self.veicolo_id.choices = [(v.id, f"{v.targa} - {v.marca} {v.modello}") 
                                  for v in Veicolo.query.all()]
    
    def validate(self, extra_validators=None):
        """Validazione personalizzata"""
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False
        
        # Validazione tipo scadenza personalizzato
        if self.tipo_scadenza.data == 'Altro' and not self.tipo_scadenza_personalizzato.data:
            self.tipo_scadenza_personalizzato.errors.append('Specifica il tipo di scadenza personalizzato')
            return False
        
        return True
