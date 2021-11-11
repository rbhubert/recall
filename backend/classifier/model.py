import fasttext

from classifier.oversampling_functions import TypeOversampling
from classifier.preprocessing_functions import TypePreprocessing
from db.database import modelDB
from enums import model, sources_base

# TODO cambiar estos directorios a algo más general...
directory_files = "/Users/rbh/dev/GitHub/recall/backend/temp/files/"
directory_models = "/Users/rbh/dev/GitHub/recall/backend/temp/models/"


class DeepLearningModel:
    def __init__(self, name, epoch=50, lr=1.0, word_n_grams=1, preprocessing_function=TypePreprocessing.BASIC,
                 training_docs=None):
        self.original_name = name
        self.model_id = self.__get_model_id()
        self.preprocess = preprocessing_function

        model_info = modelDB.get_model(self.model_id)

        if model_info is None:  # creation of model
            self.model = None
            self.train(training_docs, epoch=epoch, lr=lr, word_n_grams=word_n_grams)
        else:
            self.model = fasttext.load_model(model_info[model.FILE])

    def train(self, training_set, epoch=50, lr=1.0, word_n_grams=1):
        training_file = self.__to_file(training_set)
        self.model = fasttext.train_supervised(training_file, epoch=epoch, lr=lr, wordNgrams=word_n_grams)
        self.save_model()
        return True

    def predict(self, document_text):
        text = self.preprocess(document_text)
        result = self.model.predict(text)
        to_return = {sources_base.LABEL: result[0][0],
                     sources_base.PROBABILITY: result[1][0]}

        return to_return

    def save_model(self):
        model_file = directory_models + self.model_id + ".bin"
        self.model.save_model(model_file)
        model_info = {
            model.ID: self.model_id,
            model.ORIGINAL_NAME: self.original_name,
            model.FILE: model_file,
        }
        modelDB.save_model(model_info)
        return True

    def __get_model_id(self):
        model_id = self.original_name.lower().replace(" ", "_")
        return model_id

    def __to_file(self, training_set, training=True, oversampling=True, oversampling_function=TypeOversampling.BASIC):
        training_set[sources_base.TEXT] = training_set[sources_base.TEXT].apply(lambda x: self.preprocess(x))

        if oversampling:
            print("Oversampling: true")
            training_set = oversampling_function(training_set)

        train_test = "train" if training else "test"
        file_train = directory_files + train_test + "___" + self.model_id + ".txt"

        # Prepare data
        file = open(file_train, "w")
        for index, row in training_set.iterrows():
            line = "__label__" + row[sources_base.LABEL] + ' ' + row[sources_base.TEXT]
            file.write(line + "\n")

        return file_train

    def save_bin(self):
        model_file = directory_models + self.model_id + ".bin"
        self.model.save_model(model_file)
        return model_file
