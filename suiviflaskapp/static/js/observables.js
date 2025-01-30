"use strict";

// done ?
var doneButtons = Array.from(document.querySelectorAll(".done"));
doneButtons.forEach(function(b) {
    b.addEventListener('click', function(e) {
        var obsId = e.target.parentNode.querySelector('.obs_id').value;
        // Envoi de la requête
        var xhr = new XMLHttpRequest();
        var url = '/observables/toggle_done';
        var host = window.location.origin + url;
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({obs_id: obsId}));

        // retour de la requête
        var button = this;
        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                if (xhr.responseText != 'None') {
                    b.innerText = 'Fait le ' + xhr.responseText;
                }
                else {
                    b.innerText = 'A faire';
                }
            }
        }, false);
    }, false);
});


// resetDone
try {
    var resetDone = document.querySelector('#resetDone');
    resetDone.addEventListener('click', function(e) {
        console.log('Reset done');
        var xhr = new XMLHttpRequest();
        var url = '/observables/reset_done';
        var host = window.location.origin + url;
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({task: 'resetDone'}));

        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                doneButtons.forEach(function(b) {
                    b.innerText = 'A faire';
                });
            }
        }, false);
    }, false);
} catch (error) {
    console.log('Pas encore!');
}


// images
function del(e) {
    var obsId = e.target.parentNode.querySelector('.obs_id').value;
    var image = document.getElementById('observable_'+obsId).querySelector('img');

    // Envoi de la requête
    var xhr = new XMLHttpRequest();
    var url = '/observables/del_image';
    var host = window.location.origin + url;
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({obs_id: obsId}));

    // retour de la requête
    var button = this;
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            if (xhr.responseText == 'ok') {
                image.parentNode.removeChild(image);
                button.parentNode.removeChild(button);
            }
        }
    }, false);
}

(function() {
    var buttons = document.querySelectorAll('.del');
    buttons.forEach(function(button) {
        button.addEventListener('click', del, false);
    });
})();


// https://usefulangle.com/post/67/pure-javascript-ajax-file-upload-showing-progess-percent
(function() {
    var chooseButtons = document.querySelectorAll('.choose-button');
    chooseButtons.forEach(function(button) {
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
            var update = (image.querySelector('img') ? true : false);
            chooseFile.click();
            console.log('ok');
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
                            console.log(request.responseText);
                            if (update) {
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
                                supp.addEventListener('click', del, false);
                            }
                        }
                    });

                    var url = '/observables/upload'
                    var host = window.location.origin + url;
                    request.open('POST', host);
                    request.send(data);

                });
            }, false);
        }, false);
    });
})();

// images venues du blog (pas pour les images perso)
(function() {
    var adds = document.querySelectorAll('.blog');
    adds.forEach(function(elt) {
        elt.addEventListener('mouseup', function(e) {
            var obsId = e.target.parentNode.querySelector('.obs_id').value;
            var host = window.location.origin + '/blog/add_media/observables?obs_id=' + obsId;
            var windowObjectReference = window.open(host, "images", 'resizable=yes, location=no, width=350, height=500, menubar=no');
        }, false);
    });
})();
