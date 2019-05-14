import random, json
from flask import Flask, render_template, Markup, request, session, redirect, jsonify
from my_modules.parse_test_file import questions_generator, questions_answer_generator
from my_modules.classes import Receiver, Problem, Test
from hashlib import sha1

app = Flask(__name__)
app.secret_key = "".join([str(random.randrange(9)) for _ in range(16)])




@app.route("/temporary")
def temporary():
    return render_template("TEMPORARY.html")



@app.route("/")
def main_page():
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


@app.route("/test_results")
def test_result():
    # if "title" in session and "result_html" in session:
    return render_template("test_result.html", title=session["title"], results=Markup(session["results_html"]),
                           grade=session["grade"][0], tasks_num=session["grade"][1])
    # session.clear()
    # return redirect("/")


@app.route("/submit_test", methods=["POST"])
def submit_test():
    html_template = """<li>
                        <div class="question-res">{}</div>
                    <p class="task-res">$$ {} $$</p>
                    <span class="{}">Your answer is {}</span>
                    <p class="user-answer-res">Your answer is {}</p>
                    <p class="right-answer-res">Right answer was {}</p>
                    </li>
                    """
    grade = [0, 0]

    test_json = json.load(open("static/tests/" + request.form["filename"] + ".json"))
    res_html = ""
    for i in range(1, 51):
        if "question_" + str(i) not in test_json:
            continue
        grade[1] += 1
        current_question = test_json["question_" + str(i)]
        if current_question["kind"] == "multiple_choice":
            user_answers_keys = list(filter(lambda x: x.startswith("answer_" + str(i)), list(request.form.keys())))
            user_answers = [key[-1] for key in user_answers_keys]
            print(user_answers, len(user_answers))
            keys = list(request.form.keys())
            for right_choice in current_question["right_answers"]:
                if "answer_{}_{}".format(i, str(int(right_choice))).strip() not in keys:
                    print("\n\n")
                    print(keys)
                    print("answer_{}_{}".format(i, str(int(right_choice) + 1)).strip())
                    print("answer_{}_{}".format(i, str(int(right_choice) + 1)).strip() in keys)

                    print("Breaking because {} is not in form".format("answer_{}_{}".format(i, right_choice)))
                    break
            else:
                if len(user_answers) == len(current_question["right_answers"]):
                    grade[0] += 1
                    res_html += html_template.format(current_question["question"], current_question["task"],
                                                     "right", "right", 'number(s) ' + ", ".join(user_answers),
                                                     'number(s) ' + ", ".join(user_answers))
                    continue
            res_html += html_template.format(current_question["question"], current_question["task"],
                                             "wrong", "Wrong", 'number(s) ' + ", ".join(user_answers),
                                             'number(s) ' + ", ".join(current_question["right_answers"]))
        elif current_question["kind"] == "written_answer":
            if current_question["right_choice"] == request.form["answer_" + str(i)]:
                grade[0] += 1
                res_html += html_template.format(current_question["question"], current_question["task"],
                                                 "right", "right", "$$ " + current_question["right_choice"] + " $$",
                                                 "$$ " + current_question["right_choice"] + " $$")
            else:
                res_html += html_template.format(current_question["question"], current_question["task"],
                                                 "wrong", "wrong", "$$ " + request.form["answer_" + str(i)] + " $$",
                                                 current_question["right_choice"])

    session["results_html"] = res_html
    session["title"] = test_json["title"]
    session["grade"] = tuple(grade)
    return jsonify(dict(redirect='/test_results'))


@app.route("/pass_test")
def pass_test():
    if "filename" in request.args:
        filename = request.args.get('filename')
        session["filename"] = filename
    filename = session['filename']
    if "entered_password" not in session:
        session["entered_password"] = False
    test_json = json.load(open('static/tests/' + filename))
    session["current_test"] = filename
    if test_json["password_required"]:
        session["right_password"] = test_json["password"]
    if not test_json['password_required'] or session["entered_password"]:
        session.clear()
        return render_template("test.html", title=filename[:-5], test=Markup(Test.to_html(test_json)))
    return render_template("password_enter.html")


@app.route("/check_password", methods=['POST'])
def check_password():
    password = request.form['password']
    password = sha1(bytes(password, 'utf-8')).hexdigest()
    print(password, session["right_password"], password == session["right_password"])
    if password == session["right_password"]:
        session["entered_password"] = True
    print(session)
    return redirect("/pass_test")


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
    questions = Markup("".join(i for i in questions_answer_generator("package.json", answered)))
    return render_template("test.html", answer=questions, button=False)


@app.route("/create_test")
def test_creation():
    return render_template("test_creation.html")


@app.route("/creation_submission", methods=["POST"])
def creation_submission():
    try:
        session.clear()
        test = Test()
        test.title = request.form['title']
        receiver = Receiver()
        session["success"] = True
        if len(request.form["title"]) > 50:
            session["message"] = "Too long title"
            session["success"] = False
        test.title = request.form["title"].lower().strip().strip("./,").replace("'", "").replace('"', "").replace(" ",
                                                                                                                  '_')
        for i in range(1, int(request.form["id"]) + 1):
            question = Problem()
            if "answer_" + str(i) in request.form:
                # if the type of answer is written answer
                question.kind = "written_answer"
                question.problem = request.form["question_" + str(i)]
                question.task = request.form["task_" + str(i)]
                question.right_answers = set(request.form["answer_" + str(i)])

            elif "select_topic_" + str(i) in request.form:
                # if the type of answer is random question
                print("processing random question...")
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
                        print(question)
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
            question.replace_conflicting_characters()
            test.add_problem(question)
        session['test_id'] = test.key
        test.to_json("static/tests/")

        file = open("static/tests/tests_list.txt", "r")
        lines = file.readlines()
        lines.insert(0, test.key + "_" + test.title + "\n")
        file = open("static/tests/tests_list.txt", "w")
        file.writelines(lines)
        file.close()
    except Exception as err:
        print(err)

    return render_template("submission_result.html", success="success", message="message")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
