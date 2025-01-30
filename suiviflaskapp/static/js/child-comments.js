"use strict";

var TITLE = document.querySelector("#form").querySelector("h2");
var EDITOR = document.getElementById("editeur");
var CHILD_ID =  document.getElementById("child_id").value;
var HELP_BUTTON = document.querySelector("#help");
var HOST = window.location.origin + '/enfant/commentaires/' + CHILD_ID;
console.log(HOST);

// help
HELP_BUTTON.addEventListener('click', e => {
    var host = window.location.origin + '/enfant/commentaires/aide/' + CHILD_ID;
    var windowObjectReference = window.open(host, 'media', 'resizable=yes, location=no, width=350, height=500, menubar=no');
} );


// editeur
(function () {
    EDITOR.addEventListener('keydown', e => {
        if (e.key == 'Enter') {
            //e.preventDefault();
            console.log("lklkllk");
            //document.execCommand('insertText', false, '\n');
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
})()

var cancel = document.getElementById('cancel');
cancel.addEventListener('click', function() {
    TITLE.innerHTML = 'Ajouter un commentaire:';
    document.getElementById('save').className = 'add';
    EDITOR.innerHTML = '';
    this.style.display = 'none';
    // redescendre
    var comment = document.querySelector('#comment_' + document.getElementById('comment_id').value);
    var box = comment.getBoundingClientRect();
    var k;
    for (k = 0; k < 49; k++) {
        setTimeout('window.scrollBy(0,' + Math.floor(box.top / 49) + ')', 10 * k);
    }
}, false);

function update(e) {
    var content = e.target.parentNode.querySelector(".comment--content").textContent;
    //EDITOR.innerHTML = content;
    EDITOR.textContent = content;
    TITLE.innerHTML = "Modifier un commentaire:";
    var button = document.getElementById("save").className = "update";
    document.getElementById("comment_id").value = e.target.parentNode.querySelector(".comment_id").value;
    // bouton annuler
    document.getElementById('cancel').style.display = 'inline';
    // remontervar cancel = document.getElementById('cancel');
    cancel.addEventListener('click', function() {
        TITLE.innerHTML = 'Ajouter un commentaire:';
        document.getElementById('save').className = 'add';
        EDITOR.innerHTML = '';
        this.style.display = 'none';
        // redescendre
        var comment = document.querySelector('#comment_' + document.getElementById('comment_id').value);
        var box = comment.getBoundingClientRect();
        var k;
        for (k = 0; k < 49; k++) {
            setTimeout('window.scrollBy(0,' + Math.floor(box.top / 49) + ')', 10 * k);
        }
    }, false);
    var b = document.querySelector("#form");
    var box = b.getBoundingClientRect();
    var k;
    for (k = 0; k < 49; k++) {
        setTimeout("window.scrollBy(0," + Math.floor(box.top / 49) + ")", 10 * k);
    }
}

function del(e) {
    var comment = e.target.parentNode;
    var comId = comment.querySelector(".comment_id").value;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', HOST);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({op: 'del', comment_id: comId}));

    xhr.addEventListener("readystatechange", function() {
        if (xhr.readyState === xhr.DONE) {
            var data = JSON.parse(xhr.responseText);
            comment = document.querySelector('#comment_' + data['comment_id'])
            comment.parentNode.removeChild(comment);
            // todo: test last group
        }
    }, false);
}

(function(){
    var update_buttons = document.querySelectorAll('.update');
    var i, c;
    for (i=0, c=update_buttons.length; i<c; i++) {
        update_buttons[i].addEventListener('click', update, false);
    }
    var del_buttons = document.querySelectorAll('.del');
    for (i=0, c=del_buttons.length; i<c; i++) {
        del_buttons[i].addEventListener('click', del, false);
    }
})();

// sauvegarder
(function save() {
    var saveB = document.querySelector('#save');
    saveB.addEventListener('click', function() {
        var content = EDITOR.textContent;
        // Envoi de la requête.
        var url, request;
        var xhr = new XMLHttpRequest();
        if (saveB.className == 'add') {
            request = JSON.stringify({op: 'add', content: content});
            xhr.open('POST', HOST);
        }
        else if (saveB.className == 'update') {
            var comId = document.getElementById("comment_id").value;
            xhr.open('POST', HOST);
            request = JSON.stringify({op: 'update', comment_id: comId, content: content});
        }
        else {
            console.log('Something doesn\'t work!')
            return
        }

        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(request);
        xhr.addEventListener("readystatechange", function() {
            if (xhr.readyState === xhr.DONE) {
                var data = JSON.parse(xhr.responseText);

                if (saveB.className == 'add') {
                    var comment = document.getElementById('ref').cloneNode(true);
                    comment.style.display = 'inline';
                    comment.id = 'comment_' + data['comment_id'];
                    comment.className = 'comment';
                    comment.querySelector('.comment--content').innerHTML = data['content'];
                    comment.querySelector('.comment--context').innerHTML = 'Le ' + data['date'] + ' (' + data['author'] + ')';
                    comment.querySelector('.comment_id').value = data['comment_id'];

                    var firstCom = document.querySelector('.comment');
                    var comments = document.querySelector('#comments');
                    console.log(firstCom);
                    if (!firstCom) {
                        comments.removeChild(comments.querySelector('p'));
                    }
                    else {
                        var lastGroup = document.querySelector('.group:last-of-type').innerText;
                        console.log(lastGroup)
                        if (lastGroup != data['group']) {
                            var newGroup = document.createElement('h3');
                            newGroup.className = 'group';
                            newGroup.innerText = data['group'];
                            comments.appendChild(newGroup);
                        }
                    }

                    comments.appendChild(comment);
                    // eventlisteners
                    comment.querySelector('.update').addEventListener('click', update, false);
                    comment.querySelector('.del').addEventListener('click', del, false);
                }

                else if (saveB.className == 'update') {
                    TITLE.innerHTML = 'Ajouter un commentaire:';
                    document.getElementById("save").className = 'add';
                    var comment = document.querySelector('#comment_' + data['comment_id']);
                    comment.querySelector('.comment--content').innerHTML = EDITOR.innerHTML;
                }

                EDITOR.innerHTML = '';
                // redescendre
                var box = comment.getBoundingClientRect();
                var k;
                for (k = 0; k < 49; k++) {
                    setTimeout('window.scrollBy(0,' + Math.floor(box.top / 49) + ')', 10 * k);
                }
            }
        }, false);

    }, false);
})();
