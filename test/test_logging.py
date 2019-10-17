import sys
from os.path import abspath, join, dirname
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
import src.log as log

logging = log.init_log()
logging.info("123")
