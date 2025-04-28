import hashlib
import secrets

from flask import jsonify, request, Flask, make_response
import requests

import db_session
from model import AuthInfo

app = Flask(__name__)


@app.route('/auth/register', methods=['POST'])

def register():
    try:
        session = db_session.create_session()
        req_json = request.get_json()

        hashed_password = req_json.get('password')
        email = req_json.get('email')
        session_id = secrets.token_hex(16)

        user = AuthInfo(session_id=session_id,
                        hashed_password=hashlib.sha512(hashed_password.encode('utf-8')).hexdigest(), email=email)
        session.add(user)
        session.commit()
        responce = make_response(jsonify({'status': 'True', 'session_id': user.session_id}), 200)
        responce.set_cookie('session_id', user.session_id, httponly=True)
        return responce
    except requests.exceptions.RequestException as e:
        return make_response(jsonify({'status': 'Something went wrong!', 'message': str(e)}), 404)


@app.route('/auth/login', methods=['POST'])
def login():
    try:
        session = db_session.create_session()
        req_json = request.get_json()

        email = req_json.get('email')
        hashed_password = req_json.get('password')

        user = session.query(AuthInfo).filter(AuthInfo.email == email).first()

        if user is None:
            return make_response(jsonify({'status': 'Такого пользователя не существует!'}))
        else:
            if user.hashed_password == hashlib.sha512(hashed_password.encode('utf-8')).hexdigest():
                responce = make_response(jsonify({'status': 'True', 'session_id': user.session_id}), 200)
                responce.set_cookie('session_id', user.session_id, httponly=True)
                return responce
            else:
                return make_response(jsonify({'status': 'False', "message": "Неверный пароль!"}), 401)
    except requests.exceptions.RequestException as e:
        return make_response(jsonify({'status': 'Something went wrong!', 'message': str(e)}), 404)


@app.route('/auth/change_password', methods=['PATCH'])
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

@app.route('/auth/change_email/', methods=['PATCH'])
def change_email():
    try:
        session = db_session.create_session()
        req_json = request.get_json()

        id = req_json.get('uid')
        new_email = req_json.get('new_email')

        user = session.get(AuthInfo, id)
        user.email = new_email
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

@app.route('/auth/validate_user/', methods=['POST'])
def validate_user():
    try:
        session = db_session.create_session()
        req_json = request.get_json()
        uid = req_json.get('uid')
        user = session.get(AuthInfo, uid)
        if user:
            return make_response(jsonify({'status': 'True'}), 200)
        else:
            return make_response(jsonify({'status': 'False'}), 200)

    except requests.exceptions.RequestException as e:

        return make_response(jsonify({'status': 'Unknown error!', 'message': str(e)}), 401)




ROUTES = {

    "/chat/": "http://chat-service:5001",
    "/comment/": "http://comment-service:5002",
    "/user/": "http://user-service:5003",
    "/favourite/": "http://favourite-service:5004",
    "/media/": "http://media-service:5005",
    "/notifications/": "http://notifications-service:5006",
    "/recommendations/": "http://recommendations-service:5007",
    "/search/": "http://search-service:5008",
    "/posts/": "http://posts-service:5009",
}

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def gateway(path):

    session_id = request.cookies.get("session_id")

    if not session_id:
        return jsonify({"error": "Non-authorized"
                                 ""}), 401

    session = db_session.create_session()
    user = session.query(AuthInfo).filter_by(session_id=session_id).first()
    if not user:
        return jsonify({"error": "Invalid session"})

    uid = user.uid

    for prefix, target_url in ROUTES.items():
        if request.path.startswith(prefix):
            service_url = target_url + prefix[:-1] + request.path[len(prefix)-1:]
            break
    else:
        return jsonify({"error": "Unknown service!"})

    headers = dict(request.headers)
    headers["X-User-Id"] = str(uid)

    try:
        response = requests.request(
            method=request.method,
            url=service_url,
            headers=headers,
            params=request.args,
            json=request.get_json(silent=True)
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Service unavailable!", "detail": str(e)})
    f_response = make_response(response.content, response.status_code)
    excluded = ['content-encoding', 'transfer-encoding', 'connection', 'content-length']
    for name, value in headers.items():
        if name not in excluded:
            f_response.headers[name] = value
    print(f_response.headers)

    return f_response


app.config['SECRET_KEY'] = 'THE_MOST_SECRET_KEY_YOU_HAVE_EVER_SEEN'

db_session.global_init('db/JollyAuthDB.db')

app.run(port=5000, host='0.0.0.0')
