# Backend for [recall](./README.md)

The backend for this project was written with Python 3.8.1. The following libraries were used:
- For the server general functionality: 
  - [Flask](https://flask.palletsprojects.com/en/2.0.x/) for the set up of the web server. 
  - [rq](https://python-rq.org/) for queueing jobs and processing them in the background with workers (specifically for the searches in Reddit, Google News and Twitter).
- For the recovering of documents:
  - [googlesearch](https://github.com/Nv7-GitHub/googlesearch) and [newspaper3k](https://newspaper.readthedocs.io/en/latest/) for recovering news from Google News and scraping its content.
  - [tweepy](https://www.tweepy.org/) and [twarc](https://github.com/DocNow/twarc) for retrieving tweets and all the comments related.
  - [praw](https://github.com/praw-dev/praw) for recovering reddit posts.
- For data management:
  - [pymongo](https://pymongo.readthedocs.io/en/stable/) for the database (MongoDB) management.
  - [pandas](https://pandas.pydata.org/) for the data manipulation.
  - [fasttext](https://fasttext.cc/) for the creation and training of classification models.


#  How to run the backend

## Requeriments
Install these before running the server.

```
gunicorn===20.0.4
rq===1.4.2
redis===3.5.3
flask===1.1.2
flask-cors===3.0.8
pymongo===3.10.1

googlesearch===2.0.3
newspaper3k===0.2.8
tweepy===3.8.0
twarc===1.8.3
praw===7.0.0

pandas===1.2.1
fasttext===0.9.2
```

## Commands 
Run the following commands to have the server working properly.

Server:
```
cd /path/to/the/recall/backend
source ~/path/to/the/recall/backend/.venv/bin/activate
export FLASK_APP=main_app.py
flask run
```

Redis Queue:
```
cd /path/to/the/recall/backend
redis-server
```
Worker
```
cd /path/to/the/recall/backend
source ~/path/to/the/recall/backend/.venv/bin/activate
python worker.py
```

Database
```
mongod --dbpath ~/data/db
```

# Implementation details
For the text classification model we use the function `train_supervised` from fasttext. Fasttext uses multinomial logistic regression for the classification task, where the sentence/document vector corresponds to the features.

In this project, the parameters for training the model are: `epoch=50, lr=1.0, word_n_grams=1`. 
For the pre-processing of the data, the following tasks are carried out:
- In the case of unbalanced dataset (when we have a greater number of, say, irrelevant than relevants documents), we have a basic oversampling function that takes random samples from the minority class until we get the number of documents in the majority class.
- For each document, we do a basic pre-processing that consists of convert text to lowercase and adding spaces around special characters.

The tool also provides other preprocessing functions, such as cleaning special characters and removing punctuations, removing numbers, or replace contraction.


