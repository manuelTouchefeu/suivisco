"use strict";

var addLine = document.querySelector('#addLine');
var saveB = document.querySelector('#save');
var addDay  = document.querySelector('#addDay');
var updateScheduleButtons = document.querySelectorAll('.update_schedule');
var delLineButtons = document.querySelectorAll('.del_line');
var delDayButtons = document.querySelectorAll('.del_day');
var updateDesButtons = document.querySelectorAll('.update_des');
var upButtons = document.querySelectorAll('.up');
var downButtons = document.querySelectorAll('.down');
var items = document.querySelectorAll('.item');
var table = document.querySelector('table');
var groups = document.querySelectorAll('input[name=\'group_name\']');
groups = Array.from(groups).map(c => c.value);

var i, c;

function testButtons() {
    addLine.style.display = (document.querySelector(".day") ? 'inline' : 'none');
    addDay.style.display = (document.querySelector('.line') ? 'none' : 'inline');
    saveB.style.display = addLine.style.display;
}
testButtons();


function testPosition(line) {
    var upButton = line.querySelector('.up');
    var downButton = line.querySelector('.down');
    upButton.style.display = (line.previousElementSibling.id == 'groups' ? 'none' : 'inline')
    downButton.style.display = (line.nextElementSibling.id == 'model_line' ? 'none' : 'inline')
}
Array.from(document.querySelectorAll('.line')).forEach(line => testPosition(line));


function moveDownLine(line) {
    var nextLine = line.nextElementSibling;
    nextLine.parentNode.insertBefore(nextLine, line);
    testPosition(line);
    testPosition(nextLine);
}
function moveUpLine(line) {
    var previousLine = line.previousElementSibling;
    previousLine.parentNode.insertBefore(line, previousLine);
    testPosition(line);
    testPosition(previousLine);
}
Array.from(document.querySelectorAll('.line')).forEach(function(line) {
    line.querySelector('.up').addEventListener('click', function(e) {
        moveUpLine(line);
    }, false);
    line.querySelector('.down').addEventListener('click', function(e) {
        moveDownLine(line);
    }, false);
});


addDay.addEventListener('click', function() {
    var dayName = prompt('Nom du jour:');
    if (dayName == '') {
        return;
    }
    var days = document.querySelector('#days');
    var newDay = document.getElementById('model_day').cloneNode(true);
    newDay.removeAttribute('id');
    newDay.querySelector('.day_name').innerText = dayName;
    newDay.style.display = 'table-cell';
    newDay.className = 'day';
    delDay(newDay.querySelector('.del_day'));
    days.appendChild(newDay);

    var groupsLine = document.querySelector('#groups');
    for (i=0; i<groups.length; i++) {
        var newGroup = document.createElement('th');
        newGroup.innerText =  groups[i];
        newGroup.className = dayName + ' group';
        groupsLine.appendChild(newGroup);
    }
    testButtons();
}, false);


addLine.addEventListener('click', function() {
    var days = document.querySelectorAll(".day");
    var schedule = prompt("Une tranche horaire:");

    var newLine = document.querySelector('#model_line').cloneNode(true);
    newLine.className = 'line';
    newLine.removeAttribute('id');
    newLine.style.display = 'table-row';

    newLine.querySelector('.schedule .description').innerText = schedule;
    updateSchedule(newLine.querySelector('.update_schedule'));
    delLine(newLine.querySelector('.del_line'));

    var item = newLine.querySelector('#example');

    for (i=0; i<days.length; i++) {
        var dayName = days[i].querySelector('.day_name').innerText;
        for (c=0; c<groups.length; c++) {
            var newItem = item.cloneNode(true);
            newItem.classList.add(dayName);
            newItem.id = dayName + '_' + Math.floor(Math.random() * 100000001);
            newItem.querySelector('input[name=\'group\']').value = groups[c];
            newLine.appendChild(newItem);
            // eventListener
            // ajouter la description de l'item
            updateDes(newItem.querySelector('.update_des'));
        }
    }
    item.parentNode.removeChild(item);
    table.appendChild(newLine);
    testButtons()
}, false);

