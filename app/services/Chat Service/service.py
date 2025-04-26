import requests
import socketio

from flask import jsonify, request, make_response, Flask
from flask_socketio import SocketIO, emit, Namespace

import db_session
from model import ChatInfo, MessagesInfo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'THE_MOST_SECRET_KEY_YOU_HAVE_EVER_SEEN'
socketServer = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

connected_users = {}


@app.route('/chat/messages/<chat_id>', methods=['GET'])
def get(chat_id):
    try:
        session = db_session.create_session()
        messages = session.query(ChatInfo).filter_by(chat_id=chat_id).all()
        if len(messages) == 0:
            return make_response(jsonify({"status": "No messages!"}), 200)
        return make_response(jsonify([{

            'message': m.context,
            's_id': m.sender_id,
            'r_id': m.receiver_id,
            'timestamp': m.timestamp,

        }
            for m in messages]))
    except requests.exceptions.RequestException as e:

        return make_response(jsonify({'status': 'Unknown error!', 'message': str(e)}), 401)


@app.route('/chat/new-chat/<receiver_id>', methods=['POST'])
def create_chat(receiver_id):
    try:
        session = db_session.create_session()
        us = {
            "uid": receiver_id,
        }

        validate = requests.post('http://127.0.0.1:5000/auth/validate_user/', json=us)
        validate = validate.json()
        if validate["status"] != "True":
            return jsonify({
                "status": "False",
                "message": "User is not exists!",
            })
        else:
            if session.query(ChatInfo).filter_by(receiver_id=receiver_id,
                                                 initiator_id=request.headers.get('X-User-Id')).first() is not None:

                return make_response(jsonify({"status": "False"}, 200))

            new_chat = ChatInfo(initiator_id=request.headers.get('X-User-Id'), receiver_id=receiver_id)
            session.add(new_chat)
            session.commit()

            return make_response(jsonify({"status": "True"}))

    except Exception as e:

        return jsonify({'status': 'Unknown error!', 'message': str(e)}), 401


class SocketsChat(Namespace):

    def on_connect(self):
        user_id = request.headers.get('X-User-Id')
        if user_id:
            connected_users[user_id] = request.sid

    def on_message(self, data):
        if len(connected_users) != 2:
            return
        sender_id = str(request.headers.get('X-User-Id'))
        try:
            recipient_id = str(data.get('to'))
            message_text = data.get('text')
            recipient_sid = connected_users.get(recipient_id)
            if recipient_sid:
                emit('message', {
                    "from": sender_id,
                    "text": message_text
                },   to=recipient_sid)
                session = db_session.create_session()
                chat_id = session.query(ChatInfo).filter_by(receiver_id=recipient_id, initiator_id=sender_id).first()
                message = MessagesInfo(sender_id=sender_id, receiver_id=recipient_id, context=message_text,
                                       chat_id=chat_id)
                session.add(message)
                session.commit()
            else:

                print('Error!')

        except Exception as e:
            print(e)

    def on_disconnect(self):
        sid = request.sid
        for uid, s_sid in connected_users.items():
            if sid == s_sid:
                del connected_users[uid]
                break

socketServer.on_namespace(SocketsChat("/chat"))


db_session.global_init('db/JollyChatDB.db')

socketServer.run(app, port=5001, host='0.0.0.0')
