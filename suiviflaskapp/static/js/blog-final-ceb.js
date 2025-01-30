"use strict"

var targetButton = document.querySelector('#target-button');
var numbersButton = document.querySelector('#numbers-button');
var soluceButton = document.querySelector('#soluce-button');

// hide solucButtton
soluceButton.style.display = 'None';
var targetButtonClicked = false;
var numbersButtonClicked = false;

// tirage
var target = document.querySelector("#target");
var numbers = Array.from(document.querySelectorAll(".numbers"));
numbersArray = []

targetButton.addEventListener('click', function(e){
    target.innerText = Math.floor(Math.random() * (999 - 1 + 1)) + 1
    targetButtonClicked = true;
    soluceButton.style.display = targetButtonClicked && numbersButtonClicked ? 'Block' : 'None';
}, false);

numbersButton.addEventListener('click', function(e){
    numbers.forEach(function(elt) {
        if (elt.id == 'n1') {
            elt.innerText = [25, 50, 75, 100][Math.floor(Math.random() * 4)];
        }
        else {
            elt.innerText = Math.floor(Math.random() * (9 - 1 + 1)) + 1
        }

    });
    numbersButtonClicked = true;
    soluceButton.style.display = targetButtonClicked && numbersButtonClicked ? 'Block' : 'None';
}, false);

// solution
solucButtton.addEventListener('click', function(e){
    
}, false);

