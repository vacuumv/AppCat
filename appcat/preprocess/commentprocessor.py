import logging
import datetime
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor

import appcat.config
from utils.nlprocessor import NLProcessor

__author__ = 'Steve'
__status__ = 'Development'
__revise__ = 'yes'
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')


class CommentProcessor:
    """
    This class get the comment from mongodb and process them
    and store it back
    """

    def __init__(self):
        self.comment_db = MongoClient()[appcat.config.mongodb_collect_name][appcat.config.mongodb_doc_name]
        self.processor = NLProcessor()

    def process_all(self):
        """
        Process all apps in mongodb
        :return:
        """
        with ThreadPoolExecutor(max_workers=appcat.config.pool_size) as executor:
            # for app_id in app_id_list:
            #     executor.submit(self.downloader.get_all_comments, app_id)
            for app in self.comment_db.find({}, no_cursor_timeout=True).sort("_id"):
                executor.submit(self.process_app, app)

    def process_one(self, track_id):
        """
        Process single app in mongodb
        :param track_id: app track_id
        :return:
        """
        app = self.comment_db.find_one({"_id": track_id})
        self.process_app(app)

    def update_one(self, track_id):
        self.comment_db.update_one({"_id": track_id}, {"$set": {"lastModified": datetime.datetime.now()}})

    def get_app(self, track_id):
        return self.comment_db.find_one({"_id": track_id})

    def process_app(self, app):
        """
        Given a app, process its comments and store it back to mongodb

        app:
        {
            comments:{rating, title, content}
            comments_new:{sentences:[{origin:"",tokens:""},{...}]
            , rating, title, content}
        }

        :param app: and app dict with original comment
        :return: none
        """
        comments = []
        track_id = app["trackId"]

        if "lastModified" not in app or app["lastModified"].month != datetime.datetime.now().month:
            log.info("Start processing {}.".format(track_id))

            for comment in app["comments"]:
                comment_after = comment

                comment_content = comment["content"].encode('utf8').replace("\n", "")
                comment_sentences = self.processor.get_eng_sentences(comment_content)

                comment_sentences = [{"origin": s, "tokens": self.processor.sentence_to_tokens(s)} for s in
                                     comment_sentences]
                comment_after["sentences_eng"] = comment_sentences

                comments.append(comment_after)

            self.comment_db.find_one_and_update({"_id": track_id},
                                                {"$set": {"comments": comments,
                                                          "lastModified": datetime.datetime.now()},
                                                 "$unset": {"comments_new": ""}},
                                                upsert=True)
            log.info("{} has been sentenced, translated and stored.".format(track_id))

        else:
            log.info("{} has already been sentenced, translated and stored before.".format(track_id))
            pass


if __name__ == '__main__':
    processor = CommentProcessor()
    processor.update_one("303766373")
