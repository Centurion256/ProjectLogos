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
    <input type="checkbox">
    <span class="checkmark"></span>
</label>
"""

def make_question(id, question, task, variants):
    answers = []
    for i in range(len(variants)):
        answers.append(answer.format(variants[i]))
    return question_template.format(id, question, task, "\n".join(answers))
