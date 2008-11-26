from ApplicationFramework import RES, PluggableTool
from PyQt4 import QtCore, QtGui

class Spelling( PluggableTool, QtGui.QWidget ):
   NAME             = 'Spelling'
   VERSION          = ( 1, 0 )
   BUILD_DATE       = ( 2008, 11, 24 )
   
   DEFAULT_SETTINGS = {
                      }

   def __init__( self, parent, app ):
      PluggableTool.__init__( self )
      QtGui.QWidget.__init__( self, parent )
      
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
      gridLayout.addWidget( self._recheckBtn, row, 0, 1, 1 )
      
      self._sugList    = QtGui.QListWidget( self )
      gridLayout.addWidget( self._sugList, row, 1, 4, 1 )
      
      self._suggestion = QtGui.QLineEdit( self )
      gridLayout.addWidget( self._suggestion, row, 2, 1, 2 )
      
      row += 1
      
      self._stopBtn = QtGui.QPushButton( self )
      self._stopBtn.setText( RES.get('Tool.Spelling','stopBtnLabel',translate=True) )
      gridLayout.addWidget( self._stopBtn, row, 0, 1, 1 )
      
      self._replaceBtn = QtGui.QPushButton( self )
      self._replaceBtn.setText( RES.get('Tool.Spelling','replaceBtnLabel',translate=True) )
      gridLayout.addWidget( self._replaceBtn, row, 2, 1, 1 )
      
      self._replaceAllBtn = QtGui.QPushButton( self )
      self._replaceAllBtn.setText( RES.get('Tool.Spelling','replaceAllBtnLabel',translate=True) )
      gridLayout.addWidget( self._replaceAllBtn, row, 3, 1, 1 )
      
      row += 1
      
      self._ignoreBtn = QtGui.QPushButton( self )
      self._ignoreBtn.setText( RES.get('Tool.Spelling','ignoreBtnLabel',translate=True) )
      gridLayout.addWidget( self._ignoreBtn, row, 2, 1, 1 )
      
      self._ignoreAllBtn = QtGui.QPushButton( self )
      self._ignoreAllBtn.setText( RES.get('Tool.Spelling','ignoreAllBtnLabel',translate=True) )
      gridLayout.addWidget( self._ignoreAllBtn, row, 3, 1, 1 )
      
      row += 1
      
      self._addBtn = QtGui.QPushButton( self )
      self._addBtn.setText( RES.get('Tool.Spelling','addBtnLabel',translate=True) )
      gridLayout.addWidget( self._addBtn, row, 2, 1, 1 )

pluginClass = Spelling
