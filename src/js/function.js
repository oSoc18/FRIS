var seed = {
    "source":0
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