from MindTreeApplicationFramework import *
from OutlineModel import OutlineModelIterator, ArticleIterator, TextIterator
from PyQt4 import QtCore, QtGui

import re


class FindIterator( TextIterator ):
   def __init__( self, reObj ):
      TextIterator.__init__( self )
      self._regexObj = reObj
      self._pos      = 0
   
   def restart( self, text ):
      TextIterator.restart( self, text )
      self._pos      = 0
   
   def next( self ):
      TextIterator.next( self )
      
      match = self._regexObj.search( self._text, self._pos )
      try:
         start, stop = match.span( )
      except:
         raise StopIteration
      
      self._pos = stop
      
      return start,stop


class Find( MindTreePluggableTool, QtGui.QWidget ):
   NAME             = 'Find'
   VERSION          = ( 1, 0 )
   BUILD_DATE       = ( 2008, 11, 24 )
   
   DEFAULT_SETTINGS = {
                      # Resources
                      'wordBoundary':      '[^a-zA-Z0-9\\-\']',
                      'scopelabel':        'Scope',
                      'scopeList':         'All:Subtree:Article',
                      'findPatternLabel':  'Pattern',
                      'regExLabel':        'Regex',
                      'ignoreCaseLabel':   'Ignore Case',
                      'wholeWordsLabel':   'Whole Words Only',
                      'replaceLabel':      'Replace',
                      'findPrevBtnLabel':  'Previous',
                      'findNextBtnLabel':  'Next',
                      'replaceBtnLabel':   'Replace',
                      'replaceAllBtnLabel':'Replace All',
                      # Configuration
                      'useRegex':          'False',
                      'ignoreCase':        'False',
                      'wholeWordsOnly':    'False'
                      }

   
   def __init__( self, parent, app, outlineView ):
      MindTreePluggableTool.__init__( self, parent, app, outlineView )
      QtGui.QWidget.__init__( self, parent )
      
      self._outlineIter    = None
      self._matchIter      = None
      
      gridLayout = QtGui.QGridLayout( self )
      gridLayout.setObjectName( 'FindGridLayout' )
      gridLayout.setColumnStretch( 0, 1 )
      gridLayout.setColumnStretch( 1, 3 )
      gridLayout.setColumnStretch( 2, 3 )
      
      row = 0
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('Find','scopelabel',translate=True) )
      gridLayout.addWidget( label, row, 0, 1, 1 )
      
      self._scope = QtGui.QComboBox( self )
      self._scope.addItems( RES.getMultipartResource('Find','scopeList',translate=True) )
      gridLayout.addWidget( self._scope, row, 1, 1, 3 )
      QtCore.QObject.connect( self._scope, QtCore.SIGNAL('currentIndexChanged(int)'), self.scopeChanged )
      
      row += 1
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('Find','findPatternLabel',translate=True) )
      gridLayout.addWidget( label, row, 0, 1, 1 )
      
      self._pattern = QtGui.QLineEdit( self )
      gridLayout.addWidget( self._pattern, row, 1, 1, 3 )
      QtCore.QObject.connect( self._pattern, QtCore.SIGNAL('textChanged(QString)'), self.searchPatternChanged )
      
      row += 1
      
      self._useRegex = QtGui.QCheckBox( self )
      self._useRegex.setText( RES.get('Find','regexLabel',translate=True) )
      checked = QtCore.Qt.Checked if RES.getboolean('Find','useRegex') else QtCore.Qt.Unchecked
      self._useRegex.setCheckState( checked )
      gridLayout.addWidget( self._useRegex, row, 1, 1, 1 )
      QtCore.QObject.connect( self._useRegex, QtCore.SIGNAL('stateChanged(int)'), self.checkStateChanged )
      
      self._ignoreCase = QtGui.QCheckBox( self )
      self._ignoreCase.setText( RES.get('Find','ignoreCaseLabel',translate=True) )
      checked = QtCore.Qt.Checked if RES.getboolean('Find','ignoreCase') else QtCore.Qt.Unchecked
      self._ignoreCase.setCheckState( checked )
      gridLayout.addWidget( self._ignoreCase, row, 2, 1, 1 )
      QtCore.QObject.connect( self._ignoreCase, QtCore.SIGNAL('stateChanged(int)'), self.checkStateChanged )
      
      self._wholeWords = QtGui.QCheckBox( self )
      self._wholeWords.setText( RES.get('Find','wholeWordsLabel',translate=True) )
      checked = QtCore.Qt.Checked if RES.getboolean('Find','wholeWordsOnly') else QtCore.Qt.Unchecked
      self._wholeWords.setCheckState( checked )
      gridLayout.addWidget( self._wholeWords, row, 3, 1, 1 )
      QtCore.QObject.connect( self._wholeWords, QtCore.SIGNAL('stateChanged(int)'), self.checkStateChanged )
      
      row += 1
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('Find','replaceLabel',translate=True) )
      gridLayout.addWidget( label, row, 0, 1, 1 )
      
      self._replace = QtGui.QLineEdit( self )
      gridLayout.addWidget( self._replace, row, 1, 1, 3 )
      
      row += 1
      
      buttonBox = QtGui.QBoxLayout( QtGui.QBoxLayout.LeftToRight, self )
      gridLayout.addLayout( buttonBox, row, 0, 1, 4 )
      
      self._prevBtn = QtGui.QPushButton( self )
      self._prevBtn.setText( RES.get('Find','findPrevBtnLabel',translate=True) )
      QtCore.QObject.connect( self._prevBtn, QtCore.SIGNAL('clicked()'), self.prev )
      buttonBox.addWidget( self._prevBtn )
      
      self._nextBtn = QtGui.QPushButton( self )
      self._nextBtn.setText( RES.get('Find','findNextBtnLabel',translate=True) )
      QtCore.QObject.connect( self._nextBtn, QtCore.SIGNAL('clicked()'), self.next )
      buttonBox.addWidget( self._nextBtn )
      
      self._replBtn = QtGui.QPushButton( self )
      self._replBtn.setText( RES.get('Find','replaceBtnLabel',translate=True) )
      QtCore.QObject.connect( self._replBtn, QtCore.SIGNAL('clicked()'), self.replace )
      buttonBox.addWidget( self._replBtn )
      
      self._replAllBtn = QtGui.QPushButton( self )
      self._replAllBtn.setText( RES.get('Find','replaceAllBtnLabel',translate=True) )
      QtCore.QObject.connect( self._replAllBtn, QtCore.SIGNAL('clicked()'), self.replaceAll )
      buttonBox.addWidget( self._replAllBtn )
      
      #self._findSelection = QtGui.QTextEdit.ExtraSelection( )
      format = QtGui.QTextCharFormat( )
      format.setFontUnderline( True )
      format.setUnderlineStyle( QtGui.QTextCharFormat.SpellCheckUnderline )
      format.setUnderlineColor( QtGui.QColor( 'green' ) )
      self.defineTextSelector( format )
      #self._findSelection.format = format

   def scopeChanged( self, index ):
      self.clearFinder( )
   
   def searchPatternChanged( self, pattern ):
      self.clearFinder( )

   def checkStateChanged( self, newValue ):
      self.clearFinder( )
   
   def clearFinder( self ):
      self._outlineIter = None
      self._matchIter   = None
   
   def prev( self ):
      pass
   
   def next( self ):
      if self._outlineIter is None:
         self._outlineIter = self.createSearchIterator( )
      
      try:
         nodeIndex, span, text = self._outlineIter.next( )
         fromPos, toPos = span
         self.applyTextSelector( fromPos, toPos )
      except:
         pass

   def replace( self ):
      if self._searchIter is None:
         self._searchIter = self.createSearchIterator( )
      
      pass
   
   def replaceAll( self ):
      if self._searchIter is None:
         self._searchIter = self.createSearchIterator( )
      
      pass
   
   def createSearchIterator( self ):
      # Grab some basic information
      outlineWidget = self._outlineView.outlineWidget()
      outlineModel  = self._outlineView.getModel()
      
      # Detemine the scope of the search
      scope = self._scope.currentIndex()
      scope = RES.getMultipartResource('Find','scopeList')[ scope ]
      
      # Collect search parameters
      pattern    = unicode(self._pattern.text())
      replace    = unicode(self._replace.text())
      regex      = self._useRegex.isChecked()
      ignoreCase = self._ignoreCase.isChecked()
      wholeWords = self._wholeWords.isChecked()
      
      # Create the regex search object
      regexObj = self.buildRegex( pattern, regex, ignoreCase, wholeWords )
      
      # Determine the index to the subtree to be searched
      if scope.upper() in ( 'SELECTION', 'ARTICLE', 'SUBTREE' ):
         index = outlineWidget.currentIndex()
      elif scope.upper() == 'ALL':
         index = outlineModel.index(0,0)
      else:
         raise Exception
      
      if scope.upper() in ( 'SELECTION', 'ARTICLE' ):
         recurse = False
      else:
         recurse = True
      
      return ArticleIterator( index, FindIterator(regexObj), recurse )

   @staticmethod
   def buildRegex( pattern, regex, ignoreCase, wholeWords ):
      if not regex:
         pattern = Find.convertToRegex( pattern )
      
      if wholeWords:
         boundary = RES.get( 'Find','wordBoundary' )
         pattern = boundary + pattern + boundary
      
      if ignoreCase:
         flags = re.UNICODE | re.IGNORECASE
      else:
         flags = re.UNICODE
      
      return re.compile( pattern, flags )
   
   @staticmethod
   def convertToRegex( aPattern ):
      converted = u''
      
      for character in aPattern:
         if character == u'\\':
            converted += u'\\\\'
         elif character in u'.^$+?*{},[]|():=!<-':
            converted += u'\\' + character
         else:
            converted += character
      
      return converted


pluginClass = Find
