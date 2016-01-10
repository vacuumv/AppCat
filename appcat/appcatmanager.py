import urllib2
import json
import logging

from concurrent.futures import ThreadPoolExecutor
from utils.appreco import AppReco
from appcat.preprocess.appdownloader import CommentDownloader, MetaDownloader
from appcat.preprocess.commentprocessor import CommentProcessor

import config

__author__ = 'Steve'
__status__ = 'Development'
__date__ = '20151103'
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')


class AppCatManager:
    """
    Manipulate downloader, processor and analyzer
    """

    # TODO: Finish parallel processing
    def __init__(self):
        self.comment_downloader = CommentDownloader()
        self.meta_downloader = MetaDownloader()
        self.comment_processor = CommentProcessor()
        # self.analyzer = SentimentAnalyzer()

    def download_app_and_process(self, track_id):
        """

        :param track_id: app track id
        :return:
        """
        self.meta_downloader.get_app_meta(track_id)
        self.comment_downloader.get_app_comments(track_id)
        self.comment_processor.process_one_app(track_id)

    def download_all_app_from_list(self, app_id_list, max_workers=4):
        """
        Given a app id list, download metadata and all the comments and do comment pre-process
        :param app_id_list:
        :return:
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for track_id in app_id_list:
                executor.submit(self.meta_downloader.get_app_meta, track_id)
                executor.submit(self.comment_downloader.get_app_comments, track_id)
                executor.submit(self.comment_processor.process_one_app, track_id)

if __name__ == '__main__':
    reco = AppReco()
    id_list = reco.get_genre_list()
    print(len(id_list))
    manager = AppCatManager()
    # manager.download_app_and_process("303766373")
    manager.download_all_app_from_list(id_list)
