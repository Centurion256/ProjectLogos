from flask import Flask, render_template, Markup, request
from my_modules.parse_test_file import questions_generator, questions_answer_generator
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
    return render_template("test.html", answer=questions, button=True)

@app.route("/submit_test", methods=["POST"])
def submitting():
    form = request.form.keys()
    answered = {}
    for i in form:
        answer = i.split("-")
        if int(answer[0]) in answered:
            answered[int(answer[0])].append(int(answer[1]))
        else:
            answered[int(answer[0])] = [int(answer[1])]
    questions = ""
    answer_num = 0
    questions = Markup("".join(i for i in questions_answer_generator("package.json", answered)))
    return render_template("test.html", answer=questions, button=False)

@app.route("/create_test")
def test_creation():
    return render_template("test_creation.html")

@app.route("/creation_submission", methods=["POST"])
def creation_submission():
    for key in request.form:
        print(key, request.form[key])
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
