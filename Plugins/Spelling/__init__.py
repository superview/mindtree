from PyQt4 import QtCore, QtGui

from MindTreeApplicationFramework import *

try:
   import enchant.checker
   from enchant.tokenize import EmailFilter, URLFilter
except:
   if RES.getboolean('Spelling','hideIfPyEnchantNotFound'):
      raise


class Spelling( MindTreePluggableTool, QtGui.QWidget ):
   NAME             = 'Spelling'
   VERSION          = ( 1, 1 )
   BUILD_DATE       = ( 2008, 12, 4 )
   
   DEFAULT_SETTINGS = {
                      # Resources
                      'hideIfPyEnchantNotFound': 'True',
                      'scopeLabel':              'Scope',
                      'scopeList':               'selection:article:subtree:all',
                      'recheckBtnLabel':         'Recheck',
                      'stopBtnLabel':            'Stop',
                      'replaceBtnLabel':         'Replace',
                      'replaceAllBtnLabel':      'Replace All',
                      'ignoreBtnLabel':          'Ignore',
                      'ignoreAllBtnLabel':       'Ignore All',
                      'addBtnLabel':             'Add',
                      # Configuration
                      'language':                'en_US',
                      'personalwordlist':        ''
                      }

   def __init__( self, parent, app, outlineView ):
      MindTreePluggableTool.__init__( self, parent, app, outlineView )
      QtGui.QWidget.__init__( self, parent )
      
      try:
         language = RES.get('Spelling','language')
         self._chkr = enchant.checker.SpellChecker( language, filters=[EmailFilter,URLFilter])
      except:
         pass
      
      #self._outlineView  = outlineView
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
      label.setText( RES.get('Spelling','scopeLabel') )
      gridLayout.addWidget( label, row, 0, 1, 1 )
      
      self._scope = QtGui.QComboBox( self )
      self._scope.addItems( RES.getMultipartResource('Spelling','scopeList',translate=True) )
      gridLayout.addWidget( self._scope, row, 1, 1, 3 )
      
      ### Since we only currently support the article context, we must select
      ### make it fixed.
      for idx,name in enumerate( RES.get('Spelling','scopeList') ):
         if name.upper() == 'ARTICLE':
            break
      
      self._scope.setCurrentIndex( idx )
      self._scope.setEditable( False )
      self._scope.setEnabled( False )
      
      row += 1
      
      self._recheckBtn = QtGui.QPushButton( self )
      self._recheckBtn.setText( RES.get('Spelling','recheckBtnLabel',translate=True) )
      QtCore.QObject.connect( self._recheckBtn, QtCore.SIGNAL('clicked()'), self.recheck )
      gridLayout.addWidget( self._recheckBtn, row, 0, 1, 1 )
      
      self._sugList    = QtGui.QListWidget( self )
      self._sugList.setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
      gridLayout.addWidget( self._sugList, row, 1, 4, 1 )
      QtCore.QObject.connect( self._sugList, QtCore.SIGNAL('itemSelectionChanged()'), self.selectSuggestion )
      
      self._suggestion = QtGui.QLineEdit( self )
      gridLayout.addWidget( self._suggestion, row, 2, 1, 2 )
      
      row += 1
      
      self._stopBtn = QtGui.QPushButton( self )
      self._stopBtn.setText( RES.get('Spelling','stopBtnLabel',translate=True) )
      QtCore.QObject.connect( self._stopBtn, QtCore.SIGNAL('clicked()'), self.stop )
      gridLayout.addWidget( self._stopBtn, row, 0, 1, 1 )
      
      self._replaceBtn = QtGui.QPushButton( self )
      self._replaceBtn.setText( RES.get('Spelling','replaceBtnLabel',translate=True) )
      QtCore.QObject.connect( self._replaceBtn, QtCore.SIGNAL('clicked()'), self.replace )
      gridLayout.addWidget( self._replaceBtn, row, 2, 1, 1 )
      
      self._replaceAllBtn = QtGui.QPushButton( self )
      self._replaceAllBtn.setText( RES.get('Spelling','replaceAllBtnLabel',translate=True) )
      QtCore.QObject.connect( self._replaceAllBtn, QtCore.SIGNAL('clicked()'), self.replaceAll )
      gridLayout.addWidget( self._replaceAllBtn, row, 3, 1, 1 )
      
      row += 1
      
      self._ignoreBtn = QtGui.QPushButton( self )
      self._ignoreBtn.setText( RES.get('Spelling','ignoreBtnLabel',translate=True) )
      QtCore.QObject.connect( self._ignoreBtn, QtCore.SIGNAL('clicked()'), self.ignore )
      gridLayout.addWidget( self._ignoreBtn, row, 2, 1, 1 )
      
      self._ignoreAllBtn = QtGui.QPushButton( self )
      self._ignoreAllBtn.setText( RES.get('Spelling','ignoreAllBtnLabel',translate=True) )
      QtCore.QObject.connect( self._ignoreAllBtn, QtCore.SIGNAL('clicked()'), self.ignoreAll )
      gridLayout.addWidget( self._ignoreAllBtn, row, 3, 1, 1 )
      
      row += 1
      
      self._addBtn = QtGui.QPushButton( self )
      self._addBtn.setText( RES.get('Spelling','addBtnLabel',translate=True) )
      QtCore.QObject.connect( self._addBtn, QtCore.SIGNAL('clicked()'), self.add )
      gridLayout.addWidget( self._addBtn, row, 2, 1, 1 )
      
      # Define the special selection
      format = QtGui.QTextCharFormat( )
      format.setFontUnderline( True )
      format.setUnderlineStyle( QtGui.QTextCharFormat.SpellCheckUnderline )
      format.setUnderlineColor( QtGui.QColor( 'red' ) )
      self.defineTextSelector( format )

   def recheck( self ):
      self._sugList.clear( )
      textToCheck = unicode(self._outlineView.articleWidget( ).toPlainText( ))
      self._chkr.set_text( textToCheck )
      self.next( )

   def stop( self ):
      self._sugList.clear( )
      self._outlineView.articleWidget().setExtraSelections( [ ] )

   def selectSuggestion( self ):
      selectedItems = self._sugList.selectedItems( )
      if len(selectedItems) > 0:
         itemIndex = self._sugList.indexFromItem(selectedItems[ 0 ])
         string = unicode(itemIndex.data().toString())
         self._suggestion.setText( string )
   
   def replace( self ):
      newWord = unicode(self._suggestion.text())
      if (newWord == self._chkr.word) or (newWord == ''):
         return
      
      articleWidget = self._outlineView.articleWidget()
      spellingCursor = self.specialSelection().cursor
      
      # Replace the text in the article view widget
      spellingCursor.removeSelectedText()
      articleWidget.insertPlainText( newWord )
      
      # Replace the text in the spell checker
      self._chkr.replace( newWord )
      
      # Clear the error info from the article widget and suggestion list
      self._sugList.clear( )
      spellingCursor.clearSelection()
      
      self.next( )

   def replaceAll( self ):
      self._globalReplace[ self._chkr.word ] = unicode(self._suggestion.text())
      self.replace( )
   
   def ignore( self ):
      self.next( )
   
   def ignoreAll( self ):
      self._chkr.ignore_always( )
      self.next( )
   
   def add( self ):
      self._chkr.add_to_personal( unicode(self._suggestion.text()) )
      self.next( )

   def next( self ):
      self._errWord = ''
      self._sugList.clear( )
      self.specialSelection().cursor.clearSelection()
      
      # Identify the next error that's not in the global replace list
      try:
         self._chkr.next( )
         while self._chkr.word in self._globalReplace:
            self._errWord = self._globalReplace[ self._chkr.word ]
            self.replace( )
      except StopIteration:
         return
      
      # Mark the error in the article widget
      wordPos = self._chkr.wordpos
      wordLen = len(self._chkr.word)
      self.applyTextSelector( wordPos, wordPos + wordLen )
      
      # Put the suggestions into the list widget
      self._errWord = self._chkr.word
      for word in self._chkr.suggest( ):
         self._sugList.addItem( word )
      
      # Select the first entry in the list widget as the default
      rootIndex = self._sugList.rootIndex()
      indexOfFirst = rootIndex.child( 0, 0 )
      self._sugList.setCurrentIndex( indexOfFirst )
   

pluginClass = Spelling
