import logging
import re
import sys
import time
from pprint import pprint
from collections import defaultdict

import enchant
from pymongo import MongoClient

import utils.appreco
import config
from utils.bcolors import bcolors

__author__ = 'Steve'
__date__ = '20151103'
__revise__ = "20160110"
__version__ = '0.9'
__status__ = 'Development'
__revised__ = 'Yes'

log = logging.getLogger(__name__)


class CommentCorpusLoader:
    """
    Load single or all app comment in corpus.
    """

    def __init__(self):
        self.comment_db = MongoClient()[config.collect_name][config.comment_doc_name]
        self.pwl = config.project_folder + "appcatPwl.txt"

    def find_comment_by_keyword(self, keyword):
        """
        Query mongodb to find if specific keyword appeared in app comments
        :param keyword: the keyword you want
        :return: query result
        """
        log.info("Querying keyword [{}]...".format(keyword))
        query_result = {}

        for app in self.comment_db.find({}, no_cursor_timeout=True).sort("_id"):
            comment_list = []
            for index, comment in enumerate(app["comments"]):
                content = comment["content"]
                for sentence in comment["sentencesEng"]:
                    tokens = sentence["tokens"]
                    result = re.findall(keyword, tokens)
                    if len(result) > 0:
                        comment_list.append([index, len(result)])
            if len(comment_list) > 0:
                query_result[app["trackId"]] = comment_list

        return query_result

    def get_id_of_genre(self, genre_name="All", limit=100):
        """
        get app_id from specific genre in mongodb
        if genre name is all then not genre is specified
        """
        return utils.appreco.AppReco().get_genre_list(genre_name)[:limit]

    def get_all_id_of_processed_app_in_db(self, limit=100):
        id_list = []
        for app in self.comment_db.find().sort("_id"):
            if app["preprocessed"]:
                id_list.append(app["trackId"])
        return id_list[:limit]

    def load_comments_from_ids(self, track_ids, ratings="12345"):
        """
        get review from specific genre in mongodb and display the progress bar
        and return it as list of lists of tokens
        """
        log.info("Start loading comment (total {}).".format(len(track_ids)))
        comment_comments_list = []
        progress_list = []
        for index, track_id in enumerate(track_ids):
            comments = self.load_comment_tokens_from_single_app(track_id, ratings=ratings)
            if comments is not None:
                comment_comments_list = comment_comments_list + self.load_comment_tokens_from_single_app(track_id,
                                                                                                         ratings=ratings)
            # Progress bar
            progress = int(float(index + 1) / len(track_ids) * 100)
            if progress % 5 == 0 and progress not in progress_list:
                progress_list.append(progress)
                sys.stdout.write("\r" + bcolors.OKBLUE + "[{}] {}% comment of apps ({}) are loaded.".format(
                    progress / 5 * "=" + (20 - progress / 5) * " ", progress, index + 1) + bcolors.ENDC)
                sys.stdout.flush()

        sys.stdout.write("\n")
        time.sleep(2)

        self.corpus_rating = comment_comments_list
        self.corpus = [c[0] for c in comment_comments_list]
        log.info("Corpus loaded with length {}.".format(len(comment_comments_list)))

    def load_comment_tokens_from_single_app(self, track_id, ratings="12345"):
        """

        Return comment tokens of specific app with specific ratings,

        :param track_id: app id
        :param ratings: a string represents rating, default "12345"
        :return: list of comments [[[tokens],rating],[],...,[]]

        """
        log.debug(track_id)
        app = self.comment_db.find_one({"_id": str(track_id)})
        if app is not None:
            comment_comments_list = []
            if app['preprocessed']:
                for comment in app["comments"]:
                    rating = str(comment["rating"])
                    if rating in ratings:
                        comment_tokens = []
                        for sentence in comment["sentencesEng"]:
                            comment_tokens = comment_tokens + sentence["tokens"]
                        if len(comment_tokens) > 0:
                            comment_comments_list.append([comment_tokens, rating])
            return comment_comments_list
        else:
            return None

    # def load_all_comments_from_genre(self, genre_name="All", limit=100, ratings="12345"):
    #     """
    #     Get all comments from apps belong to specific genre
    #
    #     :param genre_name: genre name in app store, default all
    #     :param limit: numbers of apps you want, default 100
    #     :param ratings: ratings of comments you want, default all (1,2,3,4,5)
    #     :param with_rating: if true each comment will contains second element i.e. rating
    #     :return: list of (comment tokens(list),comment ratings)
    #     """
    #
    #     ids = self.get_id_of_genre(genre_name, limit=limit)
    #     comments = self.load_comments_from_ids(ids, ratings=ratings)
    #
    #     self.corpus_rating = comments
    #     self.corpus = [c[0] for c in comments]
    #     log.info("Corpus loaded with length {}.".format(len(comments)))


    def get_corpus(self, with_rating=False):
        return self.corpus if with_rating == False else self.corpus_rating

    def generate_personal_word_list(self, minimal_appear_count=100):
        """
        Generate enchant personal word list (pwl) from all comments
         if a word is not in english but appears
         more than 100 times in all comments
        :return:
        """

        self.dictionary = defaultdict(int)
        d = enchant.Dict('en_US')
        for doc in self.corpus:
            for token in doc:
                self.dictionary[token] += 1

        word_list = [item for item in self.dictionary.iteritems() if not d.check(item[0])]
        word_list = [r for r in sorted(word_list, key=lambda item: item[1], reverse=True) if
                     r[1] > minimal_appear_count]
        dict_pwl = enchant.request_pwl_dict(self.pwl)
        added = 0
        for word in word_list:
            w = str(word[0])
            if not dict_pwl.check(w):
                dict_pwl.add(w)
                added += 1
                print(w)
        log.info("{} words not in English but appears in comments more than {} times.".format(len(word_list),
                                                                                              minimal_appear_count))
        log.info("Of those {} words, {} has already exists in pwl, the rest {} ones has been added to pwl".format(
            len(word_list), len(word_list) - added, added))


