import requests
from flask import Flask, request, make_response, render_template, url_for, redirect, flash, Response, \
    stream_with_context

app = Flask(__name__)
app.config['SECRET_KEY'] = 'THE_MOST_SECRET_KEY_YOU_HAVE_EVER_SEEN'


@app.route('/register', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        file = request.files.get('image')

        files = {
            "image": (file.filename, file.stream, file.content_type),
        }

        data = {
            'username': username,
            'email': email,
            'password': password
        }

        responce = requests.post('http://auth-service:5007/auth/register', data=data, files=files)

        if responce.json()['status'] == 'True':
            resp = make_response(redirect(url_for('main')))
            cookie = responce.cookies.get('session_id')
            resp.set_cookie("session_id", cookie, httponly=True, samesite='Lax', max_age=604800)
            return resp
        else:
            flash(responce.json()['message'])
            return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        data = {
            'email': email,
            'password': password
        }

        responce = requests.post('http://auth-service:5007/auth/login', json=data)

        if responce.json()['status'] == 'True':
            resp = make_response(redirect(url_for('main')))
            cookie = responce.cookies.get('session_id')
            resp.set_cookie("session_id", cookie, httponly=True, samesite='Lax', max_age=604800)
            return resp
        else:
            flash(responce.json()['message'])
            return render_template('login.html')

    return render_template('login.html')


@app.route('/', methods=['GET'])
def main():
    headers = {
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }
    recp = requests.post('http://auth-service:5007/auth/is-exists', headers=headers).json()
    if recp['status'] != 'True':
        return make_response(redirect(url_for('registration')))

    user_data = requests.get('http://auth-service:5007/user/get-user', headers=headers).json()
    posts_data = requests.get('http://auth-service:5007/posts/all-posts', headers=headers).json()

    if len(posts_data) == 0:
        posts_data = None

    return render_template('index.html', current_user=user_data, posts=posts_data)


@app.route('/chat/<chat_id>', methods=['GET'])
def chat(chat_id):
    pass


@app.route('/post/<post_id>', methods=['GET'])
def post(post_id):
    pass


@app.route('/profile', methods=['GET'])
def profile():
    pass


@app.route('/new-post', methods=['GET'])
def new_post():
    pass

@app.route('/search', methods=['GET'])
def search():
    headers = {
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }
    recp = requests.post('http://auth-service:5007/auth/is-exists', headers=headers).json()
    if recp['status'] != 'True':
        return make_response(redirect(url_for('registration')))

    q = request.args.get('q')

    user_data = requests.get('http://auth-service:5007/user/get-user', headers=headers).json()
    posts_data = requests.get(f'http://auth-service:5007/posts/search-post/{q}', headers=headers).json()

    if len(posts_data) == 0:
        posts_data = None

    return render_template('index.html', current_user=user_data, posts=posts_data)


@app.route('/logout', methods=['GET'])
def logout():
    headers = {
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }
    recp = requests.post('http://auth-service:5007/auth/is-exists', headers=headers).json()
    if recp['status'] != 'True':
        return make_response(redirect(url_for('registration')))
    resp = make_response(redirect(url_for('registration')))
    resp.set_cookie("session_id", '', expires=0)
    return resp


@app.route('/images/<filename>', methods=['GET'])
def media_proxy(filename):
    recp = requests.get(f'http://media-service:5005/media/images/{filename}', stream=True)

    return Response(
        stream_with_context(recp.iter_content(chunk_size=8192)),
        status=recp.status_code,
        headers=dict(recp.headers)
    )


app.run(port=5000, host='0.0.0.0')
