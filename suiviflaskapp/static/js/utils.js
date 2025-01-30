"use strict";
// Pour modifier et ajouter compétenes et observables
// https://www.creativejuiz.fr/blog/javascript/recuperer-parametres-get-url-javascript
function getFromURL(param) {
	var vars = {};
	window.location.href.replace(location.hash, '').replace(
		/[?&]+([^=&]+)=?([^&]*)?/gi, // regexp
		function( m, key, value ) { // callback
			vars[key] = value !== undefined ? value : '';
		}
	);
	if ( param ) {
		return vars[param] ? vars[param] : null;
	}
	return vars;
}


var buttons = document.querySelectorAll('.rotate');
buttons.forEach(function(button) {
     button.addEventListener('click', function() {
        var imageContainer = this.parentNode;
        var image = imageContainer.querySelector('img');
        while (!image) {
            imageContainer = imageContainer.parentNode;
            image = imageContainer.querySelector('img');
        }
        var src = image.getAttribute('src').split('?')[0]
        var xhr = new XMLHttpRequest();
        var host = window.location.origin + '/rotate-image';
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({image: src}));
        // retour de la requête
        xhr.addEventListener("readystatechange", function() {
            if (xhr.readyState === xhr.DONE) {
                image.src = xhr.responseText + '?' + Math.random();
            }
        }, false);
     }, false);
});