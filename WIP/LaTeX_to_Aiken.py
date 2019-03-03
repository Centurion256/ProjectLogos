import ProblemReceiver
from Problem_reformat import Problem
import json
from pprint import pprint

def to_Aiken():
    
    while True:
        resp = ProblemReceiver.GetProblem('calculus', 'trigonometric-differentiation', 'advanced')
        #js_obj = json.load(resp)
        question = Problem(resp)
        if question.question == '' or (question.question in checks) or 'exception' in question.question or any('exception' in y for y in (x for x in question.choices)):
            continue
        break
    checks.add(question.question)
    #print(checks)
    template_header = "{} {}\n".format(question.text, question.question)
    template_body = ''
    for i in range(len(question.choices)):

        template_body += "{}) {}\n".format(chr(65+i), question.choices[i])
    
    template_answer = "ANSWER: {}\n\n".format(chr(65 + int(question.correct)))
    
    return template_header + template_body + template_answer 


if __name__ == "__main__":

    checks = set()
    #pprint(to_Aiken())    
    amount = int(input("Please enter the amount of problems you wish to generate: "))
    with open('Trigonometric Differentiation.txt', 'w') as f:
        for question in range(amount):

            f.write(to_Aiken())
        




    