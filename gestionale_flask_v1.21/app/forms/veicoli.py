from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import date

class VeicoloForm(FlaskForm):
    # DATI IDENTIFICATIVI
    targa = StringField('Targa', 
                       validators=[DataRequired(), Length(min=7, max=8)],
                       render_kw={"placeholder": "Es: AB123CD"})
    
    marca = StringField('Marca', 
                       validators=[DataRequired(), Length(max=50)],
                       render_kw={"placeholder": "Es: Fiat"})
    
    modello = StringField('Modello', 
                         validators=[DataRequired(), Length(max=50)],
                         render_kw={"placeholder": "Es: Panda"})
    
    # DATI TECNICI
    anno_immatricolazione = IntegerField('Anno Immatricolazione', 
                                       validators=[DataRequired(), NumberRange(min=1990, max=2030)])
    
    data_immatricolazione = DateField('Data Immatricolazione', 
                                    validators=[DataRequired()],
                                    default=date.today)
    
    km_attuali = IntegerField('KM Attuali', 
                             validators=[DataRequired(), NumberRange(min=0)],
                             default=0)
    
    carburante = SelectField('Carburante',
                           choices=[
                               ('Benzina', 'Benzina'),
                               ('Diesel', 'Diesel'),
                               ('GPL', 'GPL'),
                               ('Metano', 'Metano'),
                               ('Elettrico', 'Elettrico'),
                               ('Ibrido', 'Ibrido'),
                               ('Altro', 'Altro (personalizzato)')
                           ],
                           validators=[DataRequired()])
    
    carburante_personalizzato = StringField('Tipo Carburante Personalizzato',
                                          validators=[Optional(), Length(max=50)],
                                          render_kw={"placeholder": "Specifica il tipo di carburante"})
    
    cilindrata = IntegerField('Cilindrata (cc)', 
                             validators=[Optional(), NumberRange(min=500, max=10000)])
    
    colore = StringField('Colore', 
                        validators=[Optional(), Length(max=30)],
                        render_kw={"placeholder": "Es: Bianco"})
    
    # 🆕 UNITÀ OPERATIVA
    unita_operativa = SelectField('Assegnato a U.O.',
                                choices=[
                                    ('Cure Primarie ADI Via del Capitel', 'Cure Primarie ADI Via del Capitel'),
                                    ('Cure Primarie ADI Via Campania', 'Cure Primarie ADI Via Campania'),
                                    ('Guardia Medica', 'Guardia Medica'),
                                    ('Altro', 'Altro (personalizzato)')
                                ],
                                validators=[DataRequired()],
                                default='Cure Primarie ADI Via del Capitel')
    
    unita_operativa_personalizzata = StringField('U.O. Personalizzata',
                                                validators=[Optional(), Length(max=100)],
                                                render_kw={"placeholder": "Specifica l'unità operativa"})
    
    # CARTA CARBURANTE
    carta_carburante = StringField('Carta Carburante', 
                                  validators=[Optional(), Length(max=100)],
                                  render_kw={"placeholder": "Es: Q8 Easy"})
    
    pin_carburante = StringField('PIN Carta Carburante', 
                                validators=[Optional(), Length(max=20)],
                                render_kw={"type": "password", "placeholder": "PIN carta"})
    
    # SOCIETÀ NOLEGGIO
    societa_noleggio_id = SelectField('Società Noleggio',
                                    choices=[('', 'Proprietà aziendale')],
                                    validators=[Optional()],
                                    coerce=lambda x: int(x) if x else None)
    
    # NUCLEO (per admin)
    nucleo = SelectField('Nucleo',
                        choices=[
                            ('Via Capitel', 'Via Capitel'),
                            ('Campania', 'Campania')
                        ],
                        validators=[DataRequired()],
                        default='Via Capitel')
    
    # STATO
    stato = SelectField('Stato',
                       choices=[
                           ('Attivo', 'Attivo'),
                           ('Inattivo', 'Inattivo'),
                           ('In Manutenzione', 'In Manutenzione'),
                           ('Dismesso', 'Dismesso')
                       ],
                       validators=[DataRequired()],
                       default='Attivo')
    
    # NOTE
    note = TextAreaField('Note', 
                        validators=[Optional()],
                        render_kw={"rows": 4, "placeholder": "Note aggiuntive sul veicolo"})
    
    def validate(self, extra_validators=None):
        """Validazione personalizzata"""
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False
        
        # Validazione carburante personalizzato
        if self.carburante.data == 'Altro' and not self.carburante_personalizzato.data:
            self.carburante_personalizzato.errors.append('Specifica il tipo di carburante personalizzato')
            return False
        
        # Validazione unità operativa personalizzata
        if self.unita_operativa.data == 'Altro' and not self.unita_operativa_personalizzata.data:
            self.unita_operativa_personalizzata.errors.append('Specifica l\'unità operativa personalizzata')
            return False
        
        return True
