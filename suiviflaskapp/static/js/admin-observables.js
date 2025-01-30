"use strict";

// Variables
var buttons, i, c;


// Initialiser les flêches
var skills = document.querySelectorAll('.skill');
Array.from(skills).forEach(elt => testPositionSkill(elt));
var observables = document.querySelectorAll('.observable');
Array.from(observables).forEach(elt => testPositionObs(elt));

// NIVEAU des observables
function level(e) {
    var xhr = new XMLHttpRequest();
    // Envoi de la requête.
    var host = window.location.origin + '/update_level'
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({obs_id: e.target.id.split('_')[1]}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            var response = xhr.responseText
            var json = JSON.parse(xhr.responseText);
            //cycle 1: 0, 1, 2; cycle 2: 3, 4, 5; cycle 3: 6, 7, 8
            //if (response == '2' || response == '5' || response == '8'){
            if ([2, 5, 8].includes(json['level'])) {
                e.target.className = 'level level_3'; // pour le CSS
            }
            else if ([1, 4, 7].includes(json['level'])) {
                e.target.className = 'level level_2';
            }
            else if ([0, 3, 6].includes(json['level'])) {
                e.target.className = 'level level_1';
            }
            else if ([20, 50, 80].includes(json['level'])) {
                e.target.className = 'level level_4';
            }
            e.target.textContent = json['levelstr'];
        }
    }, false);
}
buttons = document.querySelectorAll(".level");
Array.from(buttons).forEach(function(b) {
    b.addEventListener('click', level, false);
});


// AJOUTER ou MODIFIER le texte d'un observable ou d'une compétence
function edit(e) {
        var itemType = this.parentNode.querySelector('input[name=\'type\']').value;
        var itemId = this.parentNode.querySelector('input[name=\'id\']').value;
        var op = this.name
        var host = window.location.origin + '/editor?id=' + itemId + '&type=' + itemType + '&op=' + op;
        var windowObjectReference = window.open(host, "edition", 'resizable=yes, location=no, width=600, height=250, menubar=no');
    }
buttons = document.querySelectorAll(".edit");
Array.from(buttons).forEach(function(elt) {
    elt.addEventListener('click' , edit, false);
});


// SUPPRIMER UNE COMPETENCE
function delSkill(e) {
    if (!confirm('Supprimer la compétence?')) {
        return;
    }
    var xhr = new XMLHttpRequest();
    // Envoi de la requête.
    var host = window.location.origin + '/del_skill';
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    var skill_id = e.target.parentNode.querySelector('input[name=\'id\']').value;
    xhr.send(JSON.stringify({skill_id: skill_id}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            var json = JSON.parse(xhr.responseText);
            var skill = document.querySelector("#skill_" + json['skill_id']);
            var obs = document.querySelectorAll(".skill_" + json['skill_id']);
            skill.parentNode.removeChild(skill);
            obs.forEach(function(o) {
                o.parentNode.removeChild(o);
            });
            for (var key in json) {
                if (key != 'skill_id') {
                    var paragraph = document.querySelector('#skill_' + key + ' .itemText');

                    paragraph.textContent = json[key];
                    testPositionSkill(document.querySelector('#skill_' + key));
                }
            }
        }
    }, false);
}
var buttons = document.querySelectorAll('.skill .del');
buttons.forEach(function(b) {
    b.addEventListener('click' , delSkill, false);
});

//SUPPRIMER UN OBSERVABLE
function delObs(e) {
    if (!confirm('Supprimer l\'observable?')) {
        return;
    }
    var xhr = new XMLHttpRequest();
    // Envoi de la requête.
    var host = window.location.origin + '/del_obs';
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    var obs_id = this.parentNode.querySelector('input[name=\'id\']').value;
    xhr.send(JSON.stringify({obs_id: obs_id}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            var json = JSON.parse(xhr.responseText);
            var line = document.querySelector('#observable_' + json['obs_id']);
            if (line.nextElementSibling.className == 'skill' &&
                    line.previousElementSibling.classList.contains('observable')) {
                line.previousElementSibling.querySelector('.down').style.display = 'none';
            }
            for (var key in json) {
                if (key != 'obs_id') {
                    var o = document.querySelector('#observable_' + key + ' .itemText');
                    o.innerText = json[key];
                }
            }
            line.parentNode.removeChild(line);
        }
    }, false);
}
buttons = document.querySelectorAll('.observable .del');
buttons.forEach(function(b) {
    b.addEventListener('mouseup', delObs, false);
});


// Ajouter les eventListeners
// Compétences
function activeCloneSkill(element) {
    var down = element.getElementsByClassName('down')[0];
    down.addEventListener('click', mdSkill, false);
    var up = element.getElementsByClassName('up')[0];
    up.addEventListener('click', muSkill, false);
    var e = element.getElementsByClassName('edit')[0];
    e.addEventListener('click', edit, false);
    var del = element.getElementsByClassName('del')[0];
    del.addEventListener('click', delSkill, false);
}
// Observable
function activeCloneObs(element) {
    var down = element.querySelector('.down');
    down.addEventListener('click', md, false);
    var up = element.querySelector('.up');
    up.addEventListener('click', mu, false);
    var e = element.querySelector('.edit');
    e.addEventListener('click', edit, false);
    var del = element.querySelector('.del');
    del.addEventListener('click', delObs, false);
    var l = element.querySelector(".level");
    l.addEventListener('click', level, false);
}
// Vérifier les flêches
function testPositionSkill(element) {
    var down = element.querySelector('.down');
    var up = element.querySelector('.up');
    down.style.display = (nextSkill(element) == undefined ? 'none' : 'inline')
    up.style.display = (previousSkill(element).className == 'field' ? 'none' : 'inline')
}