function getTimetable() {
    function Day (name, groups=[]) {
        this.name = name;
        this.groups = groups;
    }
    function Group(name, items=[]) {
        this.name = name;
        this.items = items;
    }
    function Item(description, schedule, id, className, color) {
        this.description = description;
        this.schedule = schedule;
        this.id = id;
        this.className = className;
        this.color = color;
    }

    var timeTable = [];
    var days = document.querySelectorAll(".day");
    for (i=0; i<days.length; i++) {
        var day = new Day(days[i].querySelector(".day_name").innerText);
        var items = Array.from(document.querySelectorAll(".item." + day.name));
        var item_group;
        Array.from(groups).map(function(elt) {
            var group = new Group(elt);
            items.forEach(function(item) {
                item_group = item.querySelector('input[name=\'group\']').value;
                if (item_group == group.name) {
                    //horaire
                    var schedule = item.parentNode.querySelector('.schedule .description').innerText;
                    var description = item.querySelector('.description').innerText;
                    var color = item.style.backgroundColor;
                    var newItem = new Item(description, schedule, item.id, item.className, color);
                    group.items.push(newItem);
                }
            });
            day.groups.push(group);
        });
        timeTable.push(day);
    }
    return timeTable
}

saveB.addEventListener('click', save, false);
function save() {
    var xhr = new XMLHttpRequest();
    // Envoi de la requête.
    var host = window.location.origin + '/diary_timetable_save';
    xhr.open('POST', host);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    var request = JSON.stringify({timetable: getTimetable()});
    xhr.send(request);
    console.log('saved!');
}


function updateSchedule(elt) {
    elt.addEventListener('click', function(e) {
        var s = e.target.parentNode.querySelector('.description');
        var input = prompt('Nouvel horaire:');
        s.innerText = input ? input : s.innerText;
    }, false);
}
Array.from(updateScheduleButtons).forEach(elt => updateSchedule(elt));


function delLine(elt) {
    elt.addEventListener('click', function(e) {
        if (confirm('Supprimer la ligne?')) {
            var line = e.target.parentNode;
            while (line.className != 'line') {
                line = line.parentNode;
            }
            line.parentNode.removeChild(line);
        }
    }, false);
}
Array.from(delLineButtons).forEach(elt => delLine(elt));


function delDay(elt) {
    elt.addEventListener('click', function() {
        if (confirm('Supprimer le jour?')) {
            var dayName = elt.parentNode.querySelector('.day_name').innerText;
            elt.parentNode.parentNode.removeChild(elt.parentNode);
            var items = Array.from(document.getElementsByClassName(dayName));
            items.forEach(function(element) {
                element.parentNode.removeChild(element);
            })
            var days = document.querySelectorAll(".day");
            if (days.length == 0) {
                Array.from(document.querySelectorAll('.line')).map(elt => elt.parentNode.removeChild(elt));
            }
        }

    }, false);
}
Array.from(delDayButtons).forEach(elt => delDay(elt));


function updateDes(elt) {
    elt.addEventListener('click', function() {
        var input = prompt('Une matière:');
        this.parentNode.querySelector('.description').innerText = input ? input.trim() : this.parentNode.querySelector('.description').innerText;
    }, false);
}
Array.from(updateDesButtons).forEach(elt => updateDes(elt));


// Set background color
var colorSelector = document.querySelectorAll('.color');
colorSelector.forEach(function(elt) {
    elt.addEventListener("change", function(e) {
       var color = e.target.value;
       console.log(e.target.parentNode.querySelector('.description').innerText);
       console.log(items);
       items.forEach(function(item) {
            if (item.querySelector('.description').innerText == elt.parentNode.querySelector('.description').innerText) {
                item.style = 'background-color: ' + color;
            }
       });
    }, false);
});


// get pdf
var pdf  = document.querySelector('#pdf');
pdf.addEventListener('click', function() {
    var xhr = new XMLHttpRequest();
    // Envoi de la requête.
    var host = window.location.origin + '/diary_timetable_pdf';
    xhr.open('POST', host);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    var request = JSON.stringify({timetable: getTimetable()});
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
    //window.location.href = "/diary_timetable_pdf"
}, false);
