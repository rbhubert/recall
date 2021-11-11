import pandas

from classifier.model import DeepLearningModel
from db.database import modelDB, userDB
from enums import sources_base
from enums.type_data import type_database, DataType, type_search


# TODO
# Error management:
# each function return pair (#1, #2)
# #1 is error code: if 1 not error, if 0 error
# #2 is information to return or error message


def get_user(username):
    """
    Return the information associated with :username:
    If not :username: is registered returns an error
    :param username:
    :return:
    """
    user_info = userDB.get_user(username)

    if user_info is None:
        return 0, "This user does not exist"
    else:
        return 1, user_info


def create_model(model_name, documents, username):
    """
    Creates a new model. Uses :documents: to train the model.
    Adds the model to the current ACTIVE_MODELS in the server
    :param model_name: the name of the model
    :param documents: examples documents to train the model
    :return:
    """
    model_id = __get_model_id(model_name)
    model_info = modelDB.get_model(model_id)

    if model_info:
        return 0, "This name is not available, please provide other"

    # retrieve documents first, each doc is [url, classif]
    training_docs = __retrieve_documents_df(model_name=model_name, documents=documents)

    # creation and training of the model
    model = DeepLearningModel(name=model_name, training_docs=training_docs)
    model.save_model()
    userDB.add_model(username, model_name)

    return 1, "Model trained successfully"


def load_model(model_name):
    """
    Loads the model. Adds the model to the current ACTIVE_MODELS in the serverr
    :param model_name:
    :return:
    """
    model_id = __get_model_id(model_name)
    model_info = modelDB.get_model(model_id)

    if model_info is None:
        return 0, "This model does not exist"
    else:
        return 1, model_info


def search_keywords(data_type, model_name, query):
    """
    Searches news/reddit posts/tweets using the query.
    Adds the results to the dataframe of the model in ACTIVE_MODELS
    :param data_type: type of data to make the search (google, reddit or twitter)
    :param model_name: name of the model
    :param query: the keywords to make the search
    :return:
    """

    query = query.lower()  # we always lowercase the query

    type_search[data_type].search_with_keywords(keywords=query, model_name=model_name)

    return 1, "Search done successfully"


def get_items_to_classify(model_name, range_probability):
    """
    Returns all the info items of the model with probability of relevance in the range defined by the user
    :param model_name:
    :param range_probability:
    :return:
    """

    range_start = float(range_probability)
    range_end = range_start + 0.1

    classifier = DeepLearningModel(model_name)
    df_documents = __get_dataframe(model_name, classifier)
    df_documents["relevance_probability"] = df_documents.apply(lambda row: __get_relevance_probability(row), axis=1)

    # get documents in range
    df_in_range = df_documents[
        (df_documents["relevance_probability"] >= range_start) & (df_documents["relevance_probability"] < range_end)]

    # return the information associated to each document
    documents_list = []

    for index, document in df_in_range.iterrows():
        datasearch = document[sources_base.DATATYPE]
        doc_information = datasearch.get_basic_information(document)

        doc_information[sources_base.CLASSIFICATION_BY_MODEL] = {
            sources_base.LABEL: document[sources_base.LABEL],
            sources_base.PROBABILITY: document[sources_base.PROBABILITY]
        }
        doc_information["number_words"] = len(datasearch.get_text(document).split())

        documents_list.append(doc_information)

    return 1, {"documents": documents_list}


def classify_documents(model_name, documents_list):
    """
    Classify the documents using the model ;model_name;
    Each document in documents has (url, classification_user)
    :param model_name: 
    :param documents_list: list of pairs (url, classification_user)
    :return: 
    """

    # save classification by user in db
    for document in documents_list:
        classification = "relevant" if document[sources_base.LABEL] else "no_relevant"
        type_database[document[sources_base.DATATYPE]].add_classification_user(
            info_id=document[sources_base.URL], model_name=model_name, classification=classification)

    # getting the training documents for the classifier
    training_docs = pandas.DataFrame(columns=[sources_base.TEXT, sources_base.LABEL])

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

    return 1, {"Message": "Model re-trained successfully"}


