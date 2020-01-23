# Ransomware-Detection-Mechanism
[![Build Status](https://travis-ci.com/TranAlan/Ransomware-Detection-Mechanism.svg?token=XYhputEuMBMoSF6Pp5xP&branch=master)](https://travis-ci.com/TranAlan/Ransomware-Detection-Mechanism)  
Ransomware Detection Mechanism (RDM) is a tool combining machine learning to detect ransomware viruses, namely Ryuk. Training of the model is done by feeding the machine various binaries of ransomware. This is a 2020 University of Ottawa undergraduate honours project.

## Project Members
* [Alan Tran](https://www.linkedin.com/in/alantran29/)
* [Ali Bhangoo](https://www.linkedin.com/in/ali-bhangoo-b32828105/)  
* [Peter Lam](https://www.linkedin.com/in/peter-lam-612a00138/)


## Project Supervisor
Professor [Miguel A. Garzón](http://www.site.uottawa.ca/~mgarzon/)

Faculty Member Ph.D., P.Eng.: School of Electrical Engineering and Computer Science
___
## Getting Started

Follow these instructions to setup a development environment on your local machine. This is for development or testing purposes.

### Prerequisites

You must install and setup the following to be able to run the project.


* [Setup Python Environment](#Python-Environment)
* [Install Elasticsearch](#Elasticsearch)
* [Install Kibana](#Kibana)


### Python Environment

First we must install [Python 3](https://www.python.org/) and add Python to your PATH. 

Check if Python is correctly installed.
```
> C:\Users\alan1>python -V
Python 3.8.1
```

Next is to create a python 3 virtual enviroment (venv) for the project. On CMD or Linux terminal, find a directory path for your venv. Once you chose a directory, create a venv.
```
> C:\>python3 -m venv RMD-env
```

This will create a venv and folder called RMD-env. To activate the venv you must run the activate script (must be done for every new terminal or CMD).
```
> C:\>RMD-env\Scripts\activate.bat (Windows)

> source RMD-env/bin/activate (MacOS)
```

Once the venv is activated, python will be run with the venv and all libraries can be installed specifically in the venv. Now we must install key python libraries.
```
> (RDM-env) C:\Users\alan1\pip install pylint

> (RDM-env) C:\Users\alan1\pip install requests

> (RDM-env) C:\Users\alan1\pip install pyyaml
```

### Elasticsearch
1. Download and unzip from https://www.elastic.co/downloads/elasticsearch
2. Run bin/elasticsearch (or bin\elasticsearch.bat on Windows)
3. Run curl http://localhost:9200/ or Invoke-RestMethod http://localhost:9200 with PowerShell


### Kibana
1. Download and unzip from https://www.elastic.co/downloads/kibana
2. Open config/kibana.yml in an editor
3. Set elasticsearch.hosts to point at your Elasticsearch instance
4. Run bin/kibana (or bin\kibana.bat on Windows)
5. Point your browser at http://localhost:5601   
### Setting up RDM Kibana Environment

For information on how to set up the RDM Kibana EEnvironment with the IOCS, see the [Setting Up Kibana Environment](https://github.com/TranAlan/Ransomware-Detection-Mechanism/wiki/Setting-Up-Kibana-Environment) page.
