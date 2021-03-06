

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
    "key": fs.readFileSync('/etc/letsencrypt/live/openexpertise.be/privkey.pem'),
    "cert": fs.readFileSync('/etc/letsencrypt/live/openexpertise.be/cert.pem')
}

http.createServer(function (req, res) {
    res.writeHead(301, { "Location": "https://" + req.headers['host'] + req.url });
    res.end();
}).listen(8080);
https.createServer(options, app).listen(8443);
