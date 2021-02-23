import random
import time

import pandas
import tweepy
from twarc import Twarc

from db.database import twitterDB
from enums import config
from enums import sources_base
from enums import tweets
from enums.dataType import DataType
from search.information_portal import InformationPortal


class TwitterSearch(InformationPortal):
    auth = tweepy.OAuthHandler(config.TWITTER_AUTH[0], config.TWITTER_AUTH[1])
    auth.set_access_token(config.TWITTER_ACCESS_TOKEN[0], config.TWITTER_ACCESS_TOKEN[1])

    # api rest
    twitterAPI = tweepy.API(auth, wait_on_rate_limit=True,
                            wait_on_rate_limit_notify=True)
    # api for comments
    twitterReplies = Twarc(config.TWITTER_AUTH[0], config.TWITTER_AUTH[1],
                           config.TWITTER_ACCESS_TOKEN[0], config.TWITTER_ACCESS_TOKEN[1])

    datatype = DataType.TWITTER

    def search_with_keywords(self, keywords, model_name):
        print("Searching tweets with '" + keywords + "' as keywords in Twitter")
        print("\n")

        list_tweets = []
        all_tweets = self.twitterAPI.search(q=keywords)
        for tweet in all_tweets:
            print("    >>>  " + tweet.text)
            tweet = self.__get_content(tweet_info=tweet, keywords=keywords, model_name=model_name)

            if tweet is not None:
                list_tweets.append(tweet)

        print("\n")
        print("That's all")

        return list_tweets

    def __get_content(self, tweet_info, model_name, keywords, classification=None):
        try:
            tweet_id = tweet_info.id_str
            tweet = twitterDB.get_info(tweet_id)

            if tweet is not None:
                twitterDB.add_keyword(tweet_id, keywords)
                twitterDB.add_classification_user(tweet_id, model_name, classification)
                return tweet

            tweet_item = self.__get_dic_of_tweet(tweet._json, False)
            twitterDB.add_tweet(tweet_item)

            return tweet_item

        except Exception as e:
            print("Error! Some trouble getting the information of the tweet")
            print("    > " + str(e))
            return None

    def __get_replies(self, tweet):
        all_replies = self.twitterReplies.replies(tweet, False)
        replies = []

        for reply_x in all_replies:
            if reply_x["id_str"] != tweet["id_str"]:
                reply = self.__get_dic_of_tweet(reply_x, True)
                replies.append(reply)

        return replies

    def __get_dic_of_tweet(self, tweet, is_comment):
        tweet_id = tweet["id_str"]
        dic_tweet = {
            tweets.URL: tweets.BASIC_URL + tweet_id,
            tweets.TWEET_ID: tweet_id,
            tweets.USER: {
                tweets.User.USER_ID: tweet["user"]["id_str"],
                tweets.User.USERNAME: tweet["user"]["screen_name"]
            },
            tweets.TEXT: tweet["text"],
            tweets.HASHTAGS: tweet["entities"]["hashtags"],
            tweets.USER_MENTIONS: [{
                "user_id": user["id_str"],
                "username": user["screen_name"]
            } for user in tweet["entities"]["user_mentions"]],
            tweets.CREATION_TIME: tweet["created_at"],
            tweets.IS_RETWEETED: True if "retweeted_status" in tweet else False,
            tweets.FAVORITES: tweet["favorite_count"],
            tweets.RETWEETS: tweet["retweet_count"],
            tweets.COMMENTS: [] if is_comment else self.__get_replies(tweet)
        }

        if not is_comment:
            dic_tweet[tweets.sources_base.DATATYPE] = self.datatype

        return dic_tweet

    def retrieve_from_urls(self, model_name, url_list):
        columns = [sources_base.TEXT, sources_base.LABEL]
        dataframe = pandas.DataFrame(columns=columns)

        for url_class in url_list:  # url[0] is url, url[1] is classification
            classification = url_class[1]

            tweet_id = url_class[0].split("/")[-1]
            tweet_info = self.twitterAPI.get_status(tweet_id)
            tweet = self.__get_content(tweet_info=tweet_info, keywords=model_name, model_name=model_name,
                                       classification=classification)
            if tweet is None:
                print("Error! Some trouble retrieving information from " + url_class[0])
                continue

            item_dict = {
                columns[0]: self.get_text(tweet),
                columns[1]: classification
            }

            dataframe = dataframe.append(item_dict, ignore_index=True)
            time.sleep(random.randint(2, 5))

        return dataframe

    # This could also include the twitter thread for the document
    def get_text(self, document):
        return document["text"]

    def get_basic_information(self, document):
        return {
            tweets.URL: document[tweets.URL],
            tweets.sources_base.TITLE: document[tweets.URL],
            tweets.TEXT: document[tweets.TEXT],
            tweets.sources_base.DATATYPE: self.datatype
        }


twitter_search = TwitterSearch()
