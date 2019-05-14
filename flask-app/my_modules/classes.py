import random
import ctypes
import requests
import os
import re


class Test:
    question_template = """
    <li>
       <div class="question" id="{}">
           <h4>{}</h4>
               <p class="task">$$ {} $$</p>
               {}
       </div>
    </li>"""

    answer_option = """
    <label class="question-container">$$ {} $$
        <input type="checkbox" name="{}" id="{}">
        <span class="checkmark"></span>
    </label>
    """

    written_answer_template = """
    <span class="mathquill-form" id="{}"></span>
    <script>written_answers.push(MQ.MathField(document.getElementById("{}")));</script>
    """

    def __init__(self, title=""):
        self.key = "".join([str(random.randrange(9)) for _ in range(16)])
        self._problems = []
        self.number_of_choices = 0
        self.title = title
        self.password = None

    def add_problem(self, problem):
        self._problems.append(problem)

    def to_pdf(self):
        """
        (Test) -> None
        Save test to pdf file
        """
        pass

    def to_aiken(self):
        """
        (Test) -> str
        :return: test in aiken format
        """
        pass

    def to_json(self, path):
        """
        Save to json file in given path
        """
        path = os.path.abspath(path)
        if not path.endswith("/"):
            path += "/"
        filename = self.key + "_" + self.title + ".json"
        while filename in os.listdir(path):
            self.key = "".join([str(random.randrange(9)) for _ in range(16)])
            filename = self.key + "_" + self.title + ".json"
        with open(path + filename, 'w') as file:
            file.write("{\n")
            file.write('"title": "{}",\n'.format(self.title))
            if not self.password:
                file.write('"password_required": false,\n')
            else:
                file.write('"password_required": true,\n')
                file.write('"password": {},\n'.format(self.password))
            for i in range(len(self._problems)):
                file.write('"question_{}": '.format(i + 1) + self._problems[i].to_json(i + 1))
                if i != len(self._problems) - 1:
                    file.write(",\n")
            file.write("}")

    @staticmethod
    def to_html(test_json):
        res = ""
        i = 1
        while "question_" + str(i) in test_json:
            current_question = test_json["question_" + str(i)]
            if "choices" in current_question:
                # if type of the question is multiple choice
                choices = []
                counter = 0
                for choice in current_question["choices"]:
                    choices.append(Test.answer_option.format(choice, "answer_{}_{}".format(str(i), counter), "answer_" + str(i)))
                    counter += 1
                answer_area = "\n".join(choices)
            else:
                # if type of the question is written answer:
                answer_area = Test.written_answer_template.format("answer_" + str(i), "answer_" + str(i))
            res += Test.question_template.format(i, current_question["question"], current_question["task"],
                                                 answer_area)
            i += 1
        return res


