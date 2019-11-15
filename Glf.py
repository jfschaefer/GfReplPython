"""
A Python script for combining GF with the semantics construction in MMT.
"""

import GfRepl as gf
import subprocess
import requests
import sys
import os
import time


LOCATION_MMT_JAR = '/home/jfs/mmt/systems/MMT/deploy/mmt.jar'
# GF_BIN = 'gf'   # works if gf is in path
GF_BIN = '/usr/bin/gf'

MMT_PORT = '8080'

GF_CATEGORY = 'S'                    # category for parsing
MMT_ARCHIVE = 'teaching/lbs1920'
SEMANTICS_VIEW = 'http://mathhub.info/teaching/lbs1920/assignment3/A3SemanticsConstruction'


GF_CONCRETE_FILE = '/home/jfs/mmt/content/MathHub/teaching/lbs1920/source/assignment3/Assignment3Eng.gf'

# the following files have to be relative to the source directory in the MMT archive
GF_ABSTRACT_FILES = ['assignment3/Assignment3.gf']
MMT_FILES = ['assignment3/assignment3.mmt']


printIndented = lambda s : print('    ' + s.replace(os.linesep, os.linesep + '    '))

# START MMT SERVER
extensions = ['extension info.kwarc.mmt.glf.GlfConstructServer',
              'extension info.kwarc.mmt.glf.GlfBuildServer']
mmt_proc = subprocess.Popen(
        ['java', '-jar', LOCATION_MMT_JAR,
         '-w', ' ; '.join(extensions) + ' ; server on ' + MMT_PORT])

print(('java', '-jar', LOCATION_MMT_JAR,
         '-w', '"' + ' ; '.join(extensions) + ' ; server on ' + MMT_PORT + '"'))

# INITIALIZE GF REPL
gfrepl = gf.GfRepl(GF_BIN)

print(f'Importing "{GF_CONCRETE_FILE}" into GF')
r = gfrepl.handleLine('import ' + GF_CONCRETE_FILE)
printIndented(r)


def jsonPost(url, json):
    response = requests.post(url, json=json)
    try:
        return response.json()
    except:
        print("ERROR: FAILED TO PARSE RESPONSE AS JSON!")
        print("RESPONSE:")
        print(response.text)
        sys.exit(1)

import time
print("Sleeping a little to give MMT time to start-up the server...")
time.sleep(2)

# BUILD MMT FILES AND IMPORT ABSTRACT GRAMMAR INTO MMT
build_url = 'http://localhost:' + MMT_PORT + '/:glf-build'
buildrequests = [{'archive' : MMT_ARCHIVE, 'file' : f} for f in GF_ABSTRACT_FILES + MMT_FILES]
for br in buildrequests:
    print('Trying to build ' + br['file'])
    resp = jsonPost(build_url, br)
    print('    ' + str(resp))


# START THE MAIN LOOP
print('DONE')
print('You may now enter sentences.')

construct_url = 'http://localhost:' + MMT_PORT + '/:glf-construct'
while True:
    sentence = input('> ')
    gfresponse = gfrepl.handleLine('parse -cat=' + GF_CATEGORY + ' "' + sentence.replace('"', '\\"') + '"').strip()
    printIndented(gfresponse)
    if gfresponse.startswith("The parser failed at token") or gfresponse == "The sentence is not complete":
        continue
    parsetrees = gfresponse.splitlines()
    request = {'semanticsView' : SEMANTICS_VIEW, 'ASTs' : parsetrees}
    r = jsonPost(construct_url, request)
    print(os.linesep.join(r))

