----------------------------------------------------------------------------

                  ______   _____    _____    _____        ___  
                 |  ____| |  __ \  |_   _|  / ____|      / _ \ 
                 | |__    | |__) |   | |   | (___       | | | |
                 |  __|   |  _  /    | |    \___ \      | | | |
                 | |      | | \ \   _| |_   ____) |  _  | |_| |
                 |_|      |_|  \_\ |_____| |_____/  (_)  \___/ 
                                               
                                               
----------------------------------------------------------------------------

The purpose of Fris.0 is to build a bridge between KMO’s and Universities. We provide a way to find certain expertise in a specific domain. Our website gives a easy and intuitive
way to find and explore researchgroups.


----------------------------------------------------------------------------
INSTALATION

Install:
Node.js minimum v8
npm minimum v5.6.0
Python3 3.7.0
----------------------------------------------------------------------------
To run the node website:

Navigate to FRIS\Frontend\src
run: 'npm install' to get the necessary node modules.
run: 'node app.js' to launche the website.

To run the python serverr:

Navigate to FRIS\Backend
run: 'python requirements.txt’ to get all the libraries.

if on windows there could be some problems with lxml library.
to fix this go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml 
and download the lates version of lxml.
than navigate to the downloaded file en run: ‘pip install “filename”.

To launch the python server :
python3 app.py
or  if python3 is the default python :
python app.py  &


You also need to create a nat in the firewall :
 iptables -t nat -I PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

Where the port 8080 is the port of the node application.
