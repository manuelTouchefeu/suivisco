"use strict";

var CHILD_ID = document.querySelector('#child_id').value;


(function() {
    var toggles = document.querySelectorAll(".toggle");
    Array.from(toggles).forEach(function(t) {
        t.addEventListener('click' , function() {
            var xhr = new XMLHttpRequest();
            var validated = t.classList.contains('ok') ? true : false;
            var obs_id = t.parentNode.querySelector('.obs_id').value;
            // Envoi de la requête.
            var host = window.location.origin + '/validate';
            xhr.open('POST', host);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.send(JSON.stringify({child_id: CHILD_ID, obs_id: obs_id,  validated: validated}));

            // Réception des données.
            xhr.addEventListener('readystatechange', function() {
                if (xhr.readyState === xhr.DONE) {
                    // var response = xhr.responseText
                    var json = JSON.parse(xhr.responseText);
                    console.log(json);
                    t.className = 'toggle ' + json['className'];
                    if (validated == false){
                        t.textContent = json['date'];
                    }
                    else {
                        t.textContent = '';
                    }
                }
            }, false);

        }, false);
    });
})();


(function() {
    var chooseButtons = document.querySelectorAll('.choose-button');
    Array.from(chooseButtons).forEach(function(button) {
        button.addEventListener('click', function(e) {
            var chooseButton = this;
            var obsId = e.target.parentNode.querySelector('.obs_id').value;
            var chooseFile = e.target.parentNode.querySelector('input[type=file]');
            var uploadFileFinalContainer = e.target.parentNode.querySelector('.upload-file-final-container');
            var fileName = uploadFileFinalContainer.querySelector('.file-name');
            var cancelButton = uploadFileFinalContainer.querySelector('.cancel-button');
            var uploadButton = uploadFileFinalContainer.querySelector('.upload-button');
            var uploadProgress = uploadFileFinalContainer.querySelector('.upload-progress');
            var uploadPercentage = uploadFileFinalContainer.querySelector('.upload-percentage');
            var image = chooseButton.parentNode.parentNode.querySelector('.image');
            var update = (e.target.parentNode.parentNode.querySelector('.toggle').classList.contains('ok') ? true : false);
            console.log(update);
            chooseFile.click();

            chooseFile.addEventListener('change', function() { // When a new file is selected
                var file = this.files[0];
                // en cas d'annulation
                if (file == undefined) {
                    return
                }
                uploadFileFinalContainer.style.display = 'block';
                chooseButton.style.display = 'none';
                fileName.innerText = file.name;

                // Cancel button event
                cancelButton.addEventListener('click', function() {
                    chooseButton.style.display = 'block';
                    uploadFileFinalContainer.style.display = 'none';
                    chooseFile.setAttribute('value', '');
                });

                // Upload via AJAX
                uploadButton.addEventListener('click', function() {
                    var data = new FormData();
                    data.append('file', chooseFile.files[0]);
                    data.append('obs_id', obsId);
                    data.append('child_id', CHILD_ID);
                    data.append('update', update);

                    var request = new XMLHttpRequest();

                    request.upload.addEventListener('progress', function(e) {
                        var percent_complete = (e.loaded / e.total)*100;
                        uploadPercentage.innerText = percent_complete;
                        uploadProgress.style.display = 'block';
                    });

                    request.addEventListener('load', function(e) {
                        uploadProgress.style.display = 'none';
                        cancelButton.click();
                    });

                    request.addEventListener('readystatechange', function() {

                        if (request.readyState === request.DONE) {
                            if (update && image.querySelector('img')) {
                                image.removeChild(image.querySelector('img'));
                            }
                            var img = document.createElement('img');
                            img.src = '/static/images/' + request.responseText + '?' + Math.random();
                            img.alt = 'illustration';
                            img.style.width= '100%';
                            image.appendChild(img);
                            // bouton supprimer
                            if (!update) {
                                var supp = document.createElement('input');
                                supp.type = 'submit';
                                supp.value = 'Supprimer';
                                supp.className = 'del';
                                chooseButton.parentNode.appendChild(supp);
                                // TODO: ne marche pas!
                                //supp.addEventListener('click', del, false);
                            }
                        }
                    });

                    var url = '/enfant_upload'
                    var host = window.location.origin + url;
                    request.open('POST', host);
                    request.send(data);

                });
            }, false);
        }, false);
    });
})();

(function del() {
    var delButtons = document.querySelectorAll('.del');
    Array.from(delButtons).forEach(elt => {
        var obs_id = elt.parentNode.parentNode.querySelector('.obs_id').value;
        elt.addEventListener('click', function(e) {
            //console.log(obs_id);
            var xhr = new XMLHttpRequest();
            var host = window.location.origin + '/enfant_del_image';
            xhr.open('POST', host);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            xhr.send(JSON.stringify({child_id: CHILD_ID, obs_id: obs_id}));
            // Réception des données.
            xhr.addEventListener('readystatechange', function() {
                if (xhr.readyState === xhr.DONE) {
                    var filename = JSON.parse(xhr.responseText)['image'];
                    var image = document.querySelector('#observable_' + obs_id).querySelector('img');
                    console.log(image);
                    if (!filename) {
                        image.parentNode.removeChild(image)
                    }
                    else {
                        image.src = '/static/images/' + filename;
                    }

                }
            }, false);
        }, false);

    });
})();