class Receiver:
    def get_random_problem(self, area, topic, difficulty=None):
        """
        (str, str, str) -> Problem
        :param area: area of the problem(e.g. 'algebra')
        :param topic: topic of the problem (e.g. 'linear-equations')
        :param difficulty: difficulty(beginner, intermediate, advanced)
        :return: a Problem object of current problem
        """
        basic_url = "https://math.ly/api/v1/"
        basic_url += area + "/" + topic + ".json"
        if difficulty:
            basic_url += "?difficulty=" + difficulty
        res = requests.get(basic_url).json()
        choices = [i.replace('<math>', '<math xmlns="http://www.w3.org/1998/Math/MathML">') for i in res["choices"]]
        question = '<math xmlns="http://www.w3.org/1998/Math/MathML">' + res["question"] + '</math>'
        result = Problem(res['instruction'], question, "multiple_choice", choices, [res["correct_choice"]])
        result.to_latex()
        return result

    def get_problem_from_dict(self, problem):
        """
        (dict) -> Problem
        :param problem: dict representation of the poblem
        :return:Problem object
        """
        pass

    @staticmethod
    def mml2latex(mml):
        """
        (str) -> str
        :param mml: mml code in str representation
        :return: string of LaTeX code
        """
        prefix = """
        <!DOCTYPE mml:math 
        PUBLIC "-//W3C//DTD MathML 2.0//EN"
               "http://www.w3.org/Math/DTD/mathml2/mathml2.dtd" [
        <!ENTITY % MATHML.prefixed "INCLUDE">
        <!ENTITY % MATHML.prefix "mml">
    ]>
    <math xmlns="http://www.w3.org/1998/Math/MathML"
    xsi="http://www.w3.org/2001/XMLSchema-instance"
    schemaLocation="http://www.w3.org/1998/Math/MathML
        http://www.w3.org/Math/XMLSchema/mathml2/mathml2.xsd"> 
        """
        # <math xmlns="http://www.w3.org/1998/Math/MathML">
        file = open("tmp.mml", "w", encoding='utf-8')
        if re.match("<math.*?>.+?</math>", mml) is None:

            mml = '<math xmlns="http://www.w3.org/1998/Math/MathML">{}</math>'.format(mml)
        else:

            mml = re.sub('<math.*?>', '<math xmlns="http://www.w3.org/1998/Math/MathML">', mml)

        # mml = mml.replace('&Integral;', '&#x222B;').replace('&DifferentialD;', '&#x2146;')
        reorganized = Receiver.replace_words(mml)
        print(reorganized, file=file)
        file.close()
        prompt = "xsltproc static/xsl/mmltex.xsl " + "tmp.mml"
        return os.popen(prompt).read()

    @staticmethod
    def replace_words(strin):
        transcriber = {'&ExponentialE;': '&#x2147;', '&Integral;': '&#x222B;', '&DifferentialD;': '&#x2146;'}
        for symbol in transcriber:
            strin = re.sub(symbol, transcriber[symbol], strin)

        return strin


class Problem:
    def __init__(self, problem="", task="", kind="", choices=(), right_answers=()):
        self.right_answers = set(right_answers)
        self.problem = problem
        self.task = task
        self.kind = kind
        self.answer_amount = len(choices)
        self.choices = ctypes.py_object * self.answer_amount
        self.choices = self.choices()
        for i in range(self.answer_amount):
            self.choices[i] = choices[i]

    def to_latex(self):
        """
        Change all mathml options to latex
        """
        self.task = Receiver.mml2latex(self.task).strip("$")
        for i in range(len(self.choices)):
            self.choices[i] = Receiver.mml2latex(self.choices[i]).strip("$")

    def to_json(self, problem_id):
        res = '{\n' + \
              '"id": {},\n'.format('"' + str(problem_id) + '"') + \
              '"question": {},\n'.format('"' + self.problem + '"') + \
              '"task": {},\n'.format('"' + self.task + '"') + \
              '"kind": {},\n'.format('"' + self.kind + '"')

        if self.kind == "written_answer":
            res += '"right_choice": {}\n'.format('"' + self.right_answers.pop() + '"')
        elif self.kind == "multiple_choice":
            res += '"choices": [\n' + ",\n".join(['"' + choice + '"' for choice in self.choices]) + "],\n"
            res += '"right_answers": [\n' + ",\n".join(
                ['"' + str(answer) + '"' for answer in self.right_answers]) + "]\n"
        return res + "\n}"

    def replace_conflicting_characters(self):
        self.task = self.task.replace("\\", "\\\\")
        choices = ctypes.py_object * len(self.choices)
        choices = choices()
        for i in range(len(self.choices)):
            if isinstance(self.choices[i], str):
                choices[i] = self.choices[i].replace("\\", "\\\\")
            else:
                choices[i] = self.choices[i]

        answers = set()
        for answer in self.right_answers:
            if isinstance(answer, str):
                answers.add(answer.replace("\\", "\\\\"))
            else:
                answers.add(answer)
        self.right_answers = answers
        self.choices = choices
