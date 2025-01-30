"use strict";

// le menu primaire
(function() {
    var links = Array.from(document.querySelectorAll("header a"));
    links.forEach(function(elt) {
        var link = elt.getAttribute('href').split('/')[1];
        var page = window.location.pathname.split('/')[1];
        if (link == page) {
            elt.parentNode.classList.add('a--active');

        }
        else {
            elt.parentNode.classList.remove('a--active');
        }
    });
})();


// le menu secondaire
(function() {
    var links = Array.from(document.querySelectorAll('.navbar2 a'));
    links.forEach(function(elt) {
        var link = elt.pathname.split('/');
        link = link[1] + link[2];
        var page = window.location.pathname.split('/');
        page = page[1] + page[2];
        if (link == page || (link == "journalprevoir" && page == "journalrevoir")) {
            elt.classList.add("a--active");
        }
        else {
            elt.classList.remove("a--active");
        }
    });
})();

// le menu tertiaire
(function() {
    var liens = Array.from(document.querySelectorAll(".navbar3 a"));
    liens.forEach(function(elt) {
        var link = elt.pathname.split('/');
        link = link[1] + link[2] + link[3];
        var page = window.location.pathname.split('/');
        page = page[1] + page[2] + page[3];
        if (link == page) {
            elt.classList.add("a--active");
        }
        else {
            elt.classList.remove("a--active");
        }

    });
})();

// dernnier menu
(function() {
    var liens = Array.from(document.querySelectorAll(".navbar4 a"));
    liens.map(function(elt) {
        if (elt.pathname == window.location.pathname) {
            elt.classList.add("a--active");
        }
        else {
            elt.classList.remove("a--active");
        }

    });
})();