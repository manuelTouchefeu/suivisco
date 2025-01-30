"use strict";
// source: https://jsfiddle.net/gcvgtbsh/

var LOGED = (document.querySelector('#authenticated') ? true : false);
var IS_VISITOR = null;
var USER_ID = null;
if (LOGED) {
    IS_VISITOR = document.querySelector('input[name=\'is_visitor\']').value;
    USER_ID = document.querySelector('input[name=\'user_id\']').value;
}
var UPLOAD_STATUS = false;

// comments

// toggle comments
var toggleButtons = Array.from(document.querySelectorAll('.toggle_com'));
toggleButtons.forEach(tb => toggle(tb))
function toggle(elt) {
    elt.addEventListener('click', function(e) {
        if (LOGED) {
            var blockComments = this.parentNode.querySelector('.comments');
            blockComments.style.display = (blockComments.style.display == 'block' ? 'none' : 'block');
        }
        else {
            var loginRequired = this.parentNode.querySelector('.login_required');
            loginRequired.style.display = 'block';
            setTimeout(function() {
                loginRequired.style.display = 'none';
            }, 1500);
        }
    }, false);
}

// editor
var editors = Array.from(document.querySelectorAll('.editor'))
editors.forEach(ed => {
    ed.addEventListener('keydown', function(e) {
        if (e.key == 'Enter') {
            e.preventDefault();
            document.execCommand('insertHTML', false, '<br><br>');
        }
    }, false);
} );
var i, c;

// medias
var mediaButtons = document.querySelectorAll('.choose');
Array.from(mediaButtons).forEach(btn => addMedia(btn));

function addMedia(mediaButton) {
    mediaButton.addEventListener('click', function(e) {
        var chooseFile = mediaButton.parentNode.querySelector('.selector');
        var uploadFileFinalContainer = mediaButton.parentNode.querySelector('.upload-file-final-container');
        var fileName = mediaButton.parentNode.querySelector('.file-name');
        var cancelButton = mediaButton.parentNode.querySelector('.cancel-button');
        var uploadButton = mediaButton.parentNode.querySelector('.upload-button');
        var uploadProgress = mediaButton.parentNode.querySelector('.upload-progress');
        var uploadPercentage = mediaButton.parentNode.querySelector('.upload-percentage');
        chooseFile.click();

        chooseFile.addEventListener('change', function() { // When a new file is selected
            var file = this.files[0];
            // en cas d'annulation
            if (file == undefined) {
                return
            }
            uploadFileFinalContainer.style.display = 'block';
            mediaButton.style.display = 'none';
            fileName.innerText = file.name;
            // Cancel button event
            cancelButton.addEventListener('click', function() {
                mediaButton.style.display = 'inline';
                uploadFileFinalContainer.style.display = 'none';
                chooseFile.setAttribute('value', '');
            });

            // Upload via AJAX
            uploadButton.addEventListener('click', function(e) {
                if (UPLOAD_STATUS) {
                    console.log('UPLOAD!');
                    return;
                }
                UPLOAD_STATUS = true;

                var data = new FormData();
                data.append('file', chooseFile.files[0]);
                data.append('article_id', this.value);

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
                        //var editor = document.querySelector('#article_' + json['article_id'] + ' .editor')
                        var editor = uploadButton.parentNode.parentNode.querySelector('.editor');
                        var proto = document.querySelector('#proto_' + json['content_type']).cloneNode(true);
                        proto.removeAttribute('id');
                        proto.style.display = 'inline';
                        if (json['content_type'] == 'img') {
                            proto.src = '/static/blog/visitor-data/' + json['filename'];
                        }
                        else if (json['content_type'] == 'audio' || json['content_type'] == 'video') {
                            proto.querySelector(json['content_type']).title = json['filename']
                            proto.querySelector(json['content_type']).src = '/static/blog/visitor-data/' + json['filename'];
                            proto.querySelector('figcaption').innerText = json['filename'];
                        }
                        else if (json['content_type'] == 'doc') {
                            console.log(json);
                            proto.querySelector('figcaption').querySelector('a').innerText = json['filename'];
                            console.log(proto.querySelector('figcaption').querySelector('a'));
                            Array.from(proto.querySelectorAll('a')).map(elt => elt.href = '/static/blog/visitor-data/' + json['filename']);
                            proto.querySelector('img').src = '/static/blog/docs/' + json['preview'];
                        }
                        editor.appendChild(proto);
                        editor.appendChild(document.createElement('br'));
                        editor.appendChild(document.createElement('br'));
                        UPLOAD_STATUS = false;
                    }
                });

                var host = window.location.origin + '/add-media-comment/';
                request.open('POST', host);
                request.send(data);
            });
        }, false);

    }, false);
}

