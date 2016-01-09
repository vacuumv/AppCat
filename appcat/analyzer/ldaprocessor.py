__author__ = 'Steve'
import logging

from gensim import corpora
from gensim.models.ldamulticore import LdaMulticore

from appcat.analyzer.corpusloader import CorpusProcessor

# log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')


class LdaProcessor:
    def __init__(self, ntopic=15, nword=15, iteration=50):
        """
        ntopic: number of topic wanted
        nword: list words in each topic
        iteration: passes the ldaprocessor run
        """
        self.corpus_loader=CorpusProcessor()
        self.ntopic = ntopic
        self.nword = nword
        self.iteration = iteration

        self.lda_out_file_name = "lda_out"

    def load_corpus(self):
        self.corpus=self.corpus_loader.load_processed_corpus()

    def save_lda_corpus_and_dic(self):
        """
        Given a corpus as a list of docs contains list of tokens,
        Store corpus to dict and mm file as ldaprocessor input data
        :param original_corpus:
        :return:
        """
        logging.info("Saving LDA corpus files...")

        # pprint(corpus)
        # Save dictionary
        dictionary = corpora.Dictionary(self.corpus)
        dictionary.save('/tmp/appcat.dict')

        # Save mmCorpus
        corpus_vec = [dictionary.doc2bow(doc) for doc in self.corpus]
        corpora.MmCorpus.serialize('/tmp/appcat.mm', corpus_vec)
        logging.info("LDA corpus files have been saved.")

    def load_corpus_from_file(self):
        self.corpus = corpora.MmCorpus('/tmp/appcat.mm')
        self.dictionary = corpora.Dictionary.load('/tmp/appcat.dict')

    def load_corpus_from_db(self):
        self.save_lda_corpus_and_dic()
        self.load_corpus_from_file()

    def perform(self, option='load'):
        """
        Perform LDA analysis to generate topics
        and topic distribution for each app
        """
        logging.info("Start Lda analysis")

        ldamodel = LdaMulticore(self.corpus, num_topics=self.ntopic, id2word=self.dictionary, passes=self.iteration)
        logging.info("LDA multicore modeling done")

        ldamodel.save(self.lda_out_file_name)

        self.topics = {}
        for i in range(0, self.ntopic, 1):
            self.topics["topic{}".format(i)] = ldamodel.show_topic(i, topn=self.nword)
            logging.info("Topic{}".format(i))
            words = [w[1] for w in self.topics["topic{}".format(i)]]
            logging.info(words)
            # self.result = [ldamodel[doc_bow] for doc_bow in self.corpus]

            # plogging.info(result)
            # plogging.info(type(ldamodel[doc_bow]))

    def load(self):
        """
        Load previous saved ldaprocessor results
        """
        try:
            return LdaMulticore.load(self.lda_out_file_name)
        except:
            return None


if __name__ == '__main__':
    # load_original_corpus()
    lda = LdaProcessor(iteration=5, ntopic=30)
    lda.load_corpus_from_file()
    # ldaprocessor.load_corpus_from_list(load_original_corpus())
    lda.perform()
