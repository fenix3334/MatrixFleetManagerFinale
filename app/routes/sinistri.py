"""
Blueprint e route per la gestione dei sinistri.

Il modulo ``sinistri`` consente di creare, modificare, visualizzare ed
eliminare le pratiche di sinistro associate ai veicoli.  È possibile
allegare file (ad es. CID, documenti, foto) tramite l'apposito
blueprint ``allegati_sinistri``.  Le rotte sono protette da
``@login_required`` e rispettano i permessi basati sul nucleo
dell'utente.
"""

import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from flask_login import login_required, current_user
from app.models import Sinistro, Veicolo
from app.forms.sinistri import SinistroForm, AllegatoSinistroForm
from app.extensions import db
from app.utils.nuclei import (
    get_sinistri_by_nucleo,
    get_veicoli_by_nucleo,
    can_access_record,
    get_nucleo_corrente_admin,
)

from sqlalchemy import inspect, text

sinistri_bp = Blueprint('sinistri', __name__)


# Migrazione automatica: verifica e aggiunge le colonne mancanti nella
# tabella "sinistri". SQLite non supporta l'aggiunta di colonne con
# vincoli complessi, ma è possibile aggiungere colonne semplici di tipo
# TEXT o DATE senza rompere lo schema esistente.  Questa funzione viene
# eseguita all'avvio della pagina per garantire che le nuove
# funzionalità non generino errori su database esistenti.  Se le colonne
# sono già presenti, non viene eseguita alcuna modifica.
def ensure_sinistri_columns() -> None:
    inspector = inspect(db.engine)
    try:
        columns_info = inspector.get_columns('sinistri')
    except Exception:
        return
    existing = {col['name'] for col in columns_info}
    # Elenco delle nuove colonne da creare: nome e tipo SQL
    for col_name, col_type in [
        ('numero_sinistro', 'TEXT'),
        ('cellulare_controparte', 'TEXT'),
        ('cellulare_autista', 'TEXT'),
        ('numero_patente_autista', 'TEXT'),
        ('numero_patente_controparte', 'TEXT'),
        ('comune_patente_autista', 'TEXT'),
        ('comune_patente_controparte', 'TEXT'),
        ('data_emissione_patente_autista', 'DATE'),
        ('data_scadenza_patente_autista', 'DATE'),
        ('data_emissione_patente_controparte', 'DATE'),
        ('data_scadenza_patente_controparte', 'DATE'),
    ]:
        if col_name not in existing:
            try:
                db.session.execute(text(f"ALTER TABLE sinistri ADD COLUMN {col_name} {col_type}"))
                db.session.commit()
            except Exception:
                # Ignore errors (e.g., column already exists in race conditions)
                db.session.rollback()
                pass


def validate_sinistro_access(sinistro_id: int) -> Sinistro:
    """Verifica che l'utente possa accedere al sinistro.

    Se il sinistro non esiste o l'utente non ha i permessi
    adeguati, lancia un abort con codice 404 o 403.
    """
    sinistro = Sinistro.query.get_or_404(sinistro_id)
    if not can_access_record(sinistro):
        abort(403)
    return sinistro


@sinistri_bp.route('/')
@login_required
def index_sinistri():
    """Elenca i sinistri registrati, con filtri per tipo e veicolo.

    Prima di eseguire la query, viene invocata una procedura di
    migrazione automatica che assicura la presenza delle nuove
    colonne opzionali nella tabella ``sinistri``.  Questo evita
    l'eccezione ``OperationalError: no such column`` nel caso in cui
    l'utente non abbia eseguito uno script di migrazione manuale.
    """
    # Garantisce che le nuove colonne opzionali esistano nel DB.
    ensure_sinistri_columns()
    # Filtri da querystring
    tipo_filter = request.args.get('tipo', 'tutti')
    veicolo_filter = request.args.get('veicolo', 'tutti')
    page = request.args.get('page', 1, type=int)

    query = get_sinistri_by_nucleo().order_by(Sinistro.data_sinistro.desc())
    if tipo_filter != 'tutti':
        query = query.filter_by(tipo=tipo_filter)
    if veicolo_filter != 'tutti':
        try:
            veicolo_id = int(veicolo_filter)
            query = query.filter_by(veicolo_id=veicolo_id)
        except ValueError:
            pass

    pagination = query.paginate(page=page, per_page=10)
    sinistri = pagination.items

    # Opzioni filtri
    tipi_sinistro = sorted({s.tipo for s in get_sinistri_by_nucleo().all() if s.tipo})
    veicoli_choices = [
        (v.id, f"{v.targa} - {v.marca} {v.modello}")
        for v in get_veicoli_by_nucleo().order_by(Veicolo.targa).all()
    ]

    # Statistiche rapide
    totale = get_sinistri_by_nucleo().count()
    con_controparte = get_sinistri_by_nucleo().filter_by(tipo='Con controparte').count()
    vandalico = get_sinistri_by_nucleo().filter_by(tipo='Vandalico').count()
    sconosciuto = get_sinistri_by_nucleo().filter_by(tipo='Sconosciuto').count()

    return render_template(
        'sinistri/index.html',
        sinistri=sinistri,
        pagination=pagination,
        tipi_sinistro=tipi_sinistro,
        veicoli_choices=veicoli_choices,
        tipo_filter=tipo_filter,
        veicolo_filter=veicolo_filter,
        totale=totale,
        con_controparte=con_controparte,
        vandalico=vandalico,
        sconosciuto=sconosciuto,
    )


