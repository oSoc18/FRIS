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