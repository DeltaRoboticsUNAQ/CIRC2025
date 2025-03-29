from flask import Flask, Response, jsonify
import random

app = Flask(__name__)

def generate():
    yield jsonify({"random": random.random()})

@app.route('/')
def index():
    return 

@app.route('/stream')
def streamed_response():
    return Response(generate())

if __name__ == '__main__':
    app.run(debug=True)