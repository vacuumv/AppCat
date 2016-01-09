import urllib2
import json
import logging
import re

from pymongo import MongoClient

import appcat.config

__author__ = 'Steve'
__status__ = 'Development'
__revise__ = 'yes'
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')


class CommentDownloader:
    """
    This class download unprocessed comments from iTunes to mongodb
    """

    download_url = "https://itunes.apple.com/rss/customerreviews/id=%s/sortby=mostrecent/page=%s/json"

    def __init__(self):
        self.comment_db = MongoClient()[appcat.config.mongodb_collect_name][appcat.config.mongodb_doc_name]

    def get_all_comments(self, track_id):
        """
        Get all comments given an app id
        Returns list of comments in this page (maximum 50) or a empty list
        Example: {"_id": track_id, "comments": [...], "trackId": track_id}
        """

        app = self.comment_db.find_one({"_id": track_id})
        if app is None:
            app_url = CommentDownloader.download_url % (track_id, str(1))

            # Try if this app exists
            try:
                app_json = json.load(urllib2.urlopen(app_url))

                # Get the last page number in a json field
                last_page_url = app_json["feed"]["link"][3]["attributes"]["href"]
                last_page = int(re.search("views/page=(\d+)", last_page_url).group(1))

                app = {"_id": track_id, "comments": [], "trackId": track_id}

                for page_index in range(1, last_page + 1):

                    app_url = CommentDownloader.download_url % (track_id, str(page_index))
                    msg = ("Parsing trackID [{}]: page {}".format(track_id, page_index))

                    app_json = json.load(urllib2.urlopen(app_url))

                    comments = app_json["feed"]["entry"]
                    comments.pop(0)
                    for index, comment in enumerate(comments):
                        title = comment["title"]["label"]

                        # Sometimes a comment has only title and no content
                        content = comment["content"]["label"]
                        rating = comment["im:rating"]["label"]
                        out_comment = {"title": title, "content": content, "rating": rating}
                        app["comments"].append(out_comment)

                    log.debug(msg + "\t[success]")

                log.info("trackID [{}] has {} comments".format(track_id, len(app["comments"])))
                self.comment_db.find_one_and_update({"_id": track_id},
                                                    {"$set": {"comments": app["comments"], "trackId": track_id}},
                                                    upsert=True)
                return app
            except Exception, e:
                log.debug(e)
                log.info("Url load error!! [{}]".format(app_url))
        else:
            log.info("App: {} already exists.".format(track_id))
            return app
