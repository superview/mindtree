from PyQt4 import QtCore, QtGui, Qt
import MTresources as RES


def CALLBACK( callback, *args, **kwargs ):
   def do_call():
      return callback( *args, **kwargs )
   
   return do_call


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
         theNewButton.setFont( RES.KeyboardFont )
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


class KeyboardWidget( QtGui.QTabWidget ):
   NAME_COUNTER = 0
   theApp = None
   
   def __init__( self, parent ):
      QtGui.QTabWidget.__init__( self, parent )
      
      self._keyboards = [ ]
      
      for kbTabName, kbRows in RES.KeyboardTabs.iteritems():
         self.addKeyboardTab( kbTabName, kbRows )

   def addKeyboardTab( self, name, buttonRows ):
      kb = QtGui.QWidget()
      #kb.setSizeIncrement(QtCore.QSize(1, 1))
      #kb.setMinimumHeight( 200 )
      self.addTab(kb, "")
      
      self.setTabText( len(self._keyboards), name )
      
      kb_tab = _KBTab( kb )
      kb_tab.addButtons( buttonRows )
      self._keyboards.append( kb_tab )
   
   @staticmethod
   def generateName( prefix ):
      KeyboardWidget.NAME_COUNTER += 1
      return prefix + str(KeyboardWidget.NAME_COUNTER)
   
 