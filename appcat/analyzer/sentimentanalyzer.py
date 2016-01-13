import logging

import matplotlib.pyplot as plt
from textblob import TextBlob
import operator
__author__ = 'Steve'
__status__ = 'Development'
__date__ = '20151103'
log = logging.getLogger(__name__)

# logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')


class SentimentAnalyzer:
    """
    Get an app item from mongodb and analyze the comment sentiment
    """

    # TODO: Finish the output part
    def analyze_app_plot(self, app, detail=False):

        result = {}
        track_id = app["trackId"]
        length = len(app["comments"])

        sents = []
        # For each comment
        for index, comment in enumerate(app["comments"]):
            content = comment["content"]
            blob = TextBlob(content)
            sentiment = 0
            for sentence in blob.sentences:
                sentiment += sentence.sentiment.polarity
            sents.append(sentiment)

        stat = get_list_stat(sents, 0.2)
        plt.title(track_id)
        plt.plot(stat[0], stat[1], '-')
        plt.show()

    # TODO: Finish the output part
    def analyze_app(self, app, detail=False):

        result = {}
        track_id = app["trackId"]
        length = len(app["comments"])
        neg_sentiment = 0
        pos_sentiment = 0
        neg_sentiment_count = 0
        pos_sentiment_count = 0
        for index, comment in enumerate(app["comments"]):
            content = comment["content"]
            blob = TextBlob(content)
            sentiment = 0
            for sentence in blob.sentences:
                log.debug("\t\t\t[[{}]]".format(sentence.sentiment.polarity))
                log.debug("\t\t\t{}".format(sentence))
                sentiment += sentence.sentiment.polarity

            if detail:
                log.debug("{} [{}]".format(index, sentiment))

            if sentiment > 0:
                pos_sentiment += sentiment
                pos_sentiment_count += 1
            else:
                neg_sentiment += sentiment
                neg_sentiment_count += 1
            if detail:
                log.info("\t\t{}".format(content))

        result["trackId"] = track_id
        result["count"] = length
        result["pos_pc"] = pos_sentiment / pos_sentiment_count if pos_sentiment_count > 0 else 0
        result["neg_pc"] = neg_sentiment / neg_sentiment_count if neg_sentiment_count > 0 else 0
        self.display_info(result)

    def display_info(self, result):
        log.info("\n")
        log.info("App Id:[{}]".format(result["trackId"]))
        log.info("\tTotal {} comments".format(result["count"]))
        log.info("\tPositive sentiment: {} per comment.".format(result["pos_pc"]))
        log.info("\tNegative sentiment: {} per comment.".format(result["neg_pc"]))


def get_list_stat(num_list, segment):
    """
    Get statistic for list of numbers and format it to matplotlib format.
    Also, apply normalization to statistics.
    """
    stat = {}
    for num in num_list:
        num = num // segment * segment
        stat[num] = stat.get(num, 0) + 1
    sorted_stat = sorted(stat.items(), key=operator.itemgetter(0))
    return [s[0] for s in sorted_stat], [float(s[1]) / len(num_list) for s in sorted_stat]
