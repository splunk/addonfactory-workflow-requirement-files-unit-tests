import os.path, sys
import logging
from xml.sax.handler import ContentHandler
from xml.sax import make_parser

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
output_file_handler = logging.FileHandler("test_format_output.txt", mode='w')
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)
INVALID = False

def parsefile(file):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    parser.parse(file)

print('Running XML format checker:')
try:
    inputFolder=sys.argv[1]
except:
    print('Please pass directory_name')

if len(sys.argv)!=1: 
    inputFolder = sys.argv[1]

JENKIN_STATUS = True

for dirpath, dirs, files in os.walk(inputFolder): 
  for filename in files:
    fname = os.path.join(dirpath,filename)
    if fname.endswith('.log'):
        try:
            parsefile(fname)
            print(' Pass : {}'.format(str(fname)))
        except Exception as e:
            JENKIN_STATUS = False
            logger.debug(str(e) + "\n")
            logging.error(' Failed : {}'.format(str(e)))
    if fname.endswith(".xml"):
        logger.debug(fname + ":Invalid input file format")
        JENKIN_STATUS = False

if(JENKIN_STATUS == True):
    logger.debug("No formatting errors ")
else:
    exit(1)


