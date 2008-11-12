from PyQt4 import QtCore, QtGui
from utilities import splitFilePath
import os
import os.path

#############
# Startup Information
STARTUP_DISK               = None
STARTUP_PATH               = None
STARTUP_NAME               = None
STARTUP_EXT                = None
STARTUP_DISK, STARTUP_PATH, STARTUP_NAME, STARTUP_EXT = splitFilePath( os.getcwd() )
STARTUP_DISK               += os.sep

#############
# Main Application
ARCHIVER_FILE_TYPES        = 'MindTree Outline File (*.mto);;All Files (*.*)'
ARCHIVER_FILE_EXTENSION    = 'mto'

#############
# Project
PROJECT_WORKING_DIR        = os.path.join( STARTUP_DISK, 'MindTree Data', 'Logic' )
PROJECT_BACKUP_DIR         = 'backup'

#############
# TreeEditor
treeFont                   = QtGui.QFont( 'Lucida Sans Unicode', 12 )
articleFont                = QtGui.QFont( 'Lucida Sans Unicode', 10 )
emptyArticleIcon           = 'resources\\images\\file.gif'
fullArticleIcon            = 'resources\\images\\textfile.gif'

################
# KeyboardWidget
KeyboardFont = QtGui.QFont( 'Lucida Sans Unicode', 12 )
KeyboardTabs = { 'Logic': [ # Logic
                            [ u'\u00AC',        # negation
                              u'\u2227',        # conjunction
                              u'\u2228',        # disjunction
                              u'\u2192',        # conditional
                              u'\u2194',        # biconditional
                              u'\u2200',        # universal quantifier
                              u'\u2203',        # existential quantifier
                              u'\u2204',        # does not exist
                              u'\u25A1',        # alethic logic: Necessary
                              u'\u25C7'         # alethic logic: Possible
                              ],
                            # Metalogic
                            [ u'\u22A6',        # assertion
                              u'\u22A7',        # models
                              u'\u2234',        # therefore
                              u'\u2235',        # because
                              u'\u220E',        # endOfProof
                              u'\u22A4',        # tautology
                              u'\u22A5'         # contradiction
                              ],
                            # Set Theory
                            [ u'\u2205',        # NULL
                              u'\u2208',        # member
                              u'\u2209',        # not a member
                              u'\u2229',        # intersection
                              u'\u222A',        # union
                              u'\u2282',        # subset
                              u'\u2284',        # not a subset
                              u'\u2286',        # proper subset
                              u'\u2285',        # not a proper subset
                              u'\u2283',        # superset
                              u'\u2285',        # not a superset
                              u'\u2287',        # proper superset
                              u'\u2289',        # not a proper superset
                              u'\u00D7'         # cross product
                              ],
                            # Relations
                            [ u'\u225D',        # equal by definition
                              u'\u2261'         # tripple equals
                              ]
                          ],
                 'Math Script': [
                            [ u'\u210A',        # script small G
                              u'\u210B',        # script capital H
                              u'\u210C',        # black letter H
                              u'\u210D',        # double struck capital H
                              u'\u210E',        # planck Constant
                              u'\u210F'         # planck constant over two pi
                              ],
                            [ u'\u2110',        # script capital I
                              u'\u2111',        # black letter capital I
                              u'\u2112',        # script capital L
                              u'\u2113',        # script small L
                              u'\u2115',        # double struck capital N
                              u'\u2118',        # script capital P
                              u'\u2119'         # double struck capital P
                              ],
                            [ u'\u211A',        # double struct capital Q
                              u'\u211B',        # script capital R
                              u'\u211C',        # blcak letter capital R
                              u'\u211D',        # double struck capital R
                              u'\u2124',        # double struck capital Z
                              u'\u212C'         # script capital B
                              ],
                            [ u'\u212D',        # black letter capital C
                              u'\u212F',        # script small E
                              u'\u2130',        # script capital E
                              u'\u2131',        # script capital F
                              u'\u2133',        # script capital M
                              u'\u2134'         # script small O
                              ]
                          ],
                 'Greek': [ # Greek Capitals
                            [ u'\u0391',
                              u'\u0392',
                              u'\u0393',
                              u'\u0394',
                              u'\u0395',
                              u'\u0396',
                              u'\u0397',
                              u'\u0398',
                              u'\u0399',
                              u'\u039A',
                              u'\u039B',
                              u'\u039C',
                              u'\u039D'
                              ],
                            [ u'\u03B1',
                              u'\u03B2',
                              u'\u03B3',
                              u'\u03B4',
                              u'\u03B5',
                              u'\u03B6',
                              u'\u03B7',
                              u'\u03B8',
                              u'\u03B9',
                              u'\u03BA',
                              u'\u03BB',
                              u'\u03BC',
                              u'\u03BD'
                              ],
                            [ u'\u039E',
                              u'\u039F',
                              u'\u03A0',
                              u'\u03A1',
                              u'\u03A3',
                              u'\u03A3',
                              u'\u03A4',
                              u'\u03A5',
                              u'\u03A6',
                              u'\u03A7',
                              u'\u03A8',
                              u'\u03A9'
                              ],
                            [ u'\u03BE',
                              u'\u03BF',
                              u'\u03C0',
                              u'\u03C1',
                              u'\u03C2',
                              u'\u03C3',
                              u'\u03C4',
                              u'\u03C5',
                              u'\u03C6',
                              u'\u03C7',
                              u'\u03C8',
                              u'\u03C9'
                              ]
                          ],
               }
