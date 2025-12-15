"""
Form per il caricamento di allegati associati a manutenzioni.

Utilizza un FileField per ricevere file dal browser. La validazione
verifica solo la presenza del file, lasciando eventuali controlli
sull'estensione e dimensione a livello di route.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired


class AllegatoForm(FlaskForm):
    file = FileField('Seleziona file', validators=[FileRequired()])