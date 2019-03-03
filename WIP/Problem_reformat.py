class Problem():

    def __init__(self, js):

        def tex_improve(tex):

            import re
            #tex = re.sub(r"\$ \$|\$", r"\$\$", tex)
            tex = re.sub("(?m)(?<=^)(\$|\$ \$)", "\\[\\displaystyle", tex)
            tex = re.sub("(?m)\$(?=$)", "\\]", tex)
            for function in ['sin', 'cos', 'sec', 'cosec', 'tan', 'cot']:

                tex = re.sub('(?<=\b)|(?<!mathrm)\{%s\}' %(function), '\\{}'.format(function), tex)

            if self.type == 'Trigonometric Integration' and '+C' not in tex:

                    tex = re.sub('\\displaystyle', '\\displaystyle \\int{.+}(?=dx)', tex) 

            return tex
        
        from MathMl2LaTeX import mml2latex

        self.id = js['id']
        self.type = js['topic']
        try:
            self.question = tex_improve(mml2latex(js['question']))
            self.choices = [tex_improve(mml2latex(choice)) for choice in js['choices']]
            self.correct = js['correct_choice']
            self.error = False
            self.text = js['instruction']
        except:
            self.error = True
