"use strict";

var HOST = window.location.origin + '/blog-ecole/visio';
var frame = document.querySelector('#meet');
var info = document.querySelector('#info');
var stop = document.querySelector('#stop');

var meeting = false;


const domain = 'meet.jit.si';
const options = {
    roomName: '',
    width: 700,
    height: 700,
    configOverwrite: { startWithAudioMuted: true },
    parentNode: frame
};


// chez moi
if (stop != null) {

     // si status = stop (visio commencée (retour après déconnexion))
    console.log(stop.innerText);
    if (stop.innerText == 'Stop') {
        var ref = stop.value
        options.roomName = 'Classe des CM1-CM2/' + ref;
        const api = new JitsiMeetExternalAPI(domain, options);
    }

    stop.addEventListener('click', function(e) {

        var visioStatus = (e.target.innerText == 'Start'? 'begin' : 'stop');
        console.log(visioStatus);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', HOST);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        var request = JSON.stringify({op: visioStatus});
        xhr.send(request);
        // retour
        xhr.addEventListener("readystatechange", function() {
            if (xhr.readyState === xhr.DONE) {
                var json = JSON.parse(xhr.responseText);
                console.log(json);
                if (json['status'] == true) {
                    options.roomName = 'Classe des CM1-CM2/' + json["ref"];
                    const api = new JitsiMeetExternalAPI(domain, options);
                    stop.innerText = 'Stop';
                }
                else if (json['status'] == false) {
                    stop.innerText = 'Start';
                    info.innerText = "La réunion est finie!";
                }
            }
        }, false);
    }, false);
}

// chez les autres
else {
    setInterval(function(){
        var xhr = new XMLHttpRequest();
        xhr.open('POST', HOST);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        var request = JSON.stringify({op: 'ask'});
        xhr.send(request);
        xhr.addEventListener("readystatechange", function() {
            if (xhr.readyState === xhr.DONE) {
                var json = JSON.parse(xhr.responseText);
                console.log(json);
                if (!json['status'] && !meeting) {
                    console.log('pas pret');
                }
                else if (json['status'] && meeting) {
                    console.log('Réunion en cours')
                }
                else if (json['status'] && !meeting) {
                    console.log('on commmence');
                    meeting = true;
                    info.innerText = "C'est l'heure!";
                    options.roomName = 'Classe des CM1-CM2/' + json["ref"];
                    const api = new JitsiMeetExternalAPI(domain, options);
                }
                else if (!json['status'] && meeting) {
                    console.log('on arrete');
                    meeting = false;
                    window.location.reload();
                }
            }
        }, false);
    }, 1000);
}

