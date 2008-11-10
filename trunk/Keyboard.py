from PyQt4 import QtCore, QtGui, Qt
import mt2resources as RES


def CALLBACK( callback, *args, **kwargs ):
   def do_call():
      return callback( *args, **kwargs )
   
   return do_call


class _KBTab( object ):
   def __init__( self, parent ):
      self.buttons = [ ]
      
      self.gridLayoutWidget = QtGui.QWidget(parent)
      #self.gridLayoutWidget.setGeometry(QtCore.QRect(9, 0, 641, 83))
      self.gridLayoutWidget.setObjectName( KeyboardWidget.generateName("gridLayoutWidget") )
      self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
      self.gridLayout.setObjectName( KeyboardWidget.generateName("gridLayout") )

   def addButtons( self, buttonRows ):
      for buttonRow in buttonRows:
         self.addButtonRow( buttonRow )

   def addButtonRow( self, buttons ):
      newButtonRow = [ ]
      buttonRow    = len(self.buttons)
      buttonColumn = 0
      
      for buttonString in buttons:
         theNewButton = QtGui.QToolButton( self.gridLayoutWidget )
         theNewButton.setObjectName( KeyboardWidget.generateName("keyboardButton") )
         theNewButton.setText( buttonString )
         theNewButton.setFocusPolicy( QtCore.Qt.NoFocus )
         theNewButton.setFont( RES.KeyboardFont )
         theNewButton.setAutoRaise( True )
         
         QtCore.QObject.connect( theNewButton, QtCore.SIGNAL('clicked()'), CALLBACK(self.clickedButton, buttonString) )
         self.gridLayout.addWidget( theNewButton, buttonRow, buttonColumn, 1, 1 )
         newButtonRow.append( theNewButton )
         buttonColumn += 1
      
      self.buttons.append( newButtonRow )
   
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
      
      self.parent = parent
      self.keyboards = [ ]
      
      #sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
      #sizePolicy.setHorizontalStretch(0)
      #sizePolicy.setVerticalStretch(0)
      #sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
      #self.setSizePolicy(sizePolicy)
      #self.setSizeIncrement(QtCore.QSize(1, 1))
      self.setObjectName("tabWidget")
      #self.setMinimumHeight( 200 )
      
      for kbTabName, kbRows in RES.KeyboardTabs.iteritems():
         self.addKeyboardTab( kbTabName, kbRows )

   def addKeyboardTab( self, name, buttonRows ):
      kb = QtGui.QWidget()
      #kb.setSizeIncrement(QtCore.QSize(1, 1))
      #kb.setMinimumHeight( 200 )
      self.addTab(kb, "")
      
      self.setTabText( len(self.keyboards), name )
      
      kb_tab = _KBTab( kb )
      kb_tab.addButtons( buttonRows )
      self.keyboards.append( kb_tab )
   
   @staticmethod
   def generateName( prefix ):
      KeyboardWidget.NAME_COUNTER += 1
      return prefix + str(KeyboardWidget.NAME_COUNTER)
   
 