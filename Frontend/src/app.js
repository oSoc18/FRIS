// server.js
// load the things we need
var express = require('express');
var app = express();
app.use(express.static(__dirname + '/public'));
// set the view engine to ejs
app.set('view engine', 'ejs');

// use res.render to load up an ejs view file


app.get('/keyword?:keyword', function (req, res) {
    res.render('pages/index');
});

// index page 

app.get('/', function (req, res) {
    res.render('pages/index');
});
// about page 
app.get('/explore', function (req, res) {
    res.render('pages/explore');
});

app.listen(8080);
console.log('8080 is the magic port');