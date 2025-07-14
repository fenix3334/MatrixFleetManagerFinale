from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import Veicolo, Fornitore, SocietaNoleggio
from app.forms.veicoli import VeicoloForm
from app.extensions import db
from sqlalchemy import and_

# Importa utility per gestione nuclei
from app.utils.nuclei import (
    get_veicoli_by_nucleo, 
    get_fornitori_for_choices,
    get_societa_noleggio_for_choices,
    can_access_record,
    should_filter_by_nucleo,
    get_nucleo_corrente_admin
)

veicoli_bp = Blueprint('veicoli', __name__)

def clean_field(value):
    """Pulisce i campi opzionali"""
    if value and value.strip():
        return value.strip()
    return None

def validate_veicolo_access(veicolo_id):
    """Verifica che l'utente possa accedere al veicolo"""
    veicolo = Veicolo.query.get_or_404(veicolo_id)
    
    if not can_access_record(veicolo):
        abort(403)  # Accesso negato
    
    return veicolo

@veicoli_bp.route('/')
@login_required
def index_veicoli():
    page = request.args.get('page', 1, type=int)
    
    # Query filtrata per nucleo usando utility
    veicoli_query = get_veicoli_by_nucleo()
    
    # Filtri aggiuntivi
    stato_filter = request.args.get('stato')
    carburante_filter = request.args.get('carburante')
    
    if stato_filter:
        veicoli_query = veicoli_query.filter_by(stato=stato_filter)
    
    if carburante_filter:
        veicoli_query = veicoli_query.filter_by(carburante=carburante_filter)
    
    # Paginazione
    veicoli_paginati = veicoli_query.order_by(Veicolo.targa.asc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Statistiche per filtri
    tutti_veicoli = get_veicoli_by_nucleo()
    stati_disponibili = db.session.query(Veicolo.stato).filter(
        Veicolo.id.in_([v.id for v in tutti_veicoli])
    ).distinct().all()
    carburanti_disponibili = db.session.query(Veicolo.carburante).filter(
        Veicolo.id.in_([v.id for v in tutti_veicoli])
    ).distinct().all()
    
    # ✅ FIX: Passa l'oggetto paginazione completo, non solo gli items
    return render_template('veicoli/index.html', 
                         veicoli=veicoli_paginati,  # ✅ CORRETTO: oggetto paginazione completo
                         stati=[s[0] for s in stati_disponibili],
                         carburanti=[c[0] for c in carburanti_disponibili],
                         filtro_stato=stato_filter,
                         filtro_carburante=carburante_filter)

@veicoli_bp.route('/dettaglio/<int:id>')
@login_required
def dettaglio_veicolo(id):
    # Verifica accesso e ottieni veicolo
    veicolo = validate_veicolo_access(id)
    
    return render_template('veicoli/dettaglio.html', veicolo=veicolo)

@veicoli_bp.route('/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_veicolo():
    form = VeicoloForm()
    
    # Aggiorna choices per società noleggio (filtrate per nucleo)
    form.societa_noleggio_id.choices = get_societa_noleggio_for_choices()
    
    # Se utente normale, imposta automaticamente il suo nucleo
    if current_user.ruolo != 'admin':
        form.nucleo.data = current_user.nucleo
        form.nucleo.render_kw = {'disabled': True}
    
    if form.validate_on_submit():
        try:
            # 🆕 GESTIONE UNITÀ OPERATIVA PERSONALIZZATA
            unita_operativa_finale = form.unita_operativa.data
            unita_operativa_personalizzata = None
            
            if form.unita_operativa.data == 'Altro' and form.unita_operativa_personalizzata.data:
                unita_operativa_personalizzata = clean_field(form.unita_operativa_personalizzata.data)
                unita_operativa_finale = 'Altro'  # Mantieni "Altro" nel campo principale
            
            # GESTIONE CARBURANTE PERSONALIZZATO
            carburante_finale = form.carburante.data
            carburante_personalizzato = None
            
            if form.carburante.data == 'Altro' and form.carburante_personalizzato.data:
                carburante_personalizzato = clean_field(form.carburante_personalizzato.data)
            
            veicolo = Veicolo(
                targa=form.targa.data.upper(),
                marca=form.marca.data,
                modello=form.modello.data,
                anno_immatricolazione=form.anno_immatricolazione.data,
                data_immatricolazione=form.data_immatricolazione.data,
                km_attuali=form.km_attuali.data,
                carburante=carburante_finale,
                carburante_personalizzato=carburante_personalizzato,
                cilindrata=form.cilindrata.data,
                colore=clean_field(form.colore.data),
                stato=form.stato.data,
                carta_carburante=clean_field(form.carta_carburante.data),
                pin_carburante=clean_field(form.pin_carburante.data),
                societa_noleggio_id=form.societa_noleggio_id.data if form.societa_noleggio_id.data else None,
                
                # 🆕 CAMPI UNITÀ OPERATIVA
                unita_operativa=unita_operativa_finale,
                unita_operativa_personalizzata=unita_operativa_personalizzata,
                
                note=clean_field(form.note.data),
                nucleo=form.nucleo.data if current_user.ruolo == 'admin' else current_user.nucleo
            )
            
            db.session.add(veicolo)
            db.session.commit()
            
            # Messaggio con unità operativa visualizzata
            unita_display = veicolo.unita_operativa_display
            flash(f'Veicolo {veicolo.targa} aggiunto con successo! Assegnato a: {unita_display}', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
    
    return render_template('veicoli/form.html', form=form, titolo='Aggiungi Veicolo')

@veicoli_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_veicolo(id):
    # Verifica accesso e ottieni veicolo
    veicolo = validate_veicolo_access(id)
    
    form = VeicoloForm(obj=veicolo)
    
    # Aggiorna choices per società noleggio (filtrate per nucleo)
    form.societa_noleggio_id.choices = get_societa_noleggio_for_choices()
    
    # 🆕 Se in modifica e l'unità operativa non è tra le opzioni predefinite,
    # impostala come "Altro" e popola il campo personalizzato
    opzioni_predefinite = [
        'Cure Primarie ADI Via del Capitel',
        'Cure Primarie ADI Via Campania', 
        'Guardia Medica'
    ]
    
    if request.method == 'GET' and veicolo.unita_operativa not in opzioni_predefinite:
        form.unita_operativa.data = 'Altro'
        form.unita_operativa_personalizzata.data = veicolo.unita_operativa
    
    # Se in modifica e il carburante non è tra le opzioni predefinite,
    # impostalo come "Altro" e popola il campo personalizzato
    carburanti_predefiniti = ['Benzina', 'Diesel', 'GPL', 'Metano', 'Elettrico', 'Ibrido']
    
    if request.method == 'GET' and veicolo.carburante not in carburanti_predefiniti:
        form.carburante.data = 'Altro'
        form.carburante_personalizzato.data = veicolo.carburante
    
    # Se utente normale, non può modificare il nucleo
    if current_user.ruolo != 'admin':
        form.nucleo.render_kw = {'disabled': True}
    
    if form.validate_on_submit():
        try:
            # 🆕 GESTIONE UNITÀ OPERATIVA PERSONALIZZATA
            unita_operativa_finale = form.unita_operativa.data
            unita_operativa_personalizzata = None
            
            if form.unita_operativa.data == 'Altro' and form.unita_operativa_personalizzata.data:
                unita_operativa_personalizzata = clean_field(form.unita_operativa_personalizzata.data)
                unita_operativa_finale = 'Altro'
            
            # GESTIONE CARBURANTE PERSONALIZZATO
            carburante_finale = form.carburante.data
            carburante_personalizzato = None
            
            if form.carburante.data == 'Altro' and form.carburante_personalizzato.data:
                carburante_personalizzato = clean_field(form.carburante_personalizzato.data)
            
            # Aggiorna manualmente i campi
            veicolo.targa = form.targa.data.upper()
            veicolo.marca = form.marca.data
            veicolo.modello = form.modello.data
            veicolo.anno_immatricolazione = form.anno_immatricolazione.data
            veicolo.data_immatricolazione = form.data_immatricolazione.data
            veicolo.km_attuali = form.km_attuali.data
            veicolo.carburante = carburante_finale
            veicolo.carburante_personalizzato = carburante_personalizzato
            veicolo.cilindrata = form.cilindrata.data
            veicolo.colore = clean_field(form.colore.data)
            veicolo.stato = form.stato.data
            veicolo.carta_carburante = clean_field(form.carta_carburante.data)
            veicolo.pin_carburante = clean_field(form.pin_carburante.data)
            veicolo.societa_noleggio_id = form.societa_noleggio_id.data if form.societa_noleggio_id.data else None
            
            # 🆕 AGGIORNA CAMPI UNITÀ OPERATIVA
            veicolo.unita_operativa = unita_operativa_finale
            veicolo.unita_operativa_personalizzata = unita_operativa_personalizzata
            
            veicolo.note = clean_field(form.note.data)
            
            # Solo admin può modificare il nucleo
            if current_user.ruolo == 'admin':
                veicolo.nucleo = form.nucleo.data
            
            db.session.commit()
            
            # Messaggio con unità operativa visualizzata
            unita_display = veicolo.unita_operativa_display
            flash(f'Veicolo {veicolo.targa} modificato con successo! Assegnato a: {unita_display}', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
    
    return render_template('veicoli/form.html', form=form, titolo='Modifica Veicolo')

@veicoli_bp.route('/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_veicolo(id):
    # Verifica accesso e ottieni veicolo
    veicolo = validate_veicolo_access(id)
    
    try:
        # Controlli di sicurezza prima dell'eliminazione
        if veicolo.manutenzioni:
            flash(f'Impossibile eliminare il veicolo {veicolo.targa}: ha manutenzioni associate', 'error')
            return redirect(url_for('veicoli.index_veicoli'))
        
        if veicolo.scadenze:
            flash(f'Impossibile eliminare il veicolo {veicolo.targa}: ha scadenze associate', 'error')
            return redirect(url_for('veicoli.index_veicoli'))
        
        targa_eliminata = veicolo.targa
        db.session.delete(veicolo)
        db.session.commit()
        
        flash(f'Veicolo {targa_eliminata} eliminato con successo!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
    
    return redirect(url_for('veicoli.index_veicoli'))
