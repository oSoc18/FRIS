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
    rawFile.open("GET", "js/json/"+file, true);
    rawFile.onreadystatechange = function () {
        if (rawFile.readyState === 4 && rawFile.status == "200") {
            callback(rawFile.responseText);
        }
    }
    rawFile.send(null);
}

function cosElementCircle(i,length,width){
    return (radius * Math.cos((i / (length / 2)) * Math.PI)) + (width / 2);
}

function sinElementCircle(i,length,width){
    return (radius * Math.sin((i / (length / 2)) * Math.PI)) + (width / 2);
}