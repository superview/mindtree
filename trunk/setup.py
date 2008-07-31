from distutils.core import setup
import enchant

setup( name='MindTree',
       version='0.1.0',
       description='Notes organizer/Outliner/PIM.',
       long_description='MindTree is an outliner application designed for taking and organizing notes and publishing these notes to the web.',
       url='http://code.google.com/p/mindtree',
       author='Ron Longo',
       author_email='ron.longo@cox.net',
       license='Apache License 2.0',
       data_files=[ ( 'PyEnchant', enchant.utils.win32_data_files() ) ],
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

