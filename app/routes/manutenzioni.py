from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask import send_file
from flask_login import login_required, current_user
from app.models import Manutenzione, Veicolo, Fornitore
from app.forms.manutenzioni import ManutenzioneForm
from app.extensions import db
from datetime import date
from sqlalchemy import and_, text
import io
import pandas as pd

# Importa utility per gestione nuclei
from app.utils.nuclei import (
    get_manutenzioni_by_nucleo,
    get_veicoli_for_choices,
    get_fornitori_for_choices,
    can_access_record,
    should_filter_by_nucleo,
    get_nucleo_corrente_admin
)

manutenzioni_bp = Blueprint('manutenzioni', __name__)

def clean_field(value):
    """Pulisce i campi opzionali rimuovendo spazi vuoti"""
    if value and value.strip():
        return value.strip()
    return None

def validate_manutenzione_access(manutenzione_id):
    """Verifica che l'utente possa accedere alla manutenzione"""
    manutenzione = Manutenzione.query.get_or_404(manutenzione_id)
    
    if not can_access_record(manutenzione):
        abort(403)  # Accesso negato
    
    return manutenzione

@manutenzioni_bp.route('/')
@login_required
def index_manutenzioni():
    page = request.args.get('page', 1, type=int)
    
    # Query filtrata per nucleo usando utility
    manutenzioni_query = get_manutenzioni_by_nucleo()
    
    # Filtri aggiuntivi
    stato_filter = request.args.get('stato')
    tipo_filter = request.args.get('tipo')
    veicolo_filter = request.args.get('veicolo')
    
    if stato_filter:
        manutenzioni_query = manutenzioni_query.filter_by(stato=stato_filter)
    
    if tipo_filter:
        manutenzioni_query = manutenzioni_query.filter_by(tipo_intervento=tipo_filter)
    
    if veicolo_filter:
        manutenzioni_query = manutenzioni_query.filter_by(veicolo_id=veicolo_filter)
    
    # Paginazione
    manutenzioni_paginate = manutenzioni_query.order_by(
        Manutenzione.data_intervento.desc()
    ).paginate(page=page, per_page=25, error_out=False)
    
    # Statistiche per dashboard
    tutte_manutenzioni = get_manutenzioni_by_nucleo()
    
    stats = {
        'totale': tutte_manutenzioni.count(),
        'da_fare': tutte_manutenzioni.filter_by(stato='Da Fare').count(),
        'fatte': tutte_manutenzioni.filter_by(stato='Fatto').count(),
        'questo_mese': tutte_manutenzioni.filter(
            text("strftime('%Y-%m', data_intervento) = strftime('%Y-%m', 'now')")
        ).count()
    }
    
    # Opzioni per filtri
    stati_disponibili = ['Da Fare', 'Fatto']
    tipi_disponibili = db.session.query(Manutenzione.tipo_intervento).filter(
        Manutenzione.id.in_([m.id for m in tutte_manutenzioni])
    ).distinct().all()
    veicoli_disponibili = get_veicoli_for_choices()
    
    # ✅ FIX: Passa l'oggetto paginazione completo, non solo gli items
    return render_template('manutenzioni/index.html',
                         manutenzioni=manutenzioni_paginate,  # ✅ CORRETTO: oggetto paginazione completo
                         stats=stats,
                         stati=stati_disponibili,
                         tipi=[t[0] for t in tipi_disponibili],
                         veicoli=veicoli_disponibili,
                         filtro_stato=stato_filter,
                         filtro_tipo=tipo_filter,
                         filtro_veicolo=veicolo_filter)

@manutenzioni_bp.route('/dettaglio/<int:id>')
@login_required
def dettaglio_manutenzione(id):
    # Verifica accesso e ottieni manutenzione
    manutenzione = validate_manutenzione_access(id)
    
    return render_template('manutenzioni/dettaglio.html', manutenzione=manutenzione)

