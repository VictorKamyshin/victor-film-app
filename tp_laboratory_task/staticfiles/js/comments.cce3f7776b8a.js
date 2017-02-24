$('.answer_comment_button').click(answer);

function answer() { //огромная такая джава-скриптовина
        var comment_id = $(this).data('comment_id');
        var parent_elem;
        if(!comment_id){
            var btn = document.getElementsByName('film_root_comment_add')[0]
            btn.style.display="none";
            var film_comment_wrapper = document.getElementsByName('film_comment_button_wrapper')[0]
            parent_elem = document.getElementsByName('film_comment_button_wrapper');
        } else {
            parent_elem = document.getElementsByName('comment-box-'+comment_id)
            var btn = document.getElementsByName('film_root_comment_add')[0]
            btn.style.display="block";
        }
        var form = comment_input_form;
        var form_clone = form.cloneNode(true);
        form_clone.setAttribute('name', 'form_clone');
        if(!comment_id){
            form_clone.setAttribute('parent_elem_name', 'film_comment_button_wrapper')
        } else {
            form_clone.setAttribute('parent_elem_name','comment-box-'+comment_id)
        }
        form_clone.setAttribute('comment_id',comment_id)
        form_clone.style.display = "block";
        form_clone.querySelector(".comment-submit-button").setAttribute("data-comment_id",comment_id)
        form_clone.querySelector(".comment-submit-button").addEventListener("click", send_comment );
            //она должна висеть в обработчике формы для комментария к самому фильму
        parent_elem[0].appendChild(form_clone);
        return false;
}

function send_comment() {
            var $form = $(this).parents('form');
            $data = $form.find('textarea[name=text]').val(); //омайгадебл, мы добрались до данных формы
            var film_id = $(this).data('film_id');
            var comment_id = $(this).data('comment_id');
            $.ajax({
                url: '/film_comment/',
                method: 'post',
                dataType: 'json',
                data: {
                    text: $data,
                    film_id : film_id,
                    commented_comment_id : comment_id,
                    csrfmiddlewaretoken: $form.find('input[name=csrfmiddlewaretoken]').val(),
                }
            }).done(function (resp) {
                var phantom_of_comment = document.getElementsByName('phantom_of_comment')[0];
                var comment_clone = phantom_of_comment.cloneNode(true);
                comment_clone.style.display="block";
                var comment_container = document.getElementsByName('comments_block')[0];
                comment_clone.querySelector(".thumbnail").setAttribute("name", "comment-box-"+resp.comment_id);
                comment_clone.querySelector(".answer_comment_button").setAttribute("data-comment_id", resp.comment_id);
                comment_clone.querySelector(".comment-margin").className =("col-md-"+resp.level);
                comment_clone.querySelector(".comment-block").className = ("col-md-"+resp.reverse_level);
                console.log(comment_clone.querySelector(".link-to-the-author-profile").getAttribute("href"))
                comment_clone.querySelector(".link-to-the-author-profile").setAttribute("href",
                    comment_clone.querySelector(".link-to-the-author-profile").getAttribute("href")+resp.username)

                comment_clone.querySelector(".edit-comment").setAttribute("href",
                    comment_clone.querySelector(".edit-comment").getAttribute("href")+resp.comment_id)

                delete_comment = comment_clone.querySelector(".delete-comment")
                if(delete_comment){
                    delete_comment.setAttribute("href", delete_comment.getAttribute("href")+resp.comment_id)
                }

                comment_clone.querySelector(".comment_author_field").innerHTML = resp.username;
                comment_clone.querySelector(".comment_text_field").innerHTML = $data;
                comment_clone.querySelector(".answer_comment_button").addEventListener("click", answer );
                var previous_comment = (document.getElementsByName("comment-box-"+resp.prev_comment_id)[0]);
                if(previous_comment != undefined){
                    previous_comment = previous_comment.parentNode;
                    insertAfter(comment_clone,previous_comment);
                } else {
                    comment_container.appendChild(comment_clone);
                }

            });

        var previous_form = document.getElementsByName('form_clone')
        if(previous_form.length!=0){
            previous_form = previous_form[0]
            var previous_form_parent_elem = document.getElementsByName(previous_form.getAttribute('parent_elem_name'))[0]
            previous_form_parent_elem.removeChild(previous_form)
        }

 }

function insertAfter(newElement,targetElement) {
    // target is what you want it to go after. Look for this elements parent.
    var parent = targetElement.parentNode;

    // if the parents lastchild is the targetElement...
    if (parent.lastChild == targetElement) {
        // add the newElement after the target element.
        parent.appendChild(newElement);
    } else {
        // else the target has siblings, insert the new element between the target and it's next sibling.
        parent.insertBefore(newElement, targetElement.nextSibling);
    }
}