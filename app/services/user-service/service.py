import requests
from email_validator import validate_email, EmailNotValidError
from flask import Flask, request, jsonify, make_response

import db_session
from model import UserInfo

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
    if session.query(UserInfo).filter(
            (UserInfo.email == email) | (UserInfo.username == username)
    ) is not None:
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


@app.route('/user/get-user', methods=['POST'])
def get_user():
    try:

        headers = dict(request.headers)

        session = db_session.create_session()
        req = request.get_json()

        uid = req['uid']

        user = session.query(UserInfo).filter(UserInfo.uid == uid).first()

        if user is None:
            return jsonify({"status": "False", "message": "Пользователя не существует!"})

        favourites = requests.post("http://favourite-service:5004/favourite/all-favourites",
                                   data={"user_id": uid}, headers=headers).json()

        return make_response(jsonify({"uid": uid,
                                      "username": user.username,
                                      "email": user.email,
                                      "date_joined": user.date_joined,
                                      "favourite": favourites,
                                      }), 200)
    except Exception as e:
        return jsonify({"status": "False", "message": str(e)})


@app.route('/user/add-user', methods=['POST'])
def add_user():
    try:

        headers = dict(request.headers)

        session = db_session.create_session()
        req = request.get_json()

        password = req['password']
        email = req['email']
        username = req['username']

        if check_data(password, email, username)["status"] == "True":
            auth_operation = requests.post("http://auth-service:5000/auth/register",
                                           data={"password": password, "email": email}, headers=headers).json()

            if auth_operation["status"] == "True":
                uid = auth_operation["uid"]

                user = UserInfo(uid=uid, username=username, email=email)
                session.add(user)
                session.commit()

                return jsonify({"status": "True", })

            else:
                return jsonify({"status": "False", "message": auth_operation["message"]})
        else:
            return jsonify({"status": "False", "message": check_data(password, email, username)["message"]})
    except Exception as e:
        return jsonify({"status": "False", "message": str(e)})


@app.route('/user/patch-email', methods=['PATCH'])
def patch_email():
    try:

        headers = dict(request.headers)

        session = db_session.create_session()
        req = request.get_json()

        uid = req['uid']
        new_mail = req['new_mail']

        user = session.query(UserInfo).filter(UserInfo.uid == uid).first()

        if user is None:
            return jsonify({"status": "False", "message": "Пользователя не существует!"})

        auth_operation = requests.post("http://auth-service:5000/auth/change_email",
                                       data={"uid": uid, "new_mail": new_mail}, headers=headers).json()

        if auth_operation["status"] == "True":
            return jsonify({"status": "True"})

        else:
            return jsonify({"status": "False", "message": auth_operation["message"]})


    except Exception as e:
        return jsonify({"status": "False", "message": str(e)})


@app.route('/user/patch-password', methods=['PATCH'])
def patch_password():
    headers = dict(request.headers)

    try:
        session = db_session.create_session()
        req = request.get_json()

        uid = req['uid']
        new_password = req['new_mail']

        user = session.query(UserInfo).filter(UserInfo.uid == uid).first()

        if user is None:
            return jsonify({"status": "False", "message": "Пользователя не существует!"})

        auth_operation = requests.post("http://auth-service:5000/auth/change_password",
                                       data={"uid": uid, "new_mail": new_password}, headers=headers).json()

        if auth_operation["status"] == "True":
            return jsonify({"status": "True"})

        else:
            return jsonify({"status": "False", "message": auth_operation["message"]})


    except Exception as e:
        return jsonify({"status": "False", "message": str(e)})


@app.route('/user/delete-user', methods=['DELETE'])
def delete_user():
    try:

        headers = dict(request.headers)

        session = db_session.create_session()
        req = request.get_json()

        uid = req['uid']

        user = session.query(UserInfo).filter(UserInfo.uid == uid).first()

        if user is None:
            return jsonify({"status": "False", "message": "Пользователя не существует!"})

        auth_operation = requests.post("http://auth-service:5000/auth/delete_user",
                                       data={"uid": uid}, headers=headers).json()

        if auth_operation["status"] == "True":
            session.delete(user)
            session.commit()
            return jsonify({"status": "True"})

        else:
            return jsonify({"status": "False", "message": auth_operation["message"]})

    except Exception as e:
        return jsonify({"status": "False", "message": str(e)})


db_session.global_init('db/JollyUserDB.db')
app.run(port=5003, host='0.0.0.0')
