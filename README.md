![OpenSummerofCode2018](https://github.com/oSoc18/FRIS/blob/master/Frontend/src/public/css/img/Osoc2018.jpg?raw=true "Open Summer of Code 2018")

# FRIS

## Introduction

FRIS is a research portal aimed at curious citizens, businesses, policymakers, journalists and researchers. The FRIS research portal, run by the Department of Economy, Science and Innovation (EWI) wants to be a simple, transparent and open platform to make Flemish research information publicly available. It is a virtual space collecting all information about publicly-funded scientific research in Flanders. Our team started to  is create a website, Open Expertise, that visualizes the data so it’s easy and user-friendly to interpret by the user. 

The aim is to create an expert finding tool that makes it easier to find expertise in Flanders. For example, a business could be looking for a researcher who specializes in Machine-Learning: they will be able to find and compare research in that field of study and find contact information in order to start a collaboration with the research institute. 

The FRIS research portal will make finding the right researcher for your project easier and more efficient!

Partners:
 - https://www.ewi-vlaanderen.be/
 - https://www.researchportal.be/nl


## Clone repository and Install important programs

```bash 
git clone https://github.com/oSoc18/FRIS.git
```

For our webapp you will need a few programms installed (newer versions might work):
 - Node.js v8
 - npm v5.6.0
 - Python3 3.7.0

## Before you run 

Before you can run the webapp you'll have to :
(NOTE: all this is done in command line interface)
 - Navigate to FRIS\Frontend\src
```bash 
cd \FRIS\Frontend\src
```
 - Install the necessary node modules.
```bash 
npm install
```
 - Navigate to FRIS\Backend
```bash 
cd \FRIS\Backend
```
 - Get all the python libraries.
```bash 
pip3 install -r requirements.txt
```

NOTE:
	If on windows there could be some problems with lxml library.
	to fix this go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml 
	and download the lates version of lxml.
	than navigate to the downloaded file en run install the file.	
```bash
pip install 'lxml-4.2.3-cp37-cp37m-win_amd64.whl'
```

## Run

Now you can start running the services :

### Run webserver

 - Navigate back to Frontend\src\ and run 'app.js' to launche the website.
```bash 
node app.js
```

### Run dataserver (Python)
 - Navigate to 'Backend\ and run app.py
```bash 
python3 app.py
```

Note: if python3 is the default python 
```bash 
python app.py  
```
 - You also need to create a nat in the firewall (linux command)
```bash 
iptables -t nat -I PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -I PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8000
```
Note: You can also launch the scripts in background, you need to add " &" at the end of the script
Note: We used port 8080 for our service
