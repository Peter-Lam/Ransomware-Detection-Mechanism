Ransomware-Detection-Mechanism
==============================
[![Build Status](https://travis-ci.com/TranAlan/Ransomware-Detection-Mechanism.svg?token=XYhputEuMBMoSF6Pp5xP&branch=master)](https://travis-ci.com/TranAlan/Ransomware-Detection-Mechanism)  
Ransomware Detection Mechanism (RDM) is a tool for both combining machine learning to detect ransomware viruses within a network and to collect, visualize, and analyze IOCs for emotet. This is a 2020 University of Ottawa undergraduate honours project.

## Project Members
* [Alan Tran](https://www.linkedin.com/in/alantran29/)
* [Ali Bhangoo](https://www.linkedin.com/in/ali-bhangoo-b32828105/)  
* [Peter Lam](https://www.linkedin.com/in/peter-lam-612a00138/)


## Project Supervisor
Professor [Miguel A. Garzón](http://www.site.uottawa.ca/~mgarzon/)

Faculty Member Ph.D., P.Eng.: School of Electrical Engineering and Computer Science
___
Project Organization
------------

    ├── LICENSE            <- Currently NO License
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   │    ├── binetflow <- Bidirectional netflow files for training set.
    │   │    └── validation <- Bidirectional netflow files for validation.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── preprocessed   <- Clean data set.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   ├── raw            <- The original, immutable data dump.
    │   ├── trained        <- The final data set after training and testing.
    │   └── validation     <- Results of validating model with validation data.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── metric             <- Generated files for training and validation metrics
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    └── src                <- Source code for use in this project.
        ├── __init__.py    <- Makes src a Python module
        │
        ├── data           <- Scripts to download or generate data
        │   └── make_dataset.py
        │
        ├── features       <- Scripts to turn raw data into features for modeling
        │   └── build_features.py
        │
        ├── kibana         <- Scripts to collect iocs for kibana.
        │
        ├── models         <- Scripts to train models and then use trained models to make
        │   │                 predictions
        │   ├── predict_model.py
        │   └── train_model.py
        │
        └── visualization  <- Scripts to create exploratory and results oriented visualizations
            └── visualize.py


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

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

> $ source RMD-env/bin/activate (MacOS)
```

Once the venv is activated, python will be run with the venv and all libraries can be installed specifically in the venv. Now we must install key python libraries.
```
> (RDM-env) C:\Ransomware-Detection-Mechanism\pip install -r requirements.txt
```

You are now ready to run scripts. Proceed to Kibana or Training for more information.

## IOC Dashboard (Kibana)

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
For information on how to set up the RDM Kibana Environment with the IOCS, see the [Setting Up Kibana Environment](https://github.com/TranAlan/Ransomware-Detection-Mechanism/wiki/Setting-Up-Kibana-Environment) page.

## Pipeline
    ├── 1. Preparing Data (1.3 mil rows)                  <- /src/data> python make_dataset.py
    │      ├── 1. Download data sets        (8.5  min)
    │      ├── 2. Create raw data           (8.5  sec)
    │      ├── 3. Create interim data       (8    sec)
    │      └── 4. Create preprocessed data  (30   sec)
    ├── 2. Build Features (1.3 mil rows)    (2.28 hours)   <- /src/features> python build_features.py
    ├── 3. Train Model    (1.3 mil rows)    (6.38  hours)  <- /src/models> python train_model.py
    │      ├── One Class SVM                (5.03  hours)
    │      ├── Confidence SCore             (36.4  min)
    │      ├── Save OC Features CSV         (4.4   min)
    │      ├── Linear Regression            (22.2  min)
    │      └── Save LR Features CSV         (4.6   min)
    └── 4. Predict Model                    (24.7  min)     <- /src/models> python predict_model.py

## Docker
### Train
```bash
$ docker build -f DockerTrain/Dockerfile -t train_model:latest .
$ docker run -d train_model:latest
```

### Predict
```bash
$ docker build -f DockerPredict/Dockerfile -t predict_model:latest .
$ docker run -d predict_model:latest
```
### Interact with Container
```bash
$ docker ps -a
$ docker exec -it (container id) bash
```
## Training and Predict Locally
Follow these instructions to run train or predict off the bat.
```bash
$ cd project/src/models
$ python train_model.py
$ python predict_model.py
```
## Performing Pipeline Entirely
Follow these instructions to train or test models from scratch.

```bash
$ cd project/src/data
$ python make_dataset.py
$ cd ../features
$ python build_features.py
$ cd ../models
$ python train_model.py
$ python predict_model.py
```

## More Information
Visit the [Github Wiki](https://github.com/TranAlan/Ransomware-Detection-Mechanism/wiki) for more documentation and research on the project.

### Using BulkAPI JSON Scripts
For information on how to use BulkAPI JSON scripts, see the [How to Use Bulk JSON Scripts](https://github.com/TranAlan/Ransomware-Detection-Mechanism/wiki/How-to-Use-Bulk-JSON-Scripts) page.
