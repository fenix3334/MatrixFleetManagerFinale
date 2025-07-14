from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional

class FornitoreForm(FlaskForm):
    # CAMPI BASE
    ragione_sociale = StringField('Ragione Sociale', validators=[DataRequired(), Length(max=100)])
    partita_iva = StringField('Partita IVA', validators=[Optional(), Length(max=20)])
    codice_fiscale = StringField('Codice Fiscale', validators=[Optional(), Length(max=20)])
    indirizzo = StringField('Indirizzo', validators=[Optional(), Length(max=200)])
    citta = StringField('Città', validators=[DataRequired(), Length(max=50)])
    cap = StringField('CAP', validators=[DataRequired(), Length(max=10)])
    provincia = StringField('Provincia', validators=[Optional(), Length(max=5)])
    
    # TELEFONI MULTIPLI
    telefono = StringField('Telefono Principale', validators=[Optional(), Length(max=20)])
    telefono_2 = StringField('Telefono 2', validators=[Optional(), Length(max=20)])
    telefono_3 = StringField('Telefono 3', validators=[Optional(), Length(max=20)])
    
    # EMAIL MULTIPLE
    email = StringField('Email Principale', validators=[Optional(), Email(), Length(max=100)])
    email_2 = StringField('Email 2', validators=[Optional(), Email(), Length(max=100)])
    email_3 = StringField('Email 3', validators=[Optional(), Email(), Length(max=100)])
    
    referente = StringField('Referente', validators=[Optional(), Length(max=100)])
    
    # SETTORI MULTIPLI
    settore = SelectField('Settore Principale', 
                         choices=[('', 'Seleziona settore'),
                                ('Officina', 'Officina'), 
                                ('Carrozzeria', 'Carrozzeria'),
                                ('Gommista', 'Gommista'), 
                                ('Elettrauto', 'Elettrauto'),
                                ('Carburanti', 'Carburanti'), 
                                ('Assicurazioni', 'Assicurazioni'),
                                ('Società noleggio', 'Società noleggio'),
                                ('Leasing', 'Leasing'),
                                ('Ricambi', 'Ricambi'),
                                ('Trasporti', 'Trasporti'),
                                ('Altro', 'Altro')],
                         validators=[Optional()])
    
    settore_2 = SelectField('Settore 2', 
                           choices=[('', 'Nessun settore aggiuntivo'),
                                  ('Officina', 'Officina'), 
                                  ('Carrozzeria', 'Carrozzeria'),
                                  ('Gommista', 'Gommista'), 
                                  ('Elettrauto', 'Elettrauto'),
                                  ('Carburanti', 'Carburanti'), 
                                  ('Assicurazioni', 'Assicurazioni'),
                                  ('Società noleggio', 'Società noleggio'),
                                  ('Leasing', 'Leasing'),
                                  ('Ricambi', 'Ricambi'),
                                  ('Trasporti', 'Trasporti'),
                                  ('Altro', 'Altro')],
                           validators=[Optional()])
    
    settore_3 = SelectField('Settore 3', 
                           choices=[('', 'Nessun settore aggiuntivo'),
                                  ('Officina', 'Officina'), 
                                  ('Carrozzeria', 'Carrozzeria'),
                                  ('Gommista', 'Gommista'), 
                                  ('Elettrauto', 'Elettrauto'),
                                  ('Carburanti', 'Carburanti'), 
                                  ('Assicurazioni', 'Assicurazioni'),
                                  ('Società noleggio', 'Società noleggio'),
                                  ('Leasing', 'Leasing'),
                                  ('Ricambi', 'Ricambi'),
                                  ('Trasporti', 'Trasporti'),
                                  ('Altro', 'Altro')],
                           validators=[Optional()])
    
    settore_personalizzato = StringField('Settore Personalizzato', 
                                        validators=[Optional(), Length(max=100)])
    
    # NUCLEO
    nucleo = SelectField('Nucleo',
                        choices=[('Via Capitel', 'Via Capitel'), 
                               ('Campania', 'Campania')],
                        default='Via Capitel',
                        validators=[DataRequired()])
    
    note = TextAreaField('Note')
    attivo = BooleanField('Attivo', default=True)
    
    def clean_field(self, value):
        """Funzione helper per pulire i campi vuoti"""
        if value and value.strip():
            return value.strip()
        return None
