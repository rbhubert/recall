import random
import time

import pandas
import praw

from db.database import redditDB
from enums import reddit_posts, config
from enums import sources_base
from enums.dataType import DataType
from search.information_portal import InformationPortal


# todo error message
class RedditSearch(InformationPortal):
    datatype = DataType.REDDIT
    reddit_api = praw.Reddit(user_agent=config.REDDIT_USER_AGENT,
                             client_id=config.REDDIT_CLIENT_ID, client_secret=config.REDDIT_CLIENT_SECRET)

    def search_with_keywords(self, keywords, model_name):
        print("Searching reddit posts with '", keywords, "' as keywords")
        print("\n")

        list_posts = []

        all_subreddit = self.reddit_api.subreddit("all")
        for post in all_subreddit.search(query=keywords):
            print("    >>>  " + post.title)

            reddit_post = self.__get_content(post=post, model_name=model_name, keywords=keywords)

            if reddit_post is not None:
                list_posts.append(reddit_post)

            time.sleep(random.randint(2, 5))

        print("\n")
        print("That's all")

        return list_posts

    def __get_content(self, post, keywords, model_name, classification=None):
        permanent_link = "www.reddit.com" + post.permalink
        reddit_post = redditDB.get_info(permanent_link)

        if reddit_post is not None:
            redditDB.add_keyword(permanent_link, keywords)
            redditDB.add_classification_user(info_id=permanent_link, model_name=model_name,
                                             classification=classification)
            return reddit_post

        reddit_post = self.__get_dic_post(post, model_name, classification, False)
        redditDB.add_info(reddit_post)
        return reddit_post

    def __get_dic_post(self, post, model_name, classification, is_reply):
        reddit_post = {
            reddit_posts.CREATION_TIME: post.created_utc,
            reddit_posts.USER: '[deleted]' if not post.author else post.author.name,
            reddit_posts.TEXT: post.body if is_reply else post.selftext,
            reddit_posts.UPVOTES: post.score,
            reddit_posts.COMMENTS: self.__get_comments(post, is_reply)
        }

        if not is_reply:
            reddit_post[reddit_posts.TITLE] = post.title
            reddit_post[reddit_posts.URL] = post.permalink
            reddit_post[reddit_posts.MODELS] = {model_name: classification}
            reddit_post[reddit_posts.sources_base.DATATYPE] = self.datatype

            return reddit_post

    def __get_comments(self, post, is_reply):
        comments = []

        if is_reply:
            # comment_forest = post.replies
            return comments
        # else:

        comment_forest = post.comments
        comment_forest.replace_more()

        for comment_x in comment_forest:
            comment = self.__get_dic_post(post=comment_x, model_name=None, classification=None, is_reply=True)
            comments.append(comment)

        return comments

    def retrieve_from_urls(self, model_name, url_list):
        columns = [sources_base.TEXT, sources_base.LABEL]
        dataframe = pandas.DataFrame(columns=columns)

        for url_class in url_list:  # url[0] is url, url[1] is classification
            classification = url_class[1]
            post = self.reddit_api.submission(url=url_class[0])
            reddit_post = self.__get_content(post=post, keywords=model_name, model_name=model_name,
                                             classification=classification)
            if reddit_post is None:
                print("Error! Some trouble retrieving information from " + url_class[0])
                continue

            item_dict = {
                columns[0]: self.get_text(reddit_post),
                columns[1]: classification
            }

            dataframe = dataframe.append(item_dict, ignore_index=True)
            time.sleep(random.randint(2, 5))

        return dataframe

    # This could also include text from comments
    def get_text(self, document):
        return document[reddit_posts.TITLE] + document[reddit_posts.TEXT]


reddit_search = RedditSearch()
