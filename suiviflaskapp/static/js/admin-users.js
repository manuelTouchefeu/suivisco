"use strict";

// update class
(function() {
    var updateClass = document.querySelectorAll('.update_class');
    Array.from(updateClass).forEach(elt => elt.addEventListener('change', function(e) {
        var user_id = e.target.parentNode.querySelector('input[name=\'user_id\']').value;
        var classroom_id = e.target.value;

        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/update_user_classroom';
        xhr.open("POST", host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({user_id: user_id, classroom_id: classroom_id}));
        // Réception des données.
        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                ;
            }
        }, false);

    }, false) );
})();


// toggle is_staff
(function() {
    var updateIsStaff = document.querySelectorAll('.is_staff');
    Array.from(updateIsStaff).forEach(elt => elt.addEventListener('change', function(e) {
        var user_id = e.target.parentNode.querySelector('input[name=\'user_id\']').value;
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/update_user_is_staff';
        xhr.open("POST", host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({user_id: user_id}));
        // Réception des données.
        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                ;
            }
        }, false );

    }, false ) );
})();


// del user
(function() {
    var delUser = document.querySelectorAll('.del_user');
    Array.from(delUser).forEach(elt => elt.addEventListener('click', function(e) {
        var user_id = e.target.parentNode.querySelector('input[name=\'user_id\']').value;
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/del_user';
        xhr.open("POST", host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({user_id: user_id}));
        // Réception des données.
        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                e.target.parentNode.parentNode.removeChild(e.target.parentNode)
            }
        }, false );
    }, false ) );
})();