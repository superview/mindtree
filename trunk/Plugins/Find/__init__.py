from ApplicationFramework import RES, PluggableTool
from PyQt4 import QtCore, QtGui

class Find( PluggableTool, QtGui.QWidget ):
   NAME             = 'Find'
   VERSION          = ( 1, 0 )
   BUILD_DATE       = ( 2008, 11, 24 )
   
   DEFAULT_SETTINGS = {
                      }

   def __init__( self, parent, app ):
      PluggableTool.__init__( self )
      QtGui.QWidget.__init__( self, parent )
      
      gridLayout = QtGui.QGridLayout( self )
      gridLayout.setObjectName( 'FindGridLayout' )
      gridLayout.setColumnStretch( 0, 1 )
      gridLayout.setColumnStretch( 1, 3 )
      gridLayout.setColumnStretch( 2, 3 )
      
      row = 0
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('Tool.Find','contextLabel',translate=True) )
      gridLayout.addWidget( label, row, 0, 1, 1 )
      
      self._context = QtGui.QComboBox( self )
      self._context.addItems( RES.getMultipartResource('Tool.Find','contextList',translate=True) )
      gridLayout.addWidget( self._context, row, 1, 1, 3 )
      
      row += 1
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('Tool.Find','findPatternLabel',translate=True) )
      gridLayout.addWidget( label, row, 0, 1, 1 )
      
      self._pattern = QtGui.QLineEdit( self )
      gridLayout.addWidget( self._pattern, row, 1, 1, 3 )
      
      row += 1
      
      self._useRegex = QtGui.QCheckBox( self )
      self._useRegex.setText( RES.get('Tool.Find','regexLabel',translate=True) )
      checked = QtCore.Qt.Checked if RES.getboolean('Tool.Find','useRegex') else QtCore.Qt.Unchecked
      self._useRegex.setCheckState( checked )
      gridLayout.addWidget( self._useRegex, row, 1, 1, 1 )
      
      self._ignoreCase = QtGui.QCheckBox( self )
      self._ignoreCase.setText( RES.get('Tool.Find','ignoreCaseLabel',translate=True) )
      checked = QtCore.Qt.Checked if RES.getboolean('Tool.Find','ignoreCase') else QtCore.Qt.Unchecked
      self._ignoreCase.setCheckState( checked )
      gridLayout.addWidget( self._ignoreCase, row, 2, 1, 1 )
      
      self._wholeWords = QtGui.QCheckBox( self )
      self._wholeWords.setText( RES.get('Tool.Find','wholeWordsLabel',translate=True) )
      checked = QtCore.Qt.Checked if RES.getboolean('Tool.Find','wholeWordsOnly') else QtCore.Qt.Unchecked
      self._wholeWords.setCheckState( checked )
      gridLayout.addWidget( self._wholeWords, row, 3, 1, 1 )
      
      row += 1
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('Tool.Find','replaceLabel',translate=True) )
      gridLayout.addWidget( label, row, 0, 1, 1 )
      
      self._replace = QtGui.QLineEdit( self )
      gridLayout.addWidget( self._replace, row, 1, 1, 3 )
      
      row += 1
      
      buttonBox = QtGui.QBoxLayout( QtGui.QBoxLayout.LeftToRight, self )
      gridLayout.addLayout( buttonBox, row, 0, 1, 4 )
      
      self._prevBtn = QtGui.QPushButton( self )
      self._prevBtn.setText( RES.get('Tool.Find','findPrevBtnLabel',translate=True) )
      buttonBox.addWidget( self._prevBtn )
      
      self._nextBtn = QtGui.QPushButton( self )
      self._nextBtn.setText( RES.get('Tool.Find','findNextBtnLabel',translate=True) )
      buttonBox.addWidget( self._nextBtn )
      
      self._replBtn = QtGui.QPushButton( self )
      self._replBtn.setText( RES.get('Tool.Find','replaceBtnLabel',translate=True) )
      buttonBox.addWidget( self._replBtn )
      
      self._replAllBtn = QtGui.QPushButton( self )
      self._replAllBtn.setText( RES.get('Tool.Find','replaceAllBtnLabel',translate=True) )
      buttonBox.addWidget( self._replAllBtn )

   
pluginClass = Find
