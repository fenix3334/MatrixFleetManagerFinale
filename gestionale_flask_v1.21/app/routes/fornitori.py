from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import Fornitore
from app.forms.fornitori import FornitoreForm
from app.extensions import db

fornitori_bp = Blueprint('fornitori', __name__)

def clean_field(value):
    """Helper per pulire i campi vuoti"""
    if value and value.strip():
        return value.strip()
    return None

def get_fornitori_query():
    """Restituisce query fornitori filtrata per nucleo utente o selezione admin"""
    from flask import session
    
    if current_user.ruolo == 'admin':
        # Admin può filtrare per nucleo specifico o vedere tutti
        filtro_admin = session.get('admin_nucleo_filter', 'tutti')
        
        if filtro_admin == 'tutti':
            # Admin vede tutti i fornitori
            return Fornitore.query
        else:
            # Admin con filtro specifico
            return Fornitore.query.filter_by(nucleo=filtro_admin)
    else:
        # User normale vede solo fornitori del suo nucleo
        return Fornitore.query.filter_by(nucleo=current_user.nucleo)

def validate_fornitore_access(fornitore_id):
    """Verifica che l'utente possa accedere al fornitore"""
    fornitore = Fornitore.query.get_or_404(fornitore_id)
    
    if current_user.ruolo == 'admin':
        return fornitore
    
    if fornitore.nucleo != current_user.nucleo:
        abort(403)  # Accesso negato
    
    return fornitore

@fornitori_bp.route('/')
@login_required
def index_fornitori():
    page = request.args.get('page', 1, type=int)
    
    # Query filtrata per nucleo
    fornitori_query = get_fornitori_query()
    
    # Filtri aggiuntivi
    attivo_filter = request.args.get('attivo')
    settore_filter = request.args.get('settore')
    
    if attivo_filter == 'attivi':
        fornitori_query = fornitori_query.filter_by(attivo=True)
    elif attivo_filter == 'inattivi':
        fornitori_query = fornitori_query.filter_by(attivo=False)
    
    if settore_filter:
        # Cerca il settore in tutti i campi settore
        from sqlalchemy import or_
        fornitori_query = fornitori_query.filter(
            or_(
                Fornitore.settore.contains(settore_filter),
                Fornitore.settore_2.contains(settore_filter),
                Fornitore.settore_3.contains(settore_filter),
                Fornitore.settore_personalizzato.contains(settore_filter)
            )
        )
    
    # Ordinamento e paginazione
    fornitori = fornitori_query.order_by(Fornitore.ragione_sociale).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    
    # Informazioni nucleo per l'interfaccia
    from flask import session
    nucleo_corrente = session.get('admin_nucleo_filter', 'tutti') if current_user.ruolo == 'admin' else current_user.nucleo
    nucleo_info = {
        'nome': nucleo_corrente if nucleo_corrente != 'tutti' else 'TUTTI I NUCLEI',
        'is_admin': current_user.ruolo == 'admin',
        'username': current_user.username
    }
    
    # Conta per filtri
    totale_fornitori = get_fornitori_query().count()
    fornitori_attivi = get_fornitori_query().filter_by(attivo=True).count()
    
    return render_template('fornitori/index.html', 
                         fornitori=fornitori,
                         nucleo_info=nucleo_info,
                         totale_fornitori=totale_fornitori,
                         fornitori_attivi=fornitori_attivi,
                         attivo_filter=attivo_filter,
                         settore_filter=settore_filter)

