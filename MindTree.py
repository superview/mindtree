import sys
from PyQt4 import QtCore, QtGui
from OutlineEditor import OutlineEditor
from OutlineModel import OutlineModel
from MindTreeTkImporter import importMTTkProject
from Keyboard import KeyboardWidget


class MindTree( QtGui.QMainWindow ):
   def __init__( self, parent=None ):
      QtGui.QMainWindow.__init__( self, parent )
      self.keyboards = [ ]
      
      self.setObjectName("MainWindow")
      self.resize(903, 719)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setHorizontalStretch( 1 )
      sizePolicy.setVerticalStretch( 1 )
      self.setSizePolicy(sizePolicy)
      self.buildGUI( )
      
      QtCore.QObject.connect( self.actionOpen,    QtCore.SIGNAL('triggered()'), self.openFile )
      QtCore.QObject.connect( self.actionSave,    QtCore.SIGNAL('triggered()'), self.saveFile )
      QtCore.QObject.connect( self.actionSave_as, QtCore.SIGNAL('triggered()'), self.saveFileAs )
      QtCore.QObject.connect( self.actionImport, QtCore.SIGNAL('triggered()'), self.importFile )
      QtCore.QObject.connect( self.actionExport, QtCore.SIGNAL('triggered()'), self.exportFile )
      QtCore.QObject.connect( self.actionClose,   QtCore.SIGNAL("triggered()"), self.close )
      QtCore.QObject.connect( self.actionClose_2, QtCore.SIGNAL("triggered()"), self.close )

   def buildGUI(self):
      self.splitter = QtGui.QSplitter(self)
      self.splitter.setObjectName( 'centralwidget' )
      self.splitter.setGeometry(QtCore.QRect(0, 0, 901, 671))
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setHorizontalStretch( 1 )
      sizePolicy.setVerticalStretch( 1 )
      self.splitter.setSizePolicy(sizePolicy)
      self.splitter.setOrientation(QtCore.Qt.Vertical)
      self.splitter.setChildrenCollapsible(False)
      self.splitter.setObjectName("splitter_2")
      self.splitter.setOpaqueResize( True )
      
      self.outlineEditor = OutlineEditor( self.splitter )
      
      self.kb = KeyboardWidget( self.splitter )
      
      self.setCentralWidget(self.splitter)
      self.menubar = QtGui.QMenuBar(self)
      self.menubar.setObjectName("menubar")
      self.menuFile = QtGui.QMenu(self.menubar)
      self.menuFile.setObjectName("menuFile")
      self.menuTree = QtGui.QMenu(self.menubar)
      self.menuTree.setObjectName("menuTree")
      self.menuArticle = QtGui.QMenu(self.menubar)
      self.menuArticle.setObjectName("menuArticle")
      self.menuTools = QtGui.QMenu(self.menubar)
      self.menuTools.setObjectName("menuTools")
      self.menuHelp = QtGui.QMenu(self.menubar)
      self.menuHelp.setObjectName("menuHelp")
      self.setMenuBar(self.menubar)
      self.statusbar = QtGui.QStatusBar(self)
      self.statusbar.setObjectName("statusbar")
      self.setStatusBar(self.statusbar)
      
      # Outline Menu
      self.actionNew = QtGui.QAction(self)
      self.actionNew.setObjectName("actionNew")
      self.actionOpen = QtGui.QAction(self)
      self.actionOpen.setObjectName("actionOpen")
      self.actionClose = QtGui.QAction(self)
      self.actionClose.setObjectName("actionClose")
      self.actionSave = QtGui.QAction(self)
      self.actionSave.setObjectName("actionSave")
      self.actionSave_as = QtGui.QAction(self)
      self.actionSave_as.setObjectName("actionSave_as")
      self.actionImport = QtGui.QAction(self)
      self.actionImport.setObjectName("actionImport")
      self.actionExport = QtGui.QAction(self)
      self.actionExport.setObjectName("actionExport")
      self.actionClose_2 = QtGui.QAction(self)
      self.actionClose_2.setObjectName("actionClose_2")
      self.menuFile.addAction(self.actionNew)
      self.menuFile.addAction(self.actionOpen)
      self.menuFile.addAction(self.actionClose)
      self.menuFile.addAction(self.actionSave)
      self.menuFile.addAction(self.actionSave_as)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.actionImport)
      self.menuFile.addAction(self.actionExport)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.actionClose_2)
      
      self.menuTree.addAction( self.outlineEditor.expandAllAction )
      self.menuTree.addAction( self.outlineEditor.collapseAllAction )
      self.menuTree.addAction( self.outlineEditor.expandNodeAction )
      self.menuTree.addAction( self.outlineEditor.collapseNodeAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self.outlineEditor.insertNewNodeBeforeAction )
      self.menuTree.addAction( self.outlineEditor.insertNewNodeAfterAction )
      self.menuTree.addAction( self.outlineEditor.insertNewChildAction )
      self.menuTree.addAction( self.outlineEditor.deleteNodeAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self.outlineEditor.indentNodeAction )
      self.menuTree.addAction( self.outlineEditor.dedentNodeAction )
      self.menuTree.addAction( self.outlineEditor.moveNodeUpAction )
      self.menuTree.addAction( self.outlineEditor.moveNodeDownAction )
      
      self.menubar.addAction(self.menuFile.menuAction())
      self.menubar.addAction(self.menuTree.menuAction())
      self.menubar.addAction(self.menuArticle.menuAction())
      self.menubar.addAction(self.menuTools.menuAction())
      self.menubar.addAction(self.menuHelp.menuAction())
      
      self.retranslateUi()
      QtCore.QMetaObject.connectSlotsByName(self)

   def retranslateUi(self):
      # Outline Menu
      self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MindTree", None, QtGui.QApplication.UnicodeUTF8))
      self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "Outline", None, QtGui.QApplication.UnicodeUTF8))
      self.menuTree.setTitle(QtGui.QApplication.translate("MainWindow", "Tree", None, QtGui.QApplication.UnicodeUTF8))
      self.menuArticle.setTitle(QtGui.QApplication.translate("MainWindow", "Article", None, QtGui.QApplication.UnicodeUTF8))
      self.menuTools.setTitle(QtGui.QApplication.translate("MainWindow", "Tools", None, QtGui.QApplication.UnicodeUTF8))
      self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
      self.actionNew.setText(QtGui.QApplication.translate("MainWindow", "New", None, QtGui.QApplication.UnicodeUTF8))
      self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", "Open...", None, QtGui.QApplication.UnicodeUTF8))
      self.actionClose.setText(QtGui.QApplication.translate("MainWindow", "Close", None, QtGui.QApplication.UnicodeUTF8))
      self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
      self.actionSave_as.setText(QtGui.QApplication.translate("MainWindow", "Save as...", None, QtGui.QApplication.UnicodeUTF8))
      self.actionImport.setText(QtGui.QApplication.translate("MainWindow", "Import...", None, QtGui.QApplication.UnicodeUTF8))
      self.actionExport.setText(QtGui.QApplication.translate("MainWindow", "Export...", None, QtGui.QApplication.UnicodeUTF8))
      self.actionClose_2.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
      
      # Tree Menu
      self.outlineEditor.expandAllAction.setText(QtGui.QApplication.translate("MainWindow", "Expand All", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.collapseAllAction.setText(QtGui.QApplication.translate("MainWindow", "Collapse All", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.expandNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Expand Node", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.collapseNodeAction.setText(QtGui.QApplication.translate("MainWindow", "CollapseNode", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.insertNewNodeBeforeAction.setText(QtGui.QApplication.translate("MainWindow", "New Node Before", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.insertNewNodeAfterAction.setText(QtGui.QApplication.translate("MainWindow", "New Node After", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.insertNewChildAction.setText(QtGui.QApplication.translate("MainWindow", "New Child", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.deleteNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Delete Subtree", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.indentNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Indent Node", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.dedentNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Dedent Node", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.moveNodeUpAction.setText(QtGui.QApplication.translate("MainWindow", "Move Node Up", None, QtGui.QApplication.UnicodeUTF8))
      self.outlineEditor.moveNodeDownAction.setText(QtGui.QApplication.translate("MainWindow", "Move Node Down", None, QtGui.QApplication.UnicodeUTF8))

   def newFile( self ):
      self.outlineEditor.setModel( OutlineModel( ) )

   def openFile( self ):
      dlg = QtGui.QFileDialog( self, 'Open file...', 'f:\\mindtree data' )
      dlg.setModal(True)
      dlg.exec_()
      filenames = dlg.selectedFiles( )
      
      if len(filenames) > 0:
         from filesystemTools import splitFilePath
         
         fullFilename = unicode(filenames[0])
         disk,path,filename,extension = splitFilePath( fullFilename )
         documentName = filename[0].upper() + filename[1:]
         
         theModel = importMTTkProject( fullFilename, documentName )
         self.outlineEditor.setModel( theModel )

   def saveFile( self ):
      pass
   
   def saveFileAs( self ):
      pass
   
   def importFile( self ):
      pass
   
   def exportFile( self ):
      pass
   
   def close( self ):
      pass


if __name__ == "__main__":
   # Hack to be able to move the MindTree v1.x Model Library into a subdirectory
   import os.path
   sys.path.append( os.path.join( sys.path[0], 'MindTreeTkModelLib' ) )

   app = QtGui.QApplication( sys.argv )
   KeyboardWidget.theApp = app

   myapp = MindTree( )
   myapp.setWindowTitle("MindTree Qt")
   myapp.newFile( )
   myapp.show( )

   sys.exit( app.exec_() )
