"""
Blueprint per la gestione degli allegati alle scadenze.

Permette di caricare, scaricare ed eliminare file associati ad una
scadenza. I file vengono salvati sotto la cartella static/uploads.

Questo modulo è simile a quello utilizzato per le manutenzioni, ma
è stato adattato per lavorare con il modello AllegatoScadenza e
Scadenza.
"""

import os
import time
from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    abort,
    send_from_directory,
)
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.models import Scadenza, AllegatoScadenza
from app.extensions import db
from app.utils.nuclei import can_access_record


allegati_scadenze_bp = Blueprint(
    'allegati_scadenze', __name__, url_prefix='/allegati-scadenze'
)

# Determina la cartella di upload basata sulla posizione del pacchetto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

# Estensioni consentite (solo per riferimento, non viene controllato nel codice)
ALLOWED_EXTENSIONS = {
    'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xlsx', 'txt'
}


def allowed_file(filename: str) -> bool:
    """Verifica se il file ha un'estensione consentita."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@allegati_scadenze_bp.route('/upload/<int:scadenza_id>', methods=['POST'])
@login_required
def upload_allegato_scadenza(scadenza_id: int):
    """
    Carica un allegato per la scadenza specificata. Accetta un file dal
    form e lo salva nella directory di upload. Viene creato un record nella
    tabella AllegatoScadenza.
    """
    scadenza = Scadenza.query.get_or_404(scadenza_id)
    # Verifica accesso
    if not can_access_record(scadenza):
        abort(403)
    uploaded_file = request.files.get('file')
    if not uploaded_file or uploaded_file.filename == '':
        flash('Nessun file selezionato.', 'error')
        return redirect(url_for('scadenze.dettaglio_scadenza', id=scadenza_id))
    filename = secure_filename(uploaded_file.filename)
    # Assicurati che la directory esista
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Crea un nome univoco per evitare conflitti
    unique_name = f"scadenza{scadenza_id}_{int(time.time())}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    try:
        uploaded_file.save(file_path)
        # Salva nel DB
        allegato = AllegatoScadenza(
            scadenza_id=scadenza_id,
            filename=filename,
            filepath=unique_name,
        )
        db.session.add(allegato)
        db.session.commit()
        flash('Allegato caricato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante il caricamento del file: {str(e)}', 'error')
    return redirect(url_for('scadenze.dettaglio_scadenza', id=scadenza_id))


@allegati_scadenze_bp.route('/download/<int:allegato_id>')
@login_required
def download_allegato_scadenza(allegato_id: int):
    """
    Permette di scaricare un allegato. Verifica i permessi prima di servire il file.
    """
    allegato = AllegatoScadenza.query.get_or_404(allegato_id)
    scadenza = allegato.scadenza
    if not can_access_record(scadenza):
        abort(403)
    return send_from_directory(
        UPLOAD_FOLDER,
        allegato.filepath,
        as_attachment=True,
        download_name=allegato.filename,
    )


@allegati_scadenze_bp.route('/delete/<int:allegato_id>', methods=['POST'])
@login_required
def delete_allegato_scadenza(allegato_id: int):
    """
    Elimina un allegato sia dal disco che dal database.
    """
    allegato = AllegatoScadenza.query.get_or_404(allegato_id)
    scadenza = allegato.scadenza
    if not can_access_record(scadenza):
        abort(403)
    file_path = os.path.join(UPLOAD_FOLDER, allegato.filepath)
    try:
        # Rimuove il file dal disco se esiste
        if os.path.isfile(file_path):
            os.remove(file_path)
        db.session.delete(allegato)
        db.session.commit()
        flash('Allegato eliminato con successo.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione dell\'allegato: {str(e)}', 'error')
    return redirect(url_for('scadenze.dettaglio_scadenza', id=scadenza.id))