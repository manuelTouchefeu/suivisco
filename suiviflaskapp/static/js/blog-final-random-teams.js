"use strict";

function choice(screen, list) {
    let nIntervId;
    let childID;
    let elt;
    nIntervId = setInterval(function (){
        document.querySelectorAll(".child").forEach(s => s.style.backgroundColor = 'white');
        childID = list[Math.floor(Math.random() * list.length)];
        elt = document.querySelector('#' + childID);
        elt.style.backgroundColor = 'green';
        console.log(childID);
    }, 100);
    setTimeout(function() {
        clearInterval(nIntervId);
        console.log(childID);
        elt = document.querySelector('#' + childID);
        screen.innerText = document.querySelector('#' + childID).innerText;
    }, 2000);
}

// teams
var children = [];
Array.from(document.querySelectorAll('.child')).forEach(elt => children.push(elt.id));

var teams = document.querySelector('#teams');

var teamsSelect = document.querySelector('#number');
teamsSelect.addEventListener('change', (e) => {
    // reset
    Array.from(document.querySelectorAll('.team')).forEach(elt => teams.removeChild(elt));
    document.querySelectorAll(".child").forEach(s => s.style.textDecoration = "none");

    // add teams
    let n = e.target.value;
    // add teams to the dom
    for (let i = 1; i <= n; i++) {
        let newTeam = document.createElement('p');
        newTeam.id = 'team' + i;
        newTeam.className = 'team';
        newTeam.innerText = 'Équipe ' + i + ': ';
        teams.appendChild(newTeam);
    }
}, false);

// add children in teams
var go = document.getElementById('go');
go.addEventListener('click', function(e) {
    if (e.target.className == 'disable' || teamsSelect.value == '-') return;
    e.target.className = 'disable';
    // reset
    document.querySelectorAll(".child").forEach(s => s.style.textDecoration = "none");
    Array.from(document.querySelectorAll('.player')).forEach(elt => elt.remove());

    let teamsP = document.querySelectorAll('.team');
    let index = 0;
    let childrenTemp = [];
    children.forEach(c => childrenTemp.push(c));
    let l = childrenTemp.length;

    let choose  = setInterval(function () {
        if (l-- == 0) {
            clearInterval(choose);
            e.target.className = '';
        }
        let childID = childrenTemp[Math.floor(Math.random() * childrenTemp.length)];
        childrenTemp.splice(childrenTemp.indexOf(childID), 1);
        let child = document.getElementById(childID);
        child.style.textDecoration = "line-through";
        let player = document.createElement('span');
        player.className = "player";
        player.innerText = child.innerText + ', ';
        teamsP[index].appendChild(player);
        index = (index < teamsP.length-1 ? index+1 : 0);
    }, 250);
}, false);


