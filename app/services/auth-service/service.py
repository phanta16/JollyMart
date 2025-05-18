import hashlib
import json
import secrets

import requests
from email_validator import validate_email, EmailNotValidError
from flask import jsonify, request, Flask, make_response, Request
from flask_cors import CORS

import db_session
from model import AuthInfo


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


def register(req_json:Request):
    try:

        session = db_session.create_session()
        file = req_json.files['image']

        files = {
            "image": (file.filename, file.stream, file.content_type),
        }

        username = req_json.form['username']
        hashed_password = req_json.form['password']
        email = req_json.form['email']
        session_id = secrets.token_hex(16)

        if check_data(hashed_password, email, username)["status"] != 'True':
            return make_response(
                jsonify({"status": "False", "message": check_data(hashed_password, email, username)["message"]}))

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
            responce.set_cookie('session_id', user.session_id)
            return responce
        else:
            session.delete(user)
            session.commit()
            return make_response(jsonify({'status': 'False', 'message': str(user_task["message"])}))

    except Exception as e:
        return make_response(jsonify({'status': 'False', 'message': str(e)}))


def login(reque:Request):
    try:

        req_json = reque.get_json()
        session = db_session.create_session()

        email = req_json.get('email')
        hashed_password = req_json.get('password')

        user = session.query(AuthInfo).filter(AuthInfo.email == email).first()

        if user is None:
            return make_response(jsonify({'message': 'Такого пользователя не существует!', 'status': 'False'}))
        else:
            if user.hashed_password == hashlib.sha512(hashed_password.encode('utf-8')).hexdigest():
                responce = make_response(jsonify({'status': 'True', 'session_id': user.session_id}), 200)
                responce.set_cookie('session_id', user.session_id, httponly=True)
                return responce
            else:
                return make_response(jsonify({'status': 'False', "message": "Неверный логин или пароль!"}), 401)

    except Exception as e:
        return make_response(jsonify({'status': 'False', 'message': str(e)}), 404)


def change_password(uid, new_password):
    try:

        session = db_session.create_session()

        if not check_data(new_password, 'example@gmail.com', 'XXXXXXXX'):
            return make_response(jsonify(
                {'status': 'False', 'message': check_data(new_password, 'АААААА@gmail.com', 'XXXXXXXX')["message"]}))

        new_hashed_password = hashlib.sha512(new_password.encode('utf-8')).hexdigest()

        user = session.get(AuthInfo, uid)
        user.hashed_password = new_hashed_password
        session.commit()

        return make_response(jsonify({'status': 'True', 'user_id': user.uid}), 200)

    except Exception as e:

        return make_response(jsonify({'status': 'False', 'message': str(e)}), 401)


def change_email(uid, new_email, headers):
    try:

        headers = dict(headers)

        session = db_session.create_session()

        if not check_data('example12345', new_email, 'XXXXXXXX'):
            return make_response(jsonify(
                {'status': 'False', 'message': check_data('example12345', new_email, 'XXXXXXXX')["message"]}))

        user_work = requests.patch('http://user-service:5003/user/change-email', headers=headers, json={
            "uid": uid,
            "new_mail": new_email,
        })

        if user_work.json()['status'] == 'True':
            user = session.get(AuthInfo, uid)
            user.email = new_email
            session.commit()

            return make_response(jsonify({'status': 'True', 'user_id': user.uid}), 200)
        else:
            return make_response(jsonify({"status": "False", "message": user_work.text}))

    except Exception as e:

        return make_response(jsonify({'status': 'False', 'message': str(e)}), 401)


def delete_user(uid, headers):
    try:

        session = db_session.create_session()

        headers = dict(headers)

        user_work = requests.delete('http://user-service:5003/user/delete-user', headers=headers, json={

            "uid": uid,
        })

        if user_work.json()['status'] == 'True':
            user = session.get(AuthInfo, uid)
            session.delete(user)
            session.commit()

            return make_response(jsonify({'status': 'True', 'user_id': user.uid}), 200)

        else:

            return make_response(jsonify({"status": "False", "message": user_work.text}))

    except Exception as e:

        return make_response(jsonify({'status': 'False', 'message': str(e)}), 401)


def existing_user(req_json:Request):
    try:
        session_id = req_json.cookies.get("session_id")

        if not session_id:
            return jsonify({"status": "False",
                            "message": "Non-authorized"}), 401

        session = db_session.create_session()
        user = session.query(AuthInfo).filter_by(session_id=session_id).first()
        if not user:
            return jsonify({"status": "False",
                            "message": "Invalid session"}), 401

        return jsonify({"status": "True", })

    except Exception as e:
        return make_response(jsonify({'status': 'False', 'message': str(e)}), 401)