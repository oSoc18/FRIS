![OpenSummerofCode2018](https://github.com/oSoc18/FRIS/blob/master/Frontend/src/public/css/img/Osoc2018.jpg?raw=true "Open Summer of Code 2018")

# FRIS


## Intruduction

FRIS is a research portal aimed at curious citizens, businesses, policymakers, journalists and researchers. The FRIS research portal, run by the Department of Economy, Science and Innovation (EWI) wants to be a simple, transparent and open platform to make Flemish research information publicly available. It is a virtual space collecting all information about publicly-funded scientific research in Flanders. Our team started to  is create a website, Open Expertise, that visualizes the data so it’s easy and user-friendly to interpret by the user. 

The aim is to create an expert finding tool that makes it easier to find expertise in Flanders. For example, a business could be looking for a researcher who specializes in Machine-Learning: they will be able to find and compare research in that field of study and find contact information in order to start a collaboration with the research institute. 

The FRIS research portal will make finding the right researcher for your project easier and more efficient!

Partners:
 - https://www.ewi-vlaanderen.be/
 - https://www.researchportal.be/nl


## Install important programs

For our webapp you will need a few programms installed:
 - Node.js minimum v8
 - npm minimum v5.6.0
 - Python3 3.7.0

## Before you run 

Before you can run the webapp you'll have to : 
(NOTE: all this is done in command line interface)
 - Navigate to FRIS\Frontend\src
```bash 
cd \FRIS\Frontend\src
```
 - run: 'npm install' to get the necessary node modules.
```bash 
npm install
```
 - Navigate to FRIS\Backend
```bash 
cd \FRIS\Backend
```
 - run: 'python requirements.txt’ to get all the libraries.
```bash 
python requirements.txt
```

NOTE:
	if on windows there could be some problems with lxml library.
	to fix this go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml 
	and download the lates version of lxml.
	than navigate to the downloaded file en run: ‘pip install “filename”.
	```bash 
	pip install 'lxml-4.2.3-cp37-cp37m-win_amd64.whl'
	```

## Run	
### Run webserver
 - navigate back to: Frontend\src\ and run: 'node app.js' to launche the website.
```bash 
node \app.js
```

### Run dataserver (Python)
 - navigate to: 'Backend\ and run: 'python3 app.py'
```bash 
python3 app.py
```

Note: or  if python3 is the default python :
```bash 
python app.py  &
```
You also need to create a nat in the firewall :
```bash 
iptables -t nat -I PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
```

Where the port 8080 is the port of the node application.
