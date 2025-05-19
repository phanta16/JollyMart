import requests
from flask import Flask, request, make_response, render_template, url_for, redirect, flash, Response, \
    stream_with_context

app = Flask(__name__)
app.config['SECRET_KEY'] = 'THE_MOST_SECRET_KEY_YOU_HAVE_EVER_SEEN'


def is_authenticated(example: request) -> bool:
    headers = {
        'Cookie': f'session_id={example.cookies.get("session_id")}',
    }
    recp = requests.post('http://auth-service:5007/auth/is-exists', headers=headers).json()
    if recp['status'] != 'True':
        return False
    return True


@app.route('/register', methods=['POST', 'GET'])
def registration():
    if is_authenticated(request):
        return make_response(redirect(url_for('main')))
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


@app.route('/delete_comment/<comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))

    recp = requests.delete('http://auth-service:5007/comment/delete-comment', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }, json={
        "comment_id": comment_id
    }).json()
    if recp['status'] == 'True':
        post_id = recp['post_id']
        return make_response(redirect(url_for('post', post_id=post_id)))
    else:
        flash(recp['message'])
        return make_response(redirect(url_for('main')))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_authenticated(request):
        return make_response(redirect(url_for('main')))
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
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))

    user_data = requests.get('http://auth-service:5007/user/get-user', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }).json()
    posts_data = requests.get('http://auth-service:5007/posts/all-posts', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }).json()

    if len(posts_data) == 0:
        posts_data = None

    return render_template('index.html', current_user=user_data, posts=posts_data)


@app.route('/post/<post_id>', methods=['GET'])
def post(post_id):
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))

    recp = requests.get(f'http://auth-service:5007/posts/get-post/{post_id}', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }).json()
    recp_user = requests.get(f'http://auth-service:5007/user/get-user', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }).json()
    if recp['status'] != 'True':
        flash(recp['message'])
        return redirect(url_for('main'))
    return render_template('post.html', post=recp, current_user=recp_user)


@app.route('/add_comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))

    text = request.form['context']

    recp = requests.post('http://auth-service:5007/comment/new-comment', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }, json={
        'post_id': post_id,
        'context': text,
    }).json()
    if recp['status'] != 'True':
        flash(recp['message'])
        return redirect(url_for('post', post_id=post_id))
    return redirect(url_for('post', post_id=post_id))


@app.route('/toggle_favourite/<post_id>', methods=['POST'])
def toggle_favourite(post_id):
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))
    recp = requests.post('http://auth-service:5007/favourite/dispatch-favourite', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    },
                         json={'post_id': post_id}).json()
    flash('Успех!')
    return redirect(url_for('post', post_id=post_id, is_favorite=recp['stat']))


@app.route('/delete_post/<post_id>', methods=['POST'])
def delete_post(post_id):
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))

    recp = requests.post(f'http://auth-service:5007/posts/delete-post', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    },
                         json={'post_id': post_id}).json()
    if recp['status'] != 'True':
        flash(recp['message'])
        return redirect(url_for('main'))
    flash('Успех!')
    return redirect(url_for('main'))


@app.route('/user/<id>', methods=['GET'])
def profile(id):
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))
    recp = requests.get(f'http://auth-service:5007/user/users/{id}', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }).json()
    if not recp['status'] == 'True':
        flash(recp['message'])
        return redirect(url_for('main'))
    if recp['host']:
        host = True
    else:
        host = False
    return render_template('profile.html', user=recp, is_owner=host)


@app.route('/update_password', methods=['POST'])
def change_password():
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))

    new_password = request.form['password']
    data = {
        "new_password": new_password,
    }
    recp = requests.post('http://auth-service:5007/auth/change_password', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }, json=data).json()
    if recp['status'] != 'True':
        flash(recp['message'])
        return redirect(url_for('profile', id=recp['user_id']))
    flash('Успешно!')
    return redirect(url_for('profile', id=recp['user_id']))


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))

    requests.post('http://auth-service:5007/auth/delete_user', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }).json()
    flash('Всего доброго!')
    resp = make_response(redirect(url_for('registration')))
    resp.set_cookie("session_id", '', expires=0)
    return resp


@app.route('/update_email', methods=['POST'])
def change_email():
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))

    new_email = request.form['email']
    data = {
        "new_email": new_email,
    }
    recp = requests.post('http://auth-service:5007/auth/change_email', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }, json=data).json()
    if recp['status'] != 'True':
        flash(recp['message'])
        return redirect(url_for('profile', id=recp['user_id']))
    flash('Успешно!')
    return redirect(url_for('profile', id=recp['user_id']))


@app.route('/add-post', methods=['POST', 'GET'])
def add_post():
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))

    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']
        file = request.files.get('image')

        files = {
            "image": (file.filename, file.stream, file.content_type),
        }

        data = {
            'post_headers': title,
            'price': price,
            'text': description,
        }

        responce = requests.post('http://auth-service:5007/posts/add-post', data=data, files=files, headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    })

        if responce.json()['status'] == 'True':
            return render_template('add-post.html', success=True)
        else:
            flash(responce.json()['message'])
            return render_template('add-post.html')

    return render_template('add-post.html')


@app.route('/search', methods=['GET'])
def search():
    if not is_authenticated(request):
        return make_response(redirect(url_for('registration')))

    q = request.args.get('q')

    user_data = requests.get('http://auth-service:5007/user/get-user', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }).json()
    posts_data = requests.get(f'http://auth-service:5007/posts/search-post/{q}', headers={
        'Cookie': f'session_id={request.cookies.get("session_id")}',
    }).json()

    if len(posts_data) == 0:
        posts_data = None

    return render_template('index.html', current_user=user_data, posts=posts_data)


@app.route('/logout', methods=['GET'])
def logout():
    if not is_authenticated(request):
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
