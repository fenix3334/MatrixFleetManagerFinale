"""
Blueprint per la gestione delle manutenzioni preventive.

Permette di definire intervalli di manutenzione periodica per ogni veicolo e
fornire un elenco delle attività programmate. L'obiettivo è quello di
facilitare una manutenzione proattiva senza modificare le tabelle esistenti.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import login_required, current_user
from app.models import ManutenzionePreventiva, Veicolo, LogPreventiva
from app.forms.manutenzione_preventiva import ManutenzionePreventivaForm
from app.extensions import db
from app.utils.nuclei import (
    get_manutenzioni_preventive_by_nucleo,
    get_veicoli_for_choices,
    can_access_record,
    get_nucleo_info,
)
import io
import pandas as pd


manutenzioni_preventive_bp = Blueprint('manutenzioni_preventive', __name__, url_prefix='/preventive')


def validate_preventiva_access(preventiva_id):
    """Verifica che l'utente possa accedere alla manutenzione preventiva."""
    preventiva = ManutenzionePreventiva.query.get_or_404(preventiva_id)
    if not can_access_record(preventiva):
        abort(403)
    return preventiva


@manutenzioni_preventive_bp.route('/')
@login_required
def index_preventive():
    """
    Elenco delle manutenzioni preventive. Consente filtri per tipo e veicolo.
    """
    page = request.args.get('page', 1, type=int)
    preventive_query = get_manutenzioni_preventive_by_nucleo()

    # Filtri facoltativi
    tipo_filter = request.args.get('tipo')
    veicolo_filter = request.args.get('veicolo')

    if tipo_filter:
        preventive_query = preventive_query.filter_by(tipo_intervento=tipo_filter)
    if veicolo_filter:
        preventive_query = preventive_query.filter_by(veicolo_id=veicolo_filter)

    preventive_paginate = preventive_query.order_by(
        ManutenzionePreventiva.id.desc()
    ).paginate(page=page, per_page=20, error_out=False)

    # Statistiche di base
    tutte_preventive = get_manutenzioni_preventive_by_nucleo()
    stats = {
        'totale': tutte_preventive.count(),
    }

    # Opzioni per filtri: lista dei tipi di intervento presenti nel nucleo
    tipi_query = (
        get_manutenzioni_preventive_by_nucleo()
        .with_entities(ManutenzionePreventiva.tipo_intervento)
        .distinct()
        .all()
    )
    tipi_disponibili = [t[0] for t in tipi_query if t[0]]

    return render_template(
        'manutenzioni_preventive/index.html',
        preventive=preventive_paginate,
        stats=stats,
        veicoli=get_veicoli_for_choices(),
        tipi=tipi_disponibili,
        filtro_tipo=tipo_filter,
        filtro_veicolo=veicolo_filter,
        nucleo_info=get_nucleo_info(),
    )


