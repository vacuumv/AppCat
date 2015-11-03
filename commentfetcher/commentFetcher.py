__author__ = 'Steve'
import re
import urllib2
from pprint import pprint
from inputProcesser import InputProcessor
import json
from pymongo import MongoClient
import logging
from concurrent.futures import ThreadPoolExecutor
import config
import traceback
from textblob import TextBlob

log = logging.getLogger(__name__)


class CommentFetcher:
    """ Fetch comments to mongodb """

    def __init__(self):
        self.client = MongoClient()
        self.appreco_db = self.client['appReco']
        self.app_comments_collect = self.appreco_db['appComments']
        self.executor = ThreadPoolExecutor(max_workers=config.pool_size)

    def get_comments(self, track_id, page=1):
        msg = ("Parsing trackID [{}]: page {}".format(track_id, page))
        try:
            app_url = "https://itunes.apple.com/rss/customerreviews/id=" + track_id + "/sortby=mostrecent/page=" + str(
                page) + "/json"
            # print(app_url)
            app_json = json.load(urllib2.urlopen(app_url))

            comments_output = []

            comments = app_json["feed"]["entry"]
            for index, comment in enumerate(comments):
                try:
                    title = comment["title"]["label"]


                    # Sometimes a comment has only title and no content
                    content = str(comment["content"]["label"]).replace("\n", "")
                    out_comment = {"title": title, "content": content}
                    comments_output.append(out_comment)
                except:
                    pass
            log.debug(msg + "\t[success]")
            return comments_output

        except:
            log.debug(msg + "\t[failed]")
            return []

    def get_all_comments(self, track_id):
        comments_output = []
        output = {"_id": track_id, "comments": comments_output, "trackId": track_id}
        i = 1
        comments = self.get_comments(track_id, i)
        while len(comments) != 0:
            output["comments"].extend(comments)
            i += 1
            comments = self.get_comments(track_id, i)

        # log.info("trackID [{}] has {} comments".format(track_id, len(output["comments"])))
        # self.app_comments_collect.insert(output)
        # self.app_comments_collect.update(output, upsert=True)
        return output

    def get_all_apps_comments_from_list(self, app_id_list):
        for app_id in app_id_list:
            self.executor.submit(self.get_all_comments, app_id)
            # for index, app_id in enumerate(app_id_list):
            #     self.get_all_comments(app_id)

    def semtiment_analysis_from_list(self, app_id_list, detail=False):
        for app_id in app_id_list:
            self.calculate_semtiment(app_id, detail=detail)

    def calculate_semtiment_detail(self, app_id, detail=False):
        app = self.get_all_comments(app_id)
        length = len(app["comments"])
        neg_sentiment = 0
        pos_sentiment = 0
        for index, comment in enumerate(app["comments"]):
            content = comment["content"]
            blob = TextBlob(content)
            sentiment = 0
            for sentence in blob.sentences:
                log.info("\t\t\t[[{}]]".format(sentence.sentiment.polarity))
                log.info("\t\t\t{}".format(sentence))
                sentiment += sentence.sentiment.polarity
            if detail == True:
                log.info("{} [{}]".format(index, sentiment))
            if sentiment > 0:
                pos_sentiment += sentiment
            else:
                neg_sentiment += sentiment
            if detail == True:
                log.info("\t\t{}".format(content))

        # log.info("Conclustion:")
        log.info("\n")
        log.info("App Id:[{}] , App Name:[{}]".format(app_id, self.load_meta_name(app_id)))
        log.info("\tTotal {} comments".format(length))
        log.info("\tPositive sentiment: {} per comment.".format(pos_sentiment / length))
        log.info("\tNegative sentiment: {} per comment.".format(neg_sentiment / length))

    def calculate_semtiment(self, app_id, detail=False):
        app = self.get_all_comments(app_id)
        length = len(app["comments"])
        neg_sentiment = 0
        pos_sentiment = 0
        for index, comment in enumerate(app["comments"]):
            content = comment["content"]
            blob = TextBlob(content)
            sentiment = 0
            for sentence in blob.sentences:
                # print(sentence)
                # print(sentence.sentiment.polarity)
                sentiment += sentence.sentiment.polarity
            if detail == True:
                log.info("{} [{}]".format(index, sentiment))
            if sentiment > 0:
                pos_sentiment += sentiment
            else:
                neg_sentiment += sentiment
            if detail == True:
                log.info("\t\t{}".format(content))

        # log.info("Conclustion:")
        log.info("\n")
        log.info("App Id:[{}] , App Name:[{}]".format(app_id, self.load_meta_name(app_id)))
        log.info("\tTotal {} comments".format(length))
        log.info("\tPositive sentiment: {} per comment.".format(pos_sentiment / length))
        log.info("\tNegative sentiment: {} per comment.".format(neg_sentiment / length))

    def load_meta_name(self, track_id):
        app_meta_url = "https://itunes.apple.com/lookup?id=" + str(track_id)
        app_json = json.load(urllib2.urlopen(app_meta_url))
        return app_json["results"][0]["trackName"]


def test0():
    # Display all comments
    fetcher = CommentFetcher()
    pprint(fetcher.get_all_comments("281796108"))


def test1():
    fetcher = CommentFetcher()
    # 281796108 is evernote
    fetcher.calculate_semtiment("281796108", detail=True)


def test2():
    fetcher = CommentFetcher()
    processor = InputProcessor()
    app_ids = processor.get_ids()
    fetcher.semtiment_analysis_from_list(app_ids, detail=False)


def test3():
    fetcher = CommentFetcher()
    # 281796108 is evernote
    fetcher.calculate_semtiment_detail("281796108", detail=True)


if __name__ == '__main__':
    commends = {
        "0": test0,
        "1": test1,
        "2": test2,
        "3": test3
    }
    x = str(input("Enter mode: "))
    commends[x]()
