"""Moduli di reportistica.

Questo blueprint gestisce la generazione di report e la stampa dinamica per i veicoli.
L'utente può selezionare quali sezioni includere nel report (dati veicolo,
manutenzioni, scadenze, fornitori per manutenzione). L'output è una pagina
stampabile con i dati selezionati.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Veicolo, Manutenzione, Scadenza, Fornitore
from datetime import date
from sqlalchemy import or_

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/report/veicolo/<int:veicolo_id>', methods=['GET', 'POST'])
@login_required
def vehicle_report(veicolo_id):
    """Genera un report per un singolo veicolo.

    L'utente può selezionare quali sezioni includere nel report tramite
    checkboxes. Se non viene specificato nulla, vengono inclusi tutti i dati.
    """
    veicolo = Veicolo.query.get_or_404(veicolo_id)
    # Sezioni disponibili
    sections = [
        ('dati_veicolo', 'Dati veicolo'),
        ('manutenzioni_fatte', 'Manutenzioni fatte'),
        ('manutenzioni_da_fare', 'Manutenzioni da fare'),
        ('scadenze_passate', 'Scadenze passate'),
        ('scadenze_future', 'Scadenze future'),
        ('fornitori', 'Fornitori (meccanico/gommista)')
    ]
    if request.method == 'POST':
        selected = request.form.getlist('sections')
        if not selected:
            # Se nessuna sezione è selezionata, segnala errore
            flash('Seleziona almeno una sezione da includere nel report.', 'warning')
            selected = []
    else:
        # Carica le sezioni selezionate dalla query string o tutte se non specificato
        selected = request.args.getlist('sections') or [s[0] for s in sections]
    # Raccolta dati in base alle sezioni selezionate
    manutenzioni_fatte = []
    manutenzioni_da_fare = []
    if 'manutenzioni_fatte' in selected or 'manutenzioni_da_fare' in selected:
        q_man = Manutenzione.query.filter_by(veicolo_id=veicolo.id)
        if 'manutenzioni_fatte' in selected:
            manutenzioni_fatte = q_man.filter_by(stato='Fatto').order_by(Manutenzione.data_intervento.desc()).all()
        if 'manutenzioni_da_fare' in selected:
            manutenzioni_da_fare = q_man.filter_by(stato='Da Fare').order_by(Manutenzione.data_intervento.desc()).all()
    scadenze_passate = []
    scadenze_future = []
    if 'scadenze_passate' in selected or 'scadenze_future' in selected:
        oggi = date.today()
        q_sca = Scadenza.query.filter_by(veicolo_id=veicolo.id)
        if 'scadenze_passate' in selected:
            scadenze_passate = q_sca.filter(Scadenza.data_scadenza < oggi).order_by(Scadenza.data_scadenza.desc()).all()
        if 'scadenze_future' in selected:
            scadenze_future = q_sca.filter(Scadenza.data_scadenza >= oggi).order_by(Scadenza.data_scadenza.asc()).all()
    fornitori = []
    if 'fornitori' in selected:
        # Cerca fornitori che contengono parole chiave meccanico/gommista in uno dei campi settore
        search_terms = ['meccanico', 'gommista', 'carrozzeria', 'officina']
        filters = []
        for term in search_terms:
            like_term = f"%{term}%"
            filters.append(Fornitore.settore.ilike(like_term))
            filters.append(Fornitore.settore_2.ilike(like_term))
            filters.append(Fornitore.settore_3.ilike(like_term))
            filters.append(Fornitore.settore_personalizzato.ilike(like_term))
        fornitori = (
            Fornitore.query
            .filter(Fornitore.attivo == True)
            .filter(or_(*filters))
            .order_by(Fornitore.ragione_sociale)
            .all()
        )
    return render_template(
        'reports/vehicle_report.html',
        veicolo=veicolo,
        sections=sections,
        selected=selected,
        manutenzioni_fatte=manutenzioni_fatte,
        manutenzioni_da_fare=manutenzioni_da_fare,
        scadenze_passate=scadenze_passate,
        scadenze_future=scadenze_future,
        fornitori=fornitori
    )