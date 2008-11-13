from __future__ import print_function, unicode_literals
from PyQt4 import QtGui
import MTresources as RES

from utilities import *


class OperationCanceled( Exception ):
   '''This exception is raised whenever a file operation is canceled.
   This exception does not represent an error.  It's purpose is to cause
   the call stack to be popped to return control to the Gui.'''
   def __init__( self ):
      Exception.__init__( self )


class Project( object ):
   NAME_COUNTER = 0
  
   def __init__( self, filename=None, data=None ):
      self._projectDir      = None
      self._filename        = filename
      self.modified         = False
      self.data             = data      # The actual data in the project
      
      if filename is None:
         filename = self.genUntitledFilename( )
      
      self.setFilename( filename )

   def projectDir( self, fullName=False ):
      return self._projectDir
   
   def backupDir( self, fullName=False ):
      if fullName:
         return os.path.join( self._projectDir, RES.PROJECT_BACKUP_DIR )
      else:
         return RES.PROJECT_BACKUP_DIR
   
   def filename( self, fullName=False ):
      if fullName:
         return os.path.join( self._projectDir, self._filename )
      else:
         return self._filename

   def setFilename( self, filename ):
      disk,path,name,extension = splitFilePath( filename )
      self._projectDir = os.path.join( disk, path )
      self._backupDir  = os.path.join( self._projectDir, RES.PROJECT_BACKUP_DIR )
      self._filename   = name + extension

   def activateProjectDir( self ):
      os.chdir( self._projectDir )
   
   def isNew( self ):
      if self._projectDir is None:
         return True
      else:
         return False

   def backup( self ):
      shutil.copytree( self._projectDir, RES.PROJECT_BACKUP_DIR )
   
   def genUntitledFilename( self ):
      Project.NAME_COUNTER += 1
      return 'Untitled{0:02d}'.format(Project.NAME_COUNTER)

   def validateModel( self ):
      self.data.validateModel( )


