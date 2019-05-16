import random
import ctypes
import requests
import jinja2
import json
import os
import re


class Test:
    """
    Class for representing the whole test
    """
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
        """
        Initialixetion of the Test object
        :param title: title of the test
        """
        self.key = "".join([str(random.randrange(9)) for _ in range(16)])
        self._problems = []
        self.number_of_choices = 0
        self.title = title
        self.password = None

    def add_problem(self, problem):
        """
        (Test, Problem) -> None
        :param problem: object of class Problem that will be added to the test

        Add the problem to the test
        """
        self._problems.append(problem)

    def to_pdf(self, tmpdirname):
        """
        (Test) -> None
        Save test to pdf file
        """
        # create jinja environment
        LatexEnv = jinja2.Environment(
            block_start_string='\jbegin{',
            block_end_string='\jend}',
            variable_start_string='\jvar{',
            variable_end_string='}',
            comment_start_string='\#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            autoescape=False,
            loader=jinja2.FileSystemLoader(os.path.abspath('../templates/'))
        )

        # render LaTeX template
        boilerplate = LatexEnv.from_string(open('templates/boilerplate.tex').read())
        latex = boilerplate.render(test=self)
        with open(f"{tmpdirname}/ltx{self.key}.tex", 'w') as tempf:
            tempf.write(latex)

        # convert LaTeX file to PDF
        os.system(f'pdflatex -halt-on-error -output-directory {tmpdirname} ltx{self.key}.tex')

    def to_aiken(self):
        """
        (Test) -> str
        :return: test in aiken format
        """
        # TODO: implement this
        pass

    def to_json(self, path):
        """
        (Test, str) -> None
        Save test to .json file in given directory

        :param path: path of the directory to save file in
        """
        path = os.path.abspath(path)
        if not path.endswith("/"):
            path += "/"
        filename = self.key + "_" + self.title + ".json"
        with open(path + filename, 'w') as file:

            res = {"title": self.title}
            if self.password is None:
                res['password_required'] = False
            else:
                res['password_required'] = True
                res['password'] = self.password

            for i in range(len(self._problems)):
                problem_dict = self._problems[i].to_dict(i + 1)
                res[f'question_{i + 1}'] = problem_dict
            res = json.dumps(res, indent=4, ensure_ascii=False)

            file.write(res)

    @staticmethod
    def to_html(test_json):
        """
        (dict) -> str
        :param test_json: json object containing test description
        :return: html representation of the test
        """
        res = ""
        i = 1
        while "question_" + str(i) in test_json:
            current_question = test_json["question_" + str(i)]
            if current_question["kind"] == "multiple_choice":
                # if type of the question is multiple choice
                choices = []
                counter = 0
                for choice in current_question["choices"]:
                    choices.append(
                        Test.answer_option.format(choice, "answer_{}_{}".format(str(i), counter), "answer_" + str(i)))
                    counter += 1
                answer_area = "\n".join(choices)
            else:
                # if type of the question is written answer:
                answer_area = Test.written_answer_template.format("answer_" + str(i), "answer_" + str(i))
            res += Test.question_template.format(i, current_question["question"], current_question["task"],
                                                 answer_area)
            i += 1
        return res

    @classmethod
    def from_json(cls, json):
        """
        (class, dict) -> Test
        :param json: dict containing test representation
        :return: Test object built from that dict
        """
        test = Test()
        test.title = json["title"]
        for i in range(1, 51):
            if "question_" + str(i) not in json:
                break
            current_problem = json[f"question_{str(i)}"]
            current_problem.pop("id")
            current_problem["problem"] = current_problem["question"]
            current_problem.pop("question")
            if current_problem["kind"] == "multiple_choice":
                test._problems.append(Problem(**json["question_" + str(i)]))
            else:
                new_problem = {}
                for key in ["task", "kind"]:
                    new_problem[key] = current_problem[key]
                new_problem = Problem(**new_problem)
                new_problem.right_answers = set(current_problem["right_choice"])
                test._problems.append(new_problem)
        return test


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

    @staticmethod
    def mml2latex(mml):
        """
        (str) -> str
        :param mml: mml code in str representation
        :return: string of LaTeX code

        Convert string in MathML format to LaTeX format
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
    def replace_words(string):
        """
        (str) -> str
        :param string: string the words will be replaced in
        :return: string with replaced words

        Replace some words to avoid problem in test converting into different typrs
        """
        transcriber = {'&ExponentialE;': '&#x2147;', '&Integral;': '&#x222B;', '&DifferentialD;': '&#x2146;'}
        for symbol in transcriber:
            string = re.sub(symbol, transcriber[symbol], string)

        return string


class Problem:
    def __init__(self, problem="", task="", kind="", choices=(), right_answers=()):
        """
        (Problem, str, str, str, tuple. tuple)
        initialization method
        :param problem: Problem statement
        :param task: task to be solved
        :param kind: kind of the problem
        :param choices: available choices
        :param right_answers: right_answers for the problem
        """
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
        Change all MathML options to latex
        """
        self.task = Receiver.mml2latex(self.task).strip("$")
        for i in range(len(self.choices)):
            self.choices[i] = Receiver.mml2latex(self.choices[i]).strip("$")

    def to_dict(self, problem_id):
        """
        (Problem, int) -> dict
        :param problem_id: id of the current problem
        :return: dict representation of the current problem
        """

        # A better version of to_json() function.
        res = {key if key != 'problem' else 'question': self.__dict__[key] for key in self.__dict__}
        res["right_answers"] = tuple(res["right_answers"])
        res["choices"] = tuple(res["choices"])
        res['id'] = problem_id
        if self.kind == "written_answer":
            res['right_choice'] = self.right_answers.pop()
        else:
            res['right_answers'] = [str(answer) for answer in self.right_answers]
        # json.dumps(res, indent=4, ensure_ascii=False)
        return res

    def replace_conflicting_characters(self):
        """
        (Problem) -> None
        replace backslash in test with double backslash for avoiding conflicts with writing .json file
        """
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