@manutenzioni_preventive_bp.route('/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_preventiva():
    """
    Aggiunge una nuova manutenzione preventiva.
    """
    form = ManutenzionePreventivaForm()
    form.veicolo_id.choices = get_veicoli_for_choices()

    if form.validate_on_submit():
        try:
            preventiva = ManutenzionePreventiva(
                veicolo_id=form.veicolo_id.data,
                tipo_intervento=form.tipo_intervento.data,
                intervallo_km=form.intervallo_km.data,
                intervallo_mesi=form.intervallo_mesi.data,
                ultimo_km=form.ultimo_km.data,
                ultima_data=form.ultima_data.data,
                note=form.note.data,
            )
            # Imposta nucleo in base al veicolo
            veicolo = Veicolo.query.get(form.veicolo_id.data)
            if veicolo:
                preventiva.nucleo = veicolo.nucleo
            else:
                preventiva.nucleo = current_user.nucleo

            db.session.add(preventiva)
            db.session.commit()
            # Crea log di creazione
            try:
                log = LogPreventiva(
                    preventiva_id=preventiva.id,
                    user_id=current_user.id if not current_user.is_anonymous else None,
                    azione='creazione',
                    dettagli=f"Creata manutenzione preventiva {preventiva.tipo_intervento}"
                )
                db.session.add(log)
                db.session.commit()
            except Exception:
                db.session.rollback()
            flash(
                f"Manutenzione preventiva '{preventiva.tipo_intervento}' per {preventiva.veicolo.targa} aggiunta con successo!",
                'success',
            )
            return redirect(url_for('manutenzioni_preventive.index_preventive'))
        except Exception as e:
            db.session.rollback()
            flash(f"Errore durante il salvataggio: {str(e)}", 'error')

    return render_template(
        'manutenzioni_preventive/form.html', form=form, titolo='Aggiungi Manutenzione Preventiva'
    )


@manutenzioni_preventive_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_preventiva(id):
    """
    Modifica una manutenzione preventiva esistente.
    """
    preventiva = validate_preventiva_access(id)
    form = ManutenzionePreventivaForm(obj=preventiva)
    form.veicolo_id.choices = get_veicoli_for_choices()

    if form.validate_on_submit():
        try:
            preventiva.veicolo_id = form.veicolo_id.data
            preventiva.tipo_intervento = form.tipo_intervento.data
            preventiva.intervallo_km = form.intervallo_km.data
            preventiva.intervallo_mesi = form.intervallo_mesi.data
            preventiva.ultimo_km = form.ultimo_km.data
            preventiva.ultima_data = form.ultima_data.data
            preventiva.note = form.note.data
            # Aggiorna nucleo se il veicolo è cambiato
            veicolo = Veicolo.query.get(form.veicolo_id.data)
            if veicolo:
                preventiva.nucleo = veicolo.nucleo

            db.session.commit()
            # Crea log di modifica
            try:
                # Rileva campi modificati
                changes = []
                if preventiva.tipo_intervento != form.tipo_intervento.data:
                    changes.append('tipo_intervento')
                if preventiva.intervallo_km != form.intervallo_km.data:
                    changes.append('intervallo_km')
                if preventiva.intervallo_mesi != form.intervallo_mesi.data:
                    changes.append('intervallo_mesi')
                if preventiva.ultimo_km != form.ultimo_km.data:
                    changes.append('ultimo_km')
                if preventiva.ultima_data != form.ultima_data.data:
                    changes.append('ultima_data')
                if preventiva.note != form.note.data:
                    changes.append('note')
                dettagli = ', '.join(changes) if changes else 'nessuna modifica'
                log = LogPreventiva(
                    preventiva_id=preventiva.id,
                    user_id=current_user.id if not current_user.is_anonymous else None,
                    azione='modifica',
                    dettagli=dettagli
                )
                db.session.add(log)
                db.session.commit()
            except Exception:
                db.session.rollback()
            flash(
                f"Manutenzione preventiva '{preventiva.tipo_intervento}' per {preventiva.veicolo.targa} modificata con successo!",
                'success',
            )
            return redirect(url_for('manutenzioni_preventive.index_preventive'))
        except Exception as e:
            db.session.rollback()
            flash(f"Errore durante la modifica: {str(e)}", 'error')

    return render_template(
        'manutenzioni_preventive/form.html', form=form, titolo='Modifica Manutenzione Preventiva'
    )


@manutenzioni_preventive_bp.route('/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_preventiva(id):
    """
    Elimina una manutenzione preventiva. Richiede metodo POST.
    """
    preventiva = validate_preventiva_access(id)
    try:
        descrizione = preventiva.tipo_intervento
        veic_targa = preventiva.veicolo.targa

        # L'eliminazione in cascata rimuoverà automaticamente tutti i log associati
        db.session.delete(preventiva)
        db.session.commit()

        flash(
            f"Manutenzione preventiva '{descrizione}' per {veic_targa} eliminata con successo!",
            'success',
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Errore durante l'eliminazione: {str(e)}", 'error')
    return redirect(url_for('manutenzioni_preventive.index_preventive'))


# === Funzioni aggiuntive per v1.24 ===

@manutenzioni_preventive_bp.route('/export', methods=['GET'])
@login_required
def export_preventive():
    """Esporta l'elenco delle manutenzioni preventive in formato Excel.

    L'export rispetta i filtri di tipo e veicolo passati nella query.
    Il file generato contiene le colonne principali (Veicolo, Tipo
    intervento, Intervallo, Ultimo intervento, Prossimo intervento,
    Note) ed è scaricato come allegato.
    """
    # Ricrea la query filtrata come nella vista index
    preventive_query = get_manutenzioni_preventive_by_nucleo()
    tipo_filter = request.args.get('tipo')
    veicolo_filter = request.args.get('veicolo')
    if tipo_filter:
        preventive_query = preventive_query.filter_by(tipo_intervento=tipo_filter)
    if veicolo_filter:
        preventive_query = preventive_query.filter_by(veicolo_id=veicolo_filter)

    records = preventive_query.order_by(ManutenzionePreventiva.id.desc()).all()

    # Prepara i dati per il DataFrame
    rows = []
    for mp in records:
        next_km = mp.calcola_prossimo_km()
        next_date = mp.calcola_prossima_data()
        rows.append({
            'Veicolo': mp.veicolo.targa if mp.veicolo else '',
            'Tipo intervento': mp.tipo_intervento,
            'Intervallo': f"{mp.intervallo_km or ''}{' km' if mp.intervallo_km else ''} / {mp.intervallo_mesi or ''}{' mesi' if mp.intervallo_mesi else ''}",
            'Ultimo': f"{mp.ultimo_km or ''}{' km' if mp.ultimo_km else ''}{' - ' if mp.ultima_data and mp.ultimo_km else ''}{mp.ultima_data.strftime('%d/%m/%Y') if mp.ultima_data else ''}",
            'Prossimo': f"{next_km or ''}{' km' if next_km else ''}{' / ' if next_date and next_km else ''}{next_date.strftime('%d/%m/%Y') if next_date else ''}",
            'Note': mp.note or '',
        })
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name='manutenzioni_preventive.xlsx', as_attachment=True)


@manutenzioni_preventive_bp.route('/cronologia/<int:id>')
@login_required
def cronologia_preventiva(id):
    """Mostra la cronologia (log) delle operazioni su una manutenzione preventiva."""
    preventiva = validate_preventiva_access(id)
    # Ordina i log dal più recente al più vecchio
    logs = LogPreventiva.query.filter_by(preventiva_id=id).order_by(LogPreventiva.data_creazione.desc()).all()
    return render_template('manutenzioni_preventive/cronologia.html', preventiva=preventiva, logs=logs)