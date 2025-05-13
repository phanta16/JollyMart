import os
from importlib.metadata import pass_none

import rapidfuzz
import requests
from flask import Flask, request, jsonify, make_response

import db_session
from model import PostsInfo

app = Flask(__name__)


@app.route('/posts/get-post/<post_id>', methods=['GET'])
def get_post(post_id):
    try:

        headers = dict(request.headers)

        session = db_session.create_session()

        post = session.query(PostsInfo).filter(PostsInfo.post_id == post_id).first()
        if post is None:
            return make_response(jsonify({"status": "False", "message": "Поста не существует!"}), 404)
        else:
            comment_work = requests.post("http://comment-service:5002/comment/all-comments",
                                         json={"post_id": post.post_id}, headers=headers)
            if comment_work.status_code != 200:
                return make_response(jsonify({"status": "False", "message": 'Непредвиденная ошибка!'}))

            host = 'True' if str(headers['X-User-Id']) == post.author_id else 'False'

            return make_response(jsonify({
                "status": "True",
                "post_id": post.post_id,
                "post_header": post.post_headers,
                "media_url": os.path.join('images', post.image_name),
                "host": host,
                "text": post.text,
                "author_username": post.author_username,
                "author_image": post.author_image,
                "date_created": post.date_created,
                "comments": comment_work.json()
            }))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)


@app.route('/posts/all-posts', methods=['GET'])
def all_posts():
    try:

        session = db_session.create_session()
        posts = session.query(PostsInfo).all()

        if not posts:
            return make_response(jsonify({"status": 'True', "message": "No posts!"}))

        return make_response(jsonify([{
            "post_id": post.post_id,
            "date_created": post.date_created,
            "author_id": post.author_id,
            "author_username": post.author_username,
            "author_image": post.author_image,
            "text": post.text,
            "image_path": os.path.join('images', post.image_name),
            "post_headers": post.post_headers,

        } for post in posts]))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)


@app.route('/posts/add-post', methods=['POST'])
def add_post():
    try:
        headers = dict(request.headers)
        session = db_session.create_session()
        reque = dict(request.form)
        text = reque['text']
        post_headers = reque['post_headers']

        files = {
            key: (file.filename, file.stream, file.content_type)
            for key, file in request.files.items()
        }

        author_id = request.headers.get('X-User-Id')

        if text == '':
            return make_response(jsonify({
                "status": "False",
                "message": "Вы не можете оставить пустое объявление!"
            }))

        if post_headers == '':
            return make_response(jsonify({
                "status": "False",
                "message": "Вы не можете оставить название объявления пустым!"
            }))

        user_work = requests.get('http://user-service:5003/user/get-user', headers=headers).json()
        if not user_work["status"] == 'True':
            return make_response(jsonify({"status": "False", "message": user_work["message"]}))

        media_work = requests.post("http://media-service:5005/media/add-image", files=files).json()
        if not media_work["status"] == 'True':
            return make_response(jsonify({"status": "False", "message": media_work["message"]}))

        post = PostsInfo(text=text, author_id=author_id, post_headers=post_headers,
                         image_name=media_work["filename"], author_username=user_work["username"],
                         author_image=user_work["avatar_path"])
        session.add(post)
        session.commit()
        return make_response(jsonify({"status": "True", "post_id": post.post_id}))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)


@app.route('/posts/search-post/<post_name>', methods=['POST'])
def search_post(post_name):
    try:

        session = db_session.create_session()

        posts = session.query(PostsInfo).all()

        score = [(pre, rapidfuzz.fuzz.ratio(post_name, pre.post_headers)) for pre in posts if
                 rapidfuzz.fuzz.ratio(post_name,
                                      pre.post_headers) > 70]

        return make_response(jsonify([{
                                          "post_id": post[0].post_id,
                                          "date_created": post[0].date_created,
                                          "author_id": post[0].author_id,
                                          "author_username": post[0].author_username,
                                          "author_image": post[0].author_image,
                                          "text": post[0].text,
                                          "image_name": post[0].image_name,
                                          "post_headers": post[0].post_headers,

                                      } for post in score[:10]]))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)


@app.route('/posts/delete-post', methods=['POST'])
def delete_post():
    try:

        headers = dict(request.headers)

        session = db_session.create_session()
        reque = request.get_json()

        post_id = reque['post_id']
        post = session.query(PostsInfo).filter(PostsInfo.post_id == post_id).first()

        if post is None:
            return make_response(jsonify({"status": "False", "message": "Поста не существует!"}), 404)
        else:
            work = requests.post(f'http://media-service:5005/media/delete-image/{post.image_name}',
                                 headers=headers).json()

            if work["status"] != "True":
                return make_response(jsonify({"status": "False", "message": work["message"]}), 404)

            session.delete(post)
            session.commit()

            return make_response(jsonify({"status": "True", }))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)


db_session.global_init('db/JollyPostsDB.db')
app.run(port=5009, host='0.0.0.0')
