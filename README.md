# Ransomware-Detection-Mechanism
[![Build Status](https://travis-ci.com/TranAlan/Ransomware-Detection-Mechanism.svg?token=XYhputEuMBMoSF6Pp5xP&branch=master)](https://travis-ci.com/TranAlan/Ransomware-Detection-Mechanism)  
Ransomeware Detection Mechanism (RDM) is a tool combining machine learning to detect ransomware viruses. Training of the model is done by feeding the machine various binaries of ransomware. This is a 2020 University of Ottawa undergraduate honours project.

## Project Members
Ali Bhangoo  
Peter Lam  
Alan Tran

## Project Supervisor
Professor [Miguel A. Garzón](http://www.site.uottawa.ca/~mgarzon/)

Faculty Member Ph.D., P.Eng.: School of Electrical Engineering and Computer Science
___
## Getting Started

Follow these instructions to setup a development enviroment on your local machine. This is for development or testing purposes.

### Prerequisites

You must install and setup these softwares to be able to run the project.

```
Setup Python Environment
Install LogStash
Install Elasticsearch
Install Kibana
```

### Installing

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
> C:\>RMD-env\Scripts\activate.bat
```

Once the venv is activated, python will be run with the venv and all libraries can be installed specifically in the venv. Now we must install key python libraries.
```
> (RDM-env) C:\Users\alan1\pip install pylint

> (RDM-env) C:\Users\alan1\pip install requests

> (RDM-env) C:\Users\alan1\pip install pyyaml
```

