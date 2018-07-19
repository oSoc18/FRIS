#!/bin/sh
cd backend
python app.py &
cd ../Frontend/src
node app.js &
