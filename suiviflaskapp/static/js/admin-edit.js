var cancel = document.querySelector('#cancel');
cancel.addEventListener('click', function() {
    window.close();
}, false);

var save = document.querySelector('#save');
save.addEventListener('click', function() {
    var id = getFromURL('id');
    var op = getFromURL('op');
    var name = document.querySelector('#editor').innerText;
    var type = getFromURL('type');
    var fun;
    switch(op) {
        case 'update':
            fun = '/update_name';
            var json = JSON.stringify({item_type: type, id: id, name: name});
            break;
        case 'add':
            fun = (type == 'field' ? '/add_skill' : '/add_obs');
            var cycle = getFromURL('cycle');
            var json = JSON.stringify({id: id, name: name});
            break;
        default:
            alert('erreur!');
            window.close();
    }

    var host = window.location.origin + fun;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', host);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(json);

    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            var json = JSON.parse(xhr.responseText);
            console.log(json);
            if (op == 'update') {
                var prefixe = (type == 'skill' ? 'skill_' : 'observable_');
                var item = window.opener.document.getElementById(prefixe + json['id']).querySelector('.itemText');
                item.innerText = json['position'] + '. ' + json['name'];
            }
            else if (op = 'add') {
                if (type == 'field') {
                    var skill = createSkill(json['id'], json['position'], json['name']);
                    var table = window.opener.document.querySelector('table');
                    table.appendChild(skill);
                }
                if (type == 'skill') {
                    var obs = createObs(json['skill_id'], json['id'], json['position'], json['name']);
                    var currentSkill = window.opener.document.getElementById('skill_' + json['skill_id']);
                    var next = currentSkill.nextElementSibling;
                    while (next != null && next.className != 'skill') {
                        next = next.nextElementSibling;
                    }
                    var last = next == null ? true : false;
                    if (last == false) {
                        next.parentNode.insertBefore(obs, next);
                    }
                    else {
                        currentSkill.parentNode.appendChild(obs);
                    }
                    var previousObs = obs.previousElementSibling;
                    if (previousObs.classList.contains("observable")) {
                        var down = previousObs.querySelector(".down");
                        down.style.display = "inline";
                    }
                }
            }
        }
    }, false);
}, false);


function createSkill(id, index, name) {
    var newSkill = window.opener.document.getElementById('skill_example').cloneNode(true);
    newSkill.id = "skill_" + id;
    newSkill.className = 'skill';
    newSkill.querySelector('input[name=\'id\'').value = id;
    newSkill.querySelector('.itemText').innerText = index + '. ' + name;
    return newSkill;
}

function createObs(skillId, id, index, name) {
    var newObs = window.opener.document.getElementById('obs_example').cloneNode(true);
    newObs.id = "observable_" + id;
    newObs.className = 'skill_' + skillId + ' observable';
    newObs.querySelector('input[name=\'id\'').value = id;
    newObs.querySelector('.itemText').innerText = index + '. ' + name;
    newObs.querySelector('.level').id = 'level_' + id;
    return newObs;
}


