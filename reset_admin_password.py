#!/usr/bin/env python3
"""
Script per resettare la password dell'utente admin su PostgreSQL Supabase
Uso: python reset_admin_password.py
"""
import os
import sys
from werkzeug.security import generate_password_hash

# Connection string PostgreSQL Supabase
POSTGRES_URL = os.environ.get('DATABASE_URL') or input(
    "Inserisci la connection string PostgreSQL Supabase:\n"
    "postgresql://postgres.bnhrhkfzmafosjrkqixn:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres\n> "
)

# Nuova password da impostare
NUOVA_PASSWORD = input("\nInserisci la NUOVA password per l'utente 'admin' (min 6 caratteri): ")

if len(NUOVA_PASSWORD) < 6:
    print("❌ ERRORE: La password deve essere di almeno 6 caratteri")
    sys.exit(1)

print(f"\n🔐 RESET PASSWORD UTENTE ADMIN")
print(f"🗄️  Database: PostgreSQL Supabase")

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    print(f"\n❌ ERRORE: Modulo mancante: {e}")
    print("   Installa le dipendenze: pip install sqlalchemy psycopg2-binary werkzeug")
    sys.exit(1)

def reset_password():
    """Reset password utente admin"""

    # Genera hash della nuova password
    password_hash = generate_password_hash(NUOVA_PASSWORD)
    print(f"\n✅ Hash password generato")

    # Crea connessione a PostgreSQL
    try:
        engine = create_engine(POSTGRES_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        print("✅ Connessione al database riuscita")
    except Exception as e:
        print(f"\n❌ ERRORE CONNESSIONE DATABASE:")
        print(f"   {e}")
        print("\n💡 VERIFICA:")
        print("   1. La connection string è corretta")
        print("   2. La password non contiene caratteri speciali (usa solo lettere/numeri)")
        print("   3. Il database è accessibile da internet")
        sys.exit(1)

    # Aggiorna password utente admin
    try:
        result = session.execute(
            text("UPDATE users SET password_hash = :hash WHERE username = 'admin'"),
            {"hash": password_hash}
        )
        session.commit()

        if result.rowcount == 0:
            print("\n⚠️  ATTENZIONE: Nessun utente 'admin' trovato nel database")
            print("   Verifica che l'utente esista o crea un nuovo utente admin")
        else:
            print(f"\n🎉 PASSWORD RESETTATA CON SUCCESSO!")
            print(f"\n📋 NUOVE CREDENZIALI:")
            print(f"   Username: admin")
            print(f"   Password: {NUOVA_PASSWORD}")
            print(f"\n🌐 Accedi all'app: https://matrixfleetmanagerfinale.onrender.com")

    except Exception as e:
        print(f"\n❌ ERRORE DURANTE L'AGGIORNAMENTO:")
        print(f"   {e}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()

if __name__ == '__main__':
    try:
        conferma = input(f"\n⚠️  Vuoi resettare la password dell'utente 'admin'? (si/no): ")
        if conferma.lower() in ['si', 's', 'yes', 'y']:
            reset_password()
        else:
            print("❌ Operazione annullata")
    except KeyboardInterrupt:
        print("\n\n❌ Operazione annullata dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
