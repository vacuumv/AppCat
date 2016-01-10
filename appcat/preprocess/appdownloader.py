import urllib2
import json
import logging
import re
import datetime
from pymongo import MongoClient

import appcat.config

__author__ = 'Steve'
__date__ = '20160110'
__revise__ = "20160110"
__version__ = '2.2'
__status__ = 'Development'
__revised__ = 'Yes'

log = logging.getLogger(__name__)


class CommentDownloader:
    """
    This class download unprocessed comments of apps
    from apple iTunes store and store it to mongodb
    """

    download_url = "https://itunes.apple.com/rss/customerreviews/id=%s/sortby=mostrecent/page=%s/json"

    def __init__(self):
        self.comment_db = MongoClient()[appcat.config.collect_name][appcat.config.comment_doc_name]

    def get_app_comments(self, track_id):
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

                log.info("TrackID [{}] has {} comments and has been download successfully.".format(track_id, len(
                    app["comments"])))
                self.comment_db.find_one_and_update({"_id": track_id},
                                                    {"$set": {"comments": app["comments"], "trackId": track_id,
                                                              "preprocessed": False,
                                                              "lastModified": datetime.datetime.now()}},
                                                    upsert=True)
                return
            except Exception, e:
                log.debug(e)
                log.info("Url load error!! [{}]".format(app_url))
        else:
            log.info("TrackID [{}] comments already exists.".format(track_id))

            return


class MetaDownloader:
    """
    This class is to fetch meta data about ios app
    and store it to mongodb
    """
    download_url = "https://itunes.apple.com/%s/lookup?id=%s"
    areas = [
        "us", "tw", "cn"
    ]

    def __init__(self):
        self.meta_db = MongoClient()[appcat.config.collect_name][appcat.config.meta_doc_name]

    def get_app_meta(self, track_id):
        """
        Download app from itunes and store it to mongodb, trying different areas.
        :param track_id: track id of app
        :return:
        """
        app = self.meta_db.find_one({"_id": track_id})
        if app is None:

            for area in self.areas:
                log.debug("Trying to download app meta {} from [{}]...".format(track_id, area))
                app_url = self.download_url % (area, track_id)
                log.debug(app_url)
                try:
                    app_json = json.load(urllib2.urlopen(app_url))
                    if app_json['resultCount'] > 0:

                        app = app_json['results'][0]
                        app["lastModified"] = datetime.datetime.now()
                        self.meta_db.find_one_and_update({"_id": track_id},
                                                         {"$set": app},
                                                         upsert=True)
                        log.info("TrackID [{}] metadata has been downloaded successfully.".format(track_id))
                        return app
                    else:
                        log.info("TrackID [{}] metadata download error [{}].".format(track_id, area))
                except Exception, e:
                    log.debug(e)
                    log.info("TrackID [{}] metadata download error [{}].".format(track_id, area))
        else:
            log.info("TrackID [{}] metadata already exists.".format(track_id))
            return app
