"use strict";

// nombre de connections et de visiteurs
(function() {

    var days = document.querySelectorAll('.day');
    var i, c = days.length;
    var connections, nb_visiteurs;
    for (var i=0; i<c; i++) {
        connections = document.querySelectorAll('.' + days[i].id);
        days[i].querySelector('.nb_connections').innerText = connections.length;

        // visiteurs uniques
        connections = Array.from(connections).map(elt => elt.classList.item(1));
        connections = connections.filter(function(elt, index, self) {
            return self.indexOf(elt) === index
        });
        days[i].querySelector('.nb_visitors').innerText = connections.length;
    }

    // totaux
    connections = document.querySelectorAll('.visit');
    document.querySelector('#nb_connections').innerText = connections.length;

    connections = Array.from(connections).map(function(elt) {
        return elt.classList.item(1);
    });
    connections = connections.filter(function(elt, index, self) {
        return self.indexOf(elt) === index
    });
    document.querySelector('#nb_visitors').innerText = connections.length;

})();

// visibilité des visiteurs uniques
(function() {
    var visits = Array.from(document.querySelectorAll('.visit'));
    var visitor_id, visitsOfThisVisitor;

    visits.forEach(visit => {

        visit.addEventListener('mouseenter', function(e) {
            visitor_id = visit.classList.item(1);
            visitsOfThisVisitor = Array.from(document.querySelectorAll('.' + visitor_id));
            visitsOfThisVisitor.forEach(votv => votv.style.backgroundColor = 'yellow'); // toujours 1!!!!
            this.style.backgroundColor = 'yellow'
        }, false);

        visit.addEventListener('mouseleave', function(e) {
            visitor_id = visit.classList.item(1);
            visitsOfThisVisitor = Array.from(document.querySelectorAll('.' + visitor_id));
            visitsOfThisVisitor.forEach(votv => votv.style.backgroundColor = 'white');
            this.style.backgroundColor = 'white'
        }, false);
    } );

})();
