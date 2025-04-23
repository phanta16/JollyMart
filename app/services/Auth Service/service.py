import hashlib
import secrets

from flask import jsonify, request, Flask, make_response
import requests

import db_session
from model import AuthInfo

app = Flask(__name__)


@app.route('/auth/register/', methods=['POST'])
def register():
    try:
        session = db_session.create_session()
        req_json = request.get_json()

        hashed_password = req_json.get('password')
        session_id = secrets.token_hex(16)

        user = AuthInfo(session_id=session_id,
                        hashed_password=hashlib.sha512(hashed_password.encode('utf-8')).hexdigest())
        session.add(user)
        session.commit()
        return make_response(jsonify({'status': 'True', 'session_id': session_id, 'uid': user.uid}), 200)
    except requests.exceptions.RequestException as e:
        return make_response(jsonify({'status': 'Something went wrong!', 'message': str(e)}), 404)


@app.route('/auth/login/', methods=['POST'])
def login():
    try:
        session = db_session.create_session()
        req_json = request.get_json()

        uid = req_json.get('uid')
        hashed_password = req_json.get('password')

        user = session.get(AuthInfo, uid)

        if user is None:
            return make_response(jsonify({'status': 'Такого пользователя не существует!'}), 404)
        else:
            if user.hashed_password == hashlib.sha512(hashed_password.encode('utf-8')).hexdigest():
                return make_response(jsonify({'status': 'True', 'session_id': user.session_id}), 200)
            else:
                return make_response(jsonify({'status': 'False'}), 401)
    except requests.exceptions.RequestException as e:
        return make_response(jsonify({'status': 'Something went wrong!', 'message': str(e)}), 404)


@app.route('/auth/change_password/', methods=['PATCH'])
def change_password():
    try:
        session = db_session.create_session()
        req_json = request.get_json()

        id = req_json.get('uid')
        new_password = req_json.get('new_password')

        new_hashed_password = hashlib.sha512(new_password.encode('utf-8')).hexdigest()

        user = session.get(AuthInfo, id)
        user.hashed_password = new_hashed_password
        session.commit()

        return make_response(jsonify({'status': 'True'}), 200)

    except requests.exceptions.RequestException as e:

        return make_response(jsonify({'status': 'False', 'message': str(e)}), 401)

@app.route('/auth/delete_user/', methods=['DELETE'])
def delete_user():
    try:
        session = db_session.create_session()
        req_json = request.get_json()
        uid = req_json.get('uid')
        user = session.get(AuthInfo, uid)
        session.delete(user)
        session.commit()

        return make_response(jsonify({'status': 'True'}), 200)

    except requests.exceptions.RequestException as e:

        return make_response(jsonify({'status': 'False', 'message': str(e)}), 401)




ROUTES = {

    "/chat/": "http://chat-service:5000",
    "/user/": "http://user-service:5000",
    "/comment/": "http://comment-service:5000",
    "/favourite/": "http://favourite-service:5000",
    "/media/": "http://media-service:5000",
    "/notifications/": "http://notifications-service:5000",
    "/recommendations/": "http://recommendations-service:5000",
    "/search/": "http://search-service:5000",
    "/posts/": "http://posts-service:5000",
    "/auth/": "http://auth-service:5000",
}

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def gateway(path):

    session_id = request.cookies.get("session_id")

    if not session_id:
        return jsonify({"error": "Forbidden!"}), 401

    session = db_session.create_session()
    user = session.query(AuthInfo).filter_by(session_id=session_id).first()
    if not user:
        return jsonify({"error": "Invalid session"}), 403

    uid = user.uid

    for prefix, target_url in ROUTES.items():
        if request.path.startswith(prefix):
            service_url = target_url + request.path[len(prefix)-1:]
            break
    else:
        return jsonify({"error": "Unknown service!"}), 404

    headers = dict(request.headers)
    headers["X-User-Id"] = uid

    try:
        response = requests.request(
            method=request.method,
            url=service_url,
            headers=headers,
            params=request.args,
            json=request.get_json(silent=True)
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Service unavailable!", "detail": str(e)}), 502

    f_response = make_response(response.content, response.status_code)
    for name, value in response.headers.items():
        flask_response.headers[name] = value

    return f_response


app.config['SECRET_KEY'] = 'THE_MOST_SECRET_KEY_YOU_HAVE_EVER_SEEN'

db_session.global_init('db/JollyAuthDB.db')

app.run(port=5000, host='0.0.0.0')