class Archiver( object ):
   def __init__( self, parentWidget, fileTypes, defaultExtension, initialDir=None ):
      self._parentWidget     = parentWidget
      self._extension        = defaultExtension
      self._fileTypes        = fileTypes
      self._defaultExtension = defaultExtension
      self._initialDir       = initialDir
      
      if self._initialDir is None:
         self._initialDir = os.getcwd()
   
   def setup( self, initialDir ):
      self._initialDir       = initialDir
   
   def defaultExtension( self ):
      return self._defaultExtension

   def askopenfilename( self ):
      dlg = QtGui.QFileDialog( self._parentWidget, 'Open file...', self._initialDir, self._fileTypes )
      dlg.setFileMode( QtGui.QFileDialog.ExistingFile )
      dlg.setModal(True)
      if not dlg.exec_():
         raise OperationCanceled()
      
      filenames = dlg.selectedFiles( )
      
      if len(filenames) != 1:
         raise OperationCanceled()
      
      return unicode(filenames[0])

   def asksaveasfilename( self ):
      dlg = QtGui.QFileDialog( self, 'Save file...', self._initialDir, self._defaultExtension )
      dlg.setAcceptMode( QtGui.QFileDialog.AcceptSave )
      dlg.setModal(True)
      
      if not dlg.exec_():
         raise OperationCanceled()
      
      filenames = dlg.selectedFiles( )
      
      if len(filenames) != 1:
         raise OperationCanceled()
      
      return unicode(filenames[0])

   def read( self ):
      """Read a document from a file.  The function may include user
      interaction, eg. Prompt the user for a filename.
      
      Returns:  Project
      
      Exceptions:
                No exceptions should leave this function.
      """
      filename = self.askopenfilename( )
      
      try:
         return Project( filename, self._readFile(filename) )
      except Exception, msg:
         msgBox = QtGui.QMessageBox()
         msgBox.setWindowTitle( 'Error' )
         msgBox.setText( 'Unable to read file.\n\n  - {0}'.format(msg) )
         msgBox.setIcon( QtGui.QMessageBox.Critical )
         msgBox.exec_()
         raise OperationCanceled()
      except:
         msgBox = QtGui.QMessageBox()
         msgBox.setWindowTitle( 'Error' )
         msgBox.setText( 'An unknown error occured while trying to load file.' )
         msgBox.setIcon( QtGui.QMessageBox.Critical )
         msgBox.exec_()
         raise OperationCanceled()
   
   def write( self, aProject, promptFilename=False ):
      """Write a document to a file.  The function may include user interaction,
      eg. Prompt the user for a filename.
      
      Returns:  str (filename),  The operation completed successfully.
                None,            The operation was not completed.
      
      Exceptions:
                No exceptions should leave this function.
      
      If promptFilename is false, aFilename must be supplied or an exception is
      raised.  If promptFilename is true, the user should be provided the
      opportunity to save the document under another name.  If both aFilename
      and promptFilename are provided, the user should have the opportunity to
      save the document under another name, but aFilename should be the
      default name.
      """
      if promptFilename:
         filename = self.asksaveasfilename( )
      else:
         filename = aProject.filename( fullName=True )
      
      aProject.setFilename( filename )
      
      try:
         self._writeFile( aProject.data, aProject.filename( fullName=True ) )
      except Exception, msg:
         msgBox = QtGui.QMessageBox()
         msgBox.setWindowTitle( 'Error' )
         msgBox.setText( 'The file is invalid.\n\n  - %s' % msg )
         msgBox.setIcon( QtGui.QMessageBox.Critical )
         msgBox.exec_()
         raise OperationCanceled()
      except:
         msgBox = QtGui.QMessageBox()
         msgBox.setWindowTitle( 'Error' )
         msgBox.setText( 'An unknown error occured while trying to load file.' )
         msgBox.setIcon( QtGui.QMessageBox.Critical )
         msgBox.exec_()
         raise OperationCanceled()
      
      return filename

   # Overridable Implementation
   def _readFile( self, aFilename ):
      """Read the file and return a document object.  If an error occurs,
      raise an exception.
      """
      import pickle
      data = pickle.load( open( aFilename, 'rb' ) )
      return data

   def _writeFile( self, aDocument, aFilename ):
      """Write the document to the named file.  If an error occurs,
      raise an exception.
      """
      import pickle
      f = open( aFilename, 'wb' )
      pickle.dump( aDocument, f, -1 )
   

