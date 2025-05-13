import json
import os

import requests
from flask import Flask, request, jsonify, make_response

import db_session
from model import UserInfo

app = Flask(__name__)

@app.route('/user/get-user', methods=['GET'])
def get_user():
    try:

        session = db_session.create_session()

        uid = request.headers.get('X-User-Id')

        user = session.query(UserInfo).filter(UserInfo.uid == uid).first()

        if user is None:
            return jsonify({"status": "False", "message": "Пользователя не существует!"})

        favourites = requests.post("http://favourite-service:5004/favourite/all-favourites",
                                   json={"user_id": uid})

        if not favourites.status_code == 200:
            return make_response(jsonify({"status": "False", "message": favourites.json()["message"]}))

        return make_response(jsonify({"uid": uid,
                                            "username": user.username,
                                            "email": user.email,
                                            "date_joined": user.date_joined,
                                            "favourite": favourites.json(),
                                            "avatar_path": os.path.join('images', user.avatar),
                                            "status": 'True',
                                            }), 200)
    except Exception as e:
        return jsonify({"status": "False", "message": str(e)})

@app.route('/user/users/<uid>', methods=['GET'])
def get_user_by_id(uid):
    try:

        session = db_session.create_session()

        cur_id = request.headers.get('X-User-Id')
        host = True if cur_id == uid else False

        user = session.query(UserInfo).filter(UserInfo.uid == uid).first()

        if user is None:
            return jsonify({"status": "False", "message": "Пользователя не существует!"})

        favourites = requests.post("http://favourite-service:5004/favourite/all-favourites",
                                   json={"user_id": uid})

        posts = requests.get("http://posts-service:5009/posts/get-posts",
                                   json={"user_id": uid})

        if not favourites.status_code == 200:
            return make_response(jsonify({"status": "False", "message": favourites.json()["message"]}))

        if not posts.status_code == 200:
            return make_response(jsonify({"status": "False", "message": posts.json()["message"]}))

        return make_response(jsonify({"uid": uid,
                                      "username": user.username,
                                      "email": user.email,
                                      "date_joined": user.date_joined,
                                      "favourite": favourites.json(),
                                      "avatar_path": os.path.join('images', user.avatar),
                                      "status": 'True',
                                      "posts": posts.json(),
                                      "host": host,
                                      }), 200)
    except Exception as e:
        return jsonify({"status": "False", "message": str(e)})

@app.route('/user/add-user', methods=['POST'])
def add_user():
    try:

        session = db_session.create_session()
        metadata = json.loads(request.form.get('metadata'))
        username = metadata['username']
        email = metadata['email']
        uid = metadata['uid']
        file = request.files.get('image')

        if request.files.get('image') is None:
            return make_response(jsonify({"status": "False", "message": "Пожалуйста, выберите аватар!"}))

        files = {
            "image": (file.filename, file.stream, file.content_type),
                }

        image = requests.post("http://media-service:5005/media/add-image",
                              files=files).json()

        if not image["status"] == 'True':
            return make_response(jsonify({"status": "False", "message": image["message"]}))

        user = UserInfo(username=username, email=email, uid=uid, avatar=image["filename"])
        session.add(user)
        session.commit()

        return make_response(jsonify({"status": "True"}))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))

@app.route('/user/set-avatar', methods=['POST'])
def set_avatar():
    try:
        session = db_session.create_session()
        user_id = request.form['user_id']

        user = session.query(UserInfo).filter(UserInfo.uid == user_id).first()
        if user is None:
            return jsonify({"status": "False", "message": "Пользователя не существует!"})

        file = request.files.get('image')

        if request.files.get('image') is None:
            return make_response(jsonify({"status": "False", "message": "Пожалуйста, выберите картинку!"}))

        files = {
            "image": (file.filename, file.stream, file.content_type),
        }

        image = requests.post(f"http://media-service:5005/media/set-image/{user.avatar}",
                          files=files).json()

        if not image["status"] == 'True':
            return make_response(jsonify({"status": "False", "message": image["message"]}))

        return make_response(jsonify({"status": "True", "user_id": user_id}))

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

        req = requests.post(f"http://media-service:5005/media/delete-image/{user.avatar}", headers=headers).json()

        if req["status"] == "True":

            session.delete(user)
            session.commit()

        else:
            return jsonify({"status": "False", "message": req["message"]})

        return jsonify({"status": "True"})

    except Exception as e:
        return jsonify({"status": "False", "message": str(e)})


db_session.global_init('db/JollyUserDB.db')
app.run(port=5003, host='0.0.0.0')
