"use strict";

// one
function setGroups() {
    let gr = {};
    Array.from(document.querySelectorAll('.group')).forEach(function (elt)  {
        gr[elt.id] = [];
        Array.from(document.querySelectorAll('.' + elt.id)).forEach(c => gr[elt.id].push(c.id))
    });
    return gr
}

var groups = setGroups();

var randomButtons = Array.from(document.querySelectorAll('.random'));
randomButtons.forEach(b => {
    b.addEventListener('click', function(e) {
        let children = [];
        if (e.target.value == 'all') {
             Object.keys(groups).forEach(i => children = children.concat(groups[i]));
        }
        else {
            children = groups[e.target.value];
        }
        console.log(e.target.value, children);
        choice(document.querySelector('#' + e.target.value), children);
}, false);
});


function choice(screen, list) {
    if (list.length == 0) return;
    screen.innerText = '???';
    let nIntervId;
    let childID;
    let elt;
    nIntervId = setInterval(function (){
        document.querySelectorAll(".child").forEach(s => s.style.backgroundColor = 'white');
        childID = list[Math.floor(Math.random() * list.length)];
        elt = document.querySelector('#' + childID);
        elt.style.backgroundColor = 'yellow';
    }, 50);
    setTimeout(function() {
        clearInterval(nIntervId);
        document.querySelectorAll(".child").forEach(s => s.style.backgroundColor = 'white');
        elt = document.querySelector('#' + childID);
        screen.innerText = document.querySelector('#' + childID).innerText;
        document.querySelector('#' + childID).style.textDecoration = 'line-through';
        console.log(groups);
        Object.keys(groups).forEach(k => {
            groups[k].forEach((c, index) => {
                    if (childID == c) {
                        groups[k].splice(index, 1);
                    }
            });

        });
    }, 1000);
}

// reset
document.querySelector('#reset').addEventListener('click', function(e) {
    groups = setGroups();
    document.querySelectorAll(".child").forEach(s => s.style.textDecoration = 'none');
    console.log('kooi');
}, false);