class Application( QtGui.QMainWindow ):
   '''File handling operations (new, open, save, etc.) can get quite confusing
   because there are so many cases which have overlapping solutions:

   new()
      _close()
      create a project
   
   open()
      _close()
      open a project (with a prompt)
   
   save()
      _backup()
      commit changes
      save the project
   
   saveAs()
      _backup()
      commit changes
      save the project (with a prompt)
   
   close()
      _close()
      close the project
   
   _backup()
      If the project is established and modified
         backup the project
   
   _close()
      If the project is modified
         saveAs() on prompt
   '''
   # Management
   def __init__( self, anArchiver ):
      QtGui.QMainWindow.__init__( self )
      
      self._archiver   = anArchiver
      self._project    = None
      self._plugins    = None

   def initializePlugins( self, pluginDir ):
      self._plugins = PluginManager( pluginDir )

   # Implementation
   def newFile( self ):
      try:
         self._closeCurrentProject( )
         
         self._project  = Project( data=self._makeDefaultModel( ) )
         
         self._setModelToEdit( self._project.data )
         self.updateWindowTitle( )
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   def openFile( self, anArchiver=None ):
      try:
         self._closeCurrentProject( )
         
         if anArchiver:
            self._project = anArchiver.read( )
         else:
            self._project = self._archiver.read( )
         
         if self._project is None:
            return False
         
         # Setup the project directory
         self._project.activateProjectDir( )
         
         # Install the Model
         self._setModelToEdit( self._project.data )
         self.updateWindowTitle( )
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   def saveFile( self ):
      try:
         if self._project.modified and self._project.backupDir():
            self._project.backup()
         
         self._commitDocument( )
         theDoc = self._project.data
         self._archiver.write( self._project, promptFilename=False )
         
         self._project.modified = False
         self.updateWindowTitle( )
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   def saveFileAs( self, anArchiver=None ):
      try:
         if self._project.modified and self._project.backupDir():
            self._project.backup( )
         
         self._commitDocument( )
         theDoc = self._project.data
         
         if anArchiver:
            newName = anArchiver.write( self._project, promptFilename=True )
         else:
            newName = self._archiver.write( self._project, promptFilename=True )
         
         self._project = Project( filename=newName, data=self._project.data )
         self._project.activateProjectDir( )
         
         self._project.modified = False
         self.updateWindowTitle( )
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   def closeFile( self ):
      try:
         self.newFile()
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   def exit( self ):
      try:
         self.newFile()
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   def makeBackup( self ):
      import datetime
      import shutil
      from filesystemTools import splitFilePath
      
      if not os.path.exists( self._filename ):
         return
      
      if self._filename and (self._filename != ''):
         disk,path,name,extension = splitFilePath( self._filename )
         if extension == '':
            extension = self._archiver.defaultExtension( )
         
         theDate = datetime.datetime.today( )
         theDateTimeString = theDate.strftime( '-%y%m%d-%H%M%S' )
         name = name + theDateTimeString + extension
         
         backupFilename = os.path.join( self._backupDirectory, name )
         shutil.copyfile( self._filename, backupFilename )

   # Helper Methods
   def _closeCurrentProject( self ):
      if self._project:
         if self._project.modified:
            if self._project.projectDir() and self._project.backupDir():
               self.backup()
            
            self.askSaveChanges( )
      
      return True

   def askSaveChanges( self ):
      """Close the current document.  If the user cancels the operation,
      None is returned.  Otherwise, True is returned.
      """
      self._commitDocument( )
      
      if self._project.modified:
         msgBox = QtGui.QMessageBox( )
         msgBox.setWindowTitle( 'Warning' )
         msgBox.setText( 'Do you want to save the changes to {0}'.format(self._project._filename) )
         msgBox.setIcon( QtGui.QMessageBox.Question )
         msgBox.setStandardButtons( QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel )
         msgBox.setDefaultButton( QtGui.QMessageBox.Yes )
         response = msgBox.exec_( )
         
         if response == QtGui.QMessageBox.Yes:
            self.saveAs( )
         elif response != QtGui.QMessageBox.No:
            raise OperationCanceled()

   def onModelChanged( self ):
      self._project.modified = True
      self.updateWindowTitle( )
   
   def updateWindowTitle( self ):
      theTitle = 'MindTree'
      
      if isinstance( self._project.filename, unicode ):
         theTitle += ' - [{0}]'.format(self._project.filename)
      
      if self._project.modified:
         theTitle += ' *'
      
      self._updateWindowTitle( theTitle ) 

   # Contract
   def _makeDefaultModel( self ):
      pass
   
   def _setModelToEdit( self, aModel ):
      '''Overriding method should perform its operations and call this base
      class method last.'''
      self._project.modified = False
   
   def _updateWindowTitle( self, title ):
      pass
   
   def _commitDocument( self ):
      """Any changes that have not yet been stored in the document from the GUI
      should be done so now.
      """
      pass

# ---------------- Plugin Base Classes --------------------

import os
import sys
import imp


