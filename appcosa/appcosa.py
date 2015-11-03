import urllib2
import json
import logging

from textblob import TextBlob
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor

import appcosa

__author__ = 'Steve'
__status__ = 'Development'
__date__ = '20151103'
log = logging.getLogger(__name__)


class CommentDownloader:
    """
    This class download comments from iTunes to mongodb
    """

    download_url = "https://itunes.apple.com/rss/customerreviews/id=%s/sortby=mostrecent/page=%s/json"

    def __init__(self):
        self.comment_db = MongoClient()[appcosa.mongodb_collect_name][appcosa.mongodb_doc_name]

    @staticmethod
    def get_comments(track_id, page_index=1):

        """
        Get comments given id and page
        Returns list of comments in this page (maximum 50) or a empty list
        Example: [{"title":title, "content":content}, ...,]
        """
        app_url = CommentDownloader.download_url % (track_id, str(page_index))
        msg = ("Parsing trackID [{}]: page {}".format(track_id, page_index))
        try:

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
        """
        Get all comments given an app id
        Returns list of comments in this page (maximum 50) or a empty list
        Example: {"_id": track_id, "comments": [...], "trackId": track_id}
        """

        app = {"_id": track_id, "comments": [], "trackId": track_id}
        page_index = 1
        while True:
            comments = CommentDownloader.get_comments(track_id, page_index)
            app["comments"].extend(comments)
            page_index += 1
            if len(comments) == 0:
                break

        log.debug("trackID [{}] has {} comments".format(track_id, len(app["comments"])))
        # self.app_comments_collect.insert(output)
        # self.comment_db.update(app, upsert=True)
        return app


class SentimentAnalyzer:
    """
    Get an app item from mongodb and analyze the comment sentiment
    """

    # TODO: finish the output part
    def analyze_app(self, app, detail=False):

        result = {}
        track_id = app["trackId"]
        length = len(app["comments"])
        neg_sentiment = 0
        pos_sentiment = 0
        neg_sentiment_count = 0
        pos_sentiment_count = 0
        for index, comment in enumerate(app["comments"]):
            content = comment["content"]
            blob = TextBlob(content)
            sentiment = 0
            for sentence in blob.sentences:
                log.debug("\t\t\t[[{}]]".format(sentence.sentiment.polarity))
                log.debug("\t\t\t{}".format(sentence))
                sentiment += sentence.sentiment.polarity
            if detail:
                log.debug("{} [{}]".format(index, sentiment))

            if sentiment > 0:
                pos_sentiment += sentiment
                pos_sentiment_count += 1
            else:
                neg_sentiment += sentiment
                neg_sentiment_count += 1
            if detail:
                log.info("\t\t{}".format(content))

        result["trackId"] = track_id
        result["count"] = length
        result["pos_pc"] = pos_sentiment / pos_sentiment_count
        result["neg_pc"] = neg_sentiment / neg_sentiment_count
        self.display_info(result)

    def display_info(self, result):
        log.info("\n")
        log.info("App Id:[{}]".format(result["trackId"]))
        log.info("\tTotal {} comments".format(result["count"]))
        log.info("\tPositive sentiment: {} per comment.".format(result["pos_pc"]))
        log.info("\tNegative sentiment: {} per comment.".format(result["neg_pc"]))


class CoSaManager:
    """
    Manipulate downloader and analyzer
    """

    # TODO: Finish parallel processing
    def __init__(self):
        self.downloader = CommentDownloader()
        self.analyzer = SentimentAnalyzer()

    def analyze(self, app_id):
        app = self.downloader.get_all_comments(app_id)
        self.analyzer.analyze_app(app)

    def get_all_comments_from_app_list(self, app_id_list):
        with ThreadPoolExecutor(max_workers=appcosa.pool_size) as executor:
            for app_id in app_id_list:
                executor.submit(self.analyze, app_id)

    def load_meta_name(self, track_id):
        app_meta_url = "https://itunes.apple.com/lookup?id=" + str(track_id)
        app_json = json.load(urllib2.urlopen(app_meta_url))

        return app_json["results"][0]["trackName"]
