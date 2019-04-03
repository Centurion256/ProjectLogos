from flask import Flask, render_template, Markup
from my_modules.parse_test_file import questions_generator
import json
import os

app = Flask(__name__)


@app.route("/")
def main_page():
    return render_template("index.html")

@app.route("/donate")
def donate():
    return render_template("donate.html")

@app.route("/pass")
def test_pass():
    questions = Markup("".join(i for i in questions_generator("package.json")))
    return render_template("test.html", answer=questions)



if __name__ == "__main__":
    app.run(port=5000, debug=True)