# class CommentCorpusProcessor:
#     def __init__(self):
#         self.loader = CommentCorpusLoader()
#
#     def load_processed_corpus_without_rating(self, limit=100):
#         """
#         Load corpus as list of comments with words appears once and not-english words removed
#         :return: list of comments contains tokens
#         """
#         log.info("Loading corpus")
#
#         corpus = self.loader.load_all_comments_from_genre(limit=limit)
#         corpus = [c[0] for c in corpus]
#         # d = enchant.Dict('en_US')
#
#         #
#         # remove words that appear only once
#         # log.info("Corpus has {} documents.".format(len(corpus)))

#         #
#         # # tags = nltk.pos_tag(frequency.keys())
#         # # nouns=[]
#         # # for tag in tags:
#         # #     if 'NN' in tag[1]:
#         # #         nouns.append(tag[0])
#         #
#         # nouns = frequency.keys()
#         # log.info("Total {} unique terms are now in dictionary.".format(len(nouns)))
#         # log.info("Removing terms that appears only once and not English in dictionary...")
#         # nouns = [t for t in nouns if d.check(t) and frequency[t] > 1]
#         # log.info("Total {} unique terms are now in dictionary.".format(len(nouns)))
#
#         # logging.info("Removing terms that are not noun in dictionary...")
#         # for i in range(0, 5):
#         #     nouns = [tag[0] for tag in nltk.pos_tag(nouns) if 'NN' in tag[1]]
#         # logging.info("Total {} unique terms are now in dictionary.".format(len(nouns)))
#         # logging.debug(nltk.pos_tag(nouns))
#
#         # log.info("Filtering out words that are not in dictionary...")
#         # corpus = [[token for token in doc if token in nouns]
#         #           for doc in corpus]
#         # log.info("Corpus loaded with length {} and unique words {}.".format(len(corpus), len(nouns)))
#         return corpus
