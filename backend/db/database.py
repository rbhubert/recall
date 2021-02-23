import os

import pymongo

from enums import news_items
from enums import sources_base, user, model
from enums.config import *
from enums.database import DBCollections
from utils.singleton import Singleton

MONGODB_URI = os.environ.get('MONGODB_URI', DATABASE_NEW)
MONGODB_NAME = os.environ.get('MONGODB_NAME', DATABASE_NAME_NEW)


# Database connection. This class is a Singleton.
class Database(metaclass=Singleton):
    def __init__(self):
        client = pymongo.MongoClient(MONGODB_URI)
        db_name = MONGODB_NAME
        self.__db = client[db_name]

    def __getitem__(self, item):
        return self.__db[item]


class RecoveredInfo:
    def __init__(self, collection_type):
        self.db = Database()
        self.collection = collection_type

    def exist_info(self, info_id):
        id_dict = self.__get_id()
        return self.db[self.collection].find_one({id_dict: info_id}, {"_id": 0}) is not None

    def get_info(self, info_id):
        id_dict = self.__get_id()
        return self.db[self.collection].find_one({id_dict: info_id}, {"_id": 0})

    def add_info(self, info_item):
        id_dict = self.__get_id()
        return self.db[self.collection].replace_one({id_dict: info_item[id_dict]}, info_item, upsert=True)

    def remove_info(self, info_id):
        id_dict = self.__get_id()
        return self.db[self.collection].delete_one({id_dict: info_id})

    def add_keyword(self, info_id, keyword):
        id_dict = self.__get_id()
        return self.db[self.collection].update_one({id_dict: info_id},
                                                   {"$addToSet": {news_items.sources_base.KEYWORDS: keyword}})

    def add_classification_user(self, info_id, model_name, classification):
        id_dict = self.__get_id()
        path = sources_base.MODELS + "." + model_name

        return self.db[self.collection].update_one({id_dict: info_id},
                                                   {"$set": {path: classification}})

    def get_elements_by_model(self, model_name, include_classified=False):
        path = sources_base.MODELS + "." + model_name

        if include_classified:
            return self.db[self.collection].find({path: {"$exists": True}},
                                                 {"_id": 0})
        else:
            return self.db[self.collection].find({path: {"$exists": True, "$eq": None}},
                                                 {"_id": 0})

    def get_all_classified_by_user(self, model_name):
        path = sources_base.MODELS + "." + model_name
        return self.db[self.collection].find({path: {"$ne": None}}, {"_id": 0})

    def get_all_entries(self):
        return self.db[self.collection].find({}, {"_id": 0})

    def __get_id(self):
        # if self.collection == DBCollections.TWITTER:
        #     return tweets_new.TWEET_ID
        # else:
        return sources_base.URL


class Model:
    def __init__(self):
        self.db = Database()
        self.collection = DBCollections.MODEL

    # model info will have an identification of the model (given by user)
    # and name of the file of the model
    def save_model(self, model_info):
        return self.db[self.collection].replace_one({model.ID: model_info[model.ID]}, model_info, upsert=True)

    def get_model(self, model_name):
        return self.db[self.collection].find_one({model.ID: model_name}, {"_id": 0})

    def exist_model(self, model_name):
        return self.db[self.collection].find_one({model.ID: model_name}, {"_id": 0}) is not None


class User:
    def __init__(self):
        self.db = Database()
        self.collection = DBCollections.USER

    def save_user(self, user_info):
        return self.db[self.collection].replace_one({user.USERNAME: user_info[user.USERNAME]}, user_info, upsert=True)

    def get_user(self, username):
        return self.db[self.collection].find_one({user.USERNAME: username}, {"_id": 0})

    def add_model(self, username, model_name):
        return self.db[self.collection].update_one({user.USERNAME: username},
                                                   {"$push": {user.MODELS: model_name}})


# Creation of a NewsDataBase Instance.
newsDB = RecoveredInfo(DBCollections.NEWS)

# Creation of a TwitterDataBase Instance.
twitterDB = RecoveredInfo(DBCollections.TWITTER)

# Creation of a TwitterDataBase Instance.
redditDB = RecoveredInfo(DBCollections.REDDIT)

# Creation of a ModelDatabase Instance
modelDB = Model()

# Creation of a UserDatabase Instance
userDB = User()
