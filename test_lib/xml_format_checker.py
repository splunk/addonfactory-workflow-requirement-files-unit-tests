import os.path, sys
import logging
from xml.sax.handler import ContentHandler
from xml.sax import make_parser

def parsefile(file):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    parser.parse(file)

try:
    inputFolder=sys.argv[1]
except:
    print('Please pass directory_name')

if len(sys.argv)!=1: 
    inputFolder = sys.argv[1]

JENKIN_STATUS = True
testResult = open("test_format_output.txt", "w")

for dirpath, dirs, files in os.walk(inputFolder): 
  for filename in files:
    fname = os.path.join(dirpath,filename)
    if fname.endswith('.log'):
        try:
            parsefile(fname)
            print(' Pass : {}'.format(str(fname)))
        except Exception as e:
            JENKIN_STATUS = False
            testResult.write(str(e) + "\n")
            logging.error(' Failed : {}'.format(str(e)))
    if fname.endswith(".xml"):
        testResult.write(fname + ":Invalid input file format")
        JENKIN_STATUS = False

if(JENKIN_STATUS == True):
    testResult.write("No formatting errors \n")
    testResult.close()    
else:
    testResult.close() 
    exit(1)


