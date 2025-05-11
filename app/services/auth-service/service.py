import hashlib
import json
import secrets

import requests
from email_validator import validate_email, EmailNotValidError
from flask import jsonify, request, Flask, make_response

import db_session
from model import AuthInfo

app = Flask(__name__)


def check_data(password, email, username):
    check_flag = False

    if len(password) < 8:
        return {"status": "False", "message": "Пароль должен быть как минимум 8 символов!"}

    for letter in password:
        if letter.isdigit():
            check_flag = True
            break
        if letter.isupper():
            check_flag = True
            break
    if not check_flag:
        return {"status": "False", "message": "Пароль должен содержать в себе минимум 1 заглавную букву, и одну цифру!"}

    session = db_session.create_session()
    if session.query(AuthInfo).filter(
            AuthInfo.email == email,
    ).first() is not None:
        return {"status": "False", "message": "Пользователь уже существует!"}

    if 3 > len(username):
        return {"status": "False", "message": "Недопустимое имя пользователя! Минимальная длина имени 3 символа!"}

    if len(username) > 15:
        return {"status": "False", "message": "Недопустимое имя пользователя! Максимальная длина имени 15 символов!"}

    if ' ' in username:
        return {"status": "False",
                "message": "Недопустимое имя пользователя! Имя пользователя не может содержать пробелы!"}

    try:
        validate_email(email, check_deliverability=True)


    except EmailNotValidError:
        return {"status": "False", "message": 'E-mail недействителен!'}

    return {"status": "True", }


@app.route('/auth/register', methods=['POST'])
def register():
    try:

        session = db_session.create_session()

        username = request.form['username']
        hashed_password = request.form['password']
        email = request.form['email']
        session_id = secrets.token_hex(16)
        file = request.files.get('image')

        if check_data(hashed_password, email, username)["status"] != 'True':
            return make_response(
                jsonify({"status": "False", "message": check_data(hashed_password, email, username)["message"]}))
        elif file is None:
            return make_response(
                jsonify({"status": "True"}))

        files = {
            "image": (file.filename, file.stream, file.content_type),
                }

        user = AuthInfo(session_id=session_id,
                        hashed_password=hashlib.sha512(hashed_password.encode('utf-8')).hexdigest(), email=email)
        session.add(user)
        session.commit()

        user_id = session.query(AuthInfo).filter_by(email=email).first()

        metadata = {'username': username,
                    'email': email,
                    'uid': user_id.uid}

        user_task = requests.post('http://user-service:5003/user/add-user',
                                  data={"metadata": json.dumps(metadata)}, files=files).json()

        if user_task['status'] == 'True':
            responce = make_response(jsonify({'status': 'True', }), 200)
            responce.set_cookie('session_id', user.session_id, httponly=True)
            return responce
        else:
            session.delete(user)
            session.commit()
            return make_response(jsonify({'status': 'False', 'message': str(user_task["message"])}))

    except Exception as e:
        return make_response(jsonify({'status': 'False', 'message': str(e)}))


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

    except Exception as e:
        return make_response(jsonify({'status': 'False', 'message': str(e)}), 404)


def change_password(uid, new_password, headers):
    try:

        session = db_session.create_session()

        id = uid
        new_password = new_password

        if not check_data(new_password, 'example@gmail.com', 'XXXXXXXX'):
            return make_response(jsonify(
                {'status': 'False', 'message': check_data(new_password, 'АААААА@gmail.com', 'XXXXXXXX')["message"]}))

        new_hashed_password = hashlib.sha512(new_password.encode('utf-8')).hexdigest()

        user = session.get(AuthInfo, id)
        user.hashed_password = new_hashed_password
        session.commit()

        return make_response(jsonify({'status': 'True'}), 200)

    except Exception as e:

        return make_response(jsonify({'status': 'False', 'message': str(e)}), 401)


def change_email(uid, new_email, headers):
    try:

        headers = dict(headers)

        session = db_session.create_session()

        id = uid
        new_email = new_email

        if not check_data('example12345', new_email, 'XXXXXXXX'):
            return make_response(jsonify(
                {'status': 'False', 'message': check_data('example12345', new_email, 'XXXXXXXX')["message"]}))

        user_work = requests.patch('http://user-service:5003/user/change-email', headers=headers, json={
            "uid": id,
            "new_mail": new_email,

        })

        if user_work.json()['status'] == 'True':
            user = session.get(AuthInfo, id)
            user.email = new_email
            session.commit()

            return make_response(jsonify({'status': 'True'}), 200)
        else:
            return make_response(jsonify({"status": "False", "message": user_work.text}))

    except Exception as e:

        return make_response(jsonify({'status': 'False', 'message': str(e)}), 401)


