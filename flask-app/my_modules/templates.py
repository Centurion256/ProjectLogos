question_template = """
<li>
   <div class="question" id="{}">
       <h4>{}</h4>
           <p class="question-text">{}</p>
           {}
   </div>
</li>"""

answer = """
<label class="question-container">{}
    <input type="checkbox" name="{}">
    <span class="checkmark"></span>
</label>
"""

solved_answer = """
<label class="question-container">{}
    <input type="checkbox" name="{}" disabled>
    <span class="checkmark"></span>
</label>
"""

wrong_solved_answer = solved_answer.replace("checkmark", "checkmark-disabled checkmark-disabled-wrong")

right_solved_answer = solved_answer.replace("checkmark", "checkmark-disabled chechmark-disabled-right")


def make_question(id, question, task, variants):
    answers = []
    for i in range(len(variants)):
        answers.append(answer.format(variants[i], "{}-{}".format(id, i)))
    return question_template.format(id, question, task, "\n".join(answers))


def make_solved(question, task, variants, right_variants, answered):
    answers = []
    for i in range(len(variants)):
        if i in answered and i in right_variants:
            answers.append(right_solved_answer.format(variants[i], "none"))
        elif i not in answered and i not in right_variants:
            answers.append(solved_answer.format(variants[i], "none"))
        else:
            answers.append(wrong_solved_answer.format(variants[i], "none"))
    return question_template.format(0, question, task, "\n".join(answers))

