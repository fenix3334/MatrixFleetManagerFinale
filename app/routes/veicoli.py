# app/routes/veicoli.py - VERSIONE COMPLETA CORRETTA

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import Veicolo, Fornitore, Scadenza  # Import Scadenza per creare revisioni automatiche
from app.forms.veicoli import VeicoloForm
from app.extensions import db
from sqlalchemy import and_, case

# Importa utility per gestione nuclei
from app.utils.nuclei import (
    get_veicoli_by_nucleo, 
    get_fornitori_for_choices,
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

def get_societa_noleggio_choices():
    """Restituisce choices per società di noleggio dai fornitori.

    A partire dalla versione v1.7 l'anagrafica fornitori è condivisa tra tutti i nuclei,
    pertanto non si applica alcun filtro basato sul campo `nucleo` in questa
    selezione.  Vengono restituiti tutti i fornitori attivi che hanno il settore
    "noleggio"."""
    # Recupera tutti i fornitori attivi senza filtrare per nucleo
    fornitori = Fornitore.query.filter_by(attivo=True).all()
    # Filtra solo quelli che sono società di noleggio
    societa_noleggio = [
        (fornitore.id, fornitore.ragione_sociale)
        for fornitore in fornitori
        if fornitore.is_noleggio
    ]
    return [('', 'Seleziona società...')] + societa_noleggio

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
    # Ordina i veicoli in modo da visualizzare prima quelli attivi e alla fine
    # quelli con stato "Dismesso".  Questo ordinamento garantisce che i
    # veicoli dismessi non compaiano tra i mezzi operativi.  All’interno dei
    # due gruppi l’ordinamento rimane alfabetico per targa.
    # Utilizza SQLAlchemy case expression per ordinare i veicoli mettendo quelli
    # con stato "Dismesso" alla fine.  In SQLAlchemy 2.x i valori delle
    # condizioni devono essere passati come argomenti posizionali anziché
    # all'interno di una lista.  Senza questa forma corretta viene sollevata
    # un'eccezione ArgumentError durante la costruzione della query.  La
    # condizione restituisce 1 per i veicoli dismessi e 0 altrimenti.
    order_expr = case(
        (Veicolo.stato == 'Dismesso', 1),
        else_=0
    )
    veicoli_paginati = veicoli_query.order_by(order_expr.asc(), Veicolo.targa.asc()).paginate(
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
    
    return render_template('veicoli/index.html',
                         veicoli=veicoli_paginati,
                         stati=[s[0] for s in stati_disponibili if s[0]],
                         carburanti=[c[0] for c in carburanti_disponibili if c[0]],
                         stato_filter=stato_filter,
                         carburante_filter=carburante_filter)

@veicoli_bp.route('/nuovo', methods=['GET', 'POST'])
@login_required
def nuovo_veicolo():
    form = VeicoloForm()
    
    # Popola choices società noleggio
    form.societa_noleggio_id.choices = get_societa_noleggio_choices()
    
    if form.validate_on_submit():
        try:
            # Determina nucleo per il nuovo veicolo
            if current_user.ruolo == 'admin':
                nucleo_selezionato = get_nucleo_corrente_admin() or current_user.nucleo
            else:
                nucleo_selezionato = current_user.nucleo
            
            veicolo = Veicolo(
                targa=form.targa.data.upper(),
                marca=form.marca.data,
                modello=form.modello.data,
                anno_immatricolazione=form.anno_immatricolazione.data,
                data_immatricolazione=form.data_immatricolazione.data,
                km_attuali=form.km_attuali.data,
                carburante=form.carburante.data,
                carburante_personalizzato=clean_field(form.carburante_personalizzato.data),
                cilindrata=form.cilindrata.data,
                colore=clean_field(form.colore.data),
                stato=form.stato.data,
                note=clean_field(form.note.data),
                carta_carburante=clean_field(form.carta_carburante.data),
                pin_carburante=clean_field(form.pin_carburante.data),
                societa_noleggio_id=form.societa_noleggio_id.data if form.societa_noleggio_id.data else None,
                unita_operativa=form.unita_operativa.data,
                unita_operativa_personalizzata=clean_field(form.unita_operativa_personalizzata.data),
                nucleo=nucleo_selezionato
            )
            
            db.session.add(veicolo)
            db.session.commit()

            # 🆕 Creazione automatica della scadenza revisione
            try:
                # Calcola la prima revisione: 4 anni dopo l'immatricolazione secondo la normativa vigente.
                immat_date = veicolo.data_immatricolazione
                # Gestisce eventuali date come 29 febbraio portandole al 28 in caso di anno non bisestile
                try:
                    revisione_data = immat_date.replace(year=immat_date.year + 4)
                except ValueError:
                    # Se febbraio 29 e l'anno di destinazione non è bisestile, usa 28 febbraio
                    revisione_data = immat_date.replace(year=immat_date.year + 4, day=28)
                # Crea scadenza revisione se non esistente
                scadenza = Scadenza(
                    veicolo_id=veicolo.id,
                    tipo_scadenza='Revisione',
                    data_scadenza=revisione_data,
                    stato='Attiva',
                    notifica_giorni=30,
                    nucleo=nucleo_selezionato
                )
                db.session.add(scadenza)
                db.session.commit()
            except Exception:
                # Se qualcosa va storto nella creazione della scadenza, non interrompere il flusso
                db.session.rollback()

            flash(f'Veicolo {veicolo.targa} aggiunto con successo!', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
    
    return render_template('veicoli/form.html', form=form, titolo='Nuovo Veicolo')

@veicoli_bp.route('/<int:veicolo_id>')
@login_required
def dettaglio_veicolo(veicolo_id):
    veicolo = validate_veicolo_access(veicolo_id)
    
    # Carica anche le percorrenze chilometriche
    from app.models import PercorrenzaChilometrica, LimiteChilometrico
    
    # Percorrenze recenti
    percorrenze = PercorrenzaChilometrica.query.filter_by(
        veicolo_id=veicolo_id
    ).order_by(
        PercorrenzaChilometrica.anno.desc(),
        PercorrenzaChilometrica.mese.desc()
    ).limit(6).all()
    
    # Limite attivo
    limite_attivo = veicolo.limite_attivo
    
    return render_template('veicoli/dettaglio.html', 
                         veicolo=veicolo,
                         percorrenze=percorrenze,
                         limite_attivo=limite_attivo)

@veicoli_bp.route('/<int:veicolo_id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica_veicolo(veicolo_id):
    veicolo = validate_veicolo_access(veicolo_id)
    form = VeicoloForm(obj=veicolo)
    
    # Popola choices società noleggio
    form.societa_noleggio_id.choices = get_societa_noleggio_choices()
    
    if form.validate_on_submit():
        try:
            # Aggiorna campi
            veicolo.targa = form.targa.data.upper()
            veicolo.marca = form.marca.data
            veicolo.modello = form.modello.data
            veicolo.anno_immatricolazione = form.anno_immatricolazione.data
            veicolo.data_immatricolazione = form.data_immatricolazione.data
            veicolo.km_attuali = form.km_attuali.data
            veicolo.carburante = form.carburante.data
            veicolo.carburante_personalizzato = clean_field(form.carburante_personalizzato.data)
            veicolo.cilindrata = form.cilindrata.data
            veicolo.colore = clean_field(form.colore.data)
            veicolo.stato = form.stato.data
            veicolo.note = clean_field(form.note.data)
            veicolo.carta_carburante = clean_field(form.carta_carburante.data)
            veicolo.pin_carburante = clean_field(form.pin_carburante.data)
            veicolo.societa_noleggio_id = form.societa_noleggio_id.data if form.societa_noleggio_id.data else None
            veicolo.unita_operativa = form.unita_operativa.data
            veicolo.unita_operativa_personalizzata = clean_field(form.unita_operativa_personalizzata.data)
            
            db.session.commit()
            flash(f'Veicolo {veicolo.targa} modificato con successo!', 'success')
            return redirect(url_for('veicoli.dettaglio_veicolo', veicolo_id=veicolo.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
    
    return render_template('veicoli/form.html', 
                         form=form, 
                         veicolo=veicolo, 
                         titolo=f'Modifica Veicolo {veicolo.targa}')

@veicoli_bp.route('/<int:veicolo_id>/elimina', methods=['POST'])
@login_required
def elimina_veicolo(veicolo_id):
    veicolo = validate_veicolo_access(veicolo_id)
    
    try:
        targa = veicolo.targa
        db.session.delete(veicolo)
        db.session.commit()
        flash(f'Veicolo {targa} eliminato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
    
    return redirect(url_for('veicoli.index_veicoli'))
