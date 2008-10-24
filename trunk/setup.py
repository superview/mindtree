from __future__ import print_function, unicode_literals
from distutils.core import setup
import glob
import sys
import os
import os.path
import enchant.utils

try:
   import py2exe
except:
   pass

def files(folder):
   for path in glob.glob(folder+'/*'):
      if os.path.isfile(path):
         yield path

# Setup some initial values
name='MindTree'
version='1.0.0-a002'
pythonVersion='%d.%d' % (sys.version_info[:2])
descr='Notes organizer/Outliner/PIM for Python %s.' % pythonVersion
long_descr='MindTree is an outliner application designed for taking and organizing notes and publishing these notes to the web.  Requires Python %s.' % pythonVersion
author='Ron Longo'
author_email='ron.longo@cox.net'
proj_url='http://code.google.com/p/mindtree'
dist_url=proj_url + '/downloads/list'
entryPoint='MindTree.py'

tixDataFiles = [
               ('DLLs', glob.glob(sys.prefix+'/DLLs/tix84.dll')),
               ('tcl/tix8.4', files(sys.prefix+'/tcl/tix8.4')),
               ('tcl/tix8.4/bitmaps', files(sys.prefix+'/tcl/tix8.4/bitmaps')),
               ('tcl/tix8.4/pref', files(sys.prefix+'/tcl/tix8.4/pref')),
               ]

enchantDataFiles = enchant.utils.win32_data_files()


# Make sure we've changed the version number
distName = ('%s-%s' % ( name, version )) + os.extsep + 'zip'
distPath = os.path.join( '..', 'sdist', distName )
print( 'Current path: ', os.getcwd() )
print( 'Checking for ', distPath ) )
if os.path.exists( distPath ):
   print( '###########################################################' )
   print( '# A distribution with that version number already exists. #' )
   print( '###########################################################' )
   print( 'Type \'YES\' to coninue anyway.' )
   result = raw_input( '>>> ' )
   if result != 'YES':
      sys.exit( )


# Create the Distribution
setup( name=name,
       version=version,
       description=descr,
       long_description=long_descr,
       author=author,
       author_email=author_email,
       maintainer=author,
       maintainer_email=author_email,
       url=proj_url,
       download_url=dist_url,
       license='Apache License 2.0',
       windows=[entryPoint],
       data_files=tixDataFiles + enchantDataFiles,
       classifiers=[
                   'Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Financial and Insurance Industry',
                   'Intended Audience :: Healthcare Industry',
                   'Intended Audience :: Information Technology',
                   'Intended Audience :: Manufacturing',
                   'Intended Audience :: Other Audience',
                   'Intended Audience :: Religion',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: System Administrators',
                   'Intended Audience :: Telecommunications Industry',
                   'License :: OSI Approved :: Apache Software License',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Topic :: Documentation',
                   'Topic :: Education',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Office/Business',
                   'Topic :: Scientific/Engineering :: Information Analysis'
                   ]
     )