@sinistri_bp.route('/nuovo', methods=['GET', 'POST'])
@login_required
def aggiungi_sinistro():
    """Crea un nuovo sinistro."""
    form = SinistroForm()
    # Filtra le scelte dei veicoli per nucleo, analogamente ad altri moduli
    # Mostriamo solo i veicoli del nucleo corrente (o del filtro admin) ordinati per targa.
    veicoli_query = get_veicoli_by_nucleo().order_by(Veicolo.targa)
    form.veicolo_id.choices = [
        (v.id, f"{v.targa} - {v.marca} {v.modello}") for v in veicoli_query.all()
    ]
    if form.validate_on_submit():
        # Determina il nucleo associato al sinistro in base al veicolo scelto.
        #
        # In precedenza veniva assegnato il nucleo dell'utente (o del filtro admin) al
        # sinistro. Ciò portava a una incoerenza quando si registrava un sinistro per
        # un veicolo appartenente a un altro nucleo, perché il record veniva
        # associato al nucleo dell'utente e non a quello del veicolo.  Per garantire
        # la corretta separazione per nuclei, recuperiamo il nucleo dal veicolo
        # selezionato. Se il veicolo non esiste (caso raro), ricadiamo sul nucleo
        # corrente dell'utente/admin.
        selected_vehicle = Veicolo.query.get(form.veicolo_id.data)
        if current_user.ruolo == 'admin':
            # L'admin può creare sinistri per veicoli di qualsiasi nucleo.
            # Usiamo il nucleo del veicolo se presente; in caso contrario,
            # usiamo il filtro admin corrente o il nucleo dell'admin stesso.
            nucleo_target = selected_vehicle.nucleo if selected_vehicle else (get_nucleo_corrente_admin() or current_user.nucleo)
        else:
            # L'utente normale deve utilizzare il nucleo del veicolo scelto.
            nucleo_target = selected_vehicle.nucleo if selected_vehicle else current_user.nucleo

        sinistro = Sinistro(
            veicolo_id=form.veicolo_id.data,
            data_sinistro=form.data_sinistro.data,
            luogo=form.luogo.data,
            veicoli_coinvolti=form.veicoli_coinvolti.data,
            tipo=form.tipo.data,
            descrizione=form.descrizione.data,
            # Nuovi campi aggiuntivi
            numero_sinistro=form.numero_sinistro.data,
            cellulare_controparte=form.cellulare_controparte.data,
            cellulare_autista=form.cellulare_autista.data,
            numero_patente_autista=form.numero_patente_autista.data,
            numero_patente_controparte=form.numero_patente_controparte.data,
            comune_patente_autista=form.comune_patente_autista.data,
            comune_patente_controparte=form.comune_patente_controparte.data,
            data_emissione_patente_autista=form.data_emissione_patente_autista.data,
            data_scadenza_patente_autista=form.data_scadenza_patente_autista.data,
            data_emissione_patente_controparte=form.data_emissione_patente_controparte.data,
            data_scadenza_patente_controparte=form.data_scadenza_patente_controparte.data,
            nucleo=nucleo_target,
        )
        db.session.add(sinistro)
        db.session.commit()
        flash('Sinistro creato con successo!', 'success')
        return redirect(url_for('sinistri.index_sinistri'))
    return render_template('sinistri/form.html', form=form, new=True)


