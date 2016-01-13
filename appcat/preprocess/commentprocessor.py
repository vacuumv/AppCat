import logging
import datetime

from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor

import config
from utils.nlprocessor import NLProcessor

__author__ = 'Steve'
__date__ = '20160110'
__revise__ = "20160110"
__version__ = '2.2'
__status__ = 'Development'
__revised__ = 'Yes'

log = logging.getLogger(__name__)

# logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')


class CommentProcessor:
    """
    This class get the comment from mongodb and process them
    and store it back
    """

    def __init__(self):
        self.comment_db = MongoClient()[config.collect_name][config.comment_doc_name]
        self.processor = NLProcessor()

    @DeprecationWarning
    def process_all(self):
        """
        Process all apps in mongodb
        :return:
        """
        id_list = []
        for app in self.comment_db.find({}, no_cursor_timeout=True).sort("_id"):
            id_list.append(app["trackId"])
        with ThreadPoolExecutor(max_workers=config.pool_size) as executor:
            for app_id in id_list:
                executor.submit(self.process_one_app, app_id)

    def process_one_app(self, track_id):
        """
        Process single app in mongodb
        :param track_id: app track_id
        :return:
        """
        app = self.comment_db.find_one({"_id": track_id})
        if app is not None:
            app = self.process_app_comment(app)

            self.comment_db.find_one_and_update({"_id": track_id},
                                                {"$set": app}, )
            log.info("TrackID [{}] has been sentenced, translated and stored.".format(track_id))
        else:
            log.info("TrackID [{}] not found in db.".format(track_id))

    def process_app_comment(self, app):
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

        track_id = app["trackId"]

        # if "lastModified" not in app or app["lastModified"].month != datetime.datetime.now().month:
        if not app["preprocessed"]:
            log.info("Start processing {}.".format(track_id))
            comments = []
            for comment in app["comments"]:
                comment_after = comment
                comment_content = comment["content"].encode('utf8').replace("\n", "")
                comment_sentences = self.processor.get_eng_sentences(comment_content)
                comment_sentences = [{"origin": s, "tokens": self.processor.sentence_to_tokens(s)} for s in
                                     comment_sentences]
                comment_after["sentencesEng"] = comment_sentences
                comments.append(comment_after)
            app["comments"] = comments
            app["lastModified"] = datetime.datetime.now()
            app["preprocessed"] = True

        return app
