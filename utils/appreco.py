from pymongo import MongoClient

__author__ = 'Steve'


class AppReco:
    """
    This class is to fetch app meta data in mongodb
    """

    def __init__(self):
        self.appdb = MongoClient()['appReco']['app']

    def get_genre_list(self, genre_name="All"):
        """
        Return app id list in specific genre.
        :param genre_name: Genre name in app store, default "All" genre
        :return: app id list in this genre
        """
        app_list = []
        if genre_name != "All":
            for app in self.appdb.find({'genre': genre_name}, no_cursor_timeout=True).sort("_id"):
                app_list.append(app['_id'])
            return app_list
        else:
            for app in self.appdb.find({}, no_cursor_timeout=True).sort("_id"):
                app_list.append(app['_id'])
            return app_list


if __name__ == '__main__':
    reco = AppReco()
    print(len(reco.get_genre_list()))
