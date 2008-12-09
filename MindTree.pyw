from __future__ import print_function, unicode_literals
from future_builtins import *
import sys
sys.py3kwarning = True

from PyQt4 import QtCore, QtGui
from OutlineEdit import OutlineEdit
from MindTreeApplicationFramework import *


#######################################
### Default Plugin Implementations

### Importer
'''
from OutlineModel import OutlineModel, TreeNode
from PyQt4 import QtCore, QtGui

from ApplicationFramework import ImporterPlugin, RES

class MyImporter( ImporterPlugin ):
   NAME              = 'MyImporterName'
   VERSION           = ( 1, 0 )
   BUILD_DATE        = ( 2008, 11, 15 )
   
   FILE_TYPES        = 'MindTree Data File (*.mt);;All Files (*.*)'
   FILE_EXTENSION    = 'mt'
   
   DEFAULT_SETTINGS = {
                      'fileTypes':     'MindTree Data File (*.mt);;All Files (*.*)',
                      'fileExtension': 'mt'
                      }

   def __init__( self, parentWidget ):
      workingDir = RES.get( 'Project',  'directory'     )
      
      ImporterPlugin.__init__( self, parentWidget, self.FILE_TYPES, self.FILE_EXTENSION, workingDir )
   
   def _read( self, aFilename ):
      # Manipulate the filename
      from utilities import splitFilePath
      disk,path,filename,extension = splitFilePath( aFilename )
      documentName = filename[0].upper() + filename[1:]
      
      # Read in the data
      import pickle
      data = pickle.load( open( aFilename, 'rb' ) )
      
      # Convert the data
      theConvertedProject = self.convertProject( data._tree, documentName )
      
      # Package the data for MindTree
      theModel = OutlineModel( theConvertedProject )
      return theModel, { }

   def convertProject( self, model, title ):
      pass
   
pluginClass = MT1ImportingArchiver
'''

### Exporter

### Tool
'''
from ApplicationFramework import RES, PluggableTool
from PyQt4 import QtCore, QtGui

class MyTool( PluggableTool, QtGui.QWidget ):
   NAME             = 'MyToolName'
   VERSION          = ( 1, 0 )
   BUILD_DATE       = ( 2008, 11, 24 )
   
   DEFAULT_SETTINGS = {
                      }

   def __init__( self, parent, app ):
      PluggableTool.__init__( self )
      QtGui.QWidget.__init__( self, parent )
      
      self._buildGui( parent )
   
   def _buildGui( self, aParent ):
      pass
   
pluginClass = myTool
'''

