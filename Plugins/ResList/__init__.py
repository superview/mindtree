from PyQt4 import QtCore, QtGui, Qt
from ApplicationFramework import PluggableTool, RES


class Resources( QtGui.QTabWidget, PluggableTool ):
   theApp = None

   NAME             = 'Resources'
   VERSION          = ( 1, 0 )
   BUILD_DATE       = ( 2008, 11, 24 )

   DEFAULT_SETTINGS = {
                         'font' : 'Lucida Sans Unicode:12',
                      }
   
   def __init__( self, parent, outlineView ):
      Resources.theApp = app
      
      QtGui.QTabWidget.__init__( self, parent )
      PluggableTool.__init__( self )
      
      gridLayout = QtGui.QGridLayout( self )
      gridLayout.setObjectName( 'ResGridLayout' )
      
      row = 0
      
      boxLayout = QtGui.QBoxLayout( QtGui.QBoxLayout.LeftToRight, self )
      gridLayout.addLayout( boxLayout, row, 0, 1, 2 )
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('Tool.Resources','filterLabel',translate=True) )
      boxLayout.addWidget( label, QtCore.Qt.AlignHCenter )
      
      self._filter = QtGui.QComboBox( self )
      self._filter.addItems( RES.getMultipartResource('Tool.Resources','filterList',translate=True) )
      boxLayout.addWidget( self._filter, QtCore.Qt.AlignHCenter )
      
      row += 1
      
      self._resList = QtGui.QListWidget( self )
      gridLayout.addWidget( self._resList, row, 0, 4, 2 )
      
      self._addBtn = QtGui.QPushButton( self )
      self._addBtn.setText( RES.get('Tool.Resources','addBtnLabel',translate=True) )
      gridLayout.addWidget( self._addBtn, row, 2, 1, 1 )
      
      row += 1
      
      self._removeBtn = QtGui.QPushButton( self )
      self._removeBtn.setText( RES.get('Tool.Resources','removeBtnLabel',translate=True) )
      gridLayout.addWidget( self._removeBtn, row, 2, 1, 1 )
      
      row += 1
      
      self._modifyBtn = QtGui.QPushButton( self )
      self._modifyBtn.setText( RES.get('Tool.Resources','modifyBtnLabel',translate=True) )
      gridLayout.addWidget( self._modifyBtn, row, 2, 1, 1 )
      
      row += 1
      
      self._insertBtn = QtGui.QPushButton( self )
      self._insertBtn.setText( RES.get('Tool.Resources','insertBtnLabel',translate=True) )
      gridLayout.addWidget( self._insertBtn, row, 2, 1, 1 )

 
pluginClass = Resources
