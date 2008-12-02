from PyQt4 import QtCore, QtGui, Qt
from MindTreeApplicationFramework import *


class Resources( QtGui.QTabWidget, MindTreePluggableTool ):
   theApp = None

   NAME             = 'Resources'
   VERSION          = ( 1, 0 )
   BUILD_DATE       = ( 2008, 11, 24 )

   DEFAULT_SETTINGS = {
                      # Resources
                      'filterLabel':            'Filter',
                      'filterList':             'all:images:bookmarks:links',
                      'addBtnLabel':            'Add',
                      'removeBtnLabel':         'Remove',
                      'modifyBtnLabel':         'Modify',
                      'insertBtnLabel':         'Insert',
                      # Configuration
                      'font':                   'Lucida Sans Unicode:12'
                      }
   
   def __init__( self, parent, app, outlineView ):
      Resources.theApp = app
      self._outlineView = outlineView
      
      QtGui.QTabWidget.__init__( self, parent )
      MindTreePluggableTool.__init__( self, parent, app, outlineView )
      
      gridLayout = QtGui.QGridLayout( self )
      gridLayout.setObjectName( 'ResGridLayout' )
      
      row = 0
      
      boxLayout = QtGui.QBoxLayout( QtGui.QBoxLayout.LeftToRight )
      gridLayout.addLayout( boxLayout, row, 0, 1, 2 )
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('Resources','filterLabel',translate=True) )
      boxLayout.addWidget( label, QtCore.Qt.AlignHCenter )
      
      self._filter = QtGui.QComboBox( self )
      self._filter.addItems( RES.getMultipartResource('Resources','filterList',translate=True) )
      boxLayout.addWidget( self._filter, QtCore.Qt.AlignHCenter )
      
      row += 1
      
      self._resList = QtGui.QListWidget( self )
      gridLayout.addWidget( self._resList, row, 0, 4, 2 )
      
      self._addBtn = QtGui.QPushButton( self )
      self._addBtn.setText( RES.get('Resources','addBtnLabel',translate=True) )
      gridLayout.addWidget( self._addBtn, row, 2, 1, 1 )
      
      row += 1
      
      self._removeBtn = QtGui.QPushButton( self )
      self._removeBtn.setText( RES.get('Resources','removeBtnLabel',translate=True) )
      gridLayout.addWidget( self._removeBtn, row, 2, 1, 1 )
      
      row += 1
      
      self._modifyBtn = QtGui.QPushButton( self )
      self._modifyBtn.setText( RES.get('Resources','modifyBtnLabel',translate=True) )
      gridLayout.addWidget( self._modifyBtn, row, 2, 1, 1 )
      
      row += 1
      
      self._insertBtn = QtGui.QPushButton( self )
      self._insertBtn.setText( RES.get('Resources','insertBtnLabel',translate=True) )
      gridLayout.addWidget( self._insertBtn, row, 2, 1, 1 )
      
      row += 1
      
      self._refreshBtn = QtGui.QPushButton( self )
      self._refreshBtn.setText( 'Refresh' )
      gridLayout.addWidget( self._refreshBtn, row, 2, 1, 1 )
      QtCore.QObject.connect( self._refreshBtn, QtCore.SIGNAL('clicked()'), self.populate )

   def populate( self ):
      resources = self._outlineView.getResources()
      self._resList.addItems( resources.keys() )

 
pluginClass = Resources
