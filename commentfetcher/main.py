__author__ = 'Steve'
from commentFetcher import MetaFetcher

if __name__ == "__main__":

    # MetaFetcher will call inputProcessor to fetch the app ids
    # After that it will download all the metadata in app ids list
    m = MetaFetcher()
    m.download_all()

