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
        comments = session.query(CommentaryInfo).filter_by(post_id=post_id).order_by(
            CommentaryInfo.comment_id.asc()).all()

        return make_response(jsonify([{

            'comment_id': c.comment_id,
            'comment_author_id': c.comment_author_id,
            'post_id': c.post_id,
            'context': c.context,
            'datestamp': c.timestamp,
            'comment_author_username': c.comment_author_username,
            'comment_author_image': c.comment_author_image,
            'success': True,

        }
            for c in comments]))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 500)


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
        return make_response(jsonify({"status": "True",
                                      'success': True,
                                      'comment_author_id': comment.comment_author_id,
                                      'post_id': comment.post_id,
                                      'context': comment.context,
                                      'datestamp': comment.timestamp,
                                      'comment_author_username': comment.comment_author_username,
                                      'comment_author_image': comment.comment_author_image,
                                      }))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/comment/delete-comment', methods=['DELETE'])
def delete_comment():
    request_data = request.get_json()

    session = db_session.create_session()

    try:
        comment_id = request_data['comment_id']
        comment = session.query(CommentaryInfo).filter_by(comment_id=comment_id).first()
        post_id = comment.post_id
        session.delete(comment)
        session.commit()
        return make_response(jsonify({"status": "True", "post_id": post_id}))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}))


@app.route('/comment/post-deletion', methods=['POST'])
def post_deletion_protocol():
    try:
        reque = request.get_json()
        session = db_session.create_session()

        post_id = reque.get('post_id')

        comments = session.query(CommentaryInfo).filter(CommentaryInfo.post_id == post_id).all()

        for comment in comments:
            session.delete(comment)

        session.commit()

        return make_response(jsonify([{"status": "True"}]))

    except Exception as e:
        return make_response(jsonify({"status": "False", "message": str(e)}), 400)


db_session.global_init('db/JollyCommentDB.db')
