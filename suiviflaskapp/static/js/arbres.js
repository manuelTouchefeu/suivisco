"use strict";

function getRandomInt(min, max) {
    return min + Math.floor(Math.random() * (max - min));
}

window.addEventListener('load' , function() {

    function tree(startX, startY, len, angle, branchWidth, red, green) {
            ctx.strokeStyle = "rgba(" + red + ", " + green + ", 0, 0.8)";
            ctx.lineWidth = branchWidth;
            ctx.beginPath();
            ctx.save();
            ctx.translate(startX, startY);
            ctx.rotate(angle * Math.PI/180);
            ctx.moveTo(0, 0);
            ctx.lineTo(0, -len);
            ctx.stroke();

            if(len < 10) {
                ctx.restore();
                return;
            }

            tree(0, -len, len*0.8, -getRandomInt(10, 40), branchWidth*0.8, red+getRandomInt(0, 25), green+getRandomInt(0, 25));
            tree(0, -len, len*0.8, getRandomInt(10, 40), branchWidth*0.8, red+getRandomInt(0, 25), green+getRandomInt(0, 25));
            ctx.restore();
    }

    var canvas = document.getElementById('canvas');
    canvas.width = window.innerWidth;
    //canvas.height = window.innerHeight;
    var ctx = canvas.getContext('2d');
    for (var i=0; i<4; i++) {
        var dist = getRandomInt(canvas.height*0.7, canvas.height);
        var red = 100;
        tree(getRandomInt(100, canvas.width-100), dist,
                          getRandomInt(60, 130), 0, getRandomInt(5, 10), red, red);
    }

}, false);
