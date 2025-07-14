#!/usr/bin/env python3
"""
File principale per avviare l'applicazione Flask
Matrix Fleet Manager
"""

from app import create_app
from app.extensions import db
from app.models import Veicolo, Fornitore, Manutenzione, Scadenza, User

# Crea l'app
app = create_app()

# Comando per shell context
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Veicolo': Veicolo,
        'Fornitore': Fornitore,
        'Manutenzione': Manutenzione,
        'Scadenza': Scadenza,
        'User': User
    }

if __name__ == '__main__':
    with app.app_context():
        # Crea le tabelle se non esistono
        db.create_all()
        
        # Crea utente admin se non esiste
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                nucleo='Via Capitel',
                attivo=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("👤 Utente admin creato (password: admin123)")
    
    print("🚀 Avvio Matrix Fleet Manager...")
    print("🌐 URL: http://localhost:5000")
    print("👤 Login: admin / admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)