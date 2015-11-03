import logging

__revise__ = "0915"
__author__ = 'Steve'

logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] %(asctime)s - %(message)s')
logging.getLogger(__name__).addHandler(logging.NullHandler())




