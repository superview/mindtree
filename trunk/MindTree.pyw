from __future__ import print_function, unicode_literals
from future_builtins import *
import sys
sys.py3kwarning = True

from PyQt4 import QtCore, QtGui
from OutlineView import OutlineView
from OutlineModel import OutlineModel
from ApplicationFramework import Application, Archiver, RES
from Keyboard import KeyboardWidget
from utilities import *


class MindTreeArchiver( Archiver ):
   def __init__( self, parentWidget, fileTypes, defaultExtension, initialDir=None ):
      Archiver.__init__( self, parentWidget, fileTypes, defaultExtension, initialDir )
   
   def _readFile( self, aFilename ):
      data = Archiver._readFile( self, aFilename )
      return OutlineModel( data[0] ), data[1]

   def _writeFile( self, aDocument, aFilename ):
      #if not aDocument.validate( ):
         #raise
      
      # Since the OutlineModel class is a subclass of a Qt class, it cannot
      # be included in the serialized data.
      data = aDocument[0].root( ), aDocument[1]
      Archiver._writeFile( self, data, aFilename )
   
class MindTree( Application ):
   UNTITLED_FILENAME_CT = 1

   def __init__( self ):
      fileTypes  = RES.get( 'Application', 'fileTypes'     )
      fileExts   = RES.get( 'Application', 'fileExtension' )
      workingDir = RES.get( 'Project',     'directory'     )
      
      Application.__init__( self, MindTreeArchiver(self,fileTypes,fileExts,workingDir) )
      
      self.setObjectName("MainWindow")
      
      self._MT1Importer   = None
      self._outlineEditor = None
      self._kb            = None
      
      self._buildGUI( )

   def importFile( self ):
      if self._MT1Importer is None:
         self._MT1Importer = self._plugins.makePlugin( 'MindTree1Importer', self )
      self.openFile( self._MT1Importer )
   
   def exportFile( self ):
      pass
   
   # Required Overrides
   def _makeDefaultModel( self ):
      '''Return an empty OutlineModel and empty resource dictionary.'''
      return OutlineModel( ), { }
   
   def _setupModelInView( self ):
      self._outlineEditor.setModel( self._project.data )
      Application._setupModelInView( self )

   def _updateWindowTitle( self, title ):
      self.setWindowTitle( title )
   
   def _commitDocument( self ):
      self._outlineEditor.commitChanges( )

   # Implementation
   def _buildGUI(self):
      self._buildWidgets( )
      
      self._defineActions( )
      
      self._buildMenus( )
      self._buildToolbars( )
      self._buildStatusBar( )
      
      QtCore.QMetaObject.connectSlotsByName(self)

   def _buildWidgets( self ):
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
      
      # OutlineView Widget
      self._outlineEditor = OutlineView( self.splitter )
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

   def _defineActions( self ):
      self.actionNew       = RES.installAction( 'newFile',    self )
      self.actionOpen      = RES.installAction( 'openFile',   self )
      self.actionClose     = RES.installAction( 'closeFile',  self )
      self.actionSave      = RES.installAction( 'saveFile',   self )
      self.actionSave_as   = RES.installAction( 'saveFileAs', self )
      self.actionImport    = RES.installAction( 'importFile', self )
      self.actionExport    = RES.installAction( 'exportFile', self )
      self.actionExit      = RES.installAction( 'exit',       self )
      self.actionHelp      = RES.installAction( 'help',       self )
      self.actionAbout     = RES.installAction( 'helpAbout',  self )

   def _buildMenus( self ):
      self.menubar = QtGui.QMenuBar(self)
      self.menubar.setObjectName("menubar")
      self.setMenuBar(self.menubar)
      
      self.menuFile = QtGui.QMenu(self.menubar)
      self.menuFile.setObjectName("menuFile")
      self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuTools = QtGui.QMenu(self.menubar)
      self.menuTools.setObjectName("menuTools")
      self.menuTools.setTitle(QtGui.QApplication.translate("MainWindow", "Tools", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuHelp = QtGui.QMenu(self.menubar)
      self.menuHelp.setObjectName("menuHelp")
      self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
      
      # Assemble the menubar
      self.menubar.addAction(self.menuFile.menuAction())
      #self.menubar.addAction(self.menuEdit.menuAction())
      for menu in self._outlineEditor.getFixedMenus( ):
         self.menubar.addAction( menu.menuAction() )
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
      self.menuFile.addAction(self.actionExit)
      
      # Help Menu
      self.menuHelp.addAction( self.actionHelp )
      self.menuHelp.addAction( self.actionAbout )
   
   def _buildToolbars( self ):
      self._filetoolbar = QtGui.QToolBar( 'fileToolbar', self )
      self._filetoolbar.addAction( self.actionNew )
      self._filetoolbar.addAction( self.actionOpen )
      self._filetoolbar.addAction( self.actionSave )
      self.addToolBar( self._filetoolbar )
      
      for toolbar in self._outlineEditor.getToolbars( ):
         self.addToolBar( toolbar )
   
   def _buildStatusBar( self ):
      self.statusbar = QtGui.QStatusBar(self)
      self.statusbar.setObjectName("statusbar")
      self.setStatusBar(self.statusbar)

   def help( self ):
      pass
   
   def helpAbout( self ):
      msg = 'Product name: {name}\nVersion: {version}\nBuild: {build}'.format( name=RES.APP_NAME, version=RES.APP_VERSION, build=RES.APP_BUILD )
      
      msgBox = QtGui.QMessageBox( self )
      msgBox.setWindowTitle( 'About MindTree' )
      msgBox.setIcon( QtGui.QMessageBox.Information )
      msgBox.setText( RES.APP_NAME )
      msgBox.setInformativeText( msg )
      msgBox.exec_()


if __name__ == "__main__":
   import os.path
   sys.path.append( os.path.join( sys.path[0], 'Plugins', 'MindTreeTkModelLib' ) )

   app = QtGui.QApplication( sys.argv )

   splash = QtGui.QSplashScreen( QtGui.QPixmap('resources/images/splash.gif') )
   splash.show( )
   app.processEvents( )
   
   KeyboardWidget.theApp = app
   
   RES.read( [ 'MindTreeRes.ini', 'MindTreeConfig.ini' ] )
   
   myapp = MindTree( )
   myapp.initializePlugins( 'plugins')
   
   myapp.resize(903, 719)
   sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
   sizePolicy.setHorizontalStretch( 1 )
   sizePolicy.setVerticalStretch( 1 )
   myapp.setSizePolicy(sizePolicy)
   
   myapp.newFile( )
   myapp.show( )
   splash.finish( myapp )

   sys.exit( app.exec_() )
