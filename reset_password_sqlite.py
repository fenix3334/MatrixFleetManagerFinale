#!/usr/bin/env python3
"""
Script per resettare la password admin su database SQLite LOCALE
Usa questo script PRIMA della migrazione a PostgreSQL
"""
import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

# Path del database SQLite locale
SQLITE_DB_PATH = 'instance/matrix_fleet.db'

print(f"🔐 RESET PASSWORD ADMIN - Database SQLite LOCALE")
print(f"📁 Database: {SQLITE_DB_PATH}\n")

# Verifica che il database esista
if not os.path.exists(SQLITE_DB_PATH):
    print(f"❌ ERRORE: Database non trovato in {SQLITE_DB_PATH}")
    print(f"\n💡 Assicurati di eseguire questo script nella cartella del progetto")
    print(f"   dove si trova la cartella 'instance'")
    sys.exit(1)

print(f"✅ Database SQLite trovato\n")

try:
    # Connessione al database
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    # Leggi tutti gli utenti
    print("👥 UTENTI PRESENTI NEL DATABASE:")
    print("-" * 60)
    cursor.execute("SELECT id, username, nucleo, ruolo, attivo FROM users")
    users = cursor.fetchall()

    if not users:
        print("⚠️  Nessun utente trovato nel database!")
        conn.close()
        sys.exit(1)

    for user in users:
        user_id, username, nucleo, ruolo, attivo = user
        stato = "✅ ATTIVO" if attivo else "❌ DISATTIVO"
        print(f"  ID: {user_id} | Username: {username:15} | Ruolo: {ruolo:10} | Nucleo: {nucleo:20} | {stato}")

    print("-" * 60)

    # Chiedi quale utente modificare
    print(f"\n🔧 RESET PASSWORD")
    username_target = input("Inserisci lo username da modificare (premi INVIO per 'admin'): ").strip()
    if not username_target:
        username_target = 'admin'

    # Verifica che l'utente esista
    cursor.execute("SELECT id FROM users WHERE username = ?", (username_target,))
    user = cursor.fetchone()

    if not user:
        print(f"\n❌ ERRORE: Utente '{username_target}' non trovato!")
        conn.close()
        sys.exit(1)

    # Chiedi nuova password
    nuova_password = input(f"\nInserisci la NUOVA password per '{username_target}' (min 6 caratteri): ").strip()

    if len(nuova_password) < 6:
        print("❌ ERRORE: La password deve essere di almeno 6 caratteri")
        conn.close()
        sys.exit(1)

    # Conferma
    conferma = input(f"\n⚠️  Confermi di voler cambiare la password per '{username_target}'? (si/no): ").strip().lower()

    if conferma not in ['si', 's', 'yes', 'y']:
        print("❌ Operazione annullata")
        conn.close()
        sys.exit(0)

    # Genera hash della password
    password_hash = generate_password_hash(nuova_password)

    # Aggiorna password
    cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username_target))
    conn.commit()

    print(f"\n🎉 PASSWORD AGGIORNATA CON SUCCESSO!")
    print(f"\n📋 NUOVE CREDENZIALI:")
    print(f"   Username: {username_target}")
    print(f"   Password: {nuova_password}")
    print(f"\n✅ Ora puoi accedere al gestionale Matrix Fleet Manager con queste credenziali")

    conn.close()

except sqlite3.Error as e:
    print(f"\n❌ ERRORE DATABASE SQLite:")
    print(f"   {e}")
    sys.exit(1)
except ImportError as e:
    print(f"\n❌ ERRORE: Modulo mancante: {e}")
    print("   Installa: pip install werkzeug")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERRORE:")
    print(f"   {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
