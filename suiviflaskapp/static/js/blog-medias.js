"use strict";

var MEDIATYPE = document.querySelector('input[name=\'media_type\']').value;

var UPLOAD_STATUS = false;

(function() {

    var buttons = document.querySelectorAll('.del');
    buttons.forEach(function(button) {
        button.addEventListener('click', function() {
            var media_id = this.parentNode.querySelector('input[name=\'file_id\']').value;
            // Envoi de la requête
            var xhr = new XMLHttpRequest();
            var host = window.location.origin + '/blog/media/del';
            xhr.open('POST', host);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            xhr.send(JSON.stringify({media_id: media_id, media_type: MEDIATYPE}));
            // retour de la requête
            xhr.addEventListener("readystatechange", function() {
                if (xhr.readyState === xhr.DONE) {
                    var json = JSON.parse(xhr.responseText);
                    var file = document.querySelector('#file_' + json['media_id']);
                    file.parentNode.removeChild(file);
                }
            }, false);

        }, false);
    });
})();

// upload
(function() {
    var chooseButton = document.getElementById('choose');
    chooseButton.addEventListener('click', function(e) {
        var chooseFile = document.getElementById('selector');
        var uploadFileFinalContainer = document.querySelector('.upload-file-final-container');
        var fileName = document.getElementById('file-name');
        var cancelButton = document.getElementById('cancel-button');
        var uploadButton = document.getElementById('upload-button');
        var uploadProgress = document.getElementById('upload-progress');
        var uploadPercentage = document.getElementById('upload-percentage');
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
                if (UPLOAD_STATUS) {
                    return
                }
                UPLOAD_STATUS = true;
                var data = new FormData();
                data.append('file', chooseFile.files[0]);
                data.append('media_type', MEDIATYPE)

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
                        var json = JSON.parse(request.responseText);
                        var file = document.querySelector('#proto_' + MEDIATYPE).cloneNode(true);
                        file.removeAttribute('id');
                        if (MEDIATYPE == 'img') {
                            var img = file.querySelector('img');
                            img.src = '/static/blog/images/' + json['filename'];
                            img.alt = json['filename'];
                        }
                        else if (MEDIATYPE == 'audio') {
                            var audio = file.querySelector('audio');
                            audio.src = '/static/blog/audio/' + json['filename'];
                            audio.title = json['filename'];
                            file.querySelector('.info').innerText = json['filename'];
                        }
                        else if (MEDIATYPE == 'video') {
                            var video = file.querySelector('video');
                            video.src = '/static/blog/video/' + json['filename'];
                            video.title = json['filename'];
                            file.querySelector('.info').innerText = json['filename'];
                        }
                        else if (MEDIATYPE == 'doc') {
                            var preview = file.querySelector('img');
                            preview.src = '/static/blog/docs/' + json['preview'];
                            var doc = file.querySelector('a');
                            doc.innerText = json['filename'];
                            doc.href = '/static/blog/docs/' + json['filename'];
                        }
                        file.querySelector('input[name=\'file_id\']').value = json['file_id']
                        file.style.display = 'list-item';
                        var first = document.querySelector('.file:first-child');
                        if (first) {
                            first.parentNode.insertBefore(file, first);
                        }
                        else {
                            var info = document.querySelector('#info');
                            var b = document.createElement('div');
                            b.appendChild(file);
                            info.parentNode.insertBefore(b, info);
                            info.parentNode.removeChild(info);
                        }

                        UPLOAD_STATUS = false;
                    }
                });
                var host = window.location.origin + '/blog/media/add';
                request.open('POST', host);
                request.send(data);
            });
        }, false);
    }, false);
})();
