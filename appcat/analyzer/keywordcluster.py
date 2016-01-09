__author__ = 'Steve'

import logging, multiprocessing
from gensim.models.word2vec import Word2Vec
from appcat.analyzer.corpusloader import CommentCorpusLoader

log = logging.getLogger(__name__)


def train_word2vec(limit=1000):
    sentences = CommentCorpusLoader().load_all_comments_from_genre(limit,with_rating=False)
    model = Word2Vec(sentences, size=400, window=5, min_count=5,
                     workers=multiprocessing.cpu_count())

    model.save("word2vec.model")
    model.save_word2vec_format("word2vec.format", binary=False)


def load_word2vec_model():
    return Word2Vec.load_word2vec_format("word2vec.format", binary=False)




if __name__ == '__main__':
    # train_word2vec(limit=10000)
    model = load_word2vec_model()
    print(model.most_similar("queen"))
    print(model.most_similar("man"))