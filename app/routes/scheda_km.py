
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required
from app.extensions import db
from app.models import SchedaKilometrica, Veicolo
# Importa utilities per la gestione dei nuclei.  Queste funzioni permettono
# di filtrare i veicoli in base al nucleo dell'utente corrente o al filtro
# selezionato dall'amministratore.  In questo modo la scheda kilometrica
# mostra solo i veicoli pertinenti al nucleo corrente.
from app.utils.nuclei import get_veicoli_by_nucleo
import calendar, io
import pandas as pd
from datetime import datetime

scheda_km_bp = Blueprint('scheda_km', __name__)

# A landing page for the Scheda Kilometrica that allows the user to select
# the year and month they wish to work with.  Without this endpoint the
# navigation always directs to a fixed month (September 2025).  On a GET
# request it renders a form with drop-downs for year and month.  On a POST
# it redirects to the `scheda_km_mese` view passing the chosen year and
# month.  Years are sourced from existing records in the database; if no
# records exist, the current year is used by default.  Months are
# represented by numbers (1-12) and names in Italian.
@scheda_km_bp.route('/scheda-km', methods=['GET', 'POST'])
@login_required
def select_scheda_km():
    # Determine available years from existing SchedaKilometrica records. If
    # the table is empty, fall back to the current year.
    years_query = db.session.query(SchedaKilometrica.anno).distinct().order_by(SchedaKilometrica.anno.desc()).all()
    years = [y[0] for y in years_query] if years_query else [datetime.now().year]
    # Provide a list of month tuples (number, name) for the dropdown.
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    if request.method == 'POST':
        selected_year = int(request.form.get('anno'))
        selected_month = int(request.form.get('mese'))
        return redirect(url_for('scheda_km.scheda_km_mese', anno=selected_year, mese=selected_month))
    # Default selections: the latest year and current month.
    default_year = years[0]
    default_month = datetime.now().month
    return render_template('scheda_km/select.html', years=years, months=months,
                           default_year=default_year, default_month=default_month)

@scheda_km_bp.route('/scheda-km/<int:anno>/<int:mese>', methods=['GET', 'POST'])
@login_required
def scheda_km_mese(anno, mese):
    # Filtra i veicoli per nucleo utilizzando l'utility.  Questo assicura che
    # gli utenti vedano solo i veicoli del proprio nucleo o, nel caso di
    # amministratori con un filtro attivo, solo i veicoli del nucleo selezionato.
    # Mostra solo i veicoli attivi per la compilazione della scheda mensile.
    # In assenza di una data di dismissione, si esclude chiunque abbia stato diverso da 'Attivo'.
    veicoli = get_veicoli_by_nucleo().filter_by(stato='Attivo').all()
    if request.method == 'POST':
        for veicolo in veicoli:
            km_ini = request.form.get(f'km_iniziali_{veicolo.id}')
            km_fin = request.form.get(f'km_finali_{veicolo.id}')
            record = SchedaKilometrica.query.filter_by(anno=anno, mese=mese, veicolo_id=veicolo.id).first()
            if not record:
                record = SchedaKilometrica(anno=anno, mese=mese, veicolo_id=veicolo.id)
            record.km_iniziali = int(km_ini) if km_ini else None
            record.km_finali = int(km_fin) if km_fin else None
            db.session.add(record)
        db.session.commit()
        flash('Dati aggiornati con successo!', 'success')
        return redirect(url_for('scheda_km.scheda_km_mese', anno=anno, mese=mese))

    data = []
    for veicolo in veicoli:
        record = SchedaKilometrica.query.filter_by(anno=anno, mese=mese, veicolo_id=veicolo.id).first()
        data.append({
            'veicolo': veicolo,
            'km_iniziali': record.km_iniziali if record else '',
            'km_finali': record.km_finali if record else '',
            'km_percorsi': record.km_percorsi if record else ''
        })
    # Mappa dei nomi dei mesi in italiano per visualizzazione
    mesi_ita = {
        1: 'Gennaio', 2: 'Febbraio', 3: 'Marzo', 4: 'Aprile', 5: 'Maggio', 6: 'Giugno',
        7: 'Luglio', 8: 'Agosto', 9: 'Settembre', 10: 'Ottobre', 11: 'Novembre', 12: 'Dicembre'
    }
    nome_mese = mesi_ita.get(mese, '')
    # Calcola il numero di trimestre per fornire un link diretto al riepilogo trimestrale.
    trimestre = (mese - 1) // 3 + 1
    return render_template('scheda_km/index.html', anno=anno, mese=mese, nome_mese=nome_mese,
                           data=data, trimestre=trimestre)