var postButtons = Array.from(document.querySelectorAll('.save'));
postButtons.forEach(b => saveCom(b));
function saveCom(b) {
    b.addEventListener('click', function() {
        var text = this.parentNode.querySelector('.editor').innerHTML;
        var author = document.querySelector('#username').innerText;
        var is_public = this.parentNode.querySelector('.is_public').checked;
        var json = {op: 'add', article_id: this.value, is_visitor: IS_VISITOR,
                    author: author, user_id: USER_ID, text: text, is_public: is_public};
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/articles-comments/';
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify(json));
        this.parentNode.querySelector('.editor').innerHTML = '';

        xhr.addEventListener("readystatechange", function() {
            if (xhr.readyState === xhr.DONE) {
                json = JSON.parse(xhr.responseText);
                var newComment = document.querySelector('.proto_comment').cloneNode(true);
                newComment.style.display = 'block';
                newComment.className = 'comment';
                newComment.querySelector('.comment--content').innerHTML = json['content'];
                newComment.querySelector('.c_date').innerText = json['date'];
                newComment.querySelector('.author').innerText = json['author'];
                newComment.querySelector('.comment_id').value = json['comment_id'];
                newComment.querySelector('button[name=\'del_com\']').value = json['comment_id'];
                newComment.querySelector('.update_is_public').checked = json['is_public'];
                var article = document.querySelector('#article_' + json['article_id']);
                var first = article.querySelector('.comment');
                if (first) {
                    first.parentNode.insertBefore(newComment, first);
                }
                else {
                    article.querySelector('.comments').appendChild(newComment);
                }
                delComment(newComment.querySelector('button[name=\'del_com\']'));
                toggleIsPublic(newComment.querySelector('.update_is_public'))
            }
        }, false );
    }, false );
}

// supprimer un commentaire
function delComment(comment) {
    comment.addEventListener('click', function(e) {
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/articles-comments';
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({op: 'del', comment_id: this.value}));
        xhr.addEventListener('readystatechange', function() {
            if (this.readyState === xhr.DONE) {
                console.log('remove');
                e.target.parentNode.parentNode.removeChild(e.target.parentNode);
            }
        }, false);
    }, false);
}
Array.from(document.querySelectorAll('button[name=\'del_com\']')).forEach(elt => delComment(elt));


// toggle is_public
function toggleIsPublic(comment) {
    comment.addEventListener('click', function(e) {
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/articles-comments';
        var comment_id = this.parentNode.querySelector('.comment_id').value;
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({op: 'toggle_is_public', comment_id: comment_id}));
        xhr.addEventListener('readystatechange', function() {
            if (this.readyState === xhr.DONE) {
                console.log(xhr.responseText);
            }
        }, false);
    }, false);
}
Array.from(document.querySelectorAll('.update_is_public')).forEach(elt => toggleIsPublic(elt));


var answerButtons = Array.from(document.querySelectorAll('.answer'));
answerButtons.forEach(b => saveAnswer(b));
console.log(answerButtons);
function saveAnswer(b) {
    b.addEventListener('click', function() {
        var answersBlock = b.parentNode.parentNode;
        var text = this.parentNode.querySelector('.editor').innerHTML;
        var author = document.querySelector('#username').innerText;
        var json = {op: 'add', comment_id: this.value, is_visitor: IS_VISITOR,
                    author: author, user_id: USER_ID, text: text};
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/articles-comments-answer/';
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify(json));
        this.parentNode.querySelector('.editor').innerHTML = '';

        xhr.addEventListener("readystatechange", function() {
            if (xhr.readyState === xhr.DONE) {
                json = JSON.parse(xhr.responseText);
                console.log(json);

                var newAnswer = document.querySelector('.proto_answer').cloneNode(true);
                newAnswer.style.display = 'block';
                newAnswer.className = 'answer';
                newAnswer.id = 'a_' + json['answer_id'];
                newAnswer.querySelector('.answer--content').innerHTML = json['content'];
                newAnswer.querySelector('.a_date').innerText = json['date'];
                newAnswer.querySelector('.author').innerText = json['author'];
                newAnswer.querySelector('button[name=\'del_answer\']').value = json['answer_id'];
                answersBlock.appendChild(newAnswer);
                delAnswer(newAnswer.querySelector('button[name=\'del_answer\']'));

            }
        }, false );

    }, false);
}

