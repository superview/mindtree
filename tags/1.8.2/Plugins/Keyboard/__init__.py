from PyQt4 import QtCore, QtGui, Qt
from MindTreeApplicationFramework import *


def CALLBACK( callback, *args, **kwargs ):
   def do_call():
      return callback( *args, **kwargs )
   
   return do_call

KeyboardTabs = { 'Logic': [ # Logic
                            [ u'\u00AC',        # negation
                              u'\u2227',        # conjunction
                              u'\u2228',        # disjunction
                              u'\u2192',        # conditional
                              u'\u2194',        # biconditional
                              u'\u2200',        # universal quantifier
                              u'\u2203',        # existential quantifier
                              #u'\u2204',        # does not exist
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
                            # Relations
                            [ u'\u225D',        # equal by definition
                              u'\u2261',        # tripple equals
                              ]
                          ],
                 'Set Theory': [
                            [ u'\u2205',        # NULL
                              u'\u00D7',        # cross product
                              u'\u2229',        # intersection
                              u'\u222A',        # union
                              ],
                            [ u'\u2208',        # member
                              u'\u2282',        # subset
                              u'\u2286',        # proper subset
                              u'\u2283',        # superset
                              u'\u2287',        # proper superset
                              ],
                            [ u'\u2209',        # not a member
                              u'\u2284',        # not a subset
                              u'\u2288',        # not a proper subset
                              u'\u2285',        # not a superset
                              u'\u2289'         # not a proper superset
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

class _KBTab( object ):
   def __init__( self, parent ):
      self._buttons          = [ ]
      self._gridLayoutWidget = None
      self._gridLayout       = None
      
      self._gridLayoutWidget = QtGui.QWidget(parent)
      self._gridLayoutWidget.setObjectName( KeyboardWidget.generateName("gridLayoutWidget") )
      self._gridLayout = QtGui.QGridLayout(self._gridLayoutWidget)
      self._gridLayout.setObjectName( KeyboardWidget.generateName("gridLayout") )

   def addButtons( self, buttonRows ):
      for buttonRow in buttonRows:
         self.addButtonRow( buttonRow )

   def addButtonRow( self, buttons ):
      newButtonRow = [ ]
      buttonRow    = len(self._buttons)
      buttonColumn = 0
      
      for buttonString in buttons:
         theNewButton = QtGui.QToolButton( self._gridLayoutWidget )
         theNewButton.setObjectName( KeyboardWidget.generateName("keyboardButton") )
         theNewButton.setText( buttonString )
         theNewButton.setFocusPolicy( QtCore.Qt.NoFocus )
         theNewButton.setFont( RES.getFont( 'Keyboard','Font' ) )
         theNewButton.setAutoRaise( True )
         
         QtCore.QObject.connect( theNewButton, QtCore.SIGNAL('clicked()'), CALLBACK(self.clickedButton, buttonString) )
         self._gridLayout.addWidget( theNewButton, buttonRow, buttonColumn, 1, 1 )
         newButtonRow.append( theNewButton )
         buttonColumn += 1
      
      self._buttons.append( newButtonRow )
   
   def clickedButton( self, string ):
      w = KeyboardWidget.theApp.focusWidget( )
      
      if isinstance( w, QtGui.QTextEdit ):
         w.insertPlainText( string )
      elif isinstance( w, QtGui.QLineEdit ):
         w.insert( string )


class KeyboardWidget( QtGui.QTabWidget, MindTreePluggableTool ):
   NAME_COUNTER = 0
   theApp = None

   NAME             = 'Keyboard'
   VERSION          = ( 1, 1 )
   BUILD_DATE       = ( 2008, 12, 4 )

   DEFAULT_SETTINGS = {
                         'font' : 'Lucida Sans Unicode:12',
                         #'tabs' : {
                 #'Logic': [ # Logic
                            #[ u'\u00AC',        # negation
                              #u'\u2227',        # conjunction
                              #u'\u2228',        # disjunction
                              #u'\u2192',        # conditional
                              #u'\u2194',        # biconditional
                              #u'\u2200',        # universal quantifier
                              #u'\u2203',        # existential quantifier
                              ##u'\u2204',        # does not exist
                              #u'\u25A1',        # alethic logic: Necessary
                              #u'\u25C7'         # alethic logic: Possible
                              #],
                            ## Metalogic
                            #[ u'\u22A6',        # assertion
                              #u'\u22A7',        # models
                              #u'\u2234',        # therefore
                              #u'\u2235',        # because
                              #u'\u220E',        # endOfProof
                              #u'\u22A4',        # tautology
                              #u'\u22A5'         # contradiction
                              #],
                            ## Relations
                            #[ u'\u225D',        # equal by definition
                              #u'\u2261',        # tripple equals
                              #]
                          #],
                 #'Set Theory': [
                            #[ u'\u2205',        # NULL
                              #u'\u00D7',        # cross product
                              #u'\u2229',        # intersection
                              #u'\u222A',        # union
                              #],
                            #[ u'\u2208',        # member
                              #u'\u2282',        # subset
                              #u'\u2286',        # proper subset
                              #u'\u2283',        # superset
                              #u'\u2287',        # proper superset
                              #],
                            #[ u'\u2209',        # not a member
                              #u'\u2284',        # not a subset
                              #u'\u2288',        # not a proper subset
                              #u'\u2285',        # not a superset
                              #u'\u2289'         # not a proper superset
                              #]
                          #],
                 #'Math Script': [
                            #[ u'\u210A',        # script small G
                              #u'\u210B',        # script capital H
                              #u'\u210C',        # black letter H
                              #u'\u210D',        # double struck capital H
                              #u'\u210E',        # planck Constant
                              #u'\u210F'         # planck constant over two pi
                              #],
                            #[ u'\u2110',        # script capital I
                              #u'\u2111',        # black letter capital I
                              #u'\u2112',        # script capital L
                              #u'\u2113',        # script small L
                              #u'\u2115',        # double struck capital N
                              #u'\u2118',        # script capital P
                              #u'\u2119'         # double struck capital P
                              #],
                            #[ u'\u211A',        # double struct capital Q
                              #u'\u211B',        # script capital R
                              #u'\u211C',        # blcak letter capital R
                              #u'\u211D',        # double struck capital R
                              #u'\u2124',        # double struck capital Z
                              #u'\u212C'         # script capital B
                              #],
                            #[ u'\u212D',        # black letter capital C
                              #u'\u212F',        # script small E
                              #u'\u2130',        # script capital E
                              #u'\u2131',        # script capital F
                              #u'\u2133',        # script capital M
                              #u'\u2134'         # script small O
                              #]
                          #],
                 #'Greek': [ # Greek Capitals
                            #[ u'\u0391',
                              #u'\u0392',
                              #u'\u0393',
                              #u'\u0394',
                              #u'\u0395',
                              #u'\u0396',
                              #u'\u0397',
                              #u'\u0398',
                              #u'\u0399',
                              #u'\u039A',
                              #u'\u039B',
                              #u'\u039C',
                              #u'\u039D'
                              #],
                            #[ u'\u03B1',
                              #u'\u03B2',
                              #u'\u03B3',
                              #u'\u03B4',
                              #u'\u03B5',
                              #u'\u03B6',
                              #u'\u03B7',
                              #u'\u03B8',
                              #u'\u03B9',
                              #u'\u03BA',
                              #u'\u03BB',
                              #u'\u03BC',
                              #u'\u03BD'
                              #],
                            #[ u'\u039E',
                              #u'\u039F',
                              #u'\u03A0',
                              #u'\u03A1',
                              #u'\u03A3',
                              #u'\u03A3',
                              #u'\u03A4',
                              #u'\u03A5',
                              #u'\u03A6',
                              #u'\u03A7',
                              #u'\u03A8',
                              #u'\u03A9'
                              #],
                            #[ u'\u03BE',
                              #u'\u03BF',
                              #u'\u03C0',
                              #u'\u03C1',
                              #u'\u03C2',
                              #u'\u03C3',
                              #u'\u03C4',
                              #u'\u03C5',
                              #u'\u03C6',
                              #u'\u03C7',
                              #u'\u03C8',
                              #u'\u03C9'
                              #]
                          #],
               #}
                      }
   
   def __init__( self, parent, app, outlineView ):
      KeyboardWidget.theApp = app
      
      QtGui.QTabWidget.__init__( self, parent )
      MindTreePluggableTool.__init__( self, parent, app, outlineView )
      
      self._keyboards = [ ]
      
      for kbTabName, kbRows in KeyboardTabs.iteritems():
         self.addKeyboardTab( kbTabName, kbRows )

   def addKeyboardTab( self, name, buttonRows ):
      kb = QtGui.QWidget()
      self.addTab(kb, "")
      
      self.setTabText( len(self._keyboards), name )
      
      kb_tab = _KBTab( kb )
      kb_tab.addButtons( buttonRows )
      self._keyboards.append( kb_tab )
   
   @staticmethod
   def generateName( prefix ):
      KeyboardWidget.NAME_COUNTER += 1
      return prefix + str(KeyboardWidget.NAME_COUNTER)
   
 
pluginClass = KeyboardWidget
