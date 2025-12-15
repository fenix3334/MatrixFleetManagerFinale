"""
Blueprint per la gestione degli allegati ai sinistri.

Questo modulo consente di caricare, scaricare ed eliminare file
associati a un sinistro.  I file vengono salvati nella cartella
``static/uploads/sinistri``.  L'accesso alle operazioni è limitato
agli utenti autenticati e al nucleo corretto tramite la funzione
``can_access_record``.
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

from app.models import Sinistro, AllegatoSinistro
from app.extensions import db
from app.utils.nuclei import can_access_record


allegati_sinistri_bp = Blueprint(
    'allegati_sinistri', __name__, url_prefix='/allegati-sinistri'
)

# Determina la cartella di upload basata sulla posizione del pacchetto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'sinistri')

# Estensioni consentite (solo per riferimento, non viene controllato nel codice)
ALLOWED_EXTENSIONS = {
    'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xlsx', 'txt'
}

def allowed_file(filename: str) -> bool:
    """Verifica se il file ha un'estensione consentita."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@allegati_sinistri_bp.route('/upload/<int:sinistro_id>', methods=['POST'])
@login_required
def upload_allegato_sinistro(sinistro_id: int):
    """
    Carica un allegato per il sinistro specificato.  Accetta un file dal
    form e lo salva nella directory di upload.  Viene creato un record
    nella tabella ``AllegatoSinistro``.
    """
    sinistro = Sinistro.query.get_or_404(sinistro_id)
    # Verifica accesso
    if not can_access_record(sinistro):
        abort(403)
    uploaded_file = request.files.get('file')
    if not uploaded_file or uploaded_file.filename == '':
        flash('Nessun file selezionato.', 'error')
        return redirect(url_for('sinistri.dettaglio_sinistro', sinistro_id=sinistro_id))
    filename = secure_filename(uploaded_file.filename)
    # Assicurati che la directory esista
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Crea un nome univoco per evitare conflitti
    unique_name = f"sinistro{sinistro_id}_{int(time.time())}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    try:
        uploaded_file.save(file_path)
        # Salva nel DB
        allegato = AllegatoSinistro(
            sinistro_id=sinistro_id,
            filename=filename,
            filepath=unique_name,
        )
        db.session.add(allegato)
        db.session.commit()
        flash('Allegato caricato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante il caricamento del file: {str(e)}', 'error')
    return redirect(url_for('sinistri.dettaglio_sinistro', sinistro_id=sinistro_id))


@allegati_sinistri_bp.route('/download/<int:allegato_id>')
@login_required
def download_allegato_sinistro(allegato_id: int):
    """
    Permette di scaricare un allegato.  Verifica i permessi prima di
    servire il file.
    """
    allegato = AllegatoSinistro.query.get_or_404(allegato_id)
    sinistro = allegato.sinistro
    if not can_access_record(sinistro):
        abort(403)
    return send_from_directory(
        UPLOAD_FOLDER,
        allegato.filepath,
        as_attachment=True,
        download_name=allegato.filename,
    )


@allegati_sinistri_bp.route('/delete/<int:allegato_id>', methods=['POST'])
@login_required
def delete_allegato_sinistro(allegato_id: int):
    """
    Elimina un allegato sia dal disco che dal database.
    """
    allegato = AllegatoSinistro.query.get_or_404(allegato_id)
    sinistro = allegato.sinistro
    if not can_access_record(sinistro):
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
        flash(f"Errore durante l'eliminazione dell'allegato: {str(e)}", 'error')
    return redirect(url_for('sinistri.dettaglio_sinistro', sinistro_id=sinistro.id))
