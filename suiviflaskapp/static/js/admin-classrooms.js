"use strict";

var form_child_legend = document.querySelector('#form_child_legend');
var inputs = Array.from(document.querySelector('#form_child').elements);

var CHILD_ID,
    OP = 'add_child';

var cancelButton = document.querySelector('#cancel');
cancel.style.display = 'None';
cancel.addEventListener('click', function() {
    this.style.display = 'None';
    OP = 'add';
    console.log(op.value);
    form_child_legend.innerText = 'Ajouter un enfant:'
    inputs.forEach(i => {
        if (i.id != 'submit' && i.id != 'cancel') {
            i.value = '';
        };
        if (i.id == 'speed') {
            i.value = '0';
        }
    } );
}, false );


var submitButton = document.querySelector('#submit');
submitButton.addEventListener('click', function(e) {
    e.preventDefault();
    var data = new FormData(document.querySelector('#form_child'));
    data.append('id', CHILD_ID);
    data.append('op', OP);
    var xhr = new XMLHttpRequest();
    var host = window.location.origin + '/admin/classes';
    xhr.open('POST', host);
    //xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(data);
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            // Recharge la page actuelle, sans utiliser le cache
            document.location.reload(true);
        }
    }, false);
}, false);



var updateButtons = document.querySelectorAll('.update');
console.log(updateButtons);
Array.from(updateButtons).forEach(b => b.addEventListener('click', function(e) {
    var childId = this.value;
    console.log(childId);
    var xhr = new XMLHttpRequest();
    var host = window.location.origin + '/get_child';
    xhr.open("POST", host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({child_id: childId}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            cancel.style.display = 'inline';
            form_child_legend.innerText = 'Modifier un enfant:'
            var json = JSON.parse(xhr.responseText);
            inputs.forEach(i => {
                CHILD_ID = json['id'];
                OP = 'update_child';
                if (i.id != 'submit' && i.id != 'cancel') {
                    i.value = json[i.id];
                }
            } );
        }
    }, false);
}, false) );


var delButtons = document.querySelectorAll('.del');
Array.from(delButtons).forEach(b => b.addEventListener('click', function(e) {
    if (!confirm('Supprimer cet enfant?')) {
        return
    }
    var childId = this.value;
    var data = new FormData();
    data.append('child_id', childId);
    data.append('op', 'delete_child');
    var xhr = new XMLHttpRequest();
    var host = window.location.origin + '/admin/classes';
    xhr.open('POST', host);
    xhr.send(data);
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            var c = document.querySelector('#child_' + childId);
            c.parentNode.removeChild(c);
        }
    }, false);
}, false) );


var delClassRoomButtons = Array.from(document.querySelectorAll('.del_classroom'));
delClassRoomButtons.forEach(elt => elt.addEventListener('click', function(e) {
        var classroomId = this.value;
        var data = new FormData();
        data.append('classroom_id', classroomId);
        data.append('op', 'delete_classroom');
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/admin/classes';
        xhr.open('POST', host);
        xhr.send(data);
        // Réception des données.
        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                var cl = document.querySelectorAll('.classroom_' + classroomId);
                cl.forEach(c => c.parentNode.removeChild(c));
            }
        }, false);
    }, false ) );


var updateClassRoomButtons = Array.from(document.querySelectorAll('.update_classroom'));
updateClassRoomButtons.forEach(btn => btn.addEventListener('click', function(e) {
    var name = prompt('Nom de la classe:');
    var data = new FormData();
        data.append('name', name);
        data.append('classroom_id', this.value);
        data.append('op', 'update_classroom');
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/admin/classes';
        xhr.open('POST', host);
        xhr.send(data);
        // Réception des données.
        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                e.target.parentNode.querySelector('.name').innerText = name;
            }
        }, false);
}, false ) );


// Classe des enfants.
// copié et adapté à partir de https://openclassrooms.com/fr/courses/1916641-dynamisez-vos-sites-web-avec-javascript/1922434-le-drag-drop
var dndHandler = {
    draggedElement: null, // Propriété pointant vers l'élément en cours de déplacement

    applyDragEvents: function(element) {
        element.draggable = true;
        // Cette variable est nécessaire pour que l'événement « dragstart » ci-dessous accède facilement au namespace « dndHandler »
        var dndHandler = this;
        element.addEventListener('dragstart', function(e) {
            dndHandler.draggedElement = e.target; // On sauvegarde l'élément en cours de déplacement
            e.dataTransfer.setData('text/plain', ''); // Nécessaire pour Firefox
        });
    },

    applyDropEvents: function(dropper) {

        dropper.addEventListener('dragover', function(e) {
            e.preventDefault(); // On autorise le drop d'éléments
            this.classList.add('drop_hover');
        });
        dropper.addEventListener('dragleave', function() {
            this.classList.remove('drop_hover');
        });

        // Cette variable est nécessaire pour que l'événement « drop » ci-dessous accède facilement au namespace « dndHandler »
        var dndHandler = this;
        dropper.addEventListener('drop', function(e) {

            var target = e.target,
                draggedElement = dndHandler.draggedElement; // Récupération de l'élément concerné

            while (target.className.indexOf('dropZone') == -1) { // Remonter jusqu'à la zone de drop parente
                target = target.parentNode;
            }
            var child_id = draggedElement.querySelector('button').value;
            var class_id = target.querySelector('input').value;

            var xhr = new XMLHttpRequest();
            var host = window.location.origin + '/update_classroom';
            xhr.open("POST", host);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            xhr.send(JSON.stringify({child_id: child_id, class_id: class_id}));
            // Réception des données.
            xhr.addEventListener('readystatechange', function() {
                if (xhr.readyState === xhr.DONE) {
                    target.querySelector('ul').appendChild(draggedElement);
                    target.classList.remove('drop_hover'); // Application du style par défaut
                }
            }, false);

        });
    }
};

var elements = document.querySelectorAll('.draggable');
for (var i = 0; i < elements.length; i++) {
    dndHandler.applyDragEvents(elements[i]); // Application des paramètres nécessaires aux éléments déplaçables
}
var droppers = document.querySelectorAll('.dropZone');
for (var i = 0; i < droppers.length; i++) {
    dndHandler.applyDropEvents(droppers[i]); // Application des événements nécessaires aux zones de drop
}