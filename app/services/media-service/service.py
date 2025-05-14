import os
import uuid

from flask import Flask, request, jsonify, make_response, send_from_directory

import db_session
from model import MediaInfo

app = Flask(__name__)
os.curdir = os.getcwd()

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

@app.route('/media/images/<filename>', methods=['GET'])
def get_images(filename):
    try:

        session = db_session.create_session()

        file = session.query(MediaInfo).filter(MediaInfo.filename == filename).first()
        if file is None:
            return make_response(jsonify({"status": "False", "message": 'Несуществующее изображение!'}))

        return send_from_directory('images', filename)

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/media/add-image', methods=['POST'])
def add_media():
    try:

        file = request.files['image']
        session = db_session.create_session()

        if 'image' not in request.files:
            return make_response(jsonify({"status": "False", "message": "Файл пуст!"}))

        if str(file.filename).split('.')[-1] not in ALLOWED_EXTENSIONS:
            return make_response(jsonify({"status": "False", "message": "Неверный формат файла!"}))
        else:
            extension = str(file.filename).split('.')[-1]

        filename = str(uuid.uuid4())

        file.save(os.path.join('images', filename))

        image = MediaInfo(filename=filename, extension=extension, path=os.path.join('images', filename))
        session.add(image)
        session.commit()

        return make_response(jsonify({"status": "True",
                                      "filename": filename}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/media/delete-image/<filename>', methods=['POST'])
def delete_media(filename):
    try:
        session = db_session.create_session()

        image = session.query(MediaInfo).filter(MediaInfo.filename == filename).first()

        if not image:
            return make_response(jsonify({"status": "False", "message": 'Несуществующее изображение!'}))

        os.remove(f'images/{filename}')

        session.delete(image)
        session.commit()

        return make_response(jsonify({"status": "True"}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/media/set-image/<filename>', methods=['POST'])
def set_avatar(filename):
    try:

        file = request.files['image']
        if 'image' not in request.files:
            return make_response(jsonify({"status": "False", "message": "Файл пуст!"}))

        if str(file.filename).split('.')[-1] not in ALLOWED_EXTENSIONS:
            return make_response(jsonify({"status": "False", "message": "Неверный формат файла!"}))

        os.remove(f'images/{filename}')
        file.save(os.path.join('images', filename))

        return make_response(jsonify({"status": "True",}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))

db_session.global_init('db/JollyMediaDB.db')