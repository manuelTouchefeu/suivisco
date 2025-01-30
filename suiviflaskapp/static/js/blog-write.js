"use strict";

var HTML = document.getElementById('html');
var EDITOR = document.getElementById('editeur');
var OP = (getFromURL('article') == 'new' ? 'add' : 'update');
var ARTICLEID = (OP == 'update' ?  getFromURL('article') : null);

// https://openclassrooms.com/fr/courses/1744696-creez-un-editeur-de-texte-wysiwyg - 404
(function () {
    EDITOR.addEventListener('keydown', e => {
        if (e.key == 'Enter') {
            e.preventDefault();
            document.execCommand('insertHTML', false, '<br><br>');
        }
    }, false);

    var i, c;
    // style
    var buttonStyle = document.querySelectorAll('.style');
    for (i=0, c=buttonStyle.length; i<c; i++) {
        buttonStyle[i].addEventListener('click', function(e) {
            var cmd = e.target.id;
            document.execCommand(cmd, false, '');
        }, false);
    }
    // medias
    var mediaButtons = document.querySelectorAll('.media');
    Array.from(mediaButtons).forEach(function(elt) {
        elt.addEventListener('click', function(e) {
            var host = window.location.origin + '/blog/add_media/' + elt.id;
            var windowObjectReference = window.open(host, 'media', 'resizable=yes, location=no, width=350, height=500, menubar=no');
        }, false);
    });
})();

// Sauvegarde de l'article
(function () {
    var saveB = document.querySelector('#save');
    saveB.addEventListener('mouseup', function() {
        var xhr = new XMLHttpRequest();
        // Envoi de la requête.
        var host = window.location.origin + '/blog/ecrire';
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        var title = document.querySelector('#title').value;
        var content = EDITOR.innerHTML;
        var image = document.getElementById('image').querySelector('img').alt;
        image = (image == 'alt' ? null : image);
        var request = {op: OP, title: title, content: content, image: image};
        if (OP == 'update') {
            request['article_id'] = ARTICLEID;
        }
        xhr.send(JSON.stringify(request));
        xhr.addEventListener("readystatechange", function() {
            if (xhr.readyState === xhr.DONE) {
                var json = JSON.parse(xhr.responseText);
                if (OP == 'add') {
                    OP = 'update'
                    ARTICLEID = json['article_id']
                }
            }
        }, false);

    }, false);
})();

// wysiwyg et html
(function() {
    var html = document.getElementById('html');
    var editeur = document.getElementById('editeur');

    editeur.addEventListener('input', function(e) {
        html.textContent = this.innerHTML;
    })
    html.addEventListener('input', function(e) {
        editeur.innerHTML = this.textContent;
    })
})();