import math

import matplotlib.pyplot as plt
import numpy as np
import pandas
from matplotlib import animation

from classifier.model import DeepLearningModel
from db.database import newsDB
from enums import sources_base
#
# def histogram(model_name):
#     def __probability(row):
#         probability = row[model_name][sources_base.CLASSIFICATION_PROBABILITY]
#         value = probability if row[model_name][
#                                    sources_base.CLASSIFICATION_MODEL] == "relevant" else 1 - probability
#
#         return value
#
#     all_documents = pandas.DataFrame(list(newsDB.get_all_by_model(model_name)))
#     all_documents[sources_base.CLASSIFICATION_PROBABILITY] = all_documents[sources_base.CLASSIFICATION_BY_MODEL].apply(
#         lambda dict_x: __probability(dict_x))
#
#     new_df = all_documents.groupby(
#         pandas.cut(all_documents[sources_base.CLASSIFICATION_PROBABILITY], np.arange(0, 1.0 + 0.05, 0.05))).count()[
#         sources_base.CLASSIFICATION_PROBABILITY]
#
#     new_df.plot.bar()
#     plt.show()

from enums.type_data import type_search

# TODO add information about number of examples for each loop, and total number of examples provided
# by the user at the beginning
def a_histogram(model_name, n_examples=10, n_classified=4):
    def __get_classification(row):
        datatype = row[sources_base.DATATYPE]
        result = classifier.predict(type_search[datatype].get_text(row))
        classification = result[sources_base.LABEL].replace("__label__", "")
        probability = result[sources_base.PROBABILITY]
        #return dict_classification[model_name] if model_name in dict_classification else None

    classifier = DeepLearningModel(name=model_name)

    # preparation of the examples documents (already classified by the user)
    documents_classified_by_user = pandas.DataFrame(list(newsDB.get_all_classified_by_user(model_name)))
    documents_classified_by_user[sources_base.TEXT] = documents_classified_by_user.apply(lambda x: type_search[x[sources_base.DATATYPE]].get_text(x), axis=1)

    documents_classified_by_user[sources_base.LABEL] = documents_classified_by_user[
        sources_base.MODELS].apply(lambda x: x[model_name])

    # preparation of all the documents (including those already classified by the user)
    all_documents = pandas.DataFrame(list(newsDB.get_elements_by_model(model_name, include_classified=True)))
    all_documents[sources_base.TEXT] = all_documents.apply(lambda x: type_search[x[sources_base.DATATYPE]].get_text(x), axis=1)
    all_documents[sources_base.LABEL] = all_documents[sources_base.MODELS].apply(lambda x: x[model_name])
    # all_documents["classification"] = all_documents.apply(
    #     lambda x: __get_classification(x), axis=1)
    all_documents = all_documents.drop(
        columns=['url', 'title', 'creation_time', 'search_keywords', 'datatype', 'models'])

    # this will be use every time that we train the model, its grow with every loop
    # (since we add n_classified docs each time)
    training_docs = pandas.DataFrame(columns=[sources_base.TEXT, "classification"])

    def __get_examples_doc(number_examples, first=False):
        nonlocal documents_classified_by_user, training_docs

        if first:
            div = number_examples // 2
            examples_d = documents_classified_by_user[
                documents_classified_by_user[sources_base.LABEL] == "relevant"].sample(n=math.ceil(div))
            examples_d = examples_d.append(documents_classified_by_user[documents_classified_by_user[sources_base.LABEL] == "no_relevant"].sample(
                n=math.floor(div)))
        else:
            n_examples = min(number_examples, len(documents_classified_by_user.index))
            examples_d = documents_classified_by_user.sample(n=n_examples)

        examples_d = examples_d.apply(
            lambda row: pandas.Series([row[sources_base.TEXT], row[sources_base.LABEL]]), axis=1)
        examples_d.columns = [sources_base.TEXT, sources_base.LABEL]

        documents_classified_by_user = documents_classified_by_user.drop(examples_d.index)
        training_docs = training_docs.append(examples_d)

    def get_prediction(row):
        nonlocal classifier
        prediction = classifier.predict(row[sources_base.TEXT])
        probability = prediction[sources_base.PROBABILITY]
        value = probability if prediction[
                                   sources_base.LABEL] == "__label__relevant" else 1 - probability

        return value

    def __loop(number_examples, n_loop, first=False):
        nonlocal all_documents, training_docs

        __get_examples_doc(number_examples, first)
        classifier.train(training_set=training_docs)
        all_documents["loop" + str(n_loop)] = all_documents.apply(lambda x: get_prediction(x), axis=1)

    # first call
    n_loop = 0
    __loop(n_examples, n_loop=n_loop, first=True)
    # loop-- add n_examples and train classifier
    while len(documents_classified_by_user.index) > 0:
        n_loop += 1
        __loop(n_classified, n_loop=n_loop)

    # in all_documents are all the documents and the probability value of each loop as 'loop#'
    # where # goes from 0 to n_loop
    range_np = np.arange(0, 1.0 + 0.05, 0.05)

    x_label = []
    last = str(int(range_np[0] * 100))
    for x in range_np[1:]:
        text = last + "%-"
        last = str(int(x * 100))
        x_label.append(text + last + "%")

    new_df = pandas.DataFrame()

    for i in range(0, n_loop + 1):
        name_column = "loop" + str(i)
        y = all_documents.groupby(
            pandas.cut(all_documents[name_column], range_np)).count()[name_column]

        new_df[name_column] = y

    new_df["x_label"] = x_label

    fig = plt.figure()
    rects = plt.bar(x=new_df["x_label"], height=new_df["loop0"])

    plt.xlabel('Probabilities Rel-No relevant', fontsize=10)
    plt.ylabel("Number of documents", fontsize=10)
    plt.title('Evolution. Loop 0', fontsize=12)
    plt.xticks(rotation=90)

    def animate(i):
        text = 'Evolution. Loop ' + str(i)
        plt.title(text, fontsize=12)

        name_column = "loop" + str(i)

        for rect, yi in zip(rects, new_df[name_column]):
            rect.set_height(yi)

        return rects

    anim = animation.FuncAnimation(fig, animate, frames=n_loop, interval=1000, blit=True)

    file = model_name + "__evolution.mp4"
    anim.save(file, writer=animation.FFMpegWriter(fps=2))

    # plt.show()


# model_name = "KharisseModel" # start with 6 examples
# model_name = "Gender_based_violence"  # start with 23 examples
#model_name = "kharisse_violence_migrant_women" # stars with 20 examples
# histogram(model_name)

model_name = "MiyukiModel"
a_histogram(model_name, n_examples=20)
