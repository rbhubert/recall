from db.database import newsDB, redditDB, twitterDB
from enums.dataType import DataType
from search.google import google_search
from search.reddit import reddit_search
from search.twitter import twitter_search

type_search = {
    DataType.GOOGLE: google_search,
    DataType.TWITTER: twitter_search,
    DataType.REDDIT: reddit_search
}

type_database = {
    DataType.GOOGLE: newsDB,
    DataType.TWITTER: twitterDB,
    DataType.REDDIT: redditDB
}
