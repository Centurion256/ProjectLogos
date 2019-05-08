import random
from flask import Flask, render_template, Markup, request, session
from my_modules.parse_test_file import questions_generator, questions_answer_generator
from my_modules.classes import Receiver, Problem, Test

app = Flask(__name__)
app.secret_key = "".join([str(random.randrange(9)) for _ in range(16)])


@app.route("/")
def main_page():
    print(session)
    if 'test_id' in session:
        test_id = session["test_id"]
        if 'success' in session:
            success = session.pop('success')
        else:
            success = False
        session.clear()
        if success:
            message = "Your test is successfully saved with id={}".format(test_id)
            return render_template("submission_result.html", success="success", message=message)
        return render_template("submission_result.html", success="fail", message="Something went wrong")
    session.clear()
    return render_template("index.html")


@app.route("/donate")
def donate():
    return render_template("donate.html")


@app.route("/pass")
def test_pass():
    files = open("static/tests/tests_list.txt").readlines()
    return render_template("tests_list.html", files=files)


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
    session.clear()
    test = Test()
    test.title = request.form['title']
    receiver = Receiver()
    session["success"] = True
    if len(request.form["title"]) > 50:
        session["message"] = "Too long title"
        session["success"] = False
    test.title = request.form["title"].lower().strip().strip("./,".replace("'", "").replace('"', "").replace(" ", '_'))
    for i in range(1, int(request.form["id"]) + 1):
        question = Problem()
        if "answer_" + str(i) in request.form:
            # if the type of answer is written answer
            question.kind = "written_answer"
            question.problem = request.form["question_" + str(i)]
            question.task = request.form["task_" + str(i)]
            question.right_answers = set(request.form["answer_" + str(i)])

        elif "select_topic_" + str(i) in request.form:
            # if the type of answer is random questionSS
            topic = request.form["select_topic_" + str(i)].lower().replace(" ", "-")
            subject = request.form["select_subject_" + str(i)].lower().replace(" ", "-")
            difficulty = request.form["select_difficulty_" + str(i)].lower()
            for j in range(5):
                # 5 because some tasks are got badly and raise mistake, but 5 to prevent
                # endless loop if mistake in arguments
                try:
                    if j == 4:
                        session.clear()
                        session["success"] = False
                        session["message"] = "Problems with retrieving random problem"
                        return render_template("submission_result.html", success="success", message="message")
                    problem = receiver.get_random_problem(topic, subject, difficulty)

                    problem.kind = "multiple_choice"
                    question = problem
                    break
                except Exception as error:
                    print(error)
                    continue
        else:
            # if the type is multiple choice
            question.kind = "multiple_choice"
            question.problem = request.form["question_" + str(i)]
            question.task = request.form["task_" + str(i)]
            question.right_answers = set(request.form["right_answer_" + str(i)])
            choices = []
            for j in range(1, 7):
                if "question_" + str(i) + "_" + str(j) in request.form:
                    choices.append(request.form["question_" + str(i) + "_" + str(j)])
                else:
                    break
            question.choices = tuple(choices)
        test.add_problem(question)
    session['test_id'] = test.key
    print(session)
    test.to_json("static/tests/")

    file = open("static/tests/tests_list.txt", "r")
    lines = file.readlines()
    lines.insert(0, test.key + "_" + test.title + "\n")
    file = open("static/tests/tests_list.txt", "w")
    file.writelines(lines)
    file.close()

    return render_template("submission_result.html", success="success", message="message")


@app.route("/submission")
def submission():
    # id = request.args.get('id')
    # print(id)
    return render_template("submission_result.html", success="success", message="message")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
