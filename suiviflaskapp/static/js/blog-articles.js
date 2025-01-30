"use strict";

var HOST = window.location.origin + '/blog/articles';

// Supprimer un article
(function () {
    var del = document.querySelectorAll('.del');
    var i, c = del.length, xhr, host, id;
    for (var i=0; i<c; i++) {
        del[i].addEventListener('click', function() {
            xhr = new XMLHttpRequest();
            // Envoi de la requête.
            xhr.open('POST', HOST);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            var articleId = this.parentNode.querySelector('input[name=\'article_id\'').value;
            var request = JSON.stringify({op:'del', article_id: articleId});
            xhr.send(request);
            // retour
            xhr.addEventListener("readystatechange", function() {
                if (xhr.readyState === xhr.DONE) {
                    var json = JSON.parse(xhr.responseText);
                    var article = document.querySelector('#a_' + json['article_id']);
                    article.parentNode.removeChild(article);
                }
            }, false);
        }, false);
    }
})();

// Publier / dépublier
(function () {
    var toggleStatus = document.querySelectorAll('select[name=\'publication\']');
    var i, c = toggleStatus.length, xhr, host, id;
    for (var i=0; i<c; i++) {
        toggleStatus[i].addEventListener('change', function() {
            xhr = new XMLHttpRequest();
            // Envoi de la requête.
            xhr.open('POST', HOST);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            var articleId = this.parentNode.querySelector('input[name=\'article_id\'').value;
            var request = JSON.stringify({op: 'toggle_publication', article_id: articleId});
            xhr.send(request);
            // retour
            xhr.addEventListener("readystatechange", function() {
                if (xhr.readyState === xhr.DONE) {
                    var json = JSON.parse(xhr.responseText);
                    console.log(json['article_id']);
                }
            }, false);
        }, false);
    }
})();

// Autoriser l'édition
(function () {
    var toggleStatus = document.querySelectorAll('select[name=\'edition\']');
    var i, c = toggleStatus.length, xhr, host, id;
    for (var i=0; i<c; i++) {
        toggleStatus[i].addEventListener('change', function() {
            xhr = new XMLHttpRequest();
            // Envoi de la requête.
            xhr.open('POST', HOST);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            var articleId = this.parentNode.querySelector('input[name=\'article_id\'').value;
            var request = JSON.stringify({op: 'toggle_edition', article_id: articleId});
            xhr.send(request);
            // retour
            xhr.addEventListener("readystatechange", function() {
                if (xhr.readyState === xhr.DONE) {
                    var json = JSON.parse(xhr.responseText);
                    console.log(json['article_id']);
                }
            }, false);
        }, false);
    }
})();

// Affecter à une catégorie
(function () {
    var setCategory = document.querySelectorAll('select[name=\'category\']');
    var i, c = setCategory.length, xhr, host, id;
    for (var i=0; i<c; i++) {
        setCategory[i].addEventListener('change', function() {
            console.log('okok');
            xhr = new XMLHttpRequest();
            // Envoi de la requête.
            xhr.open('POST', HOST);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            var articleId = this.parentNode.querySelector('input[name=\'article_id\'').value;
            var request = JSON.stringify({op: 'set_category', article_id: articleId, category: this.value});
            xhr.send(request);
            // retour
            xhr.addEventListener("readystatechange", function() {
                if (xhr.readyState === xhr.DONE) {
                    var json = JSON.parse(xhr.responseText);
                    console.log(json['article_id']);
                }
            }, false);
        }, false);
    }
})();