function delAnswer(b) {
    b.addEventListener('click', function(e) {
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/articles-comments-answer';
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({op: 'del', answer_id: this.value}));
        xhr.addEventListener('readystatechange', function() {
            if (this.readyState === xhr.DONE) {
                var json = JSON.parse(xhr.responseText);
                console.log('remove');
                var a = document.querySelector('#a_' + json['answer_id']);
                console.log(a);
                a.parentNode.removeChild(a);
            }
        }, false);
    }, false);
}
Array.from(document.querySelectorAll('button[name=\'del_answer\']')).forEach(elt => delAnswer(elt));
console.log(document.querySelectorAll('button[name=\'del_answer\']'));

// remonter
(function() {
    var scrollUp = document.getElementById('scrollUp');
    // remonter
    scrollUp.addEventListener('click', function() {
        //  window.scrollBy(0, window.innerHeight);
        var b = document.querySelector('body');
        var box = b.getBoundingClientRect();
        var k;
        for (k = 0; k < 49; k++) {
            setTimeout('window.scrollBy(0,' + Math.floor(box.top / 49) + ')', 10 * k);
            //setTimeout("window.scrollBy(0," + Math.floor(box.top / 50) + ")", 10 * k);
        }
    });
    // comportement du bouton
    // déclanché au chargement si scroll auto.
    window.addEventListener('scroll', function(e) {
        var b = document.querySelector('body');
        var box = b.getBoundingClientRect();

        if (box.top < -200) {
            scrollUp.style.display = 'block';
        }
        else {
            scrollUp.style.display = 'none';
        }
    });

})();


// demander des articles
(function() {
    var offset = 0;
    var more = document.getElementById('more');
    if (!more) return
    var category_id = getFromURL('cat');
    more.addEventListener('click', function() {
        offset+=4;
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/blog-ecole/';
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        var request = JSON.stringify({offset: offset, category_id: category_id});
        xhr.send(request);

        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                if (xhr.responseText.length == 0) {
                    more.parentNode.removeChild(more);
                    return;
                }
                var articles = document.querySelector('.content');
                var json = JSON.parse(xhr.responseText);
                console.log(json);
                json.articles.forEach(function(article) {
                    var newArticle = document.querySelector('.proto_article').cloneNode(true);
                    newArticle.id = 'article_'  + article.article_id;
                    newArticle.className = 'article';
                    newArticle.style.display = 'block';
                    newArticle.querySelector('.date').innerText = article.date;
                    newArticle.querySelector('.title').innerText = article.title;
                    var image = newArticle.querySelector('img')
                    if (article.image) {
                        image.src = '/static/blog/images/' + article.image;
                    }
                    else {
                        image.parentNode.removeChild(image);
                    }
                    newArticle.querySelector('.text').innerHTML = article.content;

                    if (!article.is_editable) {
                        newArticle.removeChild(newArticle.querySelector('.toggle_com'));
                        newArticle.removeChild(newArticle.querySelector('.comments'));
                    }
                    else if (LOGED) {
                        newArticle.querySelector('.toggle_com').classList.add('toggle_com--active');
                        var commentsBlock = newArticle.querySelector('.comments')
                        newArticle.querySelector('.upload-button').value = article.article_id;
                        newArticle.querySelector('.save').value = article.article_id;
                        article.comments.forEach(c => {
                            var newComment = document.querySelector('.proto_comment').cloneNode(true);
                            newComment.style.display = 'block';
                            newComment.className = 'comment';
                            newComment.querySelector('.comment--content').innerHTML = c.content;
                            newComment.querySelector('.c_date').innerText = c.date;
                            newComment.querySelector('.author').innerText = c.author;
                            newComment.querySelector('.comment_id').value = c.id;
                            newComment.querySelector('button[name=\'del_com\']').value = c.id;
                            // supprimer les boutons si pas propriétaire du commentaire
                            var upd = newComment.querySelector('.update_is_public');
                            if (c.owner == false) {
                                var label = newComment.querySelector('label');
                                label.parentNode.removeChild(label);
                                var delB = newComment.querySelector('button[name=\'del_com\']');
                                delB.parentNode.removeChild(delB);
                                upd.parentNode.removeChild(upd);
                            }
                            upd.checked = c.is_public == true;
                            commentsBlock.appendChild(newComment);
                        })
                    }
                    articles.insertBefore(newArticle, more);
                    // eventListeners
                    if (LOGED && article.is_editable) {
                        addMedia(newArticle.querySelector('.choose'));
                        saveCom(newArticle.querySelector('.save'));
                        Array.from(newArticle.querySelectorAll('.update_is_public')).forEach(btn => toggleIsPublic(btn));
                        Array.from(newArticle.querySelectorAll('button[name=\'del_com\']')).forEach(btn => delComment(btn));
                    }
                    if (article.is_editable) {
                        toggle(newArticle.querySelector('.toggle_com'));
                    }
                });

                if (json.next == false) {
                    more.parentNode.removeChild(more);
                }
            }
        }, false);

    }, false);

})();