@manutenzioni_bp.route('/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_manutenzione():
    form = ManutenzioneForm()
    
    # Aggiorna choices per veicoli e fornitori (filtrati per nucleo)
    form.veicolo_id.choices = get_veicoli_for_choices()
    form.fornitore_id.choices = get_fornitori_for_choices()
    
    if form.validate_on_submit():
        try:
            manutenzione = Manutenzione(
                veicolo_id=form.veicolo_id.data,
                fornitore_id=form.fornitore_id.data if form.fornitore_id.data else None,
                data_intervento=form.data_intervento.data,
                km_intervento=form.km_intervento.data,
                tipo_intervento=form.tipo_intervento.data,
                descrizione=clean_field(form.descrizione.data),
                
                # 🔄 RINOMINATO: numero_fattura → numero_documento
                numero_documento=clean_field(form.numero_documento.data),
                data_fattura=form.data_fattura.data,
                
                garanzia_mesi=form.garanzia_mesi.data,
                prossima_scadenza_km=form.prossima_scadenza_km.data,
                stato=form.stato.data,
                note=clean_field(form.note.data)
                
                # ❌ RIMOSSO: costo=form.costo.data
            )
            
            # IMPORTANTE: Imposta automaticamente il nucleo
            veicolo = Veicolo.query.get(form.veicolo_id.data)
            if veicolo:
                manutenzione.nucleo = veicolo.nucleo
            else:
                # Fallback: usa nucleo utente
                manutenzione.nucleo = current_user.nucleo
            
            db.session.add(manutenzione)
            db.session.commit()
            
            flash(f'Manutenzione {manutenzione.tipo_intervento} per {manutenzione.veicolo.targa} aggiunta con successo!', 'success')
            return redirect(url_for('manutenzioni.index_manutenzioni'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
    
    return render_template('manutenzioni/form.html', form=form, titolo='Aggiungi Manutenzione')

@manutenzioni_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_manutenzione(id):
    # Verifica accesso e ottieni manutenzione
    manutenzione = validate_manutenzione_access(id)
    
    form = ManutenzioneForm(obj=manutenzione)
    
    # Aggiorna choices per veicoli e fornitori (filtrati per nucleo)
    form.veicolo_id.choices = get_veicoli_for_choices()
    form.fornitore_id.choices = get_fornitori_for_choices()
    
    # Assicurati che il veicolo attualmente associato alla manutenzione sia
    # presente nelle scelte anche se non più attivo.  In questo modo il
    # menu a discesa mostra sempre la targa del veicolo corrente, evitando
    # che la selezione ricada sul primo veicolo attivo della lista.
    current_vehicle = manutenzione.veicolo
    if current_vehicle:
        # Verifica se il veicolo corrente è già nelle scelte
        if all(choice[0] != current_vehicle.id for choice in form.veicolo_id.choices):
            form.veicolo_id.choices.append(
                (current_vehicle.id, f"{current_vehicle.targa} - {current_vehicle.marca} {current_vehicle.modello}")
            )
    
    if form.validate_on_submit():
        try:
            manutenzione.veicolo_id = form.veicolo_id.data
            manutenzione.fornitore_id = form.fornitore_id.data if form.fornitore_id.data else None
            manutenzione.data_intervento = form.data_intervento.data
            manutenzione.km_intervento = form.km_intervento.data
            manutenzione.tipo_intervento = form.tipo_intervento.data
            manutenzione.descrizione = clean_field(form.descrizione.data)
            
            # 🔄 RINOMINATO: numero_fattura → numero_documento
            manutenzione.numero_documento = clean_field(form.numero_documento.data)
            manutenzione.data_fattura = form.data_fattura.data
            
            manutenzione.garanzia_mesi = form.garanzia_mesi.data
            manutenzione.prossima_scadenza_km = form.prossima_scadenza_km.data
            manutenzione.stato = form.stato.data
            manutenzione.note = clean_field(form.note.data)
            
            # ❌ RIMOSSO: manutenzione.costo = form.costo.data
            
            # Aggiorna nucleo se il veicolo è cambiato
            veicolo = Veicolo.query.get(form.veicolo_id.data)
            if veicolo:
                manutenzione.nucleo = veicolo.nucleo
            
            db.session.commit()
            flash(f'Manutenzione {manutenzione.tipo_intervento} per {manutenzione.veicolo.targa} modificata con successo!', 'success')
            return redirect(url_for('manutenzioni.index_manutenzioni'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
    
    return render_template('manutenzioni/form.html', form=form, titolo='Modifica Manutenzione')

@manutenzioni_bp.route('/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_manutenzione(id):
    # Verifica accesso e ottieni manutenzione
    manutenzione = validate_manutenzione_access(id)
    
    try:
        tipo_intervento = manutenzione.tipo_intervento
        targa_veicolo = manutenzione.veicolo.targa
        
        db.session.delete(manutenzione)
        db.session.commit()
        
        flash(f'Manutenzione {tipo_intervento} per {targa_veicolo} eliminata con successo!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
    
    return redirect(url_for('manutenzioni.index_manutenzioni'))

@manutenzioni_bp.route('/completa/<int:id>', methods=['POST'])
@login_required
def completa_manutenzione(id):
    """Segna una manutenzione come completata"""
    # Verifica accesso e ottieni manutenzione
    manutenzione = validate_manutenzione_access(id)
    
    try:
        manutenzione.stato = 'Fatto'
        db.session.commit()
        
        flash(f'Manutenzione {manutenzione.tipo_intervento} per {manutenzione.veicolo.targa} segnata come completata!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'aggiornamento: {str(e)}', 'error')
    
    return redirect(url_for('manutenzioni.index_manutenzioni'))

@manutenzioni_bp.route('/ripristina/<int:id>', methods=['POST'])
@login_required
def ripristina_manutenzione(id):
    """Ripristina una manutenzione come da fare"""
    # Verifica accesso e ottieni manutenzione
    manutenzione = validate_manutenzione_access(id)
    
    try:
        manutenzione.stato = 'Da Fare'
        db.session.commit()
        
        flash(f'Manutenzione {manutenzione.tipo_intervento} per {manutenzione.veicolo.targa} ripristinata come da fare!', 'info')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'aggiornamento: {str(e)}', 'error')
    
    return redirect(url_for('manutenzioni.index_manutenzioni'))


# === Funzioni aggiuntive per v1.24 ===

@manutenzioni_bp.route('/export', methods=['GET'])
@login_required
def export_manutenzioni():
    """Esporta l'elenco delle manutenzioni in formato Excel.

    L'export rispetta i filtri di stato, tipo e veicolo passati nella query.
    Il file include le colonne principali (Veicolo, Tipo, Data, KM, Stato,
    Fornitore) e viene scaricato come allegato Excel.
    """
    manutenzioni_query = get_manutenzioni_by_nucleo()
    stato_filter = request.args.get('stato')
    tipo_filter = request.args.get('tipo')
    veicolo_filter = request.args.get('veicolo')
    if stato_filter:
        manutenzioni_query = manutenzioni_query.filter_by(stato=stato_filter)
    if tipo_filter:
        manutenzioni_query = manutenzioni_query.filter_by(tipo_intervento=tipo_filter)
    if veicolo_filter:
        manutenzioni_query = manutenzioni_query.filter_by(veicolo_id=veicolo_filter)

    records = manutenzioni_query.order_by(Manutenzione.data_intervento.desc()).all()

    rows = []
    for m in records:
        rows.append({
            'Veicolo': m.veicolo.targa if m.veicolo else '',
            'Tipo Intervento': m.tipo_intervento,
            'Data': m.data_intervento.strftime('%d/%m/%Y') if m.data_intervento else '',
            'KM': m.km_intervento or '',
            'Stato': m.stato,
            'Fornitore': m.fornitore.ragione_sociale if m.fornitore else '',
            'Note': (m.descrizione or '')[:100],
        })
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name='manutenzioni.xlsx', as_attachment=True)
