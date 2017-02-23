$('.appraisal_button').click(function() {
    var $form = $(this).parents('form');
    $data = $form.find('select[name=value]').val() //омайгадебл, мы добрались до данных формы
    var film_id = $(this).data('film_id');
    console.log(film_id);
    $.ajax({
        url: '/appraisal/',
        method: 'post',
        dataType: 'json',
        data: {
            appraisal: $data,
            film_id : film_id,
            csrfmiddlewaretoken: $form.find('input[name=csrfmiddlewaretoken]').val(),
        }
    }).done(function (resp) {
        console.log(resp.rating);
        film_rating.innerHTML = resp.rating;
    });
    return false;

});
