// Warning before leaving the page (back button, or outgoing link)
window.onbeforeunload = function () {
    return "Do you really want to leave our brilliant application?";
};


counter = 1;
proceeded = [];
form_items = [];

function insert_new_question() {
    // insert new problem to the page

    // if there are too many problems created
    if (counter > 50) {
        alert("Too many questions are created");
        return;
    }
    let question;
    let container_block;

    question = document.createElement('div');
    question.setAttribute("id", counter);
    question.setAttribute("class", "question_block");
    let id = counter;
    question.innerHTML = "<span class=\"question_field\">Question " + id + ": </span><br>" +
        "                    <div id='label_type_" + id + "'>\n" +
        "                        <label> Type of the question:\n" +
        "                            <select name=\"type_" + id + "\" class=\"question_type type_" + id + "\">\n" +
        "\n" +
        "                                <option value=\"Multiple choice\">Multiple choice</option>\n" +
        "                                <option value=\"Written answer\">Written answer</option>\n" +
        "                                <option value='Random question'>Random question</option>\n" +
        "                            </select>\n" +
        "                        </label>\n" +
        "                        <button type=\"button\" id=\"button_submit_" + id + "\"  onclick=\"proceed_type(" + id + ")\">Proceed type</button>\n" +
        "                    </div>";


    counter++;
    container_block = document.getElementById('test_creation');

    container_block.appendChild(question);
}

function add_multiple_choice(id) {
    // add a multiple choice problem to the page
    let question_to_add;

    // get the number from html
    let number = document.getElementById("number_of_choices_" + id).value;

    question_to_add = document.getElementById(id);

    let par = document.createElement("p");
    par.appendChild(document.createTextNode("Enter answer variants: "));
    question_to_add.appendChild(par);

    // add answer options
    for (let i = 0; i < number; i++) {
        let span = document.createElement("span");
        span.setAttribute("class", "mathquill-form");
        span.setAttribute("id", "question_" + id + "_" + (i + 1));
        question_to_add.appendChild(span);
        form_items.push(MQ.MathField(document.getElementById("question_" + id + "_" + (i + 1)), {
            spaceBehavesLikeTab: false,
            autoOperatorNames: 'sin cos tan',
        }));
    }
    par = document.createElement("p");
    par.appendChild(document.createTextNode("Number of right answer: "));
    question_to_add.appendChild(par);
    let select_right = document.createElement("select");
    select_right.setAttribute("id", "right_answer_" + id);
    for (let i = 0; i < number; i++) {
        let option = document.createElement("option");
        option.appendChild(document.createTextNode(i + 1));
        select_right.appendChild(option);
    }
    question_to_add.appendChild(select_right);
    form_items.push(document.getElementById("right_answer_" + id));


    // remove unnecessary elements
    let button_submit = document.getElementById("button_submit_number_" + id);
    let input_number_field = document.getElementById("for_button_submit_number_" + id);
    question_to_add.removeChild(button_submit);
    question_to_add.removeChild(input_number_field);

}

function proceed_type(id) {
    // proceed some actions after the type of problem is chosen
    let field_to_get_type = document.getElementsByName("type_" + id)[0];
    let current_question = document.getElementById(id);
    let field_to_delete = document.getElementById("label_type_" + id);
    let type = field_to_get_type.value;
    current_question.removeChild(field_to_delete);
    if (type === 'Multiple choice') {
        proceed_multiple_choice(id);
    } else if (type === 'Written answer') {
        proceed_written_answer(id);
    } else if (type === 'Random question') {
        proceed_random_question(id);
    }
}

function proceed_written_answer(id) {
    // add a problem of type written answer
    let object_to_insert = document.getElementById(id);
    object_to_insert.innerHTML += "<br><label for='question_" + id + "'>Question</label><input name='question_" + id + "' id='question_" + id + "'>" +
        "                            <label for='task_" + id + "'>Task:</label><span class='mathquill-form' id='task_" + id + "'></span>" +
        "                            <label for='answer_" + id + "'>Right answer: </label>" +
        "<span class='mathquill-form' id='answer_" + id + "'></span>\n";

    form_items.push(document.getElementById('question_' + id));
    let editable = ["task_" + id, "answer_" + id];
    for (let edit = 0; edit < editable.length; edit++) {
        let mathFieldSpan = document.getElementById(editable[edit]);
        form_items.push(MQ.MathField(mathFieldSpan, {
            spaceBehavesLikeTab: false,
            autoOperatorNames: 'sin cos tan',
        }));
    }
}

function proceed_multiple_choice(id) {
    // add a problem of type multiple choice
    let object_to_insert = document.getElementById(id);
    document.createElement("INPUT");
    object_to_insert.innerHTML += "<br><label for='question_" + id + "'>Question</label><input name='question_" + id + "' id='question_" + id + "'>" +
        "                            <label for='task_" + id + "'>Task:</label><span class='mathquill-form' id='task_" + id + "'></span>" +
        "<label for='number_of_choices_" + id + "' id='for_button_submit_number_" + id + "'>Number of choices: <select class='number_of_choices' id='number_of_choices_" + id + "' name='number_of_choices_" + id + "'>" +
        "<option>2</option>" +
        "<option>3</option>" +
        "<option>4</option>" +
        "<option>5</option>" +
        "<option>6</option>" +
        "</select></label>" +
        "<button id='button_submit_number_" + id + "' onclick='add_multiple_choice(" + id + ")'>Submit</button>";

    alert();
    form_items.push(document.getElementById('question_' + id));
    form_items.push(MQ.MathField(document.getElementById("task_" + id), {
        spaceBehavesLikeTab: false,
        autoOperatorNames: 'sin cos tan',
        autoCommands: 'int sum sqrt pi infty infinity integral'
    }));
}