@scheda_km_bp.route('/scheda-km/trimestre/<int:anno>/<int:q>')
@login_required
def scheda_km_trimestre(anno, q):
    mesi = {1: [1,2,3], 2: [4,5,6], 3: [7,8,9], 4: [10,11,12]}[q]
    # Filtra i record in base ai veicoli del nucleo corrente.  Otteniamo gli
    # identificativi dei veicoli filtrati e utilizziamo questi ID per
    # estrarre le schede chilometriche corrispondenti.
    veicoli_ids = [v.id for v in get_veicoli_by_nucleo().all()]
    records = (
        SchedaKilometrica.query
        .filter(SchedaKilometrica.anno == anno,
                SchedaKilometrica.mese.in_(mesi),
                SchedaKilometrica.veicolo_id.in_(veicoli_ids))
        .all()
    )
    return render_template('scheda_km/trimestre.html', records=records, trimestre=q, anno=anno)


# Produces an aggregated sheet for a quarter.  For each vehicle it
# computes the initial kilometers at the start of the quarter and the
# final kilometers at the end of the quarter, along with the
# difference.  The initial value is taken from the `km_iniziali` of the
# first month in the quarter if available; if it is missing then the
# final value of the previous month is used.  The final value is taken
# from the `km_finali` of the last month in the quarter.  This view
# renders a table similar to the monthly sheet but summarizing the
# entire quarter.  No data is modified by this view.
@scheda_km_bp.route('/scheda-km/trimestre/scheda/<int:anno>/<int:q>')
@login_required
def scheda_km_trimestre_sheet(anno, q):
    months_map = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
    months = months_map.get(q, [])
    # Filtra i veicoli per nucleo
    veicoli = get_veicoli_by_nucleo().all()
    summary = []
    for v in veicoli:
        # Fetch records for this quarter ordered by month
        records = (
            SchedaKilometrica.query
            .filter_by(anno=anno, veicolo_id=v.id)
            .filter(SchedaKilometrica.mese.in_(months))
            .order_by(SchedaKilometrica.mese)
            .all()
        )
        initial_km = None
        final_km = None
        if records:
            # Determine initial km: use first record's km_iniziali if present; otherwise
            # use the km_finali of the month preceding the quarter.
            first_rec = records[0]
            initial_km = first_rec.km_iniziali
            if initial_km is None:
                # look up the previous month within the same year
                prev_month = months[0] - 1
                if prev_month >= 1:
                    prev_rec = SchedaKilometrica.query.filter_by(anno=anno, mese=prev_month, veicolo_id=v.id).first()
                    if prev_rec and prev_rec.km_finali is not None:
                        initial_km = prev_rec.km_finali
            # Determine final km: take the km_finali of the last record
            last_rec = records[-1]
            final_km = last_rec.km_finali
        # Compute difference if possible
        diff = final_km - initial_km if (final_km is not None and initial_km is not None) else None
        summary.append({
            'veicolo': v,
            'km_iniziali': initial_km,
            'km_finali': final_km,
            'km_percorsi': diff
        })
    # Render summary table. The template uses a similar layout to the monthly sheet.
    return render_template('scheda_km/trimestre_sheet.html', summary=summary, trimestre=q, anno=anno)

