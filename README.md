# recall
recall is a web tool for the recovery of **re**levant information through **c**lassification in an **a**ctive **l**earning **l**oop.

# How does it work?
The tool allows an expert user to retrieve information from different sources (in particular from Reddit, Twitter and Google News) by using keywords; and classify as relevant or irrelevant a small number of documents. With this information, the tool can identify, from the total set of recovered documents, those really relevant to the user.

For these tasks the tool makes use of classification models and active learning cycles. You can view the relevant information for the [frontend](frontend/README.md) and the [backend](backend/README.md).

# Preparation
You will need to have Angular, Python, RQ (Redis Queue), and Mongo installed. Once you have the code in your computer, open different console windows to run the following commands:

## for the frontend
```
cd /path/to/the/recall/frontend
ng serve --open
```

## for the backend

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

# How to use
The tool have three sections to use: for the [creation or selection of the model](#creation-or-selection-of-the-model), for the [information retrieval](#information-retrieval) and for the [active learning cycle](#active-learning-cycle).

## Creation or selection of the model
Once you enter your username, you can select an already created model or create a new one. You just need to enter the model name and provide some relevant and irrelevant documents as initial examples. Please think carefully about what type of information elements you want and provide the examples accordingly. The document list must be URLs to valid news, tweets, or reddit posts separated by spaces or newlines.

![image](https://user-images.githubusercontent.com/12433425/146661898-1fc65061-25dc-46de-84cc-528b6e90f663.png)

## Information retrieval
The second section of the web allows you to retrieve information from Twitter, Reddit or Google News. You will select the source, enter the desired keywords, and the tool will proceed with the search. This is time consuming due to limitations associated with the Twitter, Reddit, and Google News APIs. In the meantime, you can continue the active learning cycle.

![image](https://user-images.githubusercontent.com/12433425/146661878-e5aee771-beeb-481d-acde-816147857c40.png)

## Active learning cycle
The last section of the web is related to the manual classification of information elements by the expert user. Here, you decide which documents are relevant to you.

The tool allows you to select the range of relevance of the information items to be classified. By default, the tool retrieves four documents that it doesn't know how to classify: those with 50% -60% relevance. You can access the documents, read them and decide if they are relevant or not, and send this classification to the model. This information will be used to retrain the model, reclassifying all the documents.

![image](https://user-images.githubusercontent.com/12433425/146661941-ab631485-2f03-42b3-a21e-dfc27fe01966.png)

As you can see from the plot, at the beginning the model will not know how to classify the documents: they will all be around 50% of relevance. As you continue to classify items, the tool will learn to identify the documents that are relevant to you.

![image](https://user-images.githubusercontent.com/12433425/146662054-0e291fca-409c-4afc-9828-c3bd25cf1220.png)

You can also see how the model is classifying the news already classified by you, just to get an idea of how it is working.

![image](https://user-images.githubusercontent.com/12433425/146662077-6dd0f8ba-af6a-45de-8377-769c5124b725.png)

# Future work

I want to add the following functionalities

- [ ] Retrieval of documents from user-supplied URLs.
- [ ] Elimination of information items associated with a certain keyword.
- [ ] Download a set of documents in a specific relevance range.
- [ ] Create a new model from a set of documents in a given relevance range.
