import Tix
import TkTools
from   resources import RES
from   ConfigParser import SafeConfigParser
from   Project import Project


class Clipboard( object ):
   def __init__( self ):
      self._value = None
   
   def set( self, aNewValue ):
      self._value = aNewValue
   
   def get( self ):
      return self._value


class Archiver( object ):
   def __init__( self, fileTypes, defaultExtension, initialDir=None ):
      self._extension        = defaultExtension
      self._fileTypes        = fileTypes
      self._defaultExtension = defaultExtension
      self._initialDir       = initialDir
   
   def setup( self, initialDir ):
      self._initialDir       = initialDir
   
   def defaultExtension( self ):
      return self._defaultExtension

   def askopenfilename( self ):
      import tkFileDialog
      import os
      theFilename = tkFileDialog.askopenfilename( filetypes=self._fileTypes,
                    defaultextension=self._defaultExtension,
                    initialdir=self._initialDir )
      
      if isinstance( theFilename, str ):
         theFilename = theFilename.replace( '/', os.sep )
      
      return theFilename
   
   def read( self ):
      """Read a document from a file.  The function may include user
      interaction, eg. Prompt the user for a filename.
      
      Returns:  tuple ( document, filename ), The operation completed successfully.
                None,                         The operation was not completed.
      
      Exceptions:
                No exceptions should leave this function.
      """
      filename = self.askopenfilename( )
      
      if (filename is None) or (filename == ''):
         return
      
      try:
         return Project( filename, self._readFile(filename) )
      except Exception, msg:
         import tkMessageBox
         tkMessageBox.showerror( 'Error', 'Unable to read file.\n\n  - %s' % msg )
         return None
      except:
         import tkMessageBox
         tkMessageBox.showerror( 'Error', 'An unknown error occured while trying to load file.' )
         return None
   
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
         import tkFileDialog
         import os.path
         filename = tkFileDialog.asksaveasfilename( filetypes=self._fileTypes,
                       defaultextension=self._defaultExtension,
                       initialdir=aProject.projectDir(), initialfile=aProject.filename() )
         
         if (filename is None) or ( filename == ''):
            return 
         
         import os
         filename = filename.replace( '/', os.sep )
      else:
         filename = aProject.filename( fullName=True )
      
      aProject.setFilename( filename )
      
      try:
         self._writeFile( aProject.data, aProject.filename( fullName=True ) )
      except Exception, msg:
         import tkMessageBox
         tkMessageBox.showerror( 'Error', 'The file is invalid.\n\n  - %s' % msg )
         return None
      except:
         import tkMessageBox
         tkMessageBox.showerror( 'Error', 'An unknown error occured while trying to save file.' )
         return None
      
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
   

class Application( Tix.Tk ):
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
   CONFIG       = None

   # Management
   def __init__( self ):
      Tix.Tk.__init__( self )
      
      self._ModelClass = None
      self._ViewClass  = None
      
      self._view       = None
      self._archiver   = None
      
      self._project    = None
      
      self._plugins    = None
      self._clipboard  = Clipboard( )
      #self._backupDirectory = None
      self.protocol( 'WM_DELETE_WINDOW', self.exit )

   def setupMVC( self, aModelClass, aViewClass, archiver ):
      self._ModelClass = aModelClass
      self._ViewClass  = aViewClass
      self._archiver   = archiver
   
   def setupConfig( self, configFilename, recentProjectFilename ):
      Application.CONFIG      = SafeConfigParser( )
      Application.CONFIG.read( configFilename )
      PluginManager.CONFIG    = Application.CONFIG
      Plugin.CONFIG           = Application.CONFIG
      Project.CONFIG          = Application.CONFIG
      self._ViewClass.setupConfig( Application.CONFIG )
   
   def initializePlugins( self, pluginDir ):
      self._plugins = PluginManager( pluginDir )

   # Implementation
   def new( self ):
      self._closeCurrentProject( )
      
      self._project  = Project( data=self._ModelClass( ) )
      
      self._view.setModel( self._project )
      self.updateWindowTitle( )
   
   def open( self, anArchiver=None ):
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
      self._view.setModel( self._project )
      self.updateWindowTitle( )
   
   def save( self ):
      if self._project.modified and self._project.backupDir():
         self._project.backup()
      
      self._commitDocument( )
      theDoc = self._project.data
      if self._archiver.write( self._project, promptFilename=False ) is not None:
         self._project.modified = False
      
      self.updateWindowTitle( )
   
   def saveAs( self, promptName=True, anArchiver=None ):
      if self._project.modified and self._project.backupDir():
         self._project.backup( )
      
      self._commitDocument( )
      theDoc = self._project.data
      
      if anArchiver:
         newName = anArchiver.write( self._project, promptFilename=True )
      else:
         newName = self._archiver.write( self._project, promptFilename=True )
      
      if newName is not None:
         self._project = Project( filename=newName, data=self._project.data )
         self._project.activateProjectDir( )
      
      self.updateWindowTitle( )
   
   def close( self ):
      self._closeCurrentProject( )
      self.destroy( )
   
   def exit( self ):
      self._closeCurrentProject( )
      self.destroy( )
   
   def getClipboard( self ):
      return self._clipboard

   def makeBackup( self ):
      import datetime
      import shutil
      
      if not os.path.exists( self._filename ):
         return
      
      if self._filename and (self._filename != ''):
         disk,path,name,extension = TkTools.splitFilePath( self._filename )
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
            
            if self.askSaveChanges( ) is None:
               return None
      
      return True

   def askSaveChanges( self ):
      """Close the current document.  If the user cancels the operation,
      None is returned.  Otherwise, True is returned.
      """
      self._commitDocument( )
      
      if self._modified:
         import tkMessageBox
         response = tkMessageBox._show( 'Warning', 'Do you want to save the changes to %s' % self._filename,
                                        tkMessageBox.WARNING, tkMessageBox.YESNOCANCEL, default=tkMessageBox.YES )
         
         if response == 'yes':
            self.saveAs( )
         elif response != 'no':
            return None
      
      return True
   
   def _commitDocument( self ):
      """Any changes that have not yet been stored in the document from the GUI
      should be done so now.
      """
      self._view.commit( )

   def onModified( self, event=None ):
      self._modified = True
      self.updateWindowTitle( )
   
   def updateWindowTitle( self ):
      theTitle = RES.APP_NAME
      
      if isinstance( self._project.filename, (str,unicode) ):
         theTitle += ' - [%s]' % str(self._project.filename)
      
      if self._project.modified:
         theTitle += ' *'
      
      self.title( theTitle ) 

   # Contract
   def buildGUI( self ):
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
         print 'Plugin %s not found' % pluginName
         return
      except AttributeError:
         print 'Plugin instance %s.plugin not defined' % pluginName
         return
      
      try:
         self._plugins[ pluginClass.NAME ] = pluginClass
      except:
         print 'plugin.NAME is not defined'
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


