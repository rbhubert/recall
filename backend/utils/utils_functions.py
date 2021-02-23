# a lot of functions...

import os

import numpy as np
import pandas

from classifier.model import DeepLearningModel
from db import database, database
from db.database import newsDB, redditDB
from enums import sources_base, news
from enums.type_data import DataType, type_database, type_search


def restructuring_db():
    old_news = database.newsDB
    new_news = database.newsDB

    all_documents_old = pandas.DataFrame(list(old_news.get_all_info_items()))

    for index, doc in all_documents_old.iterrows():
        if news.sources_base.KEYWORDS in doc:
            if isinstance(doc[news.sources_base.KEYWORDS], list):
                mylist = [each_string.lower() for each_string in doc[news.sources_base.KEYWORDS]]
                keywords = list(dict.fromkeys(mylist))
            else:
                keywords = list(dict.fromkeys(doc[news.sources_base.CLASSIFICATION_BY_MODEL]))
                keywords = [each_string.lower() for each_string in keywords]
        else:
            keywords = list(dict.fromkeys(doc[news.sources_base.CLASSIFICATION_BY_MODEL]))
            keywords = [each_string.lower() for each_string in keywords]

        doc_item = {
            sources_base.URL: doc[news.URL],
            sources_base.CREATION_TIME: doc[news.CREATION_TIME],
            sources_base.TITLE: doc[news.TITLE],
            sources_base.TEXT: doc[news.CONTENT],
            sources_base.KEYWORDS: keywords,
            sources_base.DATATYPE: DataType.GOOGLE,
            sources_base.MODELS: {}
        }

        all_models = doc[news.sources_base.CLASSIFICATION_BY_MODEL]
        for model_name, classification in all_models.items():
            doc_item[sources_base.MODELS][model_name] = None

        classification_user = doc[news.sources_base.CLASSIFICATION]
        if isinstance(classification_user, dict):
            for model_name, classification in classification_user.items():
                doc_item[sources_base.MODELS][model_name] = classification
        else:
            doc_item[sources_base.MODELS]["MiyukiModel"] = classification_user

        new_news.add_info(doc_item)


def restructuring_reddit():
    all_documents = pandas.DataFrame(list(redditDB.get_all_entries()))

    for index, doc in all_documents.iterrows():
        url = doc[sources_base.URL]
        new_doc = doc.to_dict()
        new_doc[sources_base.URL] = "www.reddit.com" + url

        redditDB.add_info(new_doc)
        redditDB.remove_info(url)


def classify_url(model_name, list_relevant, list_norelevant):
    for document in zip(list_relevant, list_norelevant):
        classification = "relevant" if document in list_relevant else "no_relevant"
        newsDB.add_classification_user(
            info_id=document, model_name=model_name, classification=classification)

    training_docs = pandas.DataFrame(columns=[sources_base.TEXT, sources_base.LABEL])
    # an also all the documents that are not classified by the user
    for datatype, database in type_database.items():
        train_docs = pandas.DataFrame(list(database.get_all_classified_by_user(model_name=model_name)))
        if train_docs.empty:
            continue
        train_docs[sources_base.TEXT] = train_docs.apply(lambda row: type_search[datatype].get_text(row), axis=1)
        train_docs[sources_base.LABEL] = train_docs.apply(lambda row: row[sources_base.MODELS][model_name],
                                                          axis=1)

        training_docs = training_docs.append(train_docs[[sources_base.TEXT, sources_base.LABEL]])

    classifier = DeepLearningModel(model_name)
    classifier.train(training_set=training_docs)

    return "all done"


def get_documents_in_buckets(model_name, examples_by_bin=4):
    def __probability(classifier, row):
        prediction = classifier.predict(type_search[row[sources_base.DATATYPE]].get_text(row).replace("\n", ""))
        probability = prediction[sources_base.PROBABILITY]
        value = probability if prediction[sources_base.LABEL] == "__label__relevant" else 1 - probability

        return value

    all_documents = pandas.DataFrame()
    for datatype, database in type_database.items():
        to_classify = pandas.DataFrame(list(database.get_elements_by_model(model_name=model_name)))
        all_documents = all_documents.append(to_classify)

    classifier = DeepLearningModel(model_name)
    all_documents[sources_base.PROBABILITY] = all_documents.apply(
        lambda row: __probability(classifier, row), axis=1)

    docs_for_return = {}
    range_np = np.arange(0.5, 1.0 + 0.05, 0.05)
    last = range_np[-1]
    for element in reversed(range_np[:-1]):
        documents_in_bin = all_documents[
            (all_documents[sources_base.PROBABILITY] <= last) &
            (all_documents[sources_base.PROBABILITY] > element)]

        text = str(int(last * 100)) + "%-" + str(int(element * 100)) + "%"
        last = element

        n_examples = min(examples_by_bin, len(documents_in_bin))
        docs_for_return[text] = [element[sources_base.URL] for index, element in
                                 documents_in_bin.sample(n_examples).iterrows()]

    return docs_for_return


def change_names(directory):
    df = pandas.DataFrame(list(newsDB.get_elements_by_model("MiyukiModel", include_classified=True)))
    df[sources_base.TEXT] = df.apply(
        lambda row: row[sources_base.TITLE] + row[sources_base.TEXT], axis=1)

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            old_name = os.path.join(directory, filename)
            file = open(old_name)
            text = file.read()
            text2 = text[0: 20]
            result = df[df[sources_base.TEXT].str.startswith(text2)]
            if len(result.index) > 1:
                text3 = text[0:30]
                result = df[df[sources_base.TEXT].str.startswith(text3)]
            file.close()

            new_name = result["url"].iloc[0]
            print(old_name, "--->", new_name)
        else:
            # go again through directories
            change_names(directory + filename + "/")

# model_name = "kharisse_violence_migrant_women"
# x = get_documents_in_buckets(model_name=model_name)
# # print(x)
