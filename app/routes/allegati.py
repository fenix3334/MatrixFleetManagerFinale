"""
Blueprint per la gestione degli allegati alle manutenzioni.

Permette di caricare, scaricare ed eliminare file associati ad una
manutenzione. I file vengono salvati sotto la cartella static/uploads.
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
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import Manutenzione, AllegatoManutenzione
from app.extensions import db
from app.utils.nuclei import can_access_record


allegati_bp = Blueprint('allegati', __name__, url_prefix='/allegati')

# Determina la cartella di upload basata sulla posizione del pacchetto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

# Estensioni consentite (solo per riferimento, non viene controllato nel codice)
ALLOWED_EXTENSIONS = {
    'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xlsx', 'txt'
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@allegati_bp.route('/upload/<int:manutenzione_id>', methods=['POST'])
@login_required
def upload_allegato(manutenzione_id):
    """
    Carica un allegato per la manutenzione specificata. Accetta un file dal
    form e lo salva nella directory di upload. Viene creato un record nella
    tabella AllegatoManutenzione.
    """
    manutenzione = Manutenzione.query.get_or_404(manutenzione_id)
    # Verifica accesso
    if not can_access_record(manutenzione):
        abort(403)
    uploaded_file = request.files.get('file')
    if not uploaded_file or uploaded_file.filename == '':
        flash('Nessun file selezionato.', 'error')
        return redirect(url_for('manutenzioni.dettaglio_manutenzione', id=manutenzione_id))
    # Verifica estensione consentita (opzionale)
    filename = secure_filename(uploaded_file.filename)
    # Assicurati che la directory esista
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Crea un nome univoco per evitare conflitti
    unique_name = f"{manutenzione_id}_{int(time.time())}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    try:
        uploaded_file.save(file_path)
        # Salva nel DB
        allegato = AllegatoManutenzione(
            manutenzione_id=manutenzione_id,
            filename=filename,
            filepath=unique_name,
        )
        db.session.add(allegato)
        db.session.commit()
        flash('Allegato caricato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante il caricamento del file: {str(e)}', 'error')
    return redirect(url_for('manutenzioni.dettaglio_manutenzione', id=manutenzione_id))


@allegati_bp.route('/download/<int:allegato_id>')
@login_required
def download_allegato(allegato_id):
    """
    Permette di scaricare un allegato. Verifica i permessi prima di servire il file.
    """
    allegato = AllegatoManutenzione.query.get_or_404(allegato_id)
    manutenzione = allegato.manutenzione
    if not can_access_record(manutenzione):
        abort(403)
    # Usa send_from_directory per servire il file
    return send_from_directory(
        UPLOAD_FOLDER,
        allegato.filepath,
        as_attachment=True,
        download_name=allegato.filename,
    )


@allegati_bp.route('/delete/<int:allegato_id>', methods=['POST'])
@login_required
def delete_allegato(allegato_id):
    """
    Elimina un allegato sia dal disco che dal database.
    """
    allegato = AllegatoManutenzione.query.get_or_404(allegato_id)
    manutenzione = allegato.manutenzione
    if not can_access_record(manutenzione):
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
    return redirect(url_for('manutenzioni.dettaglio_manutenzione', id=manutenzione.id))