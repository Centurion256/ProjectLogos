from latex2pdf import latex2pdf
from MathMl2LaTeX import mml2latex
import requests
import urllib.parse

def get_problem(area, topic, difficulty=None):
    """
    (str, str, int) -> dict
    :param area: area of the problem(e.g. 'algebra')
    :param topic: topic of the problem (e.g. 'linear-equations')
    :param difficulty: difficulty(1, 2, 3)
    :return: dict represantation of random problem
    """
    difficulties = {1:"beginner", 2: "intermediate", 3: "advanced"}
    basic_url = "https://math.ly/api/v1/"
    basic_url += area + "/" + topic + ".json"
    if difficulty:
        basic_url += "?difficulty=" + difficulties[difficulty]
    res = requests.get(basic_url).json()
    choices = [mml2latex(i.replace('<math>', '<math xmlns="http://www.w3.org/1998/Math/MathML">')) for i in res["choices"]]
    question = '<math xmlns="http://www.w3.org/1998/Math/MathML">' + res["question"] + '</math>'
    question = mml2latex(question)
    result = {'choices': choices, 'right_choice': res["correct_choice"],
              'question': question}
    return result
