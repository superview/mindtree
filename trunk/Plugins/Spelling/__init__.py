from ApplicationFramework import RES, PluggableTool
from PyQt4 import QtCore, QtGui

try:
   import enchant.checker
   from enchant.tokenize import EmailFilter, URLFilter
except:
   if RES.getboolean('Tool.Spelling','hideIfPyEnchantNotFound'):
      raise


class Spelling( PluggableTool, QtGui.QWidget ):
   NAME             = 'Spelling'
   VERSION          = ( 1, 0 )
   BUILD_DATE       = ( 2008, 11, 24 )
   
   DEFAULT_SETTINGS = {
                      'language':             'en_US',
                      'personalwordlist':     ''
                      }

   def __init__( self, parent, outlineView ):
      PluggableTool.__init__( self )
      QtGui.QWidget.__init__( self, parent )
      
      try:
         language = RES.get('Spelling','language')
         self._chkr = enchant.checker.SpellChecker( language, filters=[EmailFilter,URLFilter])
      except:
         pass
      
      self._outlineView  = outlineView
      self._cursor       = None
      self._currentLine  = 0
      self._maxLine      = 0
      
      self._errWord      = ''
      self._errIndex     = '1.0'
      self._textLines    = [ ]
      self._scanLineNum  = 0
      
      self._suggestions = None
      self._entry       = None
      self._globalReplace = { }
      
      # Build GUI
      gridLayout = QtGui.QGridLayout( self )
      gridLayout.setObjectName( 'SpellingGridLayout' )
      
      row = 0
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('Tool.Spelling','contextLabel') )
      gridLayout.addWidget( label, row, 0, 1, 1 )
      
      self._context = QtGui.QComboBox( self )
      self._context.addItems( RES.getMultipartResource('Tool.Find','contextList',translate=True) )
      gridLayout.addWidget( self._context, row, 1, 1, 3 )
      
      row += 1
      
      self._recheckBtn = QtGui.QPushButton( self )
      self._recheckBtn.setText( RES.get('Tool.Spelling','recheckBtnLabel',translate=True) )
      QtCore.QObject.connect( self._recheckBtn, QtCore.SIGNAL('clicked()'), self.recheck )
      gridLayout.addWidget( self._recheckBtn, row, 0, 1, 1 )
      
      self._sugList    = QtGui.QListWidget( self )
      gridLayout.addWidget( self._sugList, row, 1, 4, 1 )
      QtCore.QObject.connect( self._sugList, QtCore.SIGNAL('itemActivated(QListWidgetItem)'), self.selectSuggestion )
      
      self._suggestion = QtGui.QLineEdit( self )
      gridLayout.addWidget( self._suggestion, row, 2, 1, 2 )
      
      row += 1
      
      self._stopBtn = QtGui.QPushButton( self )
      self._stopBtn.setText( RES.get('Tool.Spelling','stopBtnLabel',translate=True) )
      QtCore.QObject.connect( self._stopBtn, QtCore.SIGNAL('clicked()'), self.stop )
      gridLayout.addWidget( self._stopBtn, row, 0, 1, 1 )
      
      self._replaceBtn = QtGui.QPushButton( self )
      self._replaceBtn.setText( RES.get('Tool.Spelling','replaceBtnLabel',translate=True) )
      QtCore.QObject.connect( self._replaceBtn, QtCore.SIGNAL('clicked()'), self.replace )
      gridLayout.addWidget( self._replaceBtn, row, 2, 1, 1 )
      
      self._replaceAllBtn = QtGui.QPushButton( self )
      self._replaceAllBtn.setText( RES.get('Tool.Spelling','replaceAllBtnLabel',translate=True) )
      QtCore.QObject.connect( self._replaceAllBtn, QtCore.SIGNAL('clicked()'), self.replaceAll )
      gridLayout.addWidget( self._replaceAllBtn, row, 3, 1, 1 )
      
      row += 1
      
      self._ignoreBtn = QtGui.QPushButton( self )
      self._ignoreBtn.setText( RES.get('Tool.Spelling','ignoreBtnLabel',translate=True) )
      QtCore.QObject.connect( self._ignoreBtn, QtCore.SIGNAL('clicked()'), self.ignore )
      gridLayout.addWidget( self._ignoreBtn, row, 2, 1, 1 )
      
      self._ignoreAllBtn = QtGui.QPushButton( self )
      self._ignoreAllBtn.setText( RES.get('Tool.Spelling','ignoreAllBtnLabel',translate=True) )
      QtCore.QObject.connect( self._ignoreAllBtn, QtCore.SIGNAL('clicked()'), self.ignoreAll )
      gridLayout.addWidget( self._ignoreAllBtn, row, 3, 1, 1 )
      
      row += 1
      
      self._addBtn = QtGui.QPushButton( self )
      self._addBtn.setText( RES.get('Tool.Spelling','addBtnLabel',translate=True) )
      QtCore.QObject.connect( self._addBtn, QtCore.SIGNAL('clicked()'), self.add )
      gridLayout.addWidget( self._addBtn, row, 2, 1, 1 )

   def recheck( self ):
      textToCheck = self._outlineView.articleWidget( ).toPlainText( )
      self._chkr.set_text( textToCheck )
      self.next( )

   def stop( self ):
      pass

   def selectSuggestion( self, itemList ):
      pass
   
   def replace( self ):
      pass
   
   def replaceAll( self ):
      pass
   
   def ignore( self ):
      pass
   
   def ignoreAll( self ):
      pass
   
   def add( self ):
      pass

   def next( self ):
      self._errWord = ''
      
      pass
   
   def _next( self ):
      try:
         self._chkr.next( )
      except StopIteration:
         if self._scanLineNum == len(self._textLines):
            raise StopIteration
         else:
            self._chkr.set_text( self._textLines[ self._scanLineNum ] )
            self._scanLineNum += 1
         
         self._next()


pluginClass = Spelling
