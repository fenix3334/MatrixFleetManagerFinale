"""
Blueprint Report
----------------

Questo modulo definisce le route per generare report dettagliati dei veicoli.
L'utente può visualizzare e stampare una panoramica delle informazioni
relative a un veicolo specifico (dati anagrafici, scadenze, manutenzioni,
fornitori collegati) e selezionare quali sezioni includere nella stampa.

La funzionalità è pensata per fornire a colpo d'occhio lo stato di un veicolo
al momento della consultazione, consentendo di evidenziare eventuali
interventi da programmare (manutenzioni da fare, scadenze imminenti, ecc.).
"""

from flask import Blueprint, render_template, redirect, url_for, abort, request
from flask_login import login_required
from datetime import date

from app.models import Veicolo, Manutenzione, Scadenza, Fornitore
from sqlalchemy import func

# Definizione blueprint
report_bp = Blueprint('report', __name__, url_prefix='/report')


@report_bp.route('/veicolo/<int:veicolo_id>', methods=['GET'])
@login_required
def report_veicolo(veicolo_id):
    """Mostra un report dinamico per un veicolo.

    La pagina presenta le informazioni principali del veicolo e consente
    all'utente di scegliere quali sezioni stampare tramite check-box. Le
    sezioni includono: dati di base del veicolo, manutenzioni da fare,
    manutenzioni eseguite, scadenze imminenti e scadenze scadute. I fornitori
    associati a ciascuna manutenzione e scadenza vengono anch'essi mostrati.
    """

    veicolo = Veicolo.query.get_or_404(veicolo_id)

    # Recupera manutenzioni per il veicolo
    # Separiamo le manutenzioni eseguite da quelle da fare.  Usiamo un confronto
    # case-insensitive per gestire eventuali variazioni di maiuscole/minuscole
    # o spazi nel campo 'stato'.  Tutti i valori diversi da "eseguita" sono
    # considerati "da fare".
    manutenzioni_da_fare = (
        Manutenzione.query
        .filter(Manutenzione.veicolo_id == veicolo.id)
        .filter(func.lower(func.trim(Manutenzione.stato)) != 'eseguita')
        .order_by(Manutenzione.data_intervento.desc())
        .all()
    )
    manutenzioni_eseguite = (
        Manutenzione.query
        .filter(Manutenzione.veicolo_id == veicolo.id)
        .filter(func.lower(func.trim(Manutenzione.stato)) == 'eseguita')
        .order_by(Manutenzione.data_intervento.desc())
        .all()
    )

    # Recupera scadenze. Distinguere tra scadenze future/attive e scadute
    oggi = date.today()
    scadenze_attive = Scadenza.query.filter_by(veicolo_id=veicolo.id).filter(Scadenza.data_scadenza >= oggi).order_by(
        Scadenza.data_scadenza
    ).all()
    scadenze_scadute = Scadenza.query.filter_by(veicolo_id=veicolo.id).filter(Scadenza.data_scadenza < oggi).order_by(
        Scadenza.data_scadenza.desc()
    ).all()

    # I fornitori non sono direttamente collegati al veicolo, ma attraverso manutenzioni
    # e, eventualmente, la società di noleggio. Per una panoramica, estraiamo quelli
    # utilizzati nelle manutenzioni da fare.
    fornitori_utilizzati = {}
    for manutenzione in manutenzioni_da_fare + manutenzioni_eseguite:
        if manutenzione.fornitore:
            fornitori_utilizzati[manutenzione.fornitore.id] = manutenzione.fornitore

    return render_template(
        'report/veicolo.html',
        veicolo=veicolo,
        manutenzioni_da_fare=manutenzioni_da_fare,
        manutenzioni_eseguite=manutenzioni_eseguite,
        scadenze_attive=scadenze_attive,
        scadenze_scadute=scadenze_scadute,
        fornitori_utilizzati=fornitori_utilizzati
    )