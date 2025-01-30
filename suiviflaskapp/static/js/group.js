"use strict";

(function() {
    var toggles = document.querySelectorAll(".toggle");
    Array.from(toggles).forEach(function(t) {
        t.addEventListener('click' , function() {
            var xhr = new XMLHttpRequest();
            var validated = t.classList.contains('ok') ? true : false;
            var obs_id = t.parentNode.querySelector('.obs_id').value;
            var child_id = t.querySelector('.child_id').value;
            // Envoi de la requête.
            var host = window.location.origin + '/validate'
            xhr.open('POST', host);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.send(JSON.stringify({child_id: child_id, obs_id: obs_id,  validated: validated}));

            // Réception des données.
            xhr.addEventListener('readystatechange', function() {
                if (xhr.readyState === xhr.DONE) {
                    // var response = xhr.responseText
                    console.log(xhr.responseText);
                    var json = JSON.parse(xhr.responseText);
                    var hidden_input = t.querySelector('input');
                    t.className = 'toggle ' + json['className'];
                    if (validated == false){
                        t.textContent = json['date'];
                    }
                    else {
                        t.textContent = '';
                    }
                    t.appendChild(hidden_input);

                }
            }, false);

        }, false);
    });
})();