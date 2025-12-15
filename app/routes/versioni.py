from flask import Blueprint, render_template
import os

versioni_bp = Blueprint('versioni', __name__)

@versioni_bp.route('/versioni')
def mostra_versioni():
    path = os.path.join(os.path.dirname(__file__), '..', 'CHANGELOG.md')
    with open(path, 'r', encoding='utf-8') as f:
        changelog = f.read()
    return render_template('versioni.html', changelog=changelog)
