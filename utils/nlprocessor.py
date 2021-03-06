# -- coding: UTF-8 --
import logging
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from stop_words import get_stop_words
from textblob import TextBlob
from textblob import exceptions

__author__ = 'Steve'
__version__ = '2.1'
log = logging.getLogger(__name__)


class NLProcessor:
    """
    This class is a natural language processor with one instance
    to process natural language
    """

    def __init__(self):

        self.stemmer = PorterStemmer()
        self.tokenizer = RegexpTokenizer(r'[0-9a-zA-Z\']+')
        self.lemmatizer = WordNetLemmatizer()

    @staticmethod
    def translate(sentence):
        """
        Translate sentence to English in unicode format
        :param sentence: sentence in any language
        :return: english sentence in utf-8 format or empty string if translatorError occurs
        """
        # Ignore portions of a string that can't convert to utf-8
        if not isinstance(sentence, unicode):
            sentence = sentence.decode('utf-8', 'ignore')
        tb = TextBlob(sentence)
        try:
            result = unicode(tb.translate())
        except exceptions.NotTranslated:
            result = sentence
        except exceptions.TranslatorError:
            result = ""

        return result

    def get_eng_sentences(self, paragraph):
        """
        Given a paragraph in any language,
        translate it into english sentences.
        :param paragraph: parapraph in any language
        :return: list of english sentences
        """
        eng_paragraph = self.translate(paragraph)
        tb = TextBlob(eng_paragraph)
        result = [s.raw for s in tb.sentences]
        log.debug((paragraph, result))
        return result

    def sentence_to_tokens(self, sentence, option='lemmatize'):
        """
        Given a sentence in english,
        return list of tokens with stop-word filtered, or lemmatized, tokenized
        :param sentence: English sentence
        :param option: lemmatize, stemming or none
        :return: list of non-stop word english tokens
        """

        log.debug("Tokenizing sentence")
        tokens = self.tokenizer.tokenize(sentence.lower())
        log.debug(tokens)

        # filter stop words
        log.debug("Filtering stop words")
        tokens = filter(lambda word: word not in get_stop_words('en'), tokens)
        log.debug(tokens)

        if option == 'lemmatize':
            # lemmatize
            log.debug("Lemmatizing")
            tokens = [self.lemmatizer.lemmatize(w) for w in tokens]
            log.debug(tokens)
        elif option == 'stem':
            # stemming
            log.debug("Stemming")
            tokens = [self.stemmer.stem(w) for w in tokens]
            log.debug(tokens)
        else:
            pass

        return tokens

    def paragraph_to_tokens(self, paragraph):
        """
        Given a paragraph in any language, translate it and tokenize it.
        :param paragraph: Paragraph in any language
        :return: List of tokens
        """
        eng_paragraph = self.translate(paragraph)
        return self.sentence_to_tokens(eng_paragraph)
