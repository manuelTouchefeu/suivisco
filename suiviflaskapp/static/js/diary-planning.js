"use strict";

Array.from(document.querySelectorAll('input[name=\'del_skill\']')).forEach(elt => elt.addEventListener('click', function() {
       var skill = this.parentNode;
       skill.parentNode.removeChild(skill);
    }) );

// Semaine complète
(function week() {

})();

// Créer le journal
(function send() {

    function Day(name, date, groups=[]) {
        this.name = name;
        this.date = date;
        this.groups = groups;
    }
    function Group(name, items=[]) {
        this.name = name;
        this.items = items;
    }
    function Item(description, schedule, action_global, task, color) {
        this.description = description;
        this.schedule = schedule;
        this.action_global = action_global;
        this.task = task;
        this.color = color;
    }

    var saveButton = document.querySelector('#save');
    var buttons = Array.from(document.querySelectorAll('.rec'));
    var dateForm = document.getElementById('dateForm');

    buttons.forEach(b => b.addEventListener('click' , function() {

        var dayName = document.querySelector('#dayName').innerText;
        var date = document.querySelector('#date').innerText;
        console.log(date);
        if (date == '' && dateForm.style.display == 'none') { // première appel à l'enregistrment
            //date = prompt('Saisir une date (jj/mm/aaaa)');
            dateForm.style.display = 'inline';
            saveButton.style.background = 'green';
            console.log('first call');
            return
        }
        else if (date == '') { // validation de la date
            date = dateForm.value;
            date = date.replace(/-/g, '/');
            // passage au format français de date
            date = date.split('/');
            date = date[2] + '/' + date[1] + '/' + date[0];
        }
        if (date == null)  {
            return;
        }
        else if (/^\d{2}\/\d{2}\/\d{4}$/.test(date) == false) {
            alert(date + ': format de date incorrect!');
            return;
        }
        dateForm.style.display = 'none';
        saveButton.style.background = 'rgba(250, 255, 189, 0.8)';

        document.querySelector('#date').innerText = date;
        date = date.split('/');
        // !!index du mois à partir de 0
        date = new Date(parseInt(date[2], 10), parseInt(date[1], 10)-1, parseInt(date[0], 10));

        var day = new Day(dayName, date.getTime()/1000); // timestamp en secondes
        var groups = Array.from(document.querySelectorAll('th input[name=\'group_name\']'));
        groups.forEach(function(c) {
            var c = new Group(c.value);
            var items = Array.from(document.querySelectorAll('.group_' + c.name));
            items.forEach(function(i) {
                var schedule = i.parentNode.querySelector('.schedule').innerText;
                var description = i.querySelector('.description').innerText;
                var action_global = i.querySelector('.action_global').innerText;
                var task = i.querySelector('.task').innerText;
                var color = i.querySelector('.color').value;
                var newItem = new Item(description, schedule, action_global, task, color);
                c.items.push(newItem);
            });
            day.groups.push(c);
        });
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + "/journal/save";
        xhr.open('POST', host);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        // dest: "save" or "pdf" or "tasks"
        var request = JSON.stringify({dest: b.id, day: day});
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

    }, false) );
})();





