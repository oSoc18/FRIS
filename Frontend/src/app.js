// server.js
// load the things we need
var express = require('express');
var http = require('http');
var https = require('https');
var fs = require('fs');
var app = express();

app.use(express.static(__dirname + '/public'));
// set the view engine to ejs
app.set('view engine', 'ejs');

// use res.render to load up an ejs view file
// index page 
app.get('/', function (req, res) {
    res.render('pages/index');
});

app.get('/keyword?:keyword', function (req, res) {
    res.render('pages/index');
});
// about page 
app.get('/organisation', function (req, res) {
    res.render('pages/organisation');
});


// about page 
app.get('/explore', function (req, res) {
    res.render('pages/explore');
});



//app.listen(8080);
//console.log('8080 is the magic port');

const options = {
    "key": fs.readFileSync('/etc/letsencrypt/live/privkey.pem'),
    "cert": fs.readFileSync('/etc/letsencrypt/live/cert.pem')
}
http.createServer(app).listen(80);
https.createServer(options, app).listen(443);