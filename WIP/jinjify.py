import os
import random
import shutil
import jinja2
from jinja2 import Template

class Test(object):

    def __init__(self, title, problems):

        self.key = "".join([str(random.randrange(9)) for _ in range(16)])
        self.title = title
        self.problems = problems

    def to_pdf(self):


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
            loader=jinja2.FileSystemLoader(os.path.abspath('.'))
        )
        boilerplate = LatexEnv.get_template('boilerplate.tex')
        latex = boilerplate.render(test = self)
        with open(f"ltx{self.key}.tex", 'w') as tempf:

            tempf.write(latex)

        os.system(f'pdflatex ltx{self.key}.tex')
        for filename in os.listdir("."):
            
            if (filename[:-4] == f"ltx{self.key}") and not(filename.endswith('.pdf')):

                os.remove(filename)

class Problem():

    def __init__(self, problem="", task="", choices=(), right_answers=(), kind='multiple_choice'):

        self.problem = problem
        self.task = task
        self.answer_amount = len(choices)
        self.choices = choices
        self.kind = kind
    
if __name__ == "__main__":
    
    prob1 = Problem(r"$\int\limits_0^\infty e^{-x^2}$", task="Solve for x:", choices=[r"$\frac{1}{2}$", r"$\phi$", r"$\sqrt{\pi}$", r"I don't know"], right_answers=[2,3])
    prob2 = Problem(r"$\sum\limits_{n=0}^\infty \frac{1}{n^2}$", task="Solve for x:", choices=[r"$\frac{1}{2}$", r"$ \frac{\pi^2}{6}$", r"$\sqrt{\pi}$", r"I don't know"], right_answers=[1])
    prob3 = Problem(r"Lorem Ipsum...", task="Continue the text:", kind="written_answer")
    tst = Test('Hello, World!', [prob1, prob2, prob3])
    tst.to_pdf()