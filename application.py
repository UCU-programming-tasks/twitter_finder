"""Module with main routes of the application"""
from flask import Flask, render_template, request
from map_creation import main as create_map

app = Flask(__name__)


@app.route('/')
def index():
    """
    The main page with a form to enter a username.
    """
    return render_template('index.html')


@app.route('/map', methods=['POST'])
def register():
    """
    Page with a map of Twitter friends of the specified user.
    """
    username = request.form.get('username')

    return create_map(username)


app.run(debug=True, port=3000)
