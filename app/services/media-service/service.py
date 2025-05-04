import base64
import os
import uuid

from flask import Flask, request, jsonify, make_response

import db_session
from model import MediaPostInfo, MediaUserInfo

app = Flask(__name__)
os.curdir = os.getcwd()

ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']

@app.route('/media/get-media-post', methods=['POST'])
def get_media_post():
    try:

        session = db_session.create_session()
        reque = request.json
        post_id = reque['post_id']

        filename = session.query(MediaPostInfo).filter(MediaPostInfo.post_id == post_id).first()
        if filename is None:
            return make_response(jsonify({"status": "False", "message": 'Несуществующий пост!'}))

        extension = filename.extension

        with open(f'posts/{filename.filename}', 'rb') as image:
            encoded_image = base64.b64encode(image.read())

        return make_response(jsonify({
            "filename": filename.filename,
            "type": extension,
            "media": encoded_image.decode()
        }))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/media/get-media-user', methods=['POST'])
def get_media_user():

    try:

        session = db_session.create_session()
        reque = request.json
        user_id = reque['user_id']

        filename = session.query(MediaUserInfo).filter(MediaUserInfo.user_id == user_id).first()
        if filename is None:
            return make_response(jsonify({"status": "False", "message": 'Несуществующий пользователь!'}))

        extension = filename.extension

        with open(f'avatars/{filename.filename}', 'rb') as image:
            encoded_image = base64.b64encode(image.read())

        return make_response(jsonify({
            "filename": filename.filename,
            "type": extension,
            "media": encoded_image.decode()
        }))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))

@app.route('/media/add-media-post', methods=['POST'])
def add_media_post():
    try:

        session = db_session.create_session()
        reque = request.json
        post_id = reque['post_id']
        name = reque['filename']

        if name.split('.')[-1] not in ALLOWED_EXTENSIONS:
            return make_response(jsonify({"status": "False", "message": "Неверный формат файла!"}))
        else:
            extension = name.split('.')[-1]

        filename = str(uuid.uuid4())

        with open(f'posts/{filename}', 'wb') as image:
            image.write(base64.b64decode(reque['image']))

        img = MediaPostInfo(image=base64.b64decode(reque['image']), post_id=post_id, extension=extension,
                            filename=str(filename))
        session.add(img)
        session.commit()

        return make_response(jsonify({"status": "True"}))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/media/add-media-user', methods=['POST'])
def add_media_user():
    try:

        session = db_session.create_session()
        reque = request.json
        user_id = reque['user_id']
        name = reque['filename']

        if name.split('.')[-1] not in ALLOWED_EXTENSIONS:
            return make_response(jsonify({"status": "False", "message": "Неверный формат файла!"}))
        else:
            extension = name.split('.')[-1]

        filename = str(uuid.uuid4())

        with open(f'avatars/{filename}', 'wb') as image:
            image.write(base64.b64decode(reque['image']))

        img = MediaUserInfo(image=base64.b64decode(reque['image']), user_id=user_id, extension=extension,
                            filename=filename)
        session.add(img)
        session.commit()

        return make_response(jsonify({"status": "True"}))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/media/delete-media-post', methods=['POST'])
def delete_media_post():
    try:
        session = db_session.create_session()

        reque = request.json
        post_id = reque['post_id']

        image = session.query(MediaPostInfo).filter(MediaPostInfo.post_id == post_id).first()

        if not image:
            return make_response(jsonify({"status": "False", "message": 'Несуществующий поcт!'}))

        os.remove(f'posts/{image.filename}')

        session.delete(image)
        session.commit()

        return make_response(jsonify({"status": "True"}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/media/delete-media-user', methods=['POST'])
def delete_media_user():
    try:
        session = db_session.create_session()

        reque = request.json
        user_id = reque['user_id']

        image = session.query(MediaUserInfo).filter(MediaUserInfo.user_id == user_id).first()

        if not image:
            return make_response(jsonify({"status": "False", "message": 'Несуществующий пользователь!'}))

        os.remove(f'avatars/{image.filename}')

        session.delete(image)
        session.commit()

        return make_response(jsonify({"status": "True"}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/media/set-image-user', methods=['POST'])
def set_avatar():
    try:
        session = db_session.create_session()

        reque = request.json
        user_id = reque['user_id']
        new_image = reque['new_image']
        name = reque['filename']

        if name.split('.')[-1] not in ALLOWED_EXTENSIONS:
            return make_response(jsonify({"status": "False", "message": "Неверный формат файла!"}))

        img = session.query(MediaUserInfo).filter(MediaUserInfo.user_id == user_id).first()
        if not img:
            return make_response(jsonify({"status": "False", "message": "Несуществующий пользователь!"}))

        with open(f'avatars/{img.filename}', 'wb') as image:
            image.write(base64.b64decode(new_image))

        img.image = base64.b64decode(new_image)
        session.commit()

        return make_response(jsonify({"status": "True"}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))

db_session.global_init('db/JollyMediaDB.db')
app.run(port=5005, host='0.0.0.0')
