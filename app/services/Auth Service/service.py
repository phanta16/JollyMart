import hashlib
import secrets

from flask import jsonify, request, Flask
from flask_restful import Resource, Api

import db_session
from model import AuthInfo


class AuthService(Resource):

    def post(self):
        try:
            session = db_session.create_session()
            req_json = request.get_json()

            id = req_json.get('uid')
            tag = req_json.get('tag')

            if tag == 'reg':

                hashed_password = req_json.get('password')
                session_id = secrets.token_hex(16)

                user = AuthInfo(session_id=session_id,
                                hashed_password=hashlib.sha512(hashed_password.encode('utf-8')).hexdigest())
                session.add(user)
                session.commit()
                return jsonify({'status': 'True', 'session_id': session_id, 'uid': user.uid})

            elif tag == 'log':
                user = session.get(AuthInfo, id)
                hashed_password = req_json.get('password')

                if user is None:
                    return jsonify({'status': 'Invalid tag!'})
                else:
                    if user.hashed_password == hashlib.sha512(hashed_password.encode('utf-8')).hexdigest():
                        return jsonify({'status': 'True', 'session_id': user.session_id})
                    else:
                        return jsonify({'status': 'False'})

        except Exception as e:
            return jsonify({'status': f'False, message={str(e)}'})

    def patch(self):
        try:
            session = db_session.create_session()
            req_json = request.get_json()

            id = req_json.get('u id')
            new_password = req_json.get('new_password')

            new_hashed_password = hashlib.sha512(new_password.encode('utf-8')).hexdigest()

            user = session.get(AuthInfo, id)
            user.hashed_password = new_hashed_password
            session.commit()

            return jsonify({'status': 'True'})

        except Exception as e:

            return jsonify({'status': 'False'})


class AuthServices(Resource):

    def delete(self, id):
        try:
            user = session.get(AuthInfo, id)
            session.delete(user)
            session.commit()

            return jsonify({'status': 'True'})

        except Exception as e:

            return jsonify({'status': 'False'})


app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init('db/JollyAuthDB.db')

api.add_resource(AuthService, '/api/auth/')
api.add_resource(AuthServices, '/api/auth/int:<id>')

app.run()
