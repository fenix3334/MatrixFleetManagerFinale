"""
API Veicoli - CRUD completo
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Veicolo, User
from app.schemas import VeicoloSchema, VeicoloListSchema
from marshmallow import ValidationError
from datetime import datetime

# Namespace API
api = Namespace('veicoli', description='Gestione veicoli del parco auto')

# Modelli Flask-RESTX per Swagger
veicolo_model = api.model('Veicolo', {
    'id': fields.Integer(description='ID veicolo'),
    'targa': fields.String(required=True, description='Targa veicolo'),
    'marca': fields.String(required=True, description='Marca'),
    'modello': fields.String(required=True, description='Modello'),
    'anno_immatricolazione': fields.Integer(required=True, description='Anno immatricolazione'),
    'data_immatricolazione': fields.Date(required=True, description='Data immatricolazione'),
    'km_attuali': fields.Integer(description='Chilometri attuali'),
    'carburante': fields.String(required=True, description='Tipo carburante'),
    'cilindrata': fields.Integer(description='Cilindrata'),
    'colore': fields.String(description='Colore'),
    'stato': fields.String(description='Stato (Attivo/Manutenzione/Dismesso)'),
    'note': fields.String(description='Note'),
    'nucleo': fields.String(description='Nucleo di appartenenza')
})


@api.route('/')
class VeicoliList(Resource):
    """Lista veicoli e creazione nuovo"""

    @api.doc('list_veicoli', security='Bearer')
    @jwt_required()
    @api.response(200, 'Lista veicoli')
    def get(self):
        """
        Ottiene lista di tutti i veicoli
        Supporta filtri per nucleo e stato
        """
        try:
            # Ottiene utente corrente
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            # Query base
            query = Veicolo.query

            # Filtro per nucleo (se non admin)
            if not user.is_admin:
                query = query.filter_by(nucleo=user.nucleo)

            # Filtri da query parameters
            nucleo_filter = request.args.get('nucleo')
            if nucleo_filter:
                query = query.filter_by(nucleo=nucleo_filter)

            stato_filter = request.args.get('stato')
            if stato_filter:
                query = query.filter_by(stato=stato_filter)

            # Ordinamento
            query = query.order_by(Veicolo.targa)

            # Esegui query
            veicoli = query.all()

            # Serializza
            schema = VeicoloListSchema(many=True)
            result = schema.dump(veicoli)

            return {
                'success': True,
                'count': len(veicoli),
                'data': result
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Errore: {str(e)}'
            }, 500

    @api.doc('create_veicolo', security='Bearer')
    @api.expect(veicolo_model)
    @jwt_required()
    @api.response(201, 'Veicolo creato')
    @api.response(400, 'Dati non validi')
    def post(self):
        """
        Crea un nuovo veicolo
        """
        try:
            # Ottiene utente corrente
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            # Valida input
            schema = VeicoloSchema()
            data = schema.load(request.json)

            # Verifica targa duplicata
            if Veicolo.query.filter_by(targa=data['targa']).first():
                return {
                    'success': False,
                    'message': 'Targa già esistente'
                }, 400

            # Imposta nucleo dell'utente se non specificato
            if 'nucleo' not in data:
                data['nucleo'] = user.nucleo

            # Crea veicolo
            veicolo = Veicolo(**data)
            db.session.add(veicolo)
            db.session.commit()

            # Serializza
            result = schema.dump(veicolo)

            return {
                'success': True,
                'message': 'Veicolo creato con successo',
                'data': result
            }, 201

        except ValidationError as e:
            return {
                'success': False,
                'message': 'Dati non validi',
                'errors': e.messages
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Errore: {str(e)}'
            }, 500


@api.route('/<int:id>')
@api.param('id', 'ID del veicolo')
class VeicoloDetail(Resource):
    """Dettaglio, modifica ed eliminazione veicolo"""

    @api.doc('get_veicolo', security='Bearer')
    @jwt_required()
    @api.response(200, 'Dettagli veicolo')
    @api.response(404, 'Veicolo non trovato')
    def get(self, id):
        """
        Ottiene dettagli di un veicolo specifico
        """
        try:
            veicolo = Veicolo.query.get(id)

            if not veicolo:
                return {
                    'success': False,
                    'message': 'Veicolo non trovato'
                }, 404

            # Verifica permessi nucleo
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user.is_admin and veicolo.nucleo != user.nucleo:
                return {
                    'success': False,
                    'message': 'Accesso negato'
                }, 403

            # Serializza
            schema = VeicoloSchema()
            result = schema.dump(veicolo)

            return {
                'success': True,
                'data': result
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Errore: {str(e)}'
            }, 500

    @api.doc('update_veicolo', security='Bearer')
    @api.expect(veicolo_model)
    @jwt_required()
    @api.response(200, 'Veicolo aggiornato')
    @api.response(404, 'Veicolo non trovato')
    def put(self, id):
        """
        Aggiorna un veicolo esistente
        """
        try:
            veicolo = Veicolo.query.get(id)

            if not veicolo:
                return {
                    'success': False,
                    'message': 'Veicolo non trovato'
                }, 404

            # Verifica permessi
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user.is_admin and veicolo.nucleo != user.nucleo:
                return {
                    'success': False,
                    'message': 'Accesso negato'
                }, 403

            # Valida input
            schema = VeicoloSchema(partial=True)
            data = schema.load(request.json)

            # Aggiorna campi
            for key, value in data.items():
                setattr(veicolo, key, value)

            db.session.commit()

            # Serializza
            result = schema.dump(veicolo)

            return {
                'success': True,
                'message': 'Veicolo aggiornato con successo',
                'data': result
            }, 200

        except ValidationError as e:
            return {
                'success': False,
                'message': 'Dati non validi',
                'errors': e.messages
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Errore: {str(e)}'
            }, 500

    @api.doc('delete_veicolo', security='Bearer')
    @jwt_required()
    @api.response(200, 'Veicolo eliminato')
    @api.response(404, 'Veicolo non trovato')
    def delete(self, id):
        """
        Elimina un veicolo
        """
        try:
            veicolo = Veicolo.query.get(id)

            if not veicolo:
                return {
                    'success': False,
                    'message': 'Veicolo non trovato'
                }, 404

            # Verifica permessi (solo admin)
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user.is_admin:
                return {
                    'success': False,
                    'message': 'Accesso negato: richiesti privilegi di amministratore'
                }, 403

            targa = veicolo.targa
            db.session.delete(veicolo)
            db.session.commit()

            return {
                'success': True,
                'message': f'Veicolo {targa} eliminato con successo'
            }, 200

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Errore: {str(e)}'
            }, 500


@api.route('/stats')
class VeicoliStats(Resource):
    """Statistiche veicoli"""

    @api.doc('veicoli_stats', security='Bearer')
    @jwt_required()
    @api.response(200, 'Statistiche veicoli')
    def get(self):
        """
        Ottiene statistiche sui veicoli
        """
        try:
            # Ottiene utente corrente
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            # Query base
            query = Veicolo.query
            if not user.is_admin:
                query = query.filter_by(nucleo=user.nucleo)

            # Calcola statistiche
            totale_veicoli = query.count()
            veicoli_attivi = query.filter_by(stato='Attivo').count()
            veicoli_manutenzione = query.filter_by(stato='In Manutenzione').count()

            # Km totali
            veicoli = query.all()
            km_totali = sum(v.km_attuali or 0 for v in veicoli)

            return {
                'success': True,
                'data': {
                    'totale_veicoli': totale_veicoli,
                    'veicoli_attivi': veicoli_attivi,
                    'veicoli_manutenzione': veicoli_manutenzione,
                    'km_totali': km_totali
                }
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Errore: {str(e)}'
            }, 500
