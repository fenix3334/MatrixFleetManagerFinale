#!/usr/bin/env python3
"""
Script di migrazione da SQLite a PostgreSQL
Esegui questo script sul tuo computer dove hai il database SQLite
"""
import os
import sys
from datetime import datetime

# Path del database SQLite locale
SQLITE_DB_PATH = 'instance/matrix_fleet.db'  # Modifica se il tuo DB è altrove

# Connection string PostgreSQL Supabase
# SOSTITUISCI con la tua stringa completa (con password)
POSTGRES_URL = os.environ.get('DATABASE_URL') or input(
    "Inserisci la connection string PostgreSQL Supabase:\n"
    "postgresql://postgres.bnhrhkfzmafosjrkqixn:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres\n> "
)

print(f"\n🔄 MIGRAZIONE DATI SQLite → PostgreSQL")
print(f"📁 Database locale: {SQLITE_DB_PATH}")
print(f"🗄️  Database remoto: PostgreSQL Supabase")

# Verifica database SQLite
if not os.path.exists(SQLITE_DB_PATH):
    print(f"\n❌ ERRORE: Database SQLite non trovato in {SQLITE_DB_PATH}")
    print("   Modifica la variabile SQLITE_DB_PATH nello script")
    sys.exit(1)

print(f"\n✅ Database SQLite trovato")

try:
    from app import create_app
    from app.extensions import db
    # Importa solo i modelli base essenziali
    from app.models import Veicolo, Fornitore, Manutenzione, Scadenza, User, Nucleo

    # Prova a importare modelli opzionali (potrebbero non esistere)
    try:
        from app.models import Sinistro
        HAS_SINISTRI = True
    except ImportError:
        HAS_SINISTRI = False

    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    print(f"\n❌ ERRORE: Modulo mancante: {e}")
    print("   Installa le dipendenze: pip install -r requirements.txt")
    sys.exit(1)

