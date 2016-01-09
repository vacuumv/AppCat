__author__ = 'Steve'

from pprint import pprint
from time import sleep

from appcat.appcosa import CommentDownloader,CoSaManager
from utils.inputProcessor import InputProcessor
import json

def download_all_app_comments():
    downloader = CommentDownloader()
    processor = InputProcessor()
    ids = processor.get_ids()
    app_list = [str(a) for a in ids]
    for app_id in app_list:
        with open('{}_comment.json'.format(app_id),'w') as f:
            json.dump(downloader.get_all_comments(app_id),f)

        sleep(100)

def download_all_app_comments2():
    manager=CoSaManager()
    processor = InputProcessor()
    ids = processor.get_ids()
    app_list = [str(a) for a in ids]
    app_list = ["281796108"]
    manager.download_all_comments_from_app_list(app_list)

def download_all_app_comments3():
    manager=CoSaManager()
    downloader = CommentDownloader()
    processor = InputProcessor()
    ids = processor.get_ids()
    app_list = [str(a) for a in ids]
    downloader.get_all_comments(app_list[0])

if __name__ == '__main__':
    download_all_app_comments2()