@sinistri_bp.route('/modifica/<int:sinistro_id>', methods=['GET', 'POST'])
@login_required
def modifica_sinistro(sinistro_id: int):
    """Modifica un sinistro esistente."""
    sinistro = validate_sinistro_access(sinistro_id)
    form = SinistroForm(obj=sinistro)
    # Aggiorna le scelte dei veicoli in base al nucleo come per l'aggiunta
    veicoli_query = get_veicoli_by_nucleo().order_by(Veicolo.targa)
    form.veicolo_id.choices = [
        (v.id, f"{v.targa} - {v.marca} {v.modello}") for v in veicoli_query.all()
    ]
    # Includi comunque il veicolo corrente se non presente nella lista (es. veicolo dismesso)
    if all(choice[0] != sinistro.veicolo_id for choice in form.veicolo_id.choices):
        current_vehicle = Veicolo.query.get(sinistro.veicolo_id)
        if current_vehicle:
            form.veicolo_id.choices.append(
                (current_vehicle.id, f"{current_vehicle.targa} - {current_vehicle.marca} {current_vehicle.modello}")
            )
    if form.validate_on_submit():
        # Aggiorna i campi
        sinistro.veicolo_id = form.veicolo_id.data
        sinistro.data_sinistro = form.data_sinistro.data
        sinistro.luogo = form.luogo.data
        sinistro.veicoli_coinvolti = form.veicoli_coinvolti.data
        sinistro.tipo = form.tipo.data
        sinistro.descrizione = form.descrizione.data
        # Aggiorna nuovi campi
        sinistro.numero_sinistro = form.numero_sinistro.data
        sinistro.cellulare_controparte = form.cellulare_controparte.data
        sinistro.cellulare_autista = form.cellulare_autista.data
        sinistro.numero_patente_autista = form.numero_patente_autista.data
        sinistro.numero_patente_controparte = form.numero_patente_controparte.data
        sinistro.comune_patente_autista = form.comune_patente_autista.data
        sinistro.comune_patente_controparte = form.comune_patente_controparte.data
        sinistro.data_emissione_patente_autista = form.data_emissione_patente_autista.data
        sinistro.data_scadenza_patente_autista = form.data_scadenza_patente_autista.data
        sinistro.data_emissione_patente_controparte = form.data_emissione_patente_controparte.data
        sinistro.data_scadenza_patente_controparte = form.data_scadenza_patente_controparte.data
        # Aggiorna nucleo in base al veicolo selezionato per evitare inconsistenze tra
        # nucleo dell'utente e nucleo del veicolo. Recuperiamo il veicolo
        # selezionato e ne utilizziamo il nucleo. Se il veicolo non esiste (caso
        # raro), ricadiamo sul nucleo dell'utente o del filtro admin.
        selected_vehicle = Veicolo.query.get(form.veicolo_id.data)
        if current_user.ruolo == 'admin':
            nucleo_target = selected_vehicle.nucleo if selected_vehicle else (get_nucleo_corrente_admin() or current_user.nucleo)
        else:
            nucleo_target = selected_vehicle.nucleo if selected_vehicle else current_user.nucleo
        sinistro.nucleo = nucleo_target
        db.session.commit()
        flash('Sinistro aggiornato con successo.', 'success')
        return redirect(url_for('sinistri.index_sinistri'))
    return render_template('sinistri/form.html', form=form, sinistro=sinistro, new=False)


@sinistri_bp.route('/dettaglio/<int:sinistro_id>')
@login_required
def dettaglio_sinistro(sinistro_id: int):
    """Mostra il dettaglio di un sinistro."""
    sinistro = validate_sinistro_access(sinistro_id)
    allegato_form = AllegatoSinistroForm()
    return render_template('sinistri/dettaglio.html', sinistro=sinistro, allegato_form=allegato_form)


@sinistri_bp.route('/elimina/<int:sinistro_id>', methods=['POST'])
@login_required
def elimina_sinistro(sinistro_id: int):
    """Elimina un sinistro dal database e rimuove i relativi allegati."""
    sinistro = validate_sinistro_access(sinistro_id)
    # Rimuove file allegati dal disco
    # Determina la cartella di upload (stesso approccio del blueprint allegati)
    from app.routes.allegati_sinistri import UPLOAD_FOLDER as SINISTRI_UPLOAD
    for allegato in sinistro.allegati:
        file_path = os.path.join(SINISTRI_UPLOAD, allegato.filepath)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
    db.session.delete(sinistro)
    db.session.commit()
    flash('Sinistro eliminato con successo.', 'success')
    return redirect(url_for('sinistri.index_sinistri'))