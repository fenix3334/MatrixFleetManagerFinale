from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import Scadenza, Veicolo
from app.forms.scadenze import ScadenzaForm
from app.extensions import db
from datetime import date
from sqlalchemy import and_, text

# Importa utility per gestione nuclei
from app.utils.nuclei import (
    get_scadenze_by_nucleo,
    get_veicoli_for_choices,
    can_access_record,
    should_filter_by_nucleo,
    get_nucleo_corrente_admin
)

scadenze_bp = Blueprint('scadenze', __name__)

def clean_field(value):
    """Pulisce i campi opzionali rimuovendo spazi vuoti"""
    if value and value.strip():
        return value.strip()
    return None

def validate_scadenza_access(scadenza_id):
    """Verifica che l'utente possa accedere alla scadenza"""
    scadenza = Scadenza.query.get_or_404(scadenza_id)
    
    if not can_access_record(scadenza):
        abort(403)  # Accesso negato
    
    return scadenza

@scadenze_bp.route('/')
@login_required
def index_scadenze():
    page = request.args.get('page', 1, type=int)
    
    # Query filtrata per nucleo usando utility
    scadenze_query = get_scadenze_by_nucleo()
    
    # Filtri aggiuntivi
    stato_filter = request.args.get('stato')
    tipo_filter = request.args.get('tipo')
    urgenza_filter = request.args.get('urgenza')
    veicolo_filter = request.args.get('veicolo')
    
    if stato_filter:
        scadenze_query = scadenze_query.filter_by(stato=stato_filter)
    
    if tipo_filter:
        scadenze_query = scadenze_query.filter_by(tipo_scadenza=tipo_filter)
    
    if veicolo_filter:
        scadenze_query = scadenze_query.filter_by(veicolo_id=veicolo_filter)
    
    # Filtro urgenza (basato sui giorni alla scadenza)
    if urgenza_filter:
        oggi = date.today()
        if urgenza_filter == 'scadute':
            scadenze_query = scadenze_query.filter(Scadenza.data_scadenza < oggi)
        elif urgenza_filter == 'critiche':
            scadenze_query = scadenze_query.filter(
                and_(Scadenza.data_scadenza >= oggi,
                     Scadenza.data_scadenza <= text("date('now', '+7 days')"))
            )
        elif urgenza_filter == 'urgenti':
            scadenze_query = scadenze_query.filter(
                and_(Scadenza.data_scadenza > text("date('now', '+7 days')"),
                     Scadenza.data_scadenza <= text("date('now', '+30 days')"))
            )
    
    # Paginazione
    scadenze_paginate = scadenze_query.order_by(
        Scadenza.data_scadenza.asc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    # Statistiche per dashboard
    tutte_scadenze = get_scadenze_by_nucleo()
    oggi = date.today()
    
    stats = {
        'totale': tutte_scadenze.count(),
        'attive': tutte_scadenze.filter_by(stato='Attiva').count(),
        'scadute': tutte_scadenze.filter(Scadenza.data_scadenza < oggi).count(),
        'critiche': tutte_scadenze.filter(
            and_(Scadenza.data_scadenza >= oggi,
                 Scadenza.data_scadenza <= text("date('now', '+7 days')"))
        ).count(),
        'urgenti': tutte_scadenze.filter(
            and_(Scadenza.data_scadenza > text("date('now', '+7 days')"),
                 Scadenza.data_scadenza <= text("date('now', '+30 days')"))
        ).count()
    }
    
    # Opzioni per filtri
    stati_disponibili = ['Attiva', 'Scaduta', 'Rinnovata']
    tipi_disponibili = db.session.query(Scadenza.tipo_scadenza).filter(
        Scadenza.id.in_([s.id for s in tutte_scadenze])
    ).distinct().all()
    veicoli_disponibili = get_veicoli_for_choices()
    
    # ✅ FIX: Passa l'oggetto paginazione completo, non solo gli items
    return render_template('scadenze/index.html',
                         scadenze=scadenze_paginate,  # ✅ CORRETTO: oggetto paginazione completo
                         stats=stats,
                         stati=stati_disponibili,
                         tipi=[t[0] for t in tipi_disponibili],
                         veicoli=veicoli_disponibili,
                         filtro_stato=stato_filter,
                         filtro_tipo=tipo_filter,
                         filtro_urgenza=urgenza_filter,
                         filtro_veicolo=veicolo_filter)

@scadenze_bp.route('/dettaglio/<int:id>')
@login_required
def dettaglio_scadenza(id):
    # Verifica accesso e ottieni scadenza
    scadenza = validate_scadenza_access(id)
    
    return render_template('scadenze/dettaglio.html', scadenza=scadenza)

@scadenze_bp.route('/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_scadenza():
    form = ScadenzaForm()
    
    # Aggiorna choices per veicoli (filtrati per nucleo)
    form.veicolo_id.choices = get_veicoli_for_choices()
    
    if form.validate_on_submit():
        try:
            # GESTIONE TIPO SCADENZA PERSONALIZZATO
            tipo_scadenza_finale = form.tipo_scadenza.data
            if form.tipo_scadenza.data == 'Altro' and form.tipo_scadenza_personalizzato.data:
                tipo_scadenza_finale = clean_field(form.tipo_scadenza_personalizzato.data)
            
            scadenza = Scadenza(
                veicolo_id=form.veicolo_id.data,
                tipo_scadenza=tipo_scadenza_finale,
                data_scadenza=form.data_scadenza.data,
                stato=form.stato.data,
                notifica_giorni=form.notifica_giorni.data,
                note=clean_field(form.note.data)
                
                # ❌ RIMOSSO: costo=form.costo.data
            )
            
            # IMPORTANTE: Imposta automaticamente il nucleo
            veicolo = Veicolo.query.get(form.veicolo_id.data)
            if veicolo:
                scadenza.nucleo = veicolo.nucleo
            else:
                # Fallback: usa nucleo utente
                scadenza.nucleo = current_user.nucleo
            
            db.session.add(scadenza)
            db.session.commit()
            
            flash(f'Scadenza {scadenza.tipo_scadenza} per {scadenza.veicolo.targa} aggiunta con successo!', 'success')
            return redirect(url_for('scadenze.index_scadenze'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
            
    return render_template('scadenze/form.html', form=form, titolo='Aggiungi Scadenza')

@scadenze_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_scadenza(id):
    # Verifica accesso e ottieni scadenza
    scadenza = validate_scadenza_access(id)
    
    form = ScadenzaForm(obj=scadenza)
    
    # Aggiorna choices per veicoli (filtrati per nucleo)
    form.veicolo_id.choices = get_veicoli_for_choices()
    
    # Se in modifica e il tipo_scadenza non è tra le opzioni predefinite, 
    # impostalo come "Altro" e popola il campo personalizzato
    opzioni_predefinite = ['Revisione', 'Assicurazione', 'Bollo', 'Tagliando', 
                          'Controllo gas di scarico', 'Consegna auto a noleggio', 
                          'Riconsegna auto da noleggio']
    
    if request.method == 'GET' and scadenza.tipo_scadenza not in opzioni_predefinite:
        form.tipo_scadenza.data = 'Altro'
        form.tipo_scadenza_personalizzato.data = scadenza.tipo_scadenza
    
    if form.validate_on_submit():
        try:
            # GESTIONE TIPO SCADENZA PERSONALIZZATO
            tipo_scadenza_finale = form.tipo_scadenza.data
            if form.tipo_scadenza.data == 'Altro' and form.tipo_scadenza_personalizzato.data:
                tipo_scadenza_finale = clean_field(form.tipo_scadenza_personalizzato.data)
            
            # Aggiorna manualmente i campi
            scadenza.veicolo_id = form.veicolo_id.data
            scadenza.tipo_scadenza = tipo_scadenza_finale
            scadenza.data_scadenza = form.data_scadenza.data
            scadenza.stato = form.stato.data
            scadenza.notifica_giorni = form.notifica_giorni.data
            scadenza.note = clean_field(form.note.data)
            
            # ❌ RIMOSSO: scadenza.costo = form.costo.data
            
            # Aggiorna nucleo se il veicolo è cambiato
            veicolo = Veicolo.query.get(form.veicolo_id.data)
            if veicolo:
                scadenza.nucleo = veicolo.nucleo
            
            db.session.commit()
            flash(f'Scadenza {scadenza.tipo_scadenza} per {scadenza.veicolo.targa} modificata con successo!', 'success')
            return redirect(url_for('scadenze.index_scadenze'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
    
    return render_template('scadenze/form.html', form=form, titolo='Modifica Scadenza')

@scadenze_bp.route('/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_scadenza(id):
    # Verifica accesso e ottieni scadenza
    scadenza = validate_scadenza_access(id)
    
    try:
        tipo_scadenza = scadenza.tipo_scadenza
        targa_veicolo = scadenza.veicolo.targa
        
        db.session.delete(scadenza)
        db.session.commit()
        
        flash(f'Scadenza {tipo_scadenza} per {targa_veicolo} eliminata con successo!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
    
    return redirect(url_for('scadenze.index_scadenze'))

@scadenze_bp.route('/rinnova/<int:id>', methods=['POST'])
@login_required
def rinnova_scadenza(id):
    """Segna una scadenza come rinnovata"""
    # Verifica accesso e ottieni scadenza
    scadenza = validate_scadenza_access(id)
    
    try:
        scadenza.stato = 'Rinnovata'
        db.session.commit()
        
        flash(f'Scadenza {scadenza.tipo_scadenza} per {scadenza.veicolo.targa} segnata come rinnovata!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'aggiornamento: {str(e)}', 'error')
    
    return redirect(url_for('scadenze.index_scadenze'))

@scadenze_bp.route('/riattiva/<int:id>', methods=['POST'])
@login_required
def riattiva_scadenza(id):
    """Riattiva una scadenza"""
    # Verifica accesso e ottieni scadenza
    scadenza = validate_scadenza_access(id)
    
    try:
        scadenza.stato = 'Attiva'
        db.session.commit()
        
        flash(f'Scadenza {scadenza.tipo_scadenza} per {scadenza.veicolo.targa} riattivata!', 'info')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'aggiornamento: {str(e)}', 'error')
    
    return redirect(url_for('scadenze.index_scadenze'))
