"use strict";

function getMedia(btn) {
    var fig = btn.parentNode;
    while (fig.nodeName != 'FIGURE') {
        fig = fig.parentNode;
    }
    var media = fig.querySelector('.media').cloneNode(true);
    return media
}

var mediaAdd = document.querySelectorAll('.add');

(function () {
    Array.from(mediaAdd).forEach(function(elt) {
        elt.addEventListener('click', function() {
            var target = document.querySelector('#target').value;
            var media;
            if (target == 'doc') {
                media = elt.parentNode;
                while (media.nodeName != 'FIGURE') {
                    media = media.parentNode;
                }
                media = media.cloneNode(true);
            }
            else {
                media = getMedia(this);
            }

            if (target == 'main') {
                target = window.opener.document.getElementById('image')
                var targetImg = target.querySelector('img');
                target.replaceChild(media, targetImg);
                var targetFigCaption = target.querySelector('figcaption');
                targetFigCaption.innerText = media.alt;
            }
            else if (target == 'img' || target == 'audio' || target == 'video' || target == 'doc') {
                target = window.opener.document.getElementById('editeur');
                if (media.nodeName == 'IMG' || media.nodeName == 'VIDEO') {
                    media.setAttribute('width', '100%');
                }
                else if (media.nodeName == 'FIGURE') {
                    var fc = media.querySelector('figcaption');
                    fc.innerHTML = fc.innerHTML.split('|')[0];
                }
                target.appendChild(media);
                // mettre à jour l'éditeur html pour l'éditeur d'article.
                var html = window.opener.document.querySelector('#html');
                html.textContent = target.innerHTML;
            }


            // pour un observable
            else {
                var img = getMedia(this);
                var obsId = getFromURL('obs_id');
                target = window.opener.document.getElementById('observable_' + obsId).querySelector('.image');

                var xhr = new XMLHttpRequest();
                var host = window.location.origin + '/upload-from-blog';
                xhr.open('POST', host);
                xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
                // update ou ajout?
                var update = target.querySelector('img') ? true : false;

                xhr.send(JSON.stringify({obs_id: obsId, filename: img.alt, update: update}));

                // retour de la requête
                var button = this;
                xhr.addEventListener("readystatechange", function() {
                    if (xhr.readyState === xhr.DONE) {
                        console.log(target);
                        var json = JSON.parse(xhr.responseText);
                        // supprimer l'image si présente
                        if (update) {
                            target.innerHTML = '';
                        }
                        // afficher l'image
                        img = document.createElement('img');
                        img.src = '/static/images/' + json['filename'];
                        img.alt = json['filename'];
                        img.setAttribute('width', '100%');
                        target  .append(img);
                        // bouton supp
                        // TODO: bouton supp
                    };
                }, false);
            }

        }, false);
    });

})();
