import urllib2
import json
import logging

from concurrent.futures import ThreadPoolExecutor

import config

__author__ = 'Steve'
__status__ = 'Development'
__date__ = '20151103'
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')


class AppCatManager:
    """
    Manipulate downloader and analyzer
    """

    # TODO: Finish parallel processing
    def __init__(self):
        self.downloader = CommentDownloader()
        self.analyzer = SentimentAnalyzer()

    def analyze(self, app_id):
        app = self.downloader.get_all_comments(app_id)
        self.analyzer.analyze_app_plot(app)

    def get_all_comments_from_app_list(self, app_id_list):
        with ThreadPoolExecutor(max_workers=config.pool_size) as executor:
            for app_id in app_id_list:
                executor.submit(self.analyze, app_id)

    def download_all_comments_from_app_list(self, app_id_list):
        with ThreadPoolExecutor(max_workers=config.pool_size) as executor:
            for app_id in app_id_list:
                executor.submit(self.downloader.get_all_comments, app_id)

    def load_meta_name(self, track_id):
        app_meta_url = "https://itunes.apple.com/lookup?id=" + str(track_id)
        app_json = json.load(urllib2.urlopen(app_meta_url))

        return app_json["results"][0]["trackName"]
