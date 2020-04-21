FROM python:3.8

WORKDIR /usr/RDM/
RUN mkdir -p data/processed
RUN mkdir src

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY data/processed/processed.csv data/processed/processed.csv
COPY src/utils src/utils
COPY src/models src/models

WORKDIR src/models/

CMD [ "python3", "train_model.py" ]
