import csv
from pprint import pprint
import logging

from pymongo import MongoClient

import config

log = logging.getLogger(__name__)

__author__ = 'Steve'

required_fields = {
    "arm": "arm",
    "Genre": "genre",
    "trackID": "id",
    "trackName": "name",
    "rating": "rating",
    "ratingUsers": "rating_users",
}


class InputProcessor:
    """ This class is to get the app ids in csv file """
    app_list_file = config.app_list_file

    def __init__(self):
        self.client = MongoClient()
        self.appreco_db = self.client['appReco']
        self.app_collect = self.appreco_db['app']
        log.info("Reading file: {}".format(self.app_list_file))

    def write_to_db(self):
        with open(self.app_list_file, "r") as inf:
            dr = csv.DictReader(inf)
            self.field_names = [(required_fields[f], f) for f in dr.fieldnames if f in required_fields.keys()]
            # pprint(self.field_names)

            for row in dr:
                new_item = {'_id': row['trackID']}
                for f1, f2 in self.field_names:
                    new_item[f1] = row[f2]
                # pprint(new_item)
                self.app_collect.update({'_id': new_item['_id']}, new_item, upsert=True)
                # self.app_collect.insert(new_item)

    def get_ids(self):
        with open(self.app_list_file, "r") as inf:
            dr = csv.DictReader(inf)
            # Set ids
            self.ids = [row['trackID'] for row in dr]
        return self.ids


if __name__ == '__main__':
    processor = InputProcessor()
    ids = processor.get_ids()
    processor.write_to_db()
    pprint(len(ids))
