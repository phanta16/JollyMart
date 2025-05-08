import requests
import base64
from flask import Flask, request, jsonify, make_response

import db_session
from model import PostsInfo

app = Flask(__name__)


@app.route('/posts/get-post', methods=['POST'])
def get_post():
    try:

        headers = dict(request.headers)

        session = db_session.create_session()
        reque = request.get_json()

        post_id = reque['post_id']

        post = session.query(PostsInfo).filter(PostsInfo.post_id == post_id).first()
        if post is None:
            return make_response(jsonify({"status": "False", "message": "Поста не существует!"}), 404)
        else:

            headers['X-User-Id'] = str(post.author_id)
            author = requests.post('http://user-service:5003/user/get-user', headers=headers).json()

            return make_response(jsonify({
                "status": "True",
                "post_id": post.post_id,
                "media": requests.post('http://media-service:5005/media/get-media-post', headers=headers, json={
                    "post_id": str(post.post_id)

                    ,
                }).json(),
                "text": post.text,
                "author": author,
                "date_created": post.date_created,
            }))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)

@app.route('/posts/get-posts', methods=['POST'])
def get_posts():
    try:
        result = []

        session = db_session.create_session()
        batch_session = request.get_json()

        for reque in batch_session:
            post = session.query(PostsInfo).filter(PostsInfo.post_id == reque['post_id']).first()
            if post is None:
                result.append({
                    "status": "False",
                    "message": "Объявления не существует!"
                })
            else:
                result.append({
                    "status": "True",
                    "post_id": post.post_id,
                    "header": post.post_headers,
                })

        return result

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)

@app.route('/posts/all-posts', methods=['POST'])
def all_posts():
    pass

@app.route('/posts/add-post', methods=['POST'])
def add_post():

    try:
        headers = dict(request.headers)

        session = db_session.create_session()
        reque = request.get_json()

        text = reque['text']
        post_headers = reque['post_headers']
        image = reque['image']
        image_name = reque['image_name']
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

        post = PostsInfo(text=text, author_id=author_id, post_headers=post_headers)
        session.add(post)
        session.commit()

        if image != '' and image_name != '':
            media_work = requests.post("http://media-service:5005/media/add-media-post", headers=headers, json={
                "filename": image_name,
                "image": image,
                "post_id": post.post_id,
            }).json()
            if not media_work["status"] == 'True':
                session.delete(post)
                session.commit()
                return make_response(jsonify({"status": "False", "message": media_work["message"]}))
            else:
                return make_response(jsonify({"status": "True", "post_id": post.post_id}))
        else:
            return make_response(jsonify({"status": "True", "post_id": post.post_id}))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)



@app.route('/posts/update-post', methods=['POST'])
def update_post():
    pass

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

            work = requests.post('http://media-service:5005/media/delete-media-post', headers=headers,
                          json={"post_id": post_id}).json()

            if work["status"] != "True":
                return make_response(jsonify({"status": "False", "message": work["message"]}), 404)

            session.delete(post)
            session.commit()

            return make_response(jsonify({"status": "True", }))
    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)


db_session.global_init('db/JollyPostsDB.db')
app.run(port=5009, host='0.0.0.0')
