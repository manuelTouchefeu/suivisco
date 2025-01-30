"use strict";

//delCategory
(function() {
    var deleteCategory = document.querySelectorAll('.deleteCat');
    Array.from(deleteCategory).forEach(elt => elt.addEventListener('click', function(e) {
        var data = new FormData();
        data.append('op', 'del_category');
        data.append('category_id', this.value);
        var category = this.parentNode;
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/blog/categories';
        xhr.open('POST', host);
        xhr.send(data);
        xhr.addEventListener('readystatechange', function() {
            if (this.readyState === xhr.DONE) {
                category.parentNode.removeChild(category);
            }
        }, false);


    }, false ) );
} )();


//update
(function() {
    var deleteCategory = document.querySelectorAll('.updateCat');
    Array.from(deleteCategory).forEach(elt => elt.addEventListener('click', function(e) {
        document.querySelector('#category_id').value = this.value;
        document.querySelector('#op').value = 'update_category';
        document.querySelector('#name').value = this.parentNode.querySelector('.cat_name').innerText;
        document.querySelector('#description').innerText = this.parentNode.querySelector('.cat_description').innerText;
        document.querySelector('#cancel').style.display = 'inline';
    }, false ) );

    document.querySelector('#cancel').addEventListener('click', function(e) {
        document.querySelector('#category_id').value = '';
        document.querySelector('#op').value = 'add';
        document.querySelector('#name').value = '';
        document.querySelector('#description').innerText = ''
        this.style.display = 'none';
    }, false);

} )();