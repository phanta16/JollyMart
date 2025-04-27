from flask import request, Flask, make_response, jsonify

import db_session
from model import CommentaryInfo

app = Flask(__name__)


@app.route('/comment/all-comments', methods=['POST'])
def all_comments():
    request_data = request.get_json()

    session = db_session.create_session()
    post_id = request_data['post_id']

    try:
        comments = session.query(CommentaryInfo).filter_by(post_id=post_id).all()
        return make_response(jsonify([{

            'comment_id': c.comment_id,
            'comment_author_id': c.comment_author_id,
            'post_id': c.post_id,
            'context': c.context,
            'datestamp': c.timestamp,

        }
            for c in comments]))
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


@app.route('/comment/new-comment', methods=['POST'])
def new_comment():
    try:
        request_data = request.get_json()

        session = db_session.create_session()
        post_id = request_data['post_id']
        comment_author_id = request_data['comment_author_id']
        context = request_data['context']

        comment = CommentaryInfo(comment_author_id=comment_author_id, post_id=post_id, context=context)
        session.add(comment)
        session.commit()
        return make_response(jsonify({"success": "True"}))

    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


@app.route('/comment/del-comment', methods=['DELETE'])
def delete_comment():
    request_data = request.get_json()

    session = db_session.create_session()
    post_id = request_data['post_id']
    comment_author_id = request_data['comment_author_id']
    context = request_data['context']

    try:
        comment = session.query(CommentaryInfo).filter_by(comment_author_id=comment_author_id, post_id=post_id,
                                                          context=context).first()
        session.delete(comment)
        session.commit()
        return make_response(jsonify({"success": "True"}))

    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


@app.route('/comment/change-comment', methods=['PATCH'])
def change_comment():
    request_data = request.get_json()

    session = db_session.create_session()
    post_id = request_data['post_id']
    comment_author_id = request_data['comment_author_id']
    context = request_data['context']
    new_context = request_data['new_context']

    try:
        comment = session.query(CommentaryInfo).filter_by(comment_author_id=comment_author_id, post_id=post_id,
                                                          context=context).first()
        comment.context = new_context
        session.commit()
        return make_response(jsonify({"success": "True"}))

    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


db_session.global_init('db/JollyCommentDB.db')
app.run(port=5002, host='0.0.0.0')
