from app import app
from flask import render_template, request, jsonify, Blueprint

bp = Blueprint('main', __name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/filter')
def filter():
    return render_template('filter.html')
