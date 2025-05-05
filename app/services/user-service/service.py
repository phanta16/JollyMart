import requests
from flask import Flask, request, jsonify, make_response

import db_session
from model import UserInfo

app = Flask(__name__)

@app.route('/user/get-user', methods=['POST'])
def get_user():
    try:

        headers = dict(request.headers)

        session = db_session.create_session()

        uid = request.headers.get('X-User-Id')

        user = session.query(UserInfo).filter(UserInfo.uid == uid).first()

        if user is None:
            return jsonify({"status": "False", "message": "Пользователя не существует!"})

        favourites = requests.post("http://favourite-service:5004/favourite/all-favourites",
                                   json={"user_id": uid}, headers=headers)

        image = requests.post("http://media-service:5005/media/get-media-user", json={"user_id": uid},
                              headers=headers).json()

        if not image["status"] == 'True':
            return make_response(jsonify({"status": "False", "message": image["message"]}))

        if not favourites.status_code == 200:
            return make_response(jsonify({"status": "False", "message": favourites.json()["message"]}))

        return make_response(jsonify({"uid": uid,
                                      "username": user.username,
                                      "email": user.email,
                                      "date_joined": user.date_joined,
                                      "favourite": favourites.json(),
                                      "avatar": image
                                      }), 200)
    except Exception as e:
        return jsonify({"status": "False", "message": str(e)})


@app.route('/user/add-user', methods=['POST'])
def add_user():
    try:

        headers = dict(request.headers)

        session = db_session.create_session()
        req = request.get_json()
        email = req['email']
        username = req['username']
        uid = req["uid"]

        image = requests.post("http://media-service:5005/media/add-media-user",
                              json={"user_id": uid, "filename": "standart_avatar.jpg"},
                              headers=headers).json()

        if not image["status"] == 'True':
            return make_response(jsonify({"status": "False", "message": image["message"]}))

        user = UserInfo(username=username, email=email, uid=uid)
        session.add(user)
        session.commit()

        return make_response(jsonify({"status": "True"}))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/user/change-email', methods=['PATCH'])
def patch_email():
    try:

        session = db_session.create_session()
        req = request.get_json()

        uid = req['uid']
        new_mail = req['new_mail']

        user = session.query(UserInfo).filter(UserInfo.uid == uid).first()

        if user is None:
            return jsonify({"status": "False", "message": "Пользователя не существует!"})

        user.email = new_mail
        session.commit()
        return jsonify({"status": "True", })

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

        req = requests.post("http://media-service:5005/media/delete-media-user", data={"user_id": uid},
                            headers=headers).json()

        if req["status"] == "True":

            session.delete(user)
            session.commit()

        else:
            return jsonify({"status": "False", "message": req["message"]})

        return jsonify({"status": "True", })

    except Exception as e:
        return jsonify({"status": "False", "message": str(e)})


db_session.global_init('db/JollyUserDB.db')
app.run(port=5003, host='0.0.0.0')