class MindTree( Application ):
   UNTITLED_FILENAME_CT = 1

   def __init__( self ):
      fileTypes  = RES.get( 'Application', 'fileTypes'     )
      fileExts   = RES.get( 'Application', 'fileExtension' )
      workingDir = RES.get( 'Project',     'workspace'     )
      
      Application.__init__( self, Archiver(self,fileTypes,fileExts,workingDir) )
      
      self.setObjectName("MainWindow")
      
      self._MT1Importer   = None
      self._outlineView   = None
      self._kb            = None
      self._plugins       = None
      
      self._buildGUI( )

   def installPlugins( self, app, pluginDir ):
      self._plugins = PluginManager( pluginDir )
      
      # Install Importer Plugins
      def IMPORT( pluginObj ):
         def _import( ):
            return self.importFile( pluginObj )
         return _import
      
      for name in self._plugins.pluginNames( 'ImporterPlugin' ):
         action = QtGui.QAction( self )
         action.setObjectName( name )
         action.setText( name )
         QtCore.QObject.connect( action, QtCore.SIGNAL('triggered()'), IMPORT(self._plugins.makePlugin(name,self)) )
         
         self.importMenu.addAction( action )
      
      # Install Exporter Plugins
      def EXPORT( pluginObj ):
         def _export( ):
            return self.exportFile( pluginObj )
         return _export
      
      for name in self._plugins.pluginNames( 'ExporterPlugin' ):
         action = QtGui.QAction( self )
         action.setObjectName( name )
         action.setText( name )
         QtCore.QObject.connect( action, QtCore.SIGNAL('triggered()'), EXPORT(self._plugins.makePlugin(name,self)) )
         
         self.exportMenu.addAction( action )
      
      # Install Pluggable Tools
      for tabName in RES.getMultipartResource('Tools','Left'):
         if tabName in self._plugins.pluginNames('MindTreePluggableTool'):
            tabContents = self._plugins.makePlugin( tabName, self.leftToolTabs, app, self._outlineView )
            self.leftToolTabs.addTab( tabContents, tabName )
      for tabName in RES.getMultipartResource('Tools','Right'):
         if tabName in self._plugins.pluginNames('MindTreePluggableTool'):
            tabContents = self._plugins.makePlugin( tabName, self.rightToolTabs, app, self._outlineView )
            self.rightToolTabs.addTab( tabContents, tabName )

   # Required Overrides
   def _makeProject( self, filename=None, data=None ):
      '''Return an empty OutlineModel and empty resource dictionary.'''
      return MindTreeProject( data=data, filename=filename )
   
   def _setProject( self, aProject ):
      Application._setProject( self, aProject )
      self._outlineView.setProject( aProject )
   
   def _updateWindowTitle( self, title ):
      self.setWindowTitle( title )
   
   def _commitDocument( self ):
      self._outlineView.commitChanges( )

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
      
      # OutlineEdit Widget
      self._outlineView = OutlineEdit( self.splitter )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 0 )
      self._outlineView.setSizePolicy(sizePolicy)
      self._outlineView.setMinimumSize(QtCore.QSize(100, 100))
      self._outlineView.setOrientation(QtCore.Qt.Horizontal)
      self._outlineView.setChildrenCollapsible(False)
      self._outlineView.setObjectName("splitter")
      
      QtCore.QObject.connect( self._outlineView, QtCore.SIGNAL( 'modelChanged()' ), self.onModelChanged )
      
      # Tools
      self.toolSplitter = QtGui.QSplitter( self.splitter )
      self.toolSplitter.setChildrenCollapsible(False)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
      sizePolicy.setVerticalStretch( 2 )
      sizePolicy.setHorizontalStretch( 1 )
      self.toolSplitter.setSizePolicy( sizePolicy )
      self.toolSplitter.setMinimumHeight( 200 )
      
      self.leftToolTabs  = QtGui.QTabWidget( self.toolSplitter )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 1 )
      self.leftToolTabs.setSizePolicy( sizePolicy )
      
      self.rightToolTabs = QtGui.QTabWidget( self.toolSplitter )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 2 )
      self.rightToolTabs.setSizePolicy( sizePolicy )
      
      self.setCentralWidget(self.splitter)

   def _defineActions( self ):
      self.actionNew       = RES.installAction( 'newFile',    self )
      self.actionOpen      = RES.installAction( 'openFile',   self )
      self.actionClose     = RES.installAction( 'closeFile',  self )
      self.actionSave      = RES.installAction( 'saveFile',   self )
      self.actionSave_as   = RES.installAction( 'saveFileAs', self )
      self.actionExit      = RES.installAction( 'exit',       self )
      self.actionHelp      = RES.installAction( 'help',       self )
      self.actionAbout     = RES.installAction( 'helpAbout',  self )

   def _buildMenus( self ):
      self.menubar = QtGui.QMenuBar(self)
      self.menubar.setObjectName("menubar")
      self.setMenuBar(self.menubar)
      
      self.menuFile = QtGui.QMenu(self.menubar)
      self.menuFile.setObjectName("menuFile")
      self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "Project", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuTools = QtGui.QMenu(self.menubar)
      self.menuTools.setObjectName("menuTools")
      self.menuTools.setTitle(QtGui.QApplication.translate("MainWindow", "Tools", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuHelp = QtGui.QMenu(self.menubar)
      self.menuHelp.setObjectName("menuHelp")
      self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
      
      # Assemble the menubar
      self.menubar.addAction(self.menuFile.menuAction())
      #self.menubar.addAction(self.menuEdit.menuAction())
      for menu in self._outlineView.getFixedMenus( ):
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
      self.importMenu = QtGui.QMenu( self.menuFile )
      self.importMenu.setTitle( 'Import' )
      self.menuFile.addMenu( self.importMenu )
      self.exportMenu = QtGui.QMenu( self.menuFile )
      self.exportMenu.setTitle( 'Export' )
      self.menuFile.addMenu( self.exportMenu )
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
      
      for toolbar in self._outlineView.getToolbars( ):
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
   sys.path.append( os.path.join( sys.path[0], 'Plugins', 'MindTree1Importer' ) )

   app = QtGui.QApplication( sys.argv )

   # Display Splash Screen
   splash = QtGui.QSplashScreen( QtGui.QPixmap('resources/images/splash.gif') )
   splash.show( )
   app.processEvents( )

   # Load Resources
   RES.read( [ 'resources.ini', 'preferences.ini' ] )
   
   # Create the application
   myapp = MindTree( )
   myapp.resize( 903, 719 )
   sizePolicy = QtGui.QSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
   sizePolicy.setHorizontalStretch( 1 )
   sizePolicy.setVerticalStretch( 1 )
   myapp.setSizePolicy( sizePolicy )
   myapp.show( )
   
   # Install Plugins
   myapp.installPlugins( app, 'plugins' )
   
   # Install a default project
   myapp.newFile( )
   
   # Destroy the Splash Screen
   splash.finish( myapp )

   # Run the event loop
   sys.exit( app.exec_() )
