from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.forms.auth import LoginForm, ChangePasswordForm
from app.extensions import db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se l'utente è già loggato, vai alla dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Cerca l'utente nel database
        user = User.query.filter_by(username=form.username.data).first()
        
        # Verifica se l'utente esiste e la password è corretta
        if user and user.check_password(form.password.data):
            if user.attivo:
                # Login successful
                login_user(user, remember=form.remember_me.data)
                
                # Aggiorna ultimo accesso
                user.ultimo_accesso = datetime.utcnow()
                db.session.commit()
                
                flash(f'Benvenuto nel Matrix Fleet Manager, {user.username}!', 'success')
                
                # Redirect alla pagina richiesta o alla dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard.index'))
            else:
                flash('Account disattivato. Contattare l\'amministratore.', 'error')
        else:
            flash('Nome utente o password non validi.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(f'Logout effettuato con successo. Arrivederci {username}!', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Verifica che la password attuale sia corretta
        if current_user.check_password(form.current_password.data):
            try:
                # Cambia la password
                current_user.set_password(form.new_password.data)
                db.session.commit()
                
                flash('Password cambiata con successo! 🔐', 'success')
                return redirect(url_for('dashboard.index'))
                
            except Exception as e:
                db.session.rollback()
                flash('Errore durante il cambio password. Riprova.', 'error')
        else:
            flash('Password attuale non corretta. 🚫', 'error')
    
    return render_template('auth/change_password.html', form=form)
