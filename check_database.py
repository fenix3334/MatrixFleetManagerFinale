#!/usr/bin/env python3
"""
Script di verifica stato database Matrix Fleet Manager
Controlla la struttura del database senza modificare nulla
"""

import os
import sqlite3

def check_database_status():
    """Verifica lo stato del database"""
    db_path = 'instance/matrix_fleet.db'
    
    if not os.path.exists(db_path):
        print("❌ Database non trovato!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 STATO ATTUALE DATABASE")
        print("=" * 50)
        
        # Elenca tutte le tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tabelle presenti: {tables}")
        
        # Verifica struttura di ogni tabella principale
        main_tables = ['users', 'veicoli', 'manutenzioni', 'scadenze', 'fornitori']
        
        for table in main_tables:
            if table in tables:
                print(f"\n📊 TABELLA: {table}")
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                col_names = [col[1] for col in columns]
                print(f"  Colonne ({len(col_names)}): {col_names}")
                
                # Conta record
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  Record: {count}")
                
                # Verifiche specifiche
                if table == 'users':
                    if 'email' not in col_names:
                        print("  ⚠️  MANCA: colonna email")
                    if 'ruolo' not in col_names:
                        print("  ⚠️  MANCA: colonna ruolo")
                
                elif table == 'veicoli':
                    if 'unita_operativa' not in col_names:
                        print("  ⚠️  MANCA: colonna unita_operativa")
                
                elif table == 'manutenzioni':
                    if 'numero_documento' not in col_names:
                        print("  ⚠️  MANCA: colonna numero_documento")
                    if 'numero_fattura' in col_names:
                        print("  ⚠️  PRESENTE: colonna numero_fattura (da rinominare)")
                    if 'costo' in col_names:
                        print("  ⚠️  PRESENTE: colonna costo (da rimuovere)")
                
                elif table == 'scadenze':
                    if 'costo' in col_names:
                        print("  ⚠️  PRESENTE: colonna costo (da rimuovere)")
            else:
                print(f"\n❌ TABELLA MANCANTE: {table}")
        
        # Verifica utenti
        if 'users' in tables:
            print(f"\n👥 UTENTI PRESENTI:")
            try:
                cursor.execute("SELECT id, username FROM users")
                users = cursor.fetchall()
                for user_id, username in users:
                    print(f"  - {username} (ID: {user_id})")
            except Exception as e:
                print(f"  ❌ Errore lettura utenti: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Errore verifica database: {e}")
        return False

def main():
    """Funzione principale"""
    print("🔍 VERIFICA STATO DATABASE MATRIX FLEET MANAGER")
    print("=" * 60)
    
    if not os.path.exists('main.py'):
        print("❌ Eseguire dalla directory principale del progetto!")
        return
    
    if not os.path.exists('instance'):
        print("❌ Directory 'instance' non trovata!")
        return
    
    check_database_status()
    
    print("\n" + "=" * 60)
    print("🎯 COSA SIGNIFICA:")
    print("✅ Se vedi tutte le tabelle e utenti → Backup ripristinato OK")
    print("⚠️  Se vedi colonne mancanti → Serve migrazione")
    print("❌ Se vedi errori → Database corrotto")

if __name__ == "__main__":
    main()