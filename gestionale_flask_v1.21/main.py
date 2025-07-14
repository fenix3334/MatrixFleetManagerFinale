#!/usr/bin/env python3
"""
Matrix Fleet Manager - Con backup automatico e sistema login
Versione aggiornata del main.py originale
"""
import os
import shutil
from datetime import datetime
from flask import redirect, url_for
from flask_login import current_user
from app import create_app

def auto_backup():
    """Backup automatico del database all'avvio"""
    source_db = 'instance/matrix_fleet.db'
    
    if not os.path.exists(source_db):
        print("ℹ️  Database non trovato - primo avvio")
        return
    
    try:
        # Crea cartella backup se non esiste
        if not os.path.exists('backups'):
            os.makedirs('backups')
            print("📁 Cartella 'backups' creata")
        
        # Nome backup con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'auto_backup_{timestamp}.db'
        backup_path = os.path.join('backups', backup_name)
        
        # Copia database
        shutil.copy2(source_db, backup_path)
        
        file_size = os.path.getsize(backup_path) / 1024  # KB
        print(f"💾 Backup automatico: {backup_name} ({file_size:.1f} KB)")
        
        # Mantieni solo gli ultimi 10 backup automatici
        cleanup_old_backups()
        
    except Exception as e:
        print(f"⚠️  Errore backup automatico: {e}")

def cleanup_old_backups(max_backups=10):
    """Mantiene solo gli ultimi backup automatici"""
    try:
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return
        
        # Lista backup automatici ordinati per data
        auto_backups = []
        for file in os.listdir(backup_dir):
            if file.startswith('auto_backup_') and file.endswith('.db'):
                filepath = os.path.join(backup_dir, file)
                mtime = os.path.getmtime(filepath)
                auto_backups.append((mtime, filepath))
        
        # Ordina per data (più recenti prima)
        auto_backups.sort(reverse=True)
        
        # Rimuovi backup vecchi se superano il limite
        if len(auto_backups) > max_backups:
            removed_count = 0
            for _, old_backup in auto_backups[max_backups:]:
                os.remove(old_backup)
                removed_count += 1
            print(f"🗑️  Rimossi {removed_count} backup vecchi")
    
    except Exception as e:
        print(f"⚠️  Errore pulizia backup: {e}")

def show_system_info():
    """Mostra informazioni sistema e backup"""
    # Info database
    if os.path.exists('instance/matrix_fleet.db'):
        db_size = os.path.getsize('instance/matrix_fleet.db') / 1024
        print(f"💾 Database: matrix_fleet.db ({db_size:.1f} KB)")
    
    # Info backup
    backup_count = 0
    if os.path.exists('backups'):
        backup_count = len([f for f in os.listdir('backups') if f.endswith('.db')])
    print(f"📦 Backup disponibili: {backup_count}")

# Crea app Flask
app = create_app()

# Route principale - redirect a login se non autenticato
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    else:
        return redirect(url_for('auth.login'))

if __name__ == '__main__':
    print("🚀 MATRIX FLEET MANAGER - AVVIO CON SISTEMA LOGIN")
    
    # Backup automatico all'avvio
    auto_backup()
    
    # Info sistema
    show_system_info()
    
    print("🌐 Server in avvio su http://localhost:5000")
    print("👤 Login predefinito: admin / admin123")
    print("⏹️  Premi CTRL+C per fermare")
    
    try:
        app.run(
            debug=True, 
            host='0.0.0.0', 
            port=5000,
            use_reloader=False  # Evita doppi backup
        )
    except KeyboardInterrupt:
        print("\n🛑 Server fermato")
        print("💾 I tuoi dati sono protetti dai backup!")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        print("💾 Database protetto da backup automatico")
