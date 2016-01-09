import logging, json
from pprint import pprint
from appcat.analyzer.corpusloader import CommentCorpusLoader

__author__ = 'Steve'
__status__ = 'Development'
__revise__ = 'Yes'
log = logging.getLogger(__name__)


# logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

class RatingCritiria:
    @staticmethod
    def criteria1(rc):
        """
        count pos and neg ratio
        :param rc: a dict contains 1~5 rating count
        :return: ratio of pos and neg
        """
        return (rc["5"] * 1.5 + rc["4"] + 1) / (rc["1"] * 1.5 + rc["2"] + 1)

    @staticmethod
    def criteria2(rc):
        """
        count pos and neg ratio
        :param rc: a dict contains 1~5 rating count
        :return: ratio of pos and neg
        """
        return float(rc["5"] + rc["4"]) / (rc["1"] + rc["2"]) * (
            rc["5"] + rc["4"] - rc["1"] - rc["2"])


class KeywordFinder:
    """
    This class is to find keyword and count ratio
    """

    def __init__(self):
        pass

    def save_dictionary_to_json(self, file_name):
        """
        Save dictionary to a json file
        :param file_name: json file name
        :return:
        """
        with open(file_name, "w") as out_file:
            json.dump(self.dictionary, out_file)
        log.info("Dictionary has been saved to {} with size {}.".format(file_name, len(self.dictionary)))

    def load_dictionary(self, limit=100):
        """
        Count ratio and complete dictionary.
        :return: dictionary
        """
        init_word_dic = {}
        for i in range(1, 6):
            init_word_dic[str(i)] = 0

        loader = CommentCorpusLoader()
        comments = loader.load_all_comments_from_genre(limit=limit)
        dictionary = {}

        # Comment
        for comment in comments:
            # pprint(comment)
            for token in comment[0]:
                token = str(token)

                if dictionary.get(token) is None:
                    dictionary[token] = init_word_dic.copy()
                    val = 0
                else:
                    val = dictionary.get(token).get(comment[1])
                # print(dictionary[token])
                dictionary[token][comment[1]] = val + 1

        # result=[]


        self.dictionary = dictionary
        log.info("Dictionary has been loaded with size {}.".format(len(self.dictionary)))

    def compute_ratio(self, ratio_formula):
        for key in self.dictionary.keys():
            self.dictionary[key]["ratio"] = ratio_formula(self.dictionary[key])

    def load_dictionary_from_json(self, file_name):
        """
        Load dictionary into mem from a json file
        :param file_name:
        :return:
        """
        with open(file_name, "r") as in_file:
            self.dictionary = json.load(in_file)
        log.info("Dictionary has been loaded from {} with size {}.".format(file_name, len(self.dictionary)))

    def display_keyword_rating(self, limit=20, best=True):
        """
        Display the dictionary ratio with best or worst with limit size
        :param limit: number of keywords to be displayed
        :param best: true to display best keywords
        :return:
        """
        i = 0
        for key, value in sorted(self.dictionary.iteritems(), key=lambda (k, v): (v["ratio"], k), reverse=best):
            if i < limit:
                print("%s: %s" % (key, value["ratio"]))
                self.display_keyword(key)
                i += 1

    def display_keyword(self, keyword):
        """

        :param keyword: keyword want to find.
        :return:
        """
        pprint(self.dictionary[keyword])
