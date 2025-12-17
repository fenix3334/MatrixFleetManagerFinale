#!/usr/bin/env python3
"""
Script di inizializzazione PostgreSQL per Supabase
Crea utenti e nuclei predefiniti
"""
import os
from app import create_app
from app.extensions import db
from app.models import User, Nucleo

def init_database():
    """Inizializza database PostgreSQL con dati essenziali"""
    app = create_app()

    with app.app_context():
        print("🔄 Inizializzazione database PostgreSQL...")

        # Crea tutte le tabelle se non esistono
        db.create_all()
        print("✅ Tabelle create/verificate")

        # CREA NUCLEI PREDEFINITI
        print("\n🏢 Creazione nuclei...")
        nuclei_default = [
            {
                'nome': 'Via Capitel',
                'descrizione': 'Cure Primarie ADI Via del Capitel',
                'indirizzo': 'Via del Capitel, Verona',
                'telefono': '045-123456',
                'email': 'capitel@asl.vr.it'
            },
            {
                'nome': 'Campania',
                'descrizione': 'Cure Primarie ADI Via Campania',
                'indirizzo': 'Via Campania, Verona',
                'telefono': '045-654321',
                'email': 'campania@asl.vr.it'
            }
        ]

        for nucleo_data in nuclei_default:
            nucleo_esistente = Nucleo.query.filter_by(nome=nucleo_data['nome']).first()
            if not nucleo_esistente:
                nucleo = Nucleo(**nucleo_data)
                db.session.add(nucleo)
                print(f"  ✅ Nucleo '{nucleo_data['nome']}' creato")
            else:
                print(f"  ⚠️  Nucleo '{nucleo_data['nome']}' già esistente")

        db.session.commit()

        # CREA UTENTE ADMIN
        print("\n👤 Creazione utenti...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                nucleo='Via Capitel',
                ruolo='admin',
                attivo=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("  ✅ Utente admin creato (admin/admin123)")
        else:
            print("  ⚠️  Utente admin già esistente")

        # CREA UTENTI PER NUCLEI
        utenti_nuclei = [
            {'username': 'capitel', 'nucleo': 'Via Capitel', 'password': 'capitel123'},
            {'username': 'campania', 'nucleo': 'Campania', 'password': 'campania123'}
        ]

        for user_data in utenti_nuclei:
            user_esistente = User.query.filter_by(username=user_data['username']).first()
            if not user_esistente:
                user = User(
                    username=user_data['username'],
                    nucleo=user_data['nucleo'],
                    ruolo='user',
                    attivo=True
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"  ✅ Utente '{user_data['username']}' creato")
            else:
                print(f"  ⚠️  Utente '{user_data['username']}' già esistente")

        db.session.commit()

        # VERIFICA FINALE
        print("\n📊 Stato database:")
        print(f"  - Nuclei: {Nucleo.query.count()}")
        print(f"  - Utenti: {User.query.count()}")

        print("\n🎉 Inizializzazione completata!")
        print("\n🔑 Credenziali:")
        print("  - admin/admin123 (amministratore)")
        print("  - capitel/capitel123 (nucleo Via Capitel)")
        print("  - campania/campania123 (nucleo Campania)")

if __name__ == '__main__':
    init_database()
