import db_session
from model import AuthInfo

from flask_cors import CORS
import requests
import json

from flask import jsonify, request, Flask, make_response

from service import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'THE_MOST_SECRET_KEY_YOU_HAVE_EVER_SEEN'

ROUTES = {

    "/comment/": "http://comment-service:5002",
    "/user/": "http://user-service:5003",
    "/favourite/": "http://favourite-service:5004",
    "/media/": "http://media-service:5005",
    "/posts/": "http://posts-service:5009",
}


@app.before_request
def gateway():
    session_id = request.cookies.get("session_id")

    if request.path == "/auth/register":
        return register(request)

    if request.path == "/auth/login":
        return login(request)

    if request.path == "/auth/is-exists":
        return existing_user(request)

    if not session_id:
        return jsonify({"status": "False",
                        "message": "Non-authorized"}), 401

    session = db_session.create_session()
    user = session.query(AuthInfo).filter_by(session_id=session_id).first()
    if not user:
        return jsonify({"status": "False",
                        "message": "Invalid session"}), 401

    uid = user.uid

    if request.path == "/auth/change_email":
        recp = request.get_json()
        new_email = recp.get('new_email')
        headers = request.headers
        return change_email(uid, new_email, headers)

    if request.path == "/auth/change_password":
        recp = request.get_json()
        new_password = recp.get('new_password')
        headers = request.headers
        return change_password(uid, new_password, headers)

    if request.path == "/auth/delete_user":
        headers = request.headers
        return delete_user(uid, headers)

    for prefix, target_url in ROUTES.items():
        if request.path.startswith(prefix):
            service_url = target_url + prefix[:-1] + request.path[len(prefix) - 1:]
            break
    else:
        return jsonify({"status": "False", "message": "Unknown route!"})

    headers = {k: v for k, v in request.headers if k.lower() not in [
        'host', 'connection', 'content-length', 'keep-alive',
        'proxy-authenticate', 'proxy-authorization', 'te',
        'trailers', 'transfer-encoding', 'upgrade'
    ]}

    headers["X-User-Id"] = str(uid)

    if request.content_type == 'application/json':
        try:
            response = requests.request(
                method=request.method,
                url=service_url,
                headers=headers,
                params=request.args,
                json=request.get_json(silent=True)
            )
        except requests.exceptions.RequestException:
            return jsonify({"status": "False", "message": "Service is unavailable!"})
        f_response = make_response(response.content, response.status_code)
        excluded = [
            'host', 'connection', 'content-length', 'keep-alive',
            'proxy-authenticate', 'proxy-authorization', 'te',
            'trailers', 'transfer-encoding', 'upgrade'
        ]
        for name, value in headers.items():
            if name.lower() not in excluded:
                f_response.headers[name] = value

        return f_response

    if request.content_type == 'multipart/form-data':
        headers = {k: v for k, v in request.headers if k.lower() not in [
            'host', 'connection', 'content-length', 'keep-alive',
            'proxy-authenticate', 'proxy-authorization', 'te',
            'trailers', 'transfer-encoding', 'upgrade', 'content-type'
        ]}
        files = {
            key: (file.filename, file.stream, file.content_type)
            for key, file in request.files.items()
        }
        try:
            response = requests.request(
                method=request.method,
                url=service_url,
                headers=headers,
                data=request.form,
                params=request.args,
                files=files,
            )
        except requests.exceptions.RequestException:
            return jsonify({"status": "False", "message": "Service is unavailable!"})

        f_response = make_response(response.content, response.status_code)
        excluded = ['content-encoding', 'transfer-encoding', 'connection']
        for name, value in headers.items():
            if name.lower() not in excluded:
                f_response.headers[name] = value

        return f_response

    try:
        response = requests.request(
            method=request.method,
            url=service_url,
            headers=headers,
            params=request.args,
            data=request.get_data()
        )
    except requests.exceptions.RequestException:
        return jsonify({"status": "False", "message": "Service is unavailable!"})
    f_response = make_response(response.content, response.status_code)
    excluded = [
        'host', 'connection', 'content-length', 'keep-alive',
        'proxy-authenticate', 'proxy-authorization', 'te',
        'trailers', 'transfer-encoding', 'upgrade'
    ]
    for name, value in headers.items():
        if name.lower() not in excluded:
            f_response.headers[name] = value

    return f_response

db_session.global_init('db/JollyAuthDB.db')