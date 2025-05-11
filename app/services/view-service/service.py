from flask import Flask, request, jsonify, make_response, render_template, url_for, redirect, flash
import requests

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
            resp.set_cookie("session_id", cookie)
            return resp
        else:
            flash(responce.json()['message'])
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET'])
def login():
    pass

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('base.html')

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

app.run()