function submit_form() {
    // submit the form and send all the information to python function

    // check if there are some not completed problems
    if (document.getElementsByClassName("question_type").length !== 0 || document.getElementsByClassName("number_of_choices").length !== 0) {
        alert("Some questions are not finished");
        return;
    }
    let res_json = {};

    let title = document.getElementById("title").value;
    if (!title) {
        alert("Title is not filled");
        return;
    }
    if (title.length > 30) {
        alert("Title is too long");
        return;
    }
    let password = document.getElementById("password_input");
    if (password && password.value.length < 6){
        alert("Minimum password length is 6 characters");
        return;
    }
    if (password){
        form_items.push(password);
    }

    res_json["title"] = title;
    res_json["id"] = counter - 1;

    // iterate through form items and get the value of each
    for (let i = 0; i < form_items.length; i++) {
        if (form_items[i] instanceof MQ.MathField) {
            let d = form_items[i].id;
            let value = form_items[i].latex();
            if (!value) {
                alert("Some compulsory fields are not filled");
                return;
            }
            res_json[$("[mathquill-block-id=" + d + "]")[0].parentNode.id] = value;
        } else {
            res_json[form_items[i].id] = form_items[i].value;
        }
    }
    // clear the form items
    form_items.length = 0;

    // make a post request to get the filled fields in python function
    $.post("creation_submission", res_json, function () {
    });

    // go to the main page
    self.location = "/";

}

function proceed_random_question(id) {
    // add a problem of type random question
    let object_to_insert = document.getElementById(id);
    object_to_insert.innerHTML += "<label for=\"select_topic_" + id + "\">Select topic: </label>\n" +
        "                    <select id=\"select_topic_" + id + "\" name=\"select_topic_" + id + "\" onchange=\"make_subjects(this.id, 'select_subject_" + id + "')\">\n" +
        "                        <option value=\"Arithmetic\">Arithmetic</option>\n" +
        "                        <option value=\"Algebra\">Algebra</option>\n" +
        "                        <option value=\"Calculus\">Calculus</option>\n" +
        "                    </select>\n" +
        "                    <label for=\"select_subject_" + id + "\">Select subject: </label>\n" +
        "                    <select id=\"select_subject_" + id + "\" name=\"select_subject_" + id + "\">\n" +
        "\n" +
        "                    </select>\n" +
        "                    <label for=\"select_difficulty_" + id + "\">Select difficulty: </label>" +
        "                   <select name='select_difficulty_" + id + "' id='select_difficulty_" + id + "'>\n" +
        "                    <option value='Beginner'>Beginner</option>" +
        "                   <option value='Intermediate'>Intermediate</option>" +
        "                   <option value='Advanced'>Advanced</option>" +
        "</select>";
    make_subjects("select_topic_" + id, "select_subject_" + id);
    form_items.push(document.getElementById("select_topic_" + id));
    form_items.push(document.getElementById("select_subject_" + id));
    form_items.push(document.getElementById("select_difficulty_" + id));
}

function edit_password_prompt() {
    let password_required = document.getElementById("password_required").value;
    let password_div = document.getElementById("request_password");
    try {
        let password_prompt = document.getElementById("password");
        password_div.removeChild(password_prompt);
    } catch {
    }
    if (password_required === "True") {
        password_div.innerHTML += "<span id=\"password\">\n" +
            "                        <label for=\"password_input\">Password: </label><input type=\"text\" name=\"password\"\n" +
            "                                                                             id=\"password_input\">\n" +
            "                        </span>";
    }
}


function make_subjects(s1, s2) {
    // change subject options in depending what the topic is selected
    s1 = document.getElementById(s1);
    s2 = document.getElementById(s2);
    s2.innerHTML = "";
    let options = [];
    if (s1.value === "Algebra") {
        options = ["Linear Equations",
            "Equations Containing Radicals",
            "Equations Containing Absolute Values",
            "Quadratic Equations",
            "HigherOrder Polynomial Equations",
            "Equations Involving Fractions",
            "Exponential Equations",
            "Logarithmic Equations",
            "Trigonometric Equations",
            "Matrices Equations"]
    }
    if (s1.value === "Arithmetic") {
        options = ["Simple",
            "Fractions",
            "Exponents and Radicals",
            "Simple Trigonometry",
            "Matrices"]
    }
    if (s1.value === "Calculus") {
        options = ["Polynomial Differentiation",
            "Trigonometric Differentiation",
            "Exponents Differentiation",
            "Polynomial Integration",
            "Trigonometric Integration",
            "Exponents Integration",
            "Polynomial Definite Integrals",
            "Trigonometric Definite Integrals",
            "Exponents Definite Integrals",
            "First Order Differential Equations",
            "Second Order Differential Equations"]
    }
    for (let option in options) {
        s2.innerHTML += "<option value='" + options[option] + "'>" + options[option] + "</option>\n"
    }
}
