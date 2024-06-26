from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def hello():
    return "<p>Hello world</p>"

