from flask import request, Flask, make_response, jsonify

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
        return make_response(jsonify([{

            'post_id': p.post_id,

        }
            for p in posts]))
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


@app.route('/favourite/new-favourite', methods=['POST'])
def new_favourite():
    try:
        request_data = request.get_json()

        session = db_session.create_session()
        post_id = request_data['post_id']
        user_id = request_data['user_id']

        rate = FavouriteInfo(author_id=user_id, post_id=post_id)
        if not session.query(FavouriteInfo).filter_by(author_id=user_id, post_id=post_id).all():
            session.add(rate)
            session.commit()
            return make_response(jsonify({"success": "True"}))
        else:
            return make_response(
                jsonify({"success": "False", "message": "You have already left favourite on this post!"}))

    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


db_session.global_init('db/JollyFavouriteDB.db')
app.run(port=5004, host='0.0.0.0')
