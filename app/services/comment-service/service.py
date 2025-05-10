import requests
from flask import request, Flask, make_response, jsonify

import db_session
from model import CommentaryInfo

app = Flask(__name__)


@app.route('/comment/all-comments', methods=['POST'])
def all_comments():
    request_data = request.get_json()

    session = db_session.create_session()

    try:
        post_id = request_data['post_id']
        comments = session.query(CommentaryInfo).filter_by(post_id=post_id).all()
        return make_response(jsonify([{

            'comment_id': c.comment_id,
            'comment_author_id': c.comment_author_id,
            'post_id': c.post_id,
            'context': c.context,
            'datestamp': c.timestamp,
            'comment_author_username': c.comment_author_username,
            'comment_author_image': c.comment_author_image,

        }
            for c in comments]))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/comment/new-comment', methods=['POST'])
def new_comment():
    try:
        request_data = request.get_json()
        headers = dict(request.headers)

        session = db_session.create_session()
        post_id = request_data['post_id']
        comment_author_id = headers.get('X-User-Id')
        context = request_data['context']

        user_work = requests.get('http://user-service:5003/user/get-user', headers=headers).json()
        if not user_work["status"] == 'True':
            return make_response(jsonify({"status": "False", "message": user_work["message"]}))

        comment = CommentaryInfo(comment_author_id=comment_author_id, post_id=post_id, context=context,
                                 comment_author_username=user_work["username"],
                                 comment_author_image=user_work["avatar_path"])
        session.add(comment)
        session.commit()
        return make_response(jsonify({"status": "True"}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/comment/delete-comment', methods=['DELETE'])
def delete_comment():
    request_data = request.get_json()

    session = db_session.create_session()

    try:
        post_id = request_data['post_id']
        comment_author_id = request_data['comment_author_id']
        timestamp = request_data['timestamp']
        comment = session.query(CommentaryInfo).filter_by(comment_author_id=comment_author_id, post_id=post_id,
                                                          context=timestamp).first()
        session.delete(comment)
        session.commit()
        return make_response(jsonify({"status": "True"}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/comment/change-comment', methods=['PATCH'])
def change_comment():
    request_data = request.get_json()

    session = db_session.create_session()

    try:
        post_id = request_data['post_id']
        comment_author_id = request_data['comment_author_id']
        timestamp = request_data['timestamp']
        new_context = request_data['new_context']
        comment = session.query(CommentaryInfo).filter_by(comment_author_id=comment_author_id, post_id=post_id,
                                                          context=timestamp).first()
        comment.context = new_context
        session.commit()
        return make_response(jsonify({"status": "True"}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


db_session.global_init('db/JollyCommentDB.db')
app.run(port=5002, host='0.0.0.0')
