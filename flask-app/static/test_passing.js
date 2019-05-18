written_answers = [];

function check_test() {
    // gather all the filled data and send it to python function
    let $form = $("#test_passing_form");
    let multiple_choice_data = getFormData($form);
    let written_answer_data = {};

    // iterate through fields with LaTeX enabled
    for (let i = 0; i < written_answers.length; i++) {
        let d = written_answers[i].id;
        written_answer_data[$("[mathquill-block-id=" + d + "]")[0].parentNode.id] = written_answers[i].latex();
    }
    let res_data = {};

    // join 2 jsons: with written answers and multiple choice answers
    $.extend(res_data, multiple_choice_data, written_answer_data);
    written_answers.length = 0;
    res_data["filename"] = document.getElementById("title").innerHTML;
    let response = $.post("submit_test", res_data, function () {
    });
    setTimeout(function () {
        window.location.href = "/test_results";
    }, 1300);

}

function getFormData($form) {
    // get all the data from input fields of the form
    let unindexed_array = $form.serializeArray();
    let indexed_array = {};

    $.map(unindexed_array, function (n, i) {
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
}