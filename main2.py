__author__ = 'Steve'
from appcat.appcosa import CommentProcessor
from utils.inputProcessor import InputProcessor

def process_app():
    processor = CommentProcessor()
    processor.process("281796108")

def process_all_app():
    processor = CommentProcessor()

    processor.process_all()



if __name__ == '__main__':
    process_all_app()
