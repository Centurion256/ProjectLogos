written_answers = [];

function check_test() {
    let $form = $("#test_passing_form");
    let multiple_choice_data = getFormData($form);
    let written_answer_data = {};
    for (let i = 0; i < written_answers.length; i++) {
        let d = written_answers[i].id;
        let val = written_answers[i].latex();
        written_answer_data[$("[mathquill-block-id=" + d + "]")[0].parentNode.id] = val;
    }
    let res_data = {};
    $.extend(res_data, multiple_choice_data, written_answer_data);
    written_answers.length = 0;
    res_data["filename"] = document.getElementById("title").innerHTML;
    let response = $.post("submit_test", res_data, function () {
    });
    console.log(response);
    window.location.href = "/test_results";
}

function getFormData($form) {
    let unindexed_array = $form.serializeArray();
    let indexed_array = {};

    $.map(unindexed_array, function (n, i) {
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
}