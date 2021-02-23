import random
import time

import pandas
from googlesearch import *
from newspaper import Article

from db.database import newsDB
from enums import config
from enums import news_items
from enums import sources_base
from enums.dataType import DataType
from search.information_portal import InformationPortal


# TODO correct error message

class GoogleSearch(InformationPortal):
    datatype = DataType.GOOGLE

    def search_with_keywords(self, keywords, model_name):
        print("Searching news with '" + keywords + "' as keywords in Google")
        print("\n")

        list_news = []

        try:
            for news_url in search_news(keywords, extra_params={'filter': '0'}, user_agent=config.GOOGLE_USER_AGENT):
                print("    >>>  " + news_url)
                content = self.__get_content(keywords=keywords, news_url=news_url, model_name=model_name,
                                             classification=None)
                if content is not None:
                    list_news.append(content)

                time.sleep(random.randint(2, 5))
        except Exception as e:
            print("Error! Too many attempts for today. Please try again tomorrow")
            print("    > " + str(e))
            return list_news

        print("\n")
        print("That's all")

        return list_news

    def __get_content(self, keywords, news_url, model_name, classification=None):
        news_item = newsDB.get_info(news_url)

        if news_item is not None:
            newsDB.add_keyword(news_url, keywords)
            newsDB.add_classification_user(info_id=news_url, model_name=model_name, classification=classification)
            return news_item

        try:
            article = Article(news_url)
            article.download()
            article.parse()

            news_item = {
                news_items.URL: news_url,
                news_items.TITLE: article.title,
                news_items.TEXT: article.text,
                news_items.CREATION_TIME: article.publish_date,
                news_items.sources_base.DATATYPE: self.datatype,
                news_items.MODELS: {
                    model_name: classification
                }
            }

            newsDB.add_info(news_item)
            print(" ^ " + news_url + " added to db")
            return news_item
        except Exception as e:
            print("Error! Some trouble getting the information of " + news_url)
            print("    > " + str(e))
            return None

    def retrieve_from_urls(self, model_name, url_list):
        columns = [sources_base.TEXT, sources_base.LABEL]

        dataframe = pandas.DataFrame(columns=columns)

        for url_class in url_list:  # url[0] is url, url[1] is classification
            classification = url_class[1]
            news_item = self.__get_content(keywords=model_name, model_name=model_name, news_url=url_class[0],
                                           classification=classification)
            if news_item is None:
                print("Error! Some trouble retrieving information from " + url_class[0])
                continue

            item_dict = {
                columns[0]: self.get_text(news_item),
                columns[1]: classification
            }

            dataframe = dataframe.append(item_dict, ignore_index=True)
            time.sleep(random.randint(2, 5))

        return dataframe

    def get_text(self, document):
        return document[news_items.TITLE] + " " + document[news_items.TEXT]


google_search = GoogleSearch()