def migrate_data():
    """Migra tutti i dati da SQLite a PostgreSQL"""

    # Crea connessione a SQLite
    sqlite_engine = create_engine(f'sqlite:///{SQLITE_DB_PATH}')
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SqliteSession()

    # Configura app Flask per PostgreSQL
    os.environ['DATABASE_URL'] = POSTGRES_URL
    app = create_app()

    with app.app_context():
        print("\n📊 Verifica tabelle PostgreSQL...")
        db.create_all()
        print("✅ Tabelle verificate/create")

        # STEP 1: Migra Nuclei
        print("\n🏢 Migrazione Nuclei...")
        from sqlalchemy import Table, MetaData
        metadata = MetaData()
        metadata.reflect(bind=sqlite_engine)

        if 'nuclei' in metadata.tables:
            nuclei_sqlite = sqlite_session.execute(
                text("SELECT * FROM nuclei")
            ).fetchall()

            for row in nuclei_sqlite:
                if not Nucleo.query.filter_by(nome=row.nome).first():
                    nucleo = Nucleo(
                        nome=row.nome,
                        descrizione=row.descrizione if hasattr(row, 'descrizione') else None,
                        indirizzo=row.indirizzo if hasattr(row, 'indirizzo') else None,
                        telefono=row.telefono if hasattr(row, 'telefono') else None,
                        email=row.email if hasattr(row, 'email') else None,
                        attivo=row.attivo if hasattr(row, 'attivo') else True
                    )
                    db.session.add(nucleo)
            db.session.commit()
            print(f"  ✅ Migrati {len(nuclei_sqlite)} nuclei")
        else:
            print("  ⚠️  Tabella nuclei non trovata in SQLite")

        # STEP 2: Migra Users (salta admin se esiste già)
        print("\n👤 Migrazione Users...")
        users_sqlite = sqlite_session.execute(
            text("SELECT * FROM users")
        ).fetchall()

        migrated_users = 0
        for row in users_sqlite:
            if not User.query.filter_by(username=row.username).first():
                user = User(
                    username=row.username,
                    password_hash=row.password_hash,
                    nucleo=row.nucleo if hasattr(row, 'nucleo') else 'Via Capitel',
                    ruolo=row.ruolo if hasattr(row, 'ruolo') else 'user',
                    attivo=row.attivo if hasattr(row, 'attivo') else True
                )
                db.session.add(user)
                migrated_users += 1
        db.session.commit()
        print(f"  ✅ Migrati {migrated_users} utenti")

        # STEP 3: Migra Fornitori
        print("\n🏭 Migrazione Fornitori...")
        fornitori_sqlite = sqlite_session.execute(
            text("SELECT * FROM fornitori")
        ).fetchall()

        for row in fornitori_sqlite:
            fornitore = Fornitore(
                id=row.id,
                ragione_sociale=row.ragione_sociale,
                partita_iva=row.partita_iva if hasattr(row, 'partita_iva') else None,
                citta=row.citta if hasattr(row, 'citta') else None,
                cap=row.cap if hasattr(row, 'cap') else None,
                provincia=row.provincia if hasattr(row, 'provincia') else None,
                telefono=row.telefono if hasattr(row, 'telefono') else None,
                email=row.email if hasattr(row, 'email') else None,
                settore=row.settore if hasattr(row, 'settore') else None,
                nucleo=row.nucleo if hasattr(row, 'nucleo') else 'Via Capitel',
                attivo=row.attivo if hasattr(row, 'attivo') else True
            )
            db.session.merge(fornitore)
        db.session.commit()
        print(f"  ✅ Migrati {len(fornitori_sqlite)} fornitori")

        # STEP 4: Migra Veicoli
        print("\n🚗 Migrazione Veicoli...")
        veicoli_sqlite = sqlite_session.execute(
            text("SELECT * FROM veicoli")
        ).fetchall()

        for row in veicoli_sqlite:
            veicolo = Veicolo(
                id=row.id,
                targa=row.targa,
                marca=row.marca if hasattr(row, 'marca') else None,
                modello=row.modello if hasattr(row, 'modello') else None,
                anno_immatricolazione=row.anno_immatricolazione if hasattr(row, 'anno_immatricolazione') else None,
                km_attuali=row.km_attuali if hasattr(row, 'km_attuali') else 0,
                carburante=row.carburante if hasattr(row, 'carburante') else None,
                nucleo=row.nucleo if hasattr(row, 'nucleo') else 'Via Capitel',
                stato=row.stato if hasattr(row, 'stato') else 'Attivo'
            )
            db.session.merge(veicolo)
        db.session.commit()
        print(f"  ✅ Migrati {len(veicoli_sqlite)} veicoli")

        # STEP 5: Migra Manutenzioni
        print("\n🔧 Migrazione Manutenzioni...")
        manutenzioni_sqlite = sqlite_session.execute(
            text("SELECT * FROM manutenzioni")
        ).fetchall()

        for row in manutenzioni_sqlite:
            manutenzione = Manutenzione(
                id=row.id,
                veicolo_id=row.veicolo_id,
                fornitore_id=row.fornitore_id if hasattr(row, 'fornitore_id') else None,
                data_manutenzione=row.data_manutenzione,
                tipo_intervento=row.tipo_intervento if hasattr(row, 'tipo_intervento') else None,
                descrizione=row.descrizione if hasattr(row, 'descrizione') else None,
                costo=row.costo if hasattr(row, 'costo') else 0,
                km_veicolo=row.km_veicolo if hasattr(row, 'km_veicolo') else 0,
                stato=row.stato if hasattr(row, 'stato') else 'Completata',
                nucleo=row.nucleo if hasattr(row, 'nucleo') else 'Via Capitel'
            )
            db.session.merge(manutenzione)
        db.session.commit()
        print(f"  ✅ Migrate {len(manutenzioni_sqlite)} manutenzioni")

        # STEP 6: Migra Scadenze
        print("\n📅 Migrazione Scadenze...")
        scadenze_sqlite = sqlite_session.execute(
            text("SELECT * FROM scadenze")
        ).fetchall()

        for row in scadenze_sqlite:
            scadenza = Scadenza(
                id=row.id,
                veicolo_id=row.veicolo_id,
                tipo_scadenza=row.tipo_scadenza,
                data_scadenza=row.data_scadenza,
                stato=row.stato if hasattr(row, 'stato') else 'Attiva',
                note=row.note if hasattr(row, 'note') else None,
                nucleo=row.nucleo if hasattr(row, 'nucleo') else 'Via Capitel'
            )
            db.session.merge(scadenza)
        db.session.commit()
        print(f"  ✅ Migrate {len(scadenze_sqlite)} scadenze")

        # STEP 7: Migra Sinistri (se esistono e se il modello è disponibile)
        print("\n⚠️  Migrazione Sinistri...")
        if HAS_SINISTRI and 'sinistri' in metadata.tables:
            sinistri_sqlite = sqlite_session.execute(
                text("SELECT * FROM sinistri")
            ).fetchall()

            for row in sinistri_sqlite:
                sinistro = Sinistro(
                    id=row.id,
                    veicolo_id=row.veicolo_id,
                    data_sinistro=row.data_sinistro,
                    descrizione=row.descrizione if hasattr(row, 'descrizione') else None,
                    responsabilita=row.responsabilita if hasattr(row, 'responsabilita') else None,
                    nucleo=row.nucleo if hasattr(row, 'nucleo') else 'Via Capitel'
                )
                db.session.merge(sinistro)
            db.session.commit()
            print(f"  ✅ Migrati {len(sinistri_sqlite)} sinistri")
        else:
            print("  ⚠️  Tabella sinistri non disponibile o modello non presente")

        # Verifica finale
        print("\n📊 RIEPILOGO MIGRAZIONE:")
        print(f"  - Nuclei: {Nucleo.query.count()}")
        print(f"  - Utenti: {User.query.count()}")
        print(f"  - Fornitori: {Fornitore.query.count()}")
        print(f"  - Veicoli: {Veicolo.query.count()}")
        print(f"  - Manutenzioni: {Manutenzione.query.count()}")
        print(f"  - Scadenze: {Scadenza.query.count()}")

        print("\n🎉 MIGRAZIONE COMPLETATA CON SUCCESSO!")
        print("\n🌐 Accedi all'app: https://matrixfleetmanagerfinale.onrender.com")
        print("🔑 Login: admin / admin123")

    sqlite_session.close()

if __name__ == '__main__':
    try:
        migrate_data()
    except Exception as e:
        print(f"\n❌ ERRORE DURANTE LA MIGRAZIONE:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
