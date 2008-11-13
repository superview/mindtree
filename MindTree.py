import sys
from PyQt4 import QtCore, QtGui
from OutlineEditor import OutlineEditor
from OutlineModel import OutlineModel
from ApplicationFramework import Application, Archiver
from MindTreeTkImporter import importMTTkProject
from Keyboard import KeyboardWidget
import MTresources as RES


class MTTkImportingArchiver( Archiver ):
   FILE_TYPES        = 'MindTree Data File (*.mt);;All Files (*.*)'
   FILE_EXTENSION    = 'mt'
   
   def __init__( self, parentWidget ):
      Archiver.__init__( self, parentWidget, self.FILE_TYPES, self.FILE_EXTENSION, RES.PROJECT_WORKING_DIR )
   
   def _readFile( self, aFilename ):
      from utilities import splitFilePath
      disk,path,filename,extension = splitFilePath( aFilename )
      documentName = filename[0].upper() + filename[1:]
      
      theModel = importMTTkProject( aFilename, documentName )
      
      return theModel

class MindTree( Application ):
   UNTITLED_FILENAME_CT = 1

   def __init__( self ):
      Application.__init__( self, Archiver(self,RES.ARCHIVER_FILE_TYPES,RES.ARCHIVER_FILE_EXTENSION,RES.PROJECT_WORKING_DIR) )
      
      self.setObjectName("MainWindow")
      
      self._MTTKimportingArchiver = MTTkImportingArchiver(self)
      self._outlineEditor = None
      self._kb            = None
      
      self._defineActions( )
      self._buildGUI( )

   def importFile( self ):
      self.openFile( self._MTTKimportingArchiver )
   
   def exportFile( self ):
      pass
   
   # Required Overrides
   def _makeDefaultModel( self ):
      return OutlineModel( )
   
   def _setModelToEdit( self, aModel ):
      self._outlineEditor.setModel( aModel )
      Application._setModelToEdit( self, aModel )

   def _updateWindowTitle( self, title ):
      self.setWindowTitle( title )
   
   def _commitDocument( self ):
      self._outlineEditor.commitChanges( )

   # Implementation
   def _defineActions( self ):
      # New Outline
      self.actionNew = QtGui.QAction(self)
      self.actionNew.setObjectName("actionNew")
      self.actionNew.setText(QtGui.QApplication.translate("MainWindow", RES.ACTION_FILE_NEW_TEXT, None, QtGui.QApplication.UnicodeUTF8))
      self.actionNew.setIcon( QtGui.QIcon(RES.ACTION_FILE_NEW_ICON) )
      self.actionNew.setStatusTip( RES.ACTION_FILE_NEW_STATUSTIP )
      QtCore.QObject.connect( self.actionNew,    QtCore.SIGNAL('triggered()'), self.newFile )
      
      # Open Outline
      self.actionOpen = QtGui.QAction(self)
      self.actionOpen.setObjectName("actionOpen")
      self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", RES.ACTION_FILE_OPEN_TEXT, None, QtGui.QApplication.UnicodeUTF8))
      self.actionOpen.setIcon( QtGui.QIcon(RES.ACTION_FILE_OPEN_ICON) )
      self.actionOpen.setStatusTip( RES.ACTION_FILE_OPEN_STATUSTIP )
      QtCore.QObject.connect( self.actionOpen,    QtCore.SIGNAL('triggered()'), self.openFile )
      
      # Close Outline
      self.actionClose = QtGui.QAction(self)
      self.actionClose.setObjectName("actionClose")
      self.actionClose.setText(QtGui.QApplication.translate("MainWindow", "Close", None, QtGui.QApplication.UnicodeUTF8))
      QtCore.QObject.connect( self.actionClose,   QtCore.SIGNAL("triggered()"), self.close )
      
      # Save Outline
      self.actionSave = QtGui.QAction(self)
      self.actionSave.setObjectName("actionSave")
      self.actionSave.setText(QtGui.QApplication.translate("MainWindow", RES.ACTION_FILE_SAVE_TEXT, None, QtGui.QApplication.UnicodeUTF8))
      self.actionSave.setStatusTip( RES.ACTION_FILE_SAVE_STATUSTIP )
      self.actionSave.setIcon( QtGui.QIcon(RES.ACTION_FILE_SAVE_ICON) )
      QtCore.QObject.connect( self.actionSave,    QtCore.SIGNAL('triggered()'), self.saveFile )
      
      # Save Outline As
      self.actionSave_as = QtGui.QAction(self)
      self.actionSave_as.setObjectName("actionSave_as")
      self.actionSave_as.setText(QtGui.QApplication.translate("MainWindow", "Save as...", None, QtGui.QApplication.UnicodeUTF8))
      QtCore.QObject.connect( self.actionSave_as, QtCore.SIGNAL('triggered()'), self.saveFileAs )
      
      # Import Outline
      self.actionImport = QtGui.QAction(self)
      self.actionImport.setObjectName("actionImport")
      self.actionImport.setText(QtGui.QApplication.translate("MainWindow", "Import...", None, QtGui.QApplication.UnicodeUTF8))
      QtCore.QObject.connect( self.actionImport,  QtCore.SIGNAL('triggered()'), self.importFile )
      
      # Export Outline
      self.actionExport = QtGui.QAction(self)
      self.actionExport.setObjectName("actionExport")
      self.actionExport.setText(QtGui.QApplication.translate("MainWindow", "Export...", None, QtGui.QApplication.UnicodeUTF8))
      QtCore.QObject.connect( self.actionExport,  QtCore.SIGNAL('triggered()'), self.exportFile )
      
      # Close
      self.actionClose_2 = QtGui.QAction(self)
      self.actionClose_2.setObjectName("actionClose_2")
      self.actionClose_2.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
      QtCore.QObject.connect( self.actionClose_2, QtCore.SIGNAL("triggered()"), self.close )
      
      # Help
      self.actionHelp = QtGui.QAction(self)
      self.actionHelp.setObjectName("actionHelp")
      self.actionHelp.setText(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
      
      self.actionAbout = QtGui.QAction(self)
      self.actionAbout.setObjectName("actionAbout")
      self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))

   def _buildGUI(self):
      self._buildCentralWidget( )
      
      self._buildMenubar( )
      self._buildToolbars( )
      self._buildStatusBar( )
      
      QtCore.QMetaObject.connectSlotsByName(self)

   def _buildMenubar( self ):
      self.menubar = QtGui.QMenuBar(self)
      self.menubar.setObjectName("menubar")
      self.setMenuBar(self.menubar)
      
      self.menuFile = QtGui.QMenu(self.menubar)
      self.menuFile.setObjectName("menuFile")
      self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuEdit = QtGui.QMenu(self.menubar)
      self.menuEdit.setObjectName("MenuEdit")
      self.menuEdit.setTitle(QtGui.QApplication.translate("MainWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuTree = QtGui.QMenu(self.menubar)
      self.menuTree.setObjectName("menuTree")
      self.menuTree.setTitle(QtGui.QApplication.translate("MainWindow", "Tree", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuArticle = QtGui.QMenu(self.menubar)
      self.menuArticle.setObjectName("menuArticle")
      self.menuArticle.setTitle(QtGui.QApplication.translate("MainWindow", "Article", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuTools = QtGui.QMenu(self.menubar)
      self.menuTools.setObjectName("menuTools")
      self.menuTools.setTitle(QtGui.QApplication.translate("MainWindow", "Tools", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuHelp = QtGui.QMenu(self.menubar)
      self.menuHelp.setObjectName("menuHelp")
      self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menubar.addAction(self.menuFile.menuAction())
      self.menubar.addAction(self.menuEdit.menuAction())
      self.menubar.addAction(self.menuTree.menuAction())
      self.menubar.addAction(self.menuArticle.menuAction())
      self.menubar.addAction(self.menuTools.menuAction())
      self.menubar.addAction(self.menuHelp.menuAction())
      
      # Outline Menu
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
      
      # Edit Menu
      self.menuEdit.addAction(self._outlineEditor.editUndoAction)
      self.menuEdit.addAction(self._outlineEditor.editRedoAction)
      
      # Tree Menu
      self.menuTree.addAction( self._outlineEditor.cutNodeAction )
      self.menuTree.addAction( self._outlineEditor.copyNodeAction )
      self.menuTree.addAction( self._outlineEditor.pasteNodeBeforeAction )
      self.menuTree.addAction( self._outlineEditor.pasteNodeAfterAction )
      self.menuTree.addAction( self._outlineEditor.pasteNodeChildAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self._outlineEditor.expandAllAction )
      self.menuTree.addAction( self._outlineEditor.collapseAllAction )
      self.menuTree.addAction( self._outlineEditor.expandNodeAction )
      self.menuTree.addAction( self._outlineEditor.collapseNodeAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self._outlineEditor.insertNewNodeBeforeAction )
      self.menuTree.addAction( self._outlineEditor.insertNewNodeAfterAction )
      self.menuTree.addAction( self._outlineEditor.insertNewChildAction )
      self.menuTree.addAction( self._outlineEditor.deleteNodeAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self._outlineEditor.indentNodeAction )
      self.menuTree.addAction( self._outlineEditor.dedentNodeAction )
      self.menuTree.addAction( self._outlineEditor.moveNodeUpAction )
      self.menuTree.addAction( self._outlineEditor.moveNodeDownAction )
      
      # Article Menu
      self.menuArticle.addAction( self._outlineEditor.articleCutAction )
      self.menuArticle.addAction( self._outlineEditor.articleCopyAction )
      self.menuArticle.addAction( self._outlineEditor.articlePasteAction )
      self.menuArticle.addSeparator()
      self.menuArticle.addAction( self._outlineEditor.articleSelectAllAction )
      
      # Help Menu
      self.menuHelp.addAction( self.actionHelp )
      self.menuHelp.addAction( self.actionAbout )
   
   def _buildStatusBar( self ):
      self.statusbar = QtGui.QStatusBar(self)
      self.statusbar.setObjectName("statusbar")
      self.setStatusBar(self.statusbar)
   
   def _buildToolbars( self ):
      self._filetoolbar = QtGui.QToolBar( 'fileToolbar', self )
      self._filetoolbar.addAction( self.actionNew )
      self._filetoolbar.addAction( self.actionOpen )
      self._filetoolbar.addAction( self.actionSave )
      self.addToolBar( self._filetoolbar )
      
      self._articletoolbar = QtGui.QToolBar( 'articleToolbar', self )
      self._articletoolbar.addAction( self._outlineEditor.articleCutAction )
      self._articletoolbar.addAction( self._outlineEditor.articleCopyAction )
      self._articletoolbar.addAction( self._outlineEditor.articlePasteAction )
      self.addToolBar( self._articletoolbar )
      
      self._edittoolbar = QtGui.QToolBar( 'editToolbar', self )
      self._edittoolbar.addAction( self._outlineEditor.editUndoAction )
      self._edittoolbar.addAction( self._outlineEditor.editRedoAction )
      self.addToolBar( self._edittoolbar )
      
      self._treetoolbar = QtGui.QToolBar( 'treeToolbar', self )
      self._treetoolbar.addAction( self._outlineEditor.expandAllAction )
      self._treetoolbar.addAction( self._outlineEditor.collapseAllAction )
      self.addToolBar( self._treetoolbar )
   
   def _buildCentralWidget( self ):
      self.splitter = QtGui.QSplitter(self)
      self.splitter.setObjectName( 'centralwidget' )
      self.splitter.setGeometry(QtCore.QRect(0, 0, 901, 671))
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setHorizontalStretch( 1 )
      sizePolicy.setVerticalStretch( 0 )
      self.splitter.setSizePolicy(sizePolicy)
      self.splitter.setOrientation(QtCore.Qt.Vertical)
      self.splitter.setChildrenCollapsible(False)
      self.splitter.setObjectName("splitter_2")
      self.splitter.setOpaqueResize( True )
      
      # OutlineEditor Widget
      self._outlineEditor = OutlineEditor( self.splitter )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 0 )
      self._outlineEditor.setSizePolicy(sizePolicy)
      self._outlineEditor.setMinimumSize(QtCore.QSize(100, 100))
      self._outlineEditor.setOrientation(QtCore.Qt.Horizontal)
      self._outlineEditor.setChildrenCollapsible(False)
      self._outlineEditor.setObjectName("splitter")
      
      QtCore.QObject.connect( self._outlineEditor, QtCore.SIGNAL( 'modelChanged()' ), self.onModelChanged )
      
      # Keyboard Widget
      self._kb = KeyboardWidget( self.splitter )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
      sizePolicy.setVerticalStretch( 2 )
      sizePolicy.setHorizontalStretch( 1 )
      self._kb.setSizePolicy(sizePolicy)
      self._kb.setObjectName("tabWidget")
      self._kb.setMinimumHeight( 180 )
      
      self.setCentralWidget(self.splitter)

if __name__ == "__main__":
   # Hack to be able to move the MindTree v1.x Model Library into a subdirectory
   import os.path
   sys.path.append( os.path.join( sys.path[0], 'Plugins', 'MindTreeTkModelLib' ) )

   app = QtGui.QApplication( sys.argv )
   KeyboardWidget.theApp = app

   myapp = MindTree( )
   myapp.resize(903, 719)
   sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
   sizePolicy.setHorizontalStretch( 1 )
   sizePolicy.setVerticalStretch( 1 )
   myapp.setSizePolicy(sizePolicy)
   
   myapp.newFile( )
   myapp.show( )

   sys.exit( app.exec_() )
