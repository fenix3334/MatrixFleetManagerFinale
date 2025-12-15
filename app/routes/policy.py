"""
Blueprint per la sezione Policy e Documentazione.

Questa sezione espone una pagina statica contenente le linee guida aziendali
relative all'utilizzo dei veicoli, alle responsabilità e alle procedure
operative. L'accesso richiede l'autenticazione.
"""

from flask import Blueprint, render_template, current_app
from flask_login import login_required
import os


policy_bp = Blueprint('policy', __name__, url_prefix='/policy')


@policy_bp.route('/')
@login_required
def view_policy():
    """Visualizza la pagina delle policy aziendali.

    Per generare dinamicamente la sezione Policy & Procedure, vengono
    raccolte le immagini estratte dai documenti PDF presenti nella
    cartella ``static/policy``. I documenti sono ordinati in base alla
    data riportata nel nome (gg-mm-aaaa) e per ciascuno si elencano
    tutte le pagine convertite in PNG. Queste informazioni vengono
    passate al template, che provvederà a visualizzare ogni gruppo
    separatamente.
    """
    # Definisci l'ordine cronologico dei documenti (dal più vecchio al più recente)
    docs_order = [
        ('2019-07-25', '25-07-2019'),
        ('2022-02-09', '09-02-2022'),
        ('2023-03-28', '28-03-2023'),
        ('2023-12-20', '20-12-2023'),
    ]

    policy_docs = []
    # Directory base dove sono salvate le immagini dei documenti
    policy_base = os.path.join(current_app.static_folder, 'policy')
    for readable_date, folder in docs_order:
        folder_path = os.path.join(policy_base, folder)
        if not os.path.isdir(folder_path):
            continue
        # Recupera tutte le immagini PNG in ordine alfabetico
        image_files = [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith('.png')]
        # Prepara la lista di URL relativi allo static folder.
        # Utilizziamo posixpath.join per comporre percorsi con barre (/)
        # invece di os.path.join che su Windows inserirebbe backslash (\)
        # causando URL errati come "policy%5C09-02-2022%5Cpage-1.png".
        import posixpath

        image_urls = [posixpath.join('policy', folder, img) for img in image_files]
        policy_docs.append({
            'date': readable_date,
            'files': image_urls,
        })

    return render_template('policy/index.html', policy_docs=policy_docs)