# -----------------------------------------------------------------------------
# Esportazione Excel del riepilogo trimestrale
#
# Questa route genera un file Excel con i dati aggregati del trimestre
# selezionato. Calcola i chilometri iniziali e finali per ciascun veicolo e
# l'intervallo percorso, utilizzando la stessa logica del riepilogo
# trimestrale. I dati vengono poi scritti in un file Excel tramite
# openpyxl e inviati come allegato al browser.
@scheda_km_bp.route('/scheda-km/export/excel-trimestre/<int:anno>/<int:q>')
@login_required
def export_excel_trimestre(anno, q):
    # Definizione dei mesi per ogni trimestre
    months_map = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
    months = months_map.get(q, [])
    # Filtra i veicoli per nucleo
    veicoli = get_veicoli_by_nucleo().all()
    rows = []
    for v in veicoli:
        # Estrai i record per questo veicolo e trimestre
        records = (
            SchedaKilometrica.query
            .filter_by(anno=anno, veicolo_id=v.id)
            .filter(SchedaKilometrica.mese.in_(months))
            .order_by(SchedaKilometrica.mese)
            .all()
        )
        initial_km = None
        final_km = None
        if records:
            first_rec = records[0]
            initial_km = first_rec.km_iniziali
            if initial_km is None:
                # se mancano i km iniziali, usa i km finali del mese precedente
                prev_month = months[0] - 1
                if prev_month >= 1:
                    prev_rec = SchedaKilometrica.query.filter_by(
                        anno=anno, mese=prev_month, veicolo_id=v.id
                    ).first()
                    if prev_rec and prev_rec.km_finali is not None:
                        initial_km = prev_rec.km_finali
            last_rec = records[-1]
            final_km = last_rec.km_finali
        diff = final_km - initial_km if (final_km is not None and initial_km is not None) else None
        rows.append({
            'Veicolo': v.targa,
            'Km Iniziali': initial_km,
            'Km Finali': final_km,
            'Km Percorsi': diff
        })
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name=f'scheda_{anno}_trimestre{q}.xlsx', as_attachment=True)

@scheda_km_bp.route('/scheda-km/export/excel/<int:anno>/<int:mese>')
@login_required
def export_excel(anno, mese):
    # Filtra i record in base al nucleo corrente: otteniamo gli ID dei veicoli
    # pertinenti per assicurare che l'export mostri solo i veicoli del nucleo
    # corrente o selezionato dall'amministratore.
    veicoli_ids = [v.id for v in get_veicoli_by_nucleo().all()]
    records = (
        SchedaKilometrica.query
        .filter(
            SchedaKilometrica.anno == anno,
            SchedaKilometrica.mese == mese,
            SchedaKilometrica.veicolo_id.in_(veicoli_ids)
        )
        .all()
    )
    # Prepara i dati per il DataFrame
    data = [{
        'Veicolo': r.veicolo.targa,
        'Km Iniziali': r.km_iniziali,
        'Km Finali': r.km_finali,
        'Km Percorsi': r.km_percorsi
    } for r in records]
    df = pd.DataFrame(data)

    output = io.BytesIO()
    # Definizione dei nomi dei mesi in italiano (maiuscolo)
    mesi_ita = {
        1: 'GENNAIO', 2: 'FEBBRAIO', 3: 'MARZO', 4: 'APRILE', 5: 'MAGGIO', 6: 'GIUGNO',
        7: 'LUGLIO', 8: 'AGOSTO', 9: 'SETTEMBRE', 10: 'OTTOBRE', 11: 'NOVEMBRE', 12: 'DICEMBRE'
    }
    nome_mese = mesi_ita.get(mese, '').upper()
    # Usa openpyxl come engine per poter applicare stili avanzati.
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Scrive i dati a partire dalla riga 2 (startrow=1, 0-index)
        df.to_excel(writer, index=False, startrow=1)
        wb = writer.book
        ws = writer.sheets[list(writer.sheets.keys())[0]]
        from openpyxl.styles import Alignment, Font, Border, Side
        # Inserisci il nome del mese nella prima riga con font 48 e centratura
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
        cell = ws.cell(row=1, column=1)
        cell.value = nome_mese
        cell.font = Font(size=48, bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        # Imposta altezza riga per una migliore leggibilità
        ws.row_dimensions[1].height = 80
        # Applica bordi sottili a tutte le celle con dati e intestazioni
        thin = Side(border_style="thin", color="000000")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        max_row = ws.max_row
        max_col = ws.max_column
        # La riga 2 contiene le intestazioni generate da pandas
        for row in ws.iter_rows(min_row=2, max_row=max_row, min_col=1, max_col=max_col):
            for c in row:
                c.border = border
        # Applica bordi anche alla prima riga con intestazioni delle colonne
        for c in ws[2]:
            c.border = border
            # Rendi l'intestazione in grassetto
            c.font = Font(bold=True)
    output.seek(0)
    return send_file(output, download_name=f'scheda_{anno}_{mese}.xlsx', as_attachment=True)