class PluginManager( object ):
   PKG_INIT = '__init__' + os.path.extsep + 'py'
   CONFIG   = None
   
   def __init__( self, pluginDir ):
      self._plugins        = { }
      
      # Make sure the pluginDir is in the python path
      if pluginDir not in sys.path:
         sys.path.append( pluginDir )
      
      # Load all plugins
      for name in os.listdir( pluginDir ):
         fullFilename = os.path.join( pluginDir, name )
         if os.path.isdir( fullFilename ) and os.path.isfile( os.path.join( fullFilename, PluginManager.PKG_INIT ) ):
            moduleName = os.path.splitext( name )[0]
            pluginClass = self._importPlugin( moduleName )
            
            # Store the default settings for this plugin
            if pluginClass and (not self.CONFIG.has_section( pluginClass.NAME )):
               self.CONFIG.add_section( pluginClass.NAME )
               for opt,val in pluginClass.DEFAULT_SETTINGS.iteritems( ):
                  self.CONFIG.set( pluginClass.NAME, opt, val )

   def _importPlugin( self, pluginName ):
      try:
         moduleInfo  = imp.find_module( pluginName )
         module      = imp.load_module( pluginName, *moduleInfo )
         pluginClass = module.pluginClass
      except ImportError:
         print( 'Plugin %s not found' % pluginName )
         return
      except AttributeError:
         print( 'Plugin instance %s.plugin not defined' % pluginName )
         return
      
      try:
         self._plugins[ pluginClass.NAME ] = pluginClass
      except:
         print( 'plugin.NAME is not defined' )
         return
      
      return pluginClass

   def saveSettings( self ):
      if self._configFilename:
         f = file( self._configFilename, 'w' )
         self.CONFIG.write( )
         f.close( )

   def listPluginNames( self ):
      return self._plugins.keys( )

   def iterPlugins( self ):
      return self._plugins.iteritems( )
   
   def makePlugin( self, pluginName, aView ):
      return self._plugins[ pluginName ]( aView )


class Plugin( object ):
   CONFIG = None
   
   def __init__( self, aView ):
      self.name = self.NAME
      self._view = aView

   def buildGUI( self, parent, *args, **options ):
      '''This method is called once when the plugin is first loaded.  Its
      purpose is to construct and return the main GUI for the plugin.  This
      GUI is usually in the form of a frame widget.  All subwidgets must be
      constructed and rendered (placed, packed or gridded).  The main frame
      widget must not be rendered.
      '''
      raise NotImplementedError

   def setOption( self, key, value ):
      self.CONFIG.set( self.NAME, key, value )

   def getOption( self, key ):
      return self.CONFIG.get( self.NAME, key )


# Plugin __init__.py files should have the following format
"""
from PluginFramework import Plugin

class MyPlugin( Plugin ):
   NAME             = 'Build'
   DEFAULT_SETTINGS = {
                         option : value,
                         ...
                      }

   def __init__( self, aView ):
      Plugin.__init__( self, aView )
   
   def buildGUI( self, parent ):
      pass
   
pluginClass = MyPlugin
"""

class ImporterPlugin( Plugin, Archiver ):
   def __init__( self, aView, fileTypes, defaultExtension, initialDir ):
      Plugin.__init__( self, aView )
      Archiver.__init__( self, fileTypes, defaultExtension, initialDir )
   
   def _readFile( self, aFilename ):
      """Read the file and return a document object.  If an error occurs,
      raise an exception.
      """
      import pickle
      return pickle.load( open( aFilename, 'rb' ) )


class ExporterPlugin( Plugin, Archiver ):
   def __init__( self, aView, fileTypes, defaultExtension, initialDir ):
      Plugin.__init__( self, aView )
      Archiver.__init__( self, fileTypes, defaultExtension, initialDir )

   def _writeFile( self, aDocument, aFilename ):
      """Write the document to the named file.  If an error occurs,
      raise an exception.
      """
      import pickle
      f = open( aFilename, 'wb' )
      pickle.dump( aDocument, f )


class PluggableTool( Plugin ):
   '''This is a plugin which extends the View.  Therefore,
   it needs all the same information that the view has.'''
   def __init__( self, aView ):
      Plugin.__init__( self, aView )
      self._view       = aView

   def buildGUI( self, parent, *args, **options ):
      self._view  = parent.winfo_toplevel( )
   
   def getMenu( self, menuParent ):
      return None
   
   def getToolbar( self, toolbarParent ):
      return None
   
   def onActivate( self ):
      raise NotImplementedError
   
   def onDeactivate( self ):
      raise NotImplementedError


