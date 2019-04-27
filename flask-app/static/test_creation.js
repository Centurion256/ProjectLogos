// Warning before leaving the page (back button, or outgoinglink)
window.onbeforeunload = function () {
    return "Do you really want to leave our brilliant application?";
    //if we return nothing here (just calling return;) then there will be no pop-up question at all
    //return;
};


counter = 1;
proceeded = [];
form_items = [];

function insert_new_question() {
    var question;
    var container_block;

    question = document.createElement('div');
    question.setAttribute("id", counter);
    question.setAttribute("class", "question_block");
    var id = counter;
    question.innerHTML = "<span class=\"question_field\">Question " + id + ": </span><br>" +
        "                    <div id='label_type_" + id + "'>\n" +
        "                        <label> Type of the question:\n" +
        "                            <select name=\"type_" + id + "\" class=\"type_" + id + "\">\n" +
        "\n" +
        "                                <option value=\"Multiple choice\">Multiple choice</option>\n" +
        "                                <option value=\"Written answer\">Written answer</option>\n" +
        "                                <oprion value='Random question'>Random question</oprion>\n" +
        "                            </select>\n" +
        "                        </label>\n" +
        "                        <button type=\"button\" id=\"button_submit_" + id + "\"  onclick=\"proceed_type(" + id + ")\">Proceed type</button>\n" +
        "                    </div>";


    counter++;
    container_block = document.getElementById('test_creation');

    container_block.appendChild(question);
}

function add_multiple_choice(id) {
    var question_to_add;
    var number = document.getElementById("number_of_choices_" + id).value;
    if (number < 2 || number > 6) {
        alert("Only numbers from 2 to 6 are accepted");
        event.preventDefault();
        return;
    }

    question_to_add = document.getElementById(id);

    var par = document.createElement("p");
    par.appendChild(document.createTextNode("Enter answer variants: "));
    question_to_add.appendChild(par);
    for (let i = 0; i < number; i++) {
        var span = document.createElement("span");
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
    var select_right = document.createElement("select");
    select_right.setAttribute("id", "right_answer_" + id);
    for (let i = 0; i < number; i++) {
        let option = document.createElement("option");
        option.appendChild(document.createTextNode(i + 1));
        select_right.appendChild(option);
    }
    question_to_add.appendChild(select_right);
    form_items.push(document.getElementById("right_answer_" + id));


    var button_submit = document.getElementById("button_submit_number_" + id);
    var input_number_field = document.getElementById("for_button_submit_number_" + id);
    question_to_add.removeChild(button_submit);
    question_to_add.removeChild(input_number_field);

}

function proceed_type(id) {

    var field_to_get_type = document.getElementsByName("type_" + id)[0];
    var current_question = document.getElementById(id);
    var field_to_delete = document.getElementById("label_type_" + id);
    var type = field_to_get_type.value;
    current_question.removeChild(field_to_delete);
    if (type == 'Multiple choice') {
        proceed_multiple_choice(id);
    } else if (type == 'Written answer') {
        proceed_written_answer(id);
    }
}

function proceed_written_answer(id) {
    var object_to_insert = document.getElementById(id);
    object_to_insert.innerHTML += "<br><label for='question_" + id + "'>Question</label><input name='question_" + id + "' id='question_" + id + "'>" +
        "                            <label for='task_" + id + "'>Task:</label><span class='mathquill-form' id='task_" + id + "'></span>" +
        "                            <label for='answer_" + id + "'>Right answer: </label>" +
        "<span class='mathquill-form' id='answer_" + id + "'></span>\n";


    form_items.push(document.getElementById('question_' + id));
    var editable = ["task_" + id, "answer_" + id];
    for (var edit = 0; edit < editable.length; edit++) {
        var mathFieldSpan = document.getElementById(editable[edit]);
        form_items.push(MQ.MathField(mathFieldSpan, {
            spaceBehavesLikeTab: false,
            autoOperatorNames: 'sin cos tan',
        }));
    }
}

function proceed_multiple_choice(id) {
    var object_to_insert = document.getElementById(id);
    var input = document.createElement("INPUT");
    object_to_insert.innerHTML += "<br><label for='question_" + id + "'>Question</label><input name='question_" + id + "' id='question_" + id + "'>" +
        "                            <label for='task_" + id + "'>Task:</label><span class='mathquill-form' id='task_" + id + "'></span>" +
        "<label for='number_of_choices_" + id + "' id='for_button_submit_number_" + id + "'>Number of choices: <select id='number_of_choices_" + id + "' name='number_of_choices_" + id + "'>" +
        "<option>2</option>" +
        "<option>3</option>" +
        "<option>4</option>" +
        "<option>5</option>" +
        "<option>6</option>" +
        "</select></label>" +
        "<button id='button_submit_number_" + id + "' onclick='add_multiple_choice(" + id + ")'>Submit</button>";

    form_items.push(document.getElementById('question_' + id));
    form_items.push(MQ.MathField(document.getElementById("task_" + id), {
        spaceBehavesLikeTab: false,
        autoOperatorNames: 'sin cos tan',
    }));
}

function make_editable() {
    var MQ = MathQuill.getInterface(2);
    $('.mathquill-editable').each(function () {
        MQ.MathField(this);
    });
}

function submit_form() {
    var res_json = {};
    for (i = 0; i < form_items.length; i++) {
        if (form_items[i] instanceof MQ.MathField) {
            let d = form_items[i].id;
            res_json[$("[mathquill-block-id=" + d + "]")[0].parentNode.id] = form_items[i].latex();
        } else {
            res_json[form_items[i].id] = form_items[i].value;
        }
    }
    console.log(res_json);


}