@fornitori_bp.route('/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_fornitore():
    form = FornitoreForm()
    
    if form.validate_on_submit():
        try:
            fornitore = Fornitore(
                # CAMPI BASE
                ragione_sociale=form.ragione_sociale.data,
                partita_iva=clean_field(form.partita_iva.data),
                codice_fiscale=clean_field(form.codice_fiscale.data),
                indirizzo=clean_field(form.indirizzo.data),
                citta=form.citta.data,
                cap=form.cap.data,
                provincia=clean_field(form.provincia.data),
                
                # TELEFONI MULTIPLI
                telefono=clean_field(form.telefono.data),
                telefono_2=clean_field(form.telefono_2.data),
                telefono_3=clean_field(form.telefono_3.data),
                
                # EMAIL MULTIPLE
                email=clean_field(form.email.data),
                email_2=clean_field(form.email_2.data),
                email_3=clean_field(form.email_3.data),
                
                referente=clean_field(form.referente.data),
                
                # SETTORI MULTIPLI
                settore=clean_field(form.settore.data),
                settore_2=clean_field(form.settore_2.data),
                settore_3=clean_field(form.settore_3.data),
                settore_personalizzato=clean_field(form.settore_personalizzato.data),
                
                note=clean_field(form.note.data),
                attivo=form.attivo.data
            )
            
            # IMPORTANTE: Imposta automaticamente il nucleo
            from flask import session
            if current_user.ruolo == 'admin':
                filtro_admin = session.get('admin_nucleo_filter', 'tutti')
                if filtro_admin != 'tutti':
                    fornitore.nucleo = filtro_admin
                else:
                    fornitore.nucleo = form.nucleo.data if hasattr(form, 'nucleo') else 'Via Capitel'
            else:
                # User normale: nucleo automatico
                fornitore.nucleo = current_user.nucleo
            
            db.session.add(fornitore)
            db.session.commit()
            
            flash(f'Fornitore {fornitore.ragione_sociale} aggiunto con successo al nucleo {fornitore.nucleo}!', 'success')
            return redirect(url_for('fornitori.index_fornitori'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
    
    return render_template('fornitori/form.html', form=form, titolo='Aggiungi Fornitore')

@fornitori_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_fornitore(id):
    # Verifica accesso e ottieni fornitore
    fornitore = validate_fornitore_access(id)
    
    form = FornitoreForm(obj=fornitore)
    
    if form.validate_on_submit():
        try:
            # AGGIORNA CAMPI BASE
            fornitore.ragione_sociale = form.ragione_sociale.data
            fornitore.partita_iva = clean_field(form.partita_iva.data)
            fornitore.codice_fiscale = clean_field(form.codice_fiscale.data)
            fornitore.indirizzo = clean_field(form.indirizzo.data)
            fornitore.citta = form.citta.data
            fornitore.cap = form.cap.data
            fornitore.provincia = clean_field(form.provincia.data)
            
            # AGGIORNA TELEFONI MULTIPLI
            fornitore.telefono = clean_field(form.telefono.data)
            fornitore.telefono_2 = clean_field(form.telefono_2.data)
            fornitore.telefono_3 = clean_field(form.telefono_3.data)
            
            # AGGIORNA EMAIL MULTIPLE
            fornitore.email = clean_field(form.email.data)
            fornitore.email_2 = clean_field(form.email_2.data)
            fornitore.email_3 = clean_field(form.email_3.data)
            
            fornitore.referente = clean_field(form.referente.data)
            
            # AGGIORNA SETTORI MULTIPLI
            fornitore.settore = clean_field(form.settore.data)
            fornitore.settore_2 = clean_field(form.settore_2.data)
            fornitore.settore_3 = clean_field(form.settore_3.data)
            fornitore.settore_personalizzato = clean_field(form.settore_personalizzato.data)
            
            fornitore.note = clean_field(form.note.data)
            fornitore.attivo = form.attivo.data
            
            # SICUREZZA: Solo admin può cambiare nucleo (se implementiamo campo nella form)
            # Per ora il nucleo rimane invariato
            
            db.session.commit()
            flash(f'Fornitore {fornitore.ragione_sociale} modificato con successo!', 'success')
            return redirect(url_for('fornitori.index_fornitori'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
            
    return render_template('fornitori/form.html', form=form, titolo=f'Modifica Fornitore {fornitore.ragione_sociale}')

@fornitori_bp.route('/dettagli/<int:id>')
@login_required
def dettagli_fornitore(id):
    # Verifica accesso e ottieni fornitore
    fornitore = validate_fornitore_access(id)
    
    # Ottieni manutenzioni associate (filtrate per sicurezza)
    from app.models import Manutenzione
    from sqlalchemy import and_
    
    if current_user.ruolo == 'admin':
        from flask import session
        filtro_admin = session.get('admin_nucleo_filter', 'tutti')
        if filtro_admin != 'tutti':
            manutenzioni = Manutenzione.query.filter(
                and_(
                    Manutenzione.fornitore_id == fornitore.id,
                    Manutenzione.nucleo == filtro_admin
                )
            ).order_by(Manutenzione.data_intervento.desc()).limit(10).all()
        else:
            manutenzioni = fornitore.manutenzioni[:10]
    else:
        manutenzioni = Manutenzione.query.filter(
            and_(
                Manutenzione.fornitore_id == fornitore.id,
                Manutenzione.nucleo == current_user.nucleo
            )
        ).order_by(Manutenzione.data_intervento.desc()).limit(10).all()
    
    return render_template('fornitori/dettagli.html', 
                         fornitore=fornitore,
                         manutenzioni=manutenzioni)

@fornitori_bp.route('/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_fornitore(id):
    # Verifica accesso e ottieni fornitore
    fornitore = validate_fornitore_access(id)
    
    try:
        # Controlla se ci sono manutenzioni associate
        if fornitore.manutenzioni:
            flash(f'Impossibile eliminare {fornitore.ragione_sociale}: ci sono {len(fornitore.manutenzioni)} manutenzioni associate a questo fornitore.', 'error')
            return redirect(url_for('fornitori.dettagli_fornitore', id=id))
        
        ragione_sociale = fornitore.ragione_sociale
        nucleo = fornitore.nucleo
        
        db.session.delete(fornitore)
        db.session.commit()
        
        flash(f'Fornitore {ragione_sociale} eliminato con successo dal nucleo {nucleo}!', 'success')
        return redirect(url_for('fornitori.index_fornitori'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
        return redirect(url_for('fornitori.dettagli_fornitore', id=id))
