import sys

from flask import Flask, render_template, request, redirect, Response
import json

app = Flask(__name__, static_folder="static")

@app.route('/')
def output():
    # serve index template
    return render_template('index.html', name='Joe')

@app.route('/receiver', methods = ['POST'])
def worker():
    # read json + reply
    data = request.get_json(force=True)
    with open("res.json", "w") as f:
        json.dump(data, f)
    return render_template("index.html")

if __name__ == '__main__':
    # run!
    app.run(debug=True)