def get_information_plot(model_name, already_classified=False):
    classifier = DeepLearningModel(model_name)
    df_documents = __get_dataframe(model_name=model_name, classifier=classifier, already_classified=True)

    df_documents["user_label"] = df_documents[sources_base.MODELS].apply(lambda x: x[model_name])

    df_documents["model_probability"] = df_documents.apply(lambda row: __get_relevance_probability(row), axis=1)
    df_documents["number_words"] = df_documents.apply(lambda row: __get_number_words(row), axis=1)
    df_documents["text_to_display"] = df_documents.apply(lambda row: __get_text(row), axis=1)

    df_user = df_documents[~df_documents["user_label"].isnull()]
    df_relevant = df_user[df_user["user_label"] == "relevant"]
    df_no_relevant = df_user[df_user["user_label"] != "relevant"]

    if already_classified:
        user_x = df_documents.apply(lambda row: 1 if row["user_label"] == "relevant" else 0, axis=1)

        to_return = {
            "traces": {
                "number_relevants": df_relevant.shape[0],
                "number_no_relevants": df_no_relevant.shape[0],
                "number_model": df_documents.shape[0] - df_user.shape[0],
                "trace_model": {
                    "x": df_documents["model_probability"].values.tolist(),
                    "y": df_documents["number_words"].values.tolist(),
                    "text": df_documents["text_to_display"].values.tolist()
                },
                "trace_user": {
                    "x": user_x.values.tolist(),
                    "y": df_user["number_words"].values.tolist(),
                    "text": df_user["text_to_display"].values.tolist()
                },
                "max_words": max(df_documents["number_words"])
            },
            "classified_by_user": {
                "relevant": [],
                "no_relevant": []
            }
        }
    else:

        to_return = {
            "trace_relevant": {
                "x": df_relevant["model_probability"].values.tolist(),
                "y": df_relevant["number_words"].values.tolist(),
                "text": df_relevant["text_to_display"].values.tolist()
            },
            "trace_no_relevant": {
                "x": df_no_relevant["model_probability"].values.tolist(),
                "y": df_no_relevant["number_words"].values.tolist(),
                "text": df_no_relevant["text_to_display"].values.tolist()
            },
        }

    return to_return


def __get_number_words(row):
    datasearch = row[sources_base.DATATYPE]
    return len(datasearch.get_text(row).split())


def __get_text(row):
    title = row[sources_base.TITLE]
    url = row[sources_base.URL]

    return title + "\n" + url


def update_document(url_item, title, text):
    # todo
    return


def __retrieve_documents_df(model_name, documents):
    """
    Given a list of (url, classification) from the user, retrieve the items and create a dataframe
    :param model_name: name of the model
    :param documents: list of pairs (url, classification)
    :return: dataframe with the recovered items
    """
    df_ = pandas.DataFrame(["url", "classification", "datatype"])

    # the urls can be from reddit, twitter or some newspaper portal
    for doc in documents:  # doc[0] url, doc[1] classification
        some_part_url = doc[0].split("//")[1]
        if "reddit" in some_part_url:
            df_ = df_.append({"url": doc[0], "classification": doc[1], sources_base.DATATYPE: DataType.REDDIT},
                             ignore_index=True)
        elif "twitter" in some_part_url:
            df_ = df_.append({"url": doc[0], "classification": doc[1], sources_base.DATATYPE: DataType.TWITTER},
                             ignore_index=True)
        else:
            df_ = df_.append({"url": doc[0], "classification": doc[1], sources_base.DATATYPE: DataType.GOOGLE},
                             ignore_index=True)

    documents_df = pandas.DataFrame()
    for datatype, search in type_search.items():
        df_ = df_[df_[sources_base.DATATYPE] == datatype]
        urls = df_[["url", "classification"]].to_records(index=False)
        documents_df = documents_df.append(search.retrieve_from_urls(model_name=model_name, url_list=urls))

    return documents_df


# this will get the classification from the model for each document
def __get_dataframe(model_name, classifier, already_classified=False):
    """
    Gets all documents associated with the model and classify them
    :param model_name:
    :param classifier:
    :return: a dataframe with the documents and its classification (label and probability)
    """
    df_documents = pandas.DataFrame()

    for key, db in type_database.items():
        list_docs = pandas.DataFrame(
            list(db.get_elements_by_model(model_name=model_name, include_classified=already_classified)))
        list_docs[sources_base.DATATYPE] = list_docs.apply(lambda row: type_search[key], axis=1)

        if list_docs.empty:
            continue

        list_docs = __classify_dataframe(df_documents=list_docs, classifier=classifier)
        df_documents = df_documents.append(list_docs, ignore_index=True)

    # todo remove unnecessary columns of df_documents

    return df_documents


def __classify_dataframe(df_documents, classifier):
    """
    Classify the documents using the classifier
    :param df_documents:
    :param classifier:
    :return: a dataframe with the documents and its classification (label and probability)
    """
    df_documents[sources_base.LABEL], df_documents[sources_base.PROBABILITY] = zip(*df_documents.apply(
        lambda row: __get_prediction(row, classifier), axis=1))

    return df_documents


def __get_prediction(row, classifier):
    """
    Return the prediction of the classifier for a given document
    :param row:
    :param classifier:
    :return:
    """
    text = row[sources_base.DATATYPE].get_text(row).replace("\n", "")
    result = classifier.predict(text)
    classification = result[sources_base.LABEL].replace("__label__", "")
    probability = result[sources_base.PROBABILITY]

    return classification, probability


def __get_relevance_probability(document):
    """
    Return the probability of the document of being relevant
    :param document:
    :return:
    """
    probability = document[sources_base.PROBABILITY]
    return probability if document[
                              sources_base.LABEL] == "relevant" else 1 - probability


def __get_model_id(model_name):
    """
    Returns the id for the model_name
    :param model_name:
    :return:
    """
    model_id = model_name.lower().replace(" ", "_")
    return model_id
