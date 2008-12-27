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


# #########################
# Collect Distribution Info

from ConfigParser import SafeConfigParser

RES = SafeConfigParser()
RES.read( [ 'resources.ini' ] )

name =          RES.get('Application','NAME')
version =       RES.get('Application','VERSION')
pythonVersion = RES.get('Application','REQUIRED_PYTHON_VERSION')
descr =         RES.get('Application','description')
long_descr =    RES.get('Application','longDescription')
author =        RES.get('Application','author')
author_email =  RES.get('Application','authorEmail')
proj_url =      RES.get('Application','projectURL')
dist_url =      RES.get('Application','distributionURL')
entryPoint =    RES.get('Application','entryPoint')
license =       RES.get('Application','license')

distName =      ('%s-%s' % ( name, version )) + os.extsep + 'zip'
distPath =      os.path.join( '..', 'sdist', distName )

# Make sure we've changed the version number
print( 'Current path: ', os.getcwd() )
print( 'Checking for ', distPath )
if os.path.exists( distPath ):
   print( '###########################################################' )
   print( '# A distribution with that version number already exists. #' )
   print( '###########################################################' )
   print( 'Type \'YES\' to coninue anyway.' )
   result = raw_input( '>>> ' )
   if result != 'YES':
      sys.exit( )


enchantDataFiles = enchant.utils.win32_data_files()
print( 'Enchant files', enchantDataFiles )


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
       license=license,
       windows=[entryPoint],
       data_files=enchantDataFiles,
       classifiers=[
                   'Development Status :: 4 - Beta',
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
                   'Programming Language :: Python :: 2.6',
                   'Topic :: Documentation',
                   'Topic :: Education',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Office/Business',
                   'Topic :: Scientific/Engineering :: Information Analysis'
                   ]
     )

