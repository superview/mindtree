# setup.py
import glob
import os
import sys
from distutils.core import setup
import py2exe

def files( folder ):
   for path in glob.glob( folder + '\\*' ):
      if os.path.isfile( path ):
         yield path

data_files=[
           ( '.', glob.glob(sys.prefix + '\\DLLs\\tix8184.dll' )),
           ( 'tcl\\tix8.1', files(sys.prefix+'\\tcl\\tix8.1')),
           ( 'tcl\\tix8.1\\bitmaps', files( sys.prefix + '\\tcl\tix8.1\bitmaps')),
           ( 'tcl\\tix8.1\pref', files(sys.prefix+'\\tcl\\tix8.1\\pref')),
           ]

for entry in data_files:
   print entry

setup(windows=["MindTree.py"], packages=[ "TkTools" ])
