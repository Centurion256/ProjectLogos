import random
import json
import tempfile
from flask import Flask, render_template, Markup, request, session, redirect, jsonify, send_file
from my_modules.classes import Receiver, Problem, Test
from hashlib import sha1

app = Flask(__name__)
app.secret_key = "".join([str(random.randrange(9)) for _ in range(16)])


@app.route("/")
def main_page():
    session.clear()
    return render_template("index.html")


@app.route("/download_pdf/<filename>")
def download_pdf(filename):
    if "../" in filename:
        return render_template("error.html", error="You cannot access other directories, little hacker")
    test_json = json.load(open("static/tests/" + filename + ".json"))
    test = Test.from_json(test_json)
    print("Creating temp file")
    with tempfile.TemporaryDirectory() as tmpdirname:
        print(tmpdirname)
        print("EKFEKKEKEF")
        test.to_pdf(tmpdirname)
        return send_file(f"{tmpdirname}/ltx{test.key}.pdf")


@app.route("/test_results")
def test_result():
    if "title" not in session or "results_html" not in session:
        session.clear()
        return render_template("error.html", error="Ooops... something went wrong")
    return render_template("test_result.html", title=session["title"], results=Markup(session["results_html"]),
                           grade=session["grade"][0], tasks_num=session["grade"][1])


@app.route("/submit_test", methods=["POST"])
def submit_test():
    # submitting the test after passing it
    html_template = """<li>
                        <div class="question-res">{}</div>
                    <p class="task-res">$$ {} $$</p>
                    <span class="{}">Your answer is {}</span>
                    <p class="user-answer-res">Your answer is {}</p>
                    <p class="right-answer-res">Right answer was {}</p>
                    </li>
                    """
    grade = [0, 0]

    # load file for comparing right answers and users ones
    test_json = json.load(open("static/tests/" + request.form["filename"] + ".json"))
    res_html = ""

    # try to check all the possible questions
    for i in range(1, 51):
        if "question_" + str(i) not in test_json:
            continue
        grade[1] += 1
        current_question = test_json["question_" + str(i)]
        if current_question["kind"] == "multiple_choice":
            # get user answers for the test
            user_answers_keys = list(filter(lambda x: x.startswith("answer_" + str(i)), list(request.form.keys())))
            user_answers = [key[-1] for key in user_answers_keys]

            keys = list(request.form.keys())
            for right_choice in current_question["right_answers"]:
                if "answer_{}_{}".format(i, str(int(right_choice))).strip() not in keys:
                    # break if there are some wrongly answered questions
                    break
            else:
                if len(user_answers) == len(current_question["right_answers"]):
                    # if all the right answers are chosen and no more ones
                    grade[0] += 1
                    res_html += html_template.format(current_question["question"], current_question["task"],
                                                     "right", "right", 'number(s) ' + ", ".join(user_answers),
                                                     'number(s) ' + ", ".join(user_answers))
                    continue
            res_html += html_template.format(current_question["question"], current_question["task"],
                                             "wrong", "wrong", 'number(s) ' + ", ".join(user_answers),
                                             'number(s) ' + ", ".join(current_question["right_answers"]))

        elif current_question["kind"] == "written_answer":
            # simply check if right answer and users one are equal
            # TODO: add more complicated check whether two answers are equal
            if current_question["right_choice"].strip() == request.form["answer_" + str(i)].strip():
                grade[0] += 1
                res_html += html_template.format(current_question["question"], current_question["task"],
                                                 "right", "right", "$$ " + current_question["right_choice"] + " $$",
                                                 "$$ " + current_question["right_choice"] + " $$")
            else:
                res_html += html_template.format(current_question["question"], current_question["task"],
                                                 "wrong", "wrong", "$$ " + request.form["answer_" + str(i)] + " $$",
                                                 current_question["right_choice"])

    # write test results to session to remember them
    session["results_html"] = res_html
    session["title"] = test_json["title"]
    session["grade"] = tuple(grade)
    return jsonify(dict(redirect='/test_results'))


@app.route("/pass_test")
def pass_test():
    # check if filename is now passed with arguments ans set it to the one from session if no
    if "filename" in request.args:
        filename = request.args.get('filename')
        session["filename"] = filename
    filename = session['filename']

    # if user have not entered the password
    if "entered_password" not in session:
        session["entered_password"] = False
    test_json = json.load(open('static/tests/' + filename))
    session["current_test"] = filename
    if test_json["password_required"]:
        session["right_password"] = test_json["password"]

    # return a form for entering password if it is required and is not submitted yet
    if not test_json['password_required'] or session["entered_password"]:
        session.clear()
        return render_template("test.html", title=filename[:-5], test=Markup(Test.to_html(test_json)))
    return render_template("password_enter.html")


@app.route("/check_password", methods=['POST'])
def check_password():
    password = request.form['password']
    password = sha1(bytes(password, 'utf-8')).hexdigest()
    if password == session["right_password"]:
        session["entered_password"] = True
    return redirect("/pass_test")


@app.route("/donate")
def donate():
    return render_template("donate.html")


@app.route("/pass")
def test_pass():
    files = open("static/tests/tests_list.txt").readlines()
    return render_template("tests_list.html", files=files)


@app.route("/search_test", methods=['POST', 'GET'])
def search_test():
    if request.method == 'POST':
        files = open("static/tests/tests_list.txt").readlines()
        search_string = request.form["test_name"]
        found_files = list(filter(lambda x: search_string in x, files))
        return render_template("tests_list.html", files=found_files)
    else:
        return redirect("/pass")


@app.route("/create_test")
def test_creation():
    return render_template("test_creation.html")


@app.route("/creation_submission", methods=["POST"])
def creation_submission():
    session.clear()

    # create net Test and Receiver objects
    test = Test()
    test.title = request.form['title']
    receiver = Receiver()

    # check if title is right
    if len(request.form["title"]) > 50:
        return render_template("error.html", error="Title too long")
    test.title = request.form["title"].lower().strip().strip("./,").replace("'", "").replace('"', "").replace(" ",
                                                                                                              '_')

    if "password_input" in request.form:
        test.password = sha1(bytes(request.form["password_input"], 'utf-8')).hexdigest()

    # iterate through all the passed questions
    for i in range(1, int(request.form["id"]) + 1):
        question = Problem()
        if "answer_" + str(i) in request.form:
            # if the type of answer is written answer
            question.kind = "written_answer"
            question.problem = request.form["question_" + str(i)]
            question.task = request.form["task_" + str(i)]
            question.right_answers = {request.form["answer_" + str(i)]}

        elif "select_topic_" + str(i) in request.form:
            # if the type of answer is random question
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
            question.right_answers = {int((request.form["right_answer_" + str(i)])) - 1}
            choices = []
            for j in range(1, 7):
                if "question_" + str(i) + "_" + str(j) in request.form:
                    choices.append(request.form["question_" + str(i) + "_" + str(j)])
                else:
                    break
            question.choices = tuple(choices)
        # question.replace_conflicting_characters()
        test.add_problem(question)

    # save the test id to the session and save the test to json file
    test.to_json("static/tests/")

    # save the name of the json file to tests_list.txt where names of all the present tests are stored
    file = open("static/tests/tests_list.txt", "r")
    lines = file.readlines()
    lines.insert(0, test.key + "_" + test.title + "\n")
    file = open("static/tests/tests_list.txt", "w")
    file.writelines(lines)
    file.close()

    return render_template("index.html")


# @app.errorhandler(Exception)
# def all_exception_handler(error):
#     print(error)
#     return redirect("/")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
