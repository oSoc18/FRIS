var page = [];

function appendPage(attributes) {
    page.push(attributes);
    localStorage.setItem("page", attributes);
    l(localStorage.getItem("page"));
}

function getPage() {
    return page;
}

function readJSON(file) {
    var result;
    $.getJSON(file, {}, function (data) {
        result = data;
    });
    return result;

}

function parseJSON(file) {
    return JSON.parse(file);
}

function wrapWord(word) {
    return word.replace(/ .*/, '');
}
// Shortchut of console.log
function l(text) {
    console.log(text);
}
// Remove double quote from string object
function clearString(string) {
    return string.replace(/['"]+/g, '');
}

function readTextFile(file, callback) {
    var rawFile = new XMLHttpRequest();
    rawFile.overrideMimeType("application/json");
    rawFile.open("GET", "js/json/" + file, true);
    rawFile.onreadystatechange = function () {
        if (rawFile.readyState === 4 && rawFile.status == "200") {
            callback(rawFile.responseText);
        }
    }
    rawFile.send(null);
}

function cosElementCircle(i, length, width) {
    return (radius * Math.cos((i / (length / 2)) * Math.PI)) + (width / 2);
}

function sinElementCircle(i, length, width) {
    return (radius * Math.sin((i / (length / 2)) * Math.PI)) + (width / 2);
}

function getJSONP(url, success) {

    var ud = '_' + +new Date,
        script = document.createElement('script'),
        head = document.getElementsByTagName('head')[0] ||
        document.documentElement;

    window[ud] = function (data) {
        head.removeChild(script);
        success && success(data);
    };

    script.src = url.replace('callback=?', 'callback=' + ud);
    head.appendChild(script);

}

function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
}


function minimizeText(texte, limit) {
    l(texte);
    if (texte.length > limit) {
        return texte.substring(1, 100);
    }

}