function testPositionObs(element) {
    var down = element.querySelector('.down');
    var up = element.querySelector('.up');
    if (element.nextElementSibling == undefined || element.nextElementSibling.className == 'skill') {
        down.style.display = 'none';
    }
    else {
        down.style.display = 'inline';
    }
    if (element.previousElementSibling.className == 'skill') {
        up.style.display = 'none';
    }
    else {
        up.style.display = 'inline';
    }
}

function nextSkill(element) {
    var next = element.nextElementSibling;
    while(next != null && next.className != 'skill') {
        next = next.nextElementSibling;
    }
    return next;
}
function previousSkill(element) {
    var previous = element.previousElementSibling;
    while(previous.className != 'field' && previous.className != 'skill') {
        previous = previous.previousElementSibling;
    }
    return previous;
}


// DÉPLACER
// Descendre = monter le précédent
function moveSkill(skill) {
    var previousS = previousSkill(skill);
    var previousId = previousS.querySelector('input[name=\'id\']').value;
    var currentId = skill.querySelector('input[name=\'id\']').value;
    var xhr = new XMLHttpRequest();
    // Envoi de la requête.
    var host = window.location.origin + '/move_skill';
    xhr.open('POST', host);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    var request = JSON.stringify({up: currentId, down: previousId});
    xhr.send(request);
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            var json = JSON.parse(xhr.responseText);
            var clone = skill.cloneNode(true);
            var observables = document.querySelectorAll('.skill_' + currentId);
            var clones = Array.from(observables).map(function(obs) {
                obs.parentNode.removeChild(obs);
                return obs.cloneNode(true)
            });
            skill.parentNode.removeChild(skill);
            clone.querySelector('.itemText').innerText = json['up'];
            previousS.querySelector('.itemText').innerText = json['down'];
            // Insérer la compétence et ses observables
            previousS.parentNode.insertBefore(clone, previousS);
            clones.forEach(function(value, index, clones) {
                previousS.parentNode.insertBefore(value, previousS);
                activeCloneObs(value);
            });
            activeCloneSkill(clone);
            testPositionSkill(clone);
            testPositionSkill(previousS);
        }
    }, false);
}

function mdSkill(e) {
    var currentId = e.target.parentNode.querySelector('input[name=\'id\']').value;
    var nextComp = nextSkill(document.getElementById('skill_' + currentId));
    moveSkill(nextComp);
}
buttons = document.querySelectorAll('.skill .down');
buttons.forEach(function(b) {
    b.addEventListener('click', mdSkill, false);
});


function muSkill(e) {
    var currentId = e.target.parentNode.querySelector('input[name=\'id\']').value;
    var currentSkill = document.getElementById('skill_' + currentId);
    moveSkill(currentSkill);
}
buttons = document.querySelectorAll('.skill .up');
c=buttons.length;
for (i=0; i<c; i++) {
    buttons[i].addEventListener('click', muSkill, false);
}

// monte l'observable
function moveObs(currentObs) {
    var currentId = currentObs.querySelector('input[name=\'id\']').value;
    var previousObs = currentObs.previousElementSibling;
    var previousId = previousObs.querySelector('input[name=\'id\']').value;
    var xhr = new XMLHttpRequest();
    // Envoi de la requête.
    var host = window.location.origin + '/move_obs';
    xhr.open('POST', host);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({up: currentId, down: previousId}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            var json = JSON.parse(xhr.responseText);
            var clone = currentObs.cloneNode(true);
            clone.querySelector('.itemText').innerText = json['up'];
            previousObs.querySelector('.itemText').innerText = json['down'];
            currentObs.parentNode.removeChild(currentObs);
            previousObs.parentNode.insertBefore(clone, previousObs);
            testPositionObs(previousObs);
            testPositionObs(clone);
            activeCloneObs(clone);
        }
    }, false);
}

function md(e) {
    var currentId = e.target.parentNode.querySelector('input[name=\'id\']').value;
    var currentObs = document.getElementById('observable_' + currentId);
    var nextObs = currentObs.nextElementSibling;
    moveObs(nextObs);
}
buttons = document.querySelectorAll('.observable .down');
buttons.forEach(function(btn) {
    btn.addEventListener('click', md, false);
});

function mu(e) {
    var currentId = e.target.parentNode.querySelector('input[name=\'id\']').value;
    var currentObs = document.getElementById('observable_' + currentId);
    moveObs(currentObs);
}
buttons = document.querySelectorAll('.observable .up');
buttons.forEach(function(btn) {
    btn.addEventListener('click', mu, false);
});


// export pdf
var button = document.querySelector('#exportPdf');
button.addEventListener('click', function(e) {
    var xhr = new XMLHttpRequest();
    var host = window.location.origin + "/admin_observables_pdf";
    xhr.open('POST', host);
    xhr.setRequestHeader("Content-Type", "application/json;charset= UTF-8");
    var cycleId = document.getElementById('cycle_id').value;
    console.log('cycleId=', cycleId);
    var request = JSON.stringify({dest: 'pdf', cycle_id: cycleId});
    xhr.send(request);

    xhr.addEventListener("readystatechange", function() {
        if (xhr.readyState === xhr.DONE) {
            console.log(xhr.responseText);

            var filename = xhr.responseText;
            if (filename.length > 3) {
                window.location.href = "/static/pdf/" + filename;
            }
        }
    }, false);

}, false);