def delete_user(uid, headers):
    try:

        session = db_session.create_session()
        uid = uid

        headers = dict(headers)

        user_work = requests.delete('http://user-service:5003/user/delete-user', headers=headers, json={

            "uid": uid,
        })

        if user_work.json()['status'] == 'True':
            user = session.get(AuthInfo, uid)
            session.delete(user)
            session.commit()

            return make_response(jsonify({'status': 'True'}), 200)

        else:

            return make_response(jsonify({"status": "False", "message": user_work.text}))

    except Exception as e:

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
            return make_response(jsonify({'status': 'False', 'message': 'Неавторизованный пользователь!'}), 200)

    except Exception as e:

        return make_response(jsonify({'status': 'False', 'message': str(e)}), 401)


ROUTES = {

    "/chat/": "http://chat-service:5001",
    "/comment/": "http://comment-service:5002",
    "/user/": "http://user-service:5003",
    "/favourite/": "http://favourite-service:5004",
    "/media/": "http://media-service:5005",
    "/posts/": "http://posts-service:5009",
}


@app.before_request
def gateway():
    session_id = request.cookies.get("session_id")

    if request.path == "/auth/register" or request.path == "/auth/login":
        return

    if not session_id:
        return jsonify({"error": "Non-authorized"
                                 ""}), 401

    session = db_session.create_session()
    user = session.query(AuthInfo).filter_by(session_id=session_id).first()
    if not user:
        return jsonify({"error": "Invalid session"})

    uid = user.uid

    if request.path == "/auth/change_email":
        recp = request.get_json()
        new_email = recp.get('new_email')
        headers = request.headers
        return change_email(uid, new_email, headers)

    if request.path == "/auth/change_password":
        recp = request.get_json()
        new_password = recp.get('new_password')
        headers = request.headers
        return change_password(uid, new_password, headers)

    if request.path == "/auth/delete_user":
        headers = request.headers
        return delete_user(uid, headers)

    for prefix, target_url in ROUTES.items():
        if request.path.startswith(prefix):
            service_url = target_url + prefix[:-1] + request.path[len(prefix) - 1:]
            break
    else:
        return jsonify({"error": "Unknown service!"})

    headers = {k: v for k, v in request.headers if k.lower() not in [
        'host', 'connection', 'content-length', 'keep-alive',
        'proxy-authenticate', 'proxy-authorization', 'te',
        'trailers', 'transfer-encoding', 'upgrade'
    ]}

    headers["X-User-Id"] = str(uid)

    if request.content_type == 'application/json':
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
        excluded = [
            'host', 'connection', 'content-length', 'keep-alive',
            'proxy-authenticate', 'proxy-authorization', 'te',
            'trailers', 'transfer-encoding', 'upgrade'
        ]
        for name, value in headers.items():
            if name.lower() not in excluded:
                f_response.headers[name] = value

        return f_response


    if request.content_type == 'multipart/form-data':
        headers = {k: v for k, v in request.headers if k.lower() not in [
            'host', 'connection', 'content-length', 'keep-alive',
            'proxy-authenticate', 'proxy-authorization', 'te',
            'trailers', 'transfer-encoding', 'upgrade', 'content-type'
        ]}
        files = {
            key: (file.filename, file.stream, file.content_type)
            for key, file in request.files.items()
        }
        try:
            response = requests.request(
                method=request.method,
                url=service_url,
                headers=headers,
                data=request.form,
                params=request.args,
                files=files,
            )
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Service unavailable!", "detail": str(e)})

        f_response = make_response(response.content, response.status_code)
        excluded = ['content-encoding', 'transfer-encoding', 'connection']
        for name, value in headers.items():
            if name.lower() not in excluded:
                f_response.headers[name] = value

        return f_response

    try:
        response = requests.request(
            method=request.method,
            url=service_url,
            headers=headers,
            params=request.args,
            data=request.get_data()
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Service unavailable!", "detail": str(e)})
    f_response = make_response(response.content, response.status_code)
    excluded = [
        'host', 'connection', 'content-length', 'keep-alive',
        'proxy-authenticate', 'proxy-authorization', 'te',
        'trailers', 'transfer-encoding', 'upgrade'
                ]
    for name, value in headers.items():
        if name.lower() not in excluded:
            f_response.headers[name] = value

    return f_response


app.config['SECRET_KEY'] = 'THE_MOST_SECRET_KEY_YOU_HAVE_EVER_SEEN'

db_session.global_init('db/JollyAuthDB.db')

app.run(port=5000, host='0.0.0.0')
