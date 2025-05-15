from flask import request, Flask, make_response, jsonify
import requests
import os

import db_session
from model import FavouriteInfo

app = Flask(__name__)


@app.route('/favourite/all-favourites', methods=['POST'])
def favourite_all():
    request_data = request.get_json()

    session = db_session.create_session()
    try:
        user_id = request_data['user_id']
        posts = session.query(FavouriteInfo).filter_by(author_id=user_id).all()

        return make_response(jsonify([{"status": "True",
                                      "post_header": p.post_header,
                                      "post_image": p.post_image,
                                      "post_id": p.post_id}
                                       for p in posts]), 200)

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}, 400))

@app.route('/favourite/delete-post', methods=['POST'])
def favourite_deletion_protocol():
    try:
        reque = request.get_json()
        session = db_session.create_session()

        post_id = reque.get('post_id')

        favs = session.query(FavouriteInfo).filter(FavouriteInfo.post_id == post_id).all()

        for fav in favs:
            session.delete(fav)

        session.commit()

        return make_response(jsonify({"status": "True"}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)

@app.route('/favourite/dispatch-favourite', methods=['POST'])
def favourite():
    try:
        headers = dict(request.headers)

        request_data = request.get_json()

        session = db_session.create_session()
        post_id = request_data['post_id']
        user_id = str(request.headers['X-User-Id'])

        if not session.query(FavouriteInfo).filter(
                (FavouriteInfo.post_id == post_id) & (FavouriteInfo.author_id == user_id)).first():
            return new_favourite(post_id, user_id, headers)
        else:
            return delete_favourite(post_id, user_id)
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}, 400))



def new_favourite(post_id, user_id, headers):
    try:

        session = db_session.create_session()

        post_info = requests.get(f'http://posts-service:5009/posts/get-post/{post_id}', headers=headers).json()
        if post_info['status'] == 'True':
            rate = FavouriteInfo(author_id=user_id, post_id=post_id, post_header=post_info['post_header'],
                                 post_image=post_info['media_url'])
            if not session.query(FavouriteInfo).filter_by(author_id=user_id, post_id=post_id).all():
                session.add(rate)
                session.commit()
                return make_response(jsonify({"status": "True", "stat": True, "post_id": post_id}))
            else:
                return make_response(
                    jsonify({"status": "False", "message": "Непредвиденная ошибка!"}))
        else:
            return make_response(
                jsonify({"status": "False", "message": post_info['message']}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}, 400))


def delete_favourite(post_id, user_id):
    try:

        session = db_session.create_session()

        rate = session.query(FavouriteInfo).filter_by(author_id=user_id, post_id=post_id).first()
        if not session.query(FavouriteInfo).filter_by(author_id=user_id, post_id=post_id).first():
            return make_response(jsonify({"status": "False", "message": "Непредвиденная ошибка!"}))
        else:
            session.delete(rate)
            session.commit()
            return make_response(
                jsonify({"status": "True", "stat": False, "post_id": post_id}))

    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


db_session.global_init('db/JollyFavouriteDB.db')
