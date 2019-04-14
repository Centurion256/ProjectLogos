import json
from my_modules.templates import make_question, make_solved


def questions_generator(filename):
    """
    (str) -> Markup()
    :param filename:
    :return:
    """
    file = open("static/" + filename, "r").read()
    file_json = json.loads(file)
    for question in file_json:
        if question in ["name", "version", "dependencies"]:
            continue
        id = file_json[question]["id"]
        variants = file_json[question]["choices"]
        title = file_json[question]["instruction"]
        task = file_json[question]["question"]
        yield make_question(id, title, task, variants)


def questions_answer_generator(filename, answered_variants):
    file = open("static/" + filename, "r").read()
    file_json = json.loads(file)
    for question in file_json:
        if question in ["name", "version", "dependencies"]:
            continue
        id = file_json[question]["id"]
        if id in answered_variants:
            answered = answered_variants[id]
        else:
            answered = []
        right_variants = [int(file_json[question]["correct_choice"])]
        variants = file_json[question]["choices"]
        title = file_json[question]["instruction"]
        task = file_json[question]["question"]
        yield make_solved(title, task, variants, right_variants, answered)
