from __future__ import print_function, unicode_literals
from PyQt4 import QtGui

from utilities import *


from ConfigParser import SafeConfigParser

class OperationCanceled( Exception ):
   '''This exception is raised whenever a file operation is canceled.
   This exception does not represent an error.  It's purpose is to cause
   the call stack to be popped to return control to the Gui.'''
   def __init__( self ):
      Exception.__init__( self )


class Resources( SafeConfigParser ):
   def __init__( self ):
      SafeConfigParser.__init__( self )
      self._actions = { }
   
   # Actions
   def defAction( self, name, **resources ):
      self.add_section( name )
      for resName, resValue in resources.iteritems():
         self.set( name, resName, resValue )

   def installAction( self, name, parent, handlerObj=None, handlerFn=None ):
      if self.has_section( name ):
         actionName = name
      elif self.has_section( 'action.' + name ):
         actionName = 'action.' + name
      elif self.has_section( name + '.action' ):
         actionName = name + '.action'
      elif self.has_section( name + 'Action' ):
         actionName = name + 'Action'
      else:
         fatalErrorPopup( 'Unrecoverable error:  Resource definition not found: {0}'.format( name ) )
      
      resources = dict( self.items(actionName) )
      
      theAction = self.makeActionObj( name, actionName, parent, handlerObj, handlerFn, **resources )
      self._actions[ name ] = theAction
      return theAction

   def getAction( name ):
      return self._actions[ name ]

   # Resource Values
   def get( self, section, option, translate=False, default=None ):
      try:
         resValue = SafeConfigParser.get( self, section, option )
      except:
         resValue = default
      
      if translate:
         resValue = QtGui.QApplication.translate("MainWindow", resValue, None, QtGui.QApplication.UnicodeUTF8)
      return resValue

   def getPath( self, section, option ):
      return os.path.normpath( self.get(section,option) )

   def getFont( self, section, option ):
      elements = self.getMultipartResource(section,option)
      numElements = len(elements)
      
      fontFamily = elements[0]
      
      if numElements >= 2:
         fontSize = int(elements[1])
      else:
         fontSize = 8
      
      if numElements >= 3:
         fontWeight = elements[2].upper()
         if fontWeight in [ '1', 'YES', 'TRUE', 'BOLD' ]:
            fontWeight = QtGui.QFont.Bold
         else:
            try:
               fontWeight = int(fontWeight)
            except:
               fontWeight = -1
      else:
         fontWeight = -1
      
      if numElements >= 4:
         fontSlant = elements[3].upper()
         fontSlant = fontItalic in [ '1', 'YES', 'TRUE', 'ITALIC' ]
      else:
         fontSlant = False
      
      return QtGui.QFont( fontFamily, fontSize, fontWeight, fontSlant )
   
   def getIcon( self, section, option ):
      return QtGui.QIcon( self.get(section,option) )
   
   def getPixmap( self, section, option ):
      return QtGui.QPixmap( self.get(section,option) )
   
   def getCursor( self, section, option ):
      filename, hotspotX, hotspotY = self.getMultipartResource(section, option)
      hotspotX = int(hotspotX)
      hotspotY = int(hotspotY)
      pixmap = QtGui.QPixmap( filename )
      cur    = QtGui.QCursor( pixmap, hotspotX, hotspotY )
      return cur

   def getDragCursor( self, section, option ):
      filename, hotspotX, hotspotY = self.getMultipartResource(section, option)
      hotspotX = int(hotspotX)
      hotspotY = int(hotspotY)
      pixmap = QtGui.QPixmap( filename, None, QtCore.Qt.MonoOnly )
      hotspot = QtCore.QPoint( hotspotX, hotspotY )
      return pixmap, hotspot

   def getColor( self, section, option ):
      parts = self.getMultipartResource( section, option )
      if len(parts) == 3:
         red,green,blue = parts
         red = int(red)
         green = int(green)
         blue = int(blue)
         return QtGui.QColor( red, green, blue )
      elif len(parts) == 1:
         return QtGui.QColor( parts[0] )
      else:
         raise

   def getMultipartResource( self, section, option, translate=False, sep=':' ):
      parts = self.get(section,option).split(':')
      if translate:
         parts = [ QtGui.QApplication.translate("MainWindow", resValue, None, QtGui.QApplication.UnicodeUTF8) for resValue in parts ]
      return parts

   def makeActionObj( self, name, actionName, parent, handlerObj=None, handlerFn=None, **resources ):
      if handlerFn is None:
         if handlerObj is None:
            handlerObj = parent
         
         handlerFn = handlerObj.__getattribute__( name )
      
      # Create the action
      theAction = QtGui.QAction( parent )
      theAction.setObjectName( name )
      QtCore.QObject.connect( theAction, QtCore.SIGNAL('triggered()'), handlerFn )
      
      shortcuts    = [ ]
      
      # Populate the resources
      for resName, resValue in resources.iteritems():
         if resName == 'text':
            theAction.setText( QtGui.QApplication.translate("MainWindow", resValue, None, QtGui.QApplication.UnicodeUTF8) )
         
         elif resName == 'statustip':
            theAction.setStatusTip( QtGui.QApplication.translate("MainWindow", resValue, None, QtGui.QApplication.UnicodeUTF8) )
         
         elif resName == 'tooltip':
            theAction.setToolTip( QtGui.QApplication.translate("MainWindow", resValue, None, QtGui.QApplication.UnicodeUTF8) )
         
         elif resName == 'icon':
            theAction.setIcon( QtGui.QIcon(os.path.normpath(resValue)) )
         
         elif resName == 'shortcut':
            if isinstance( resValue, (str,unicode) ):
               shortcut = QtGui.QApplication.translate("MainWindow", resValue, None, QtGui.QApplication.UnicodeUTF8)
            else:
               shortcut = resValue
            
            shortcuts.append( resValue )
         
         elif resName == 'checkable':
            theAction.setCheckable( self.getboolean(actionName,resName) )
         
         elif resName == 'font':
            font = self.getFont( name, 'font' )
            theAction.setFont( font )
      
      if len(shortcuts) > 0:
         theAction.setShortcuts( shortcuts )
      
      return theAction

   @staticmethod
   def fontStringToFont( val ):
      elements = val.split( ':' )
      numElements = len(elements)
      
      fontFamily = elements[0]
      
      if numElements >= 2:
         fontSize = int(elements[1])
      else:
         fontSize = 8
      
      if numElements >= 3:
         fontWeight = elements[2].upper()
         if fontWeight in [ '1', 'YES', 'TRUE', 'BOLD' ]:
            fontWeight = QtGui.QFont.Bold
         else:
            try:
               fontWeight = int(fontWeight)
            except:
               fontWeight = -1
      else:
         fontWeight = -1
      
      if numElements >= 4:
         fontSlant = elements[3].upper()
         fontSlant = fontItalic in [ '1', 'YES', 'TRUE', 'ITALIC' ]
      else:
         fontSlant = False
      
      return QtGui.QFont( fontFamily, fontSize, fontWeight, fontSlant )
   
   @staticmethod
   def displayText( self, val ):
      pass


RES = Resources( )


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

   def askdir( self, title ):
      dlg = QtGui.QFileDialog( self._parentWidget, title, self._initialDir )
      dlg.setFileMode( QtGui.QFileDialog.DirectoryOnly )
      dlg.setModal(True)
      
      if not dlg.exec_( ):
         raise OperationCanceled()
      
      dirNames = dlg.selectedFiles()
      
      if len(dirNames) != 1:
         raise OperationCanceled()
      
      return unicode(dirNames[0])

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
      dlg = QtGui.QFileDialog( self._parentWidget, 'Save file...', self._initialDir, self._defaultExtension )
      dlg.setAcceptMode( QtGui.QFileDialog.AcceptSave )
      dlg.setModal(True)
      
      if not dlg.exec_():
         raise OperationCanceled()
      
      filenames = dlg.selectedFiles( )
      
      if len(filenames) != 1:
         raise OperationCanceled()
      
      filename = unicode(filenames[0])
      fileExtension = os.extsep + self._defaultExtension
      if not filename.endswith( fileExtension ):
         filename += fileExtension
      
      return filename

   def read( self ):
      """Read a document from a file.  The function may include user
      interaction, eg. Prompt the user for a filename.
      
      Returns:  Project
      
      Exceptions:
                No exceptions should leave this function.
      """
      filename = self.askopenfilename( )
      
      try:
         return filename, self._read(filename)
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
   
   def write( self, data, filename=None ):
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
      if not filename:
         filename = self.asksaveasfilename( )
      
      try:
         self._write( data, filename )
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
   def _read( self, aFilename ):
      """Read the file and return a project object.  If an error occurs,
      raise an exception.
      """
      import pickle
      return pickle.load( open( aFilename, 'rb' ) )

   def _write( self, data, filename ):
      """Write the persistent data in the project.  If an error occurs,
      raise an exception.
      """
      import pickle
      f = open( filename, 'wb' )
      pickle.dump( data, f, pickle.HIGHEST_PROTOCOL )
   

class Project( object ):
   NAME_COUNTER = 0

   def __init__( self, data=None, workspace=None, filename=None, name=None ):
      '''
      empty              init as default
      archiver           init from file
      data               init from data
      '''
      self._name       = name
      self._workspace  = workspace
      self._filename   = filename
      self._modified   = False
      
      if data is not None:
         self.setPersistentData( data )
      else:
         self.setDefaultData( )
      
      if self._filename:
         disk,path,name,ext = splitFilePath(self._filename)
         
         if self._name is None:
            self._name = self._name[0].upper() + self._name[1:]
         
         if self._workspace is None:
            self._workspace = os.path.join( disk, path )
      
      if self._workspace is None:
         self._workspace = RES.get( 'Project','workspace' )

   def name( self ):
      return self._name

   def setName( self, newTitle ):
      self._name = newTitle

   def filename( self, fullName=False ):
      if fullName:
         return os.path.join( self._workspace, self._filename )
      else:
         return self._filename

   def setFilename( self, filename ):
      backupDir = RES.get( 'Project', 'backupDir' )
      
      disk,path,name,extension = splitFilePath( filename )
      self._projectDir = os.path.join( disk, path )
      self._backupDir  = os.path.join( self._projectDir, backupDir )
      self._filename   = name + extension

   def activateProjectDir( self ):
      os.chdir( self._workspace )
   
   def genDefaultName( self ):
      Project.NAME_COUNTER += 1
      return 'Untitled{0:02d}'.format(Project.NAME_COUNTER)

   def backup( self ):
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

   # Contract
   def validate( self ):
      if not isinstance( self._name, (str,unicode) ):
         raise

   def setDefaultData( self ):
      self._name = self.genDefaultName( )

   def setPersistentData( self, data ):
      if not isinstance( data, (str,unicode) ):
         raise
      
      self._name = data

   def getPersistentData( self ):
      return self._name
   

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
   def __init__( self, archiver ):
      QtGui.QMainWindow.__init__( self )
      
      self._archiver   = archiver
      self._project    = None

   # Implementation
   def newFile( self ):
      try:
         self._closeCurrentProject( )
         
         self._project = self._makeProject( )
         
         self._setupModelInView( )
         self.updateWindowTitle( )
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   def openFile( self ):
      try:
         self._closeCurrentProject( )
         
         filename, data = self._archiver.read( )
         self._project = self._makeProject( filename, data )
         
         if self._project is None:
            return False
         
         # Setup the project directory
         self._project.activateProjectDir( )
         
         # Install the Model
         self._setupModelInView( )
         self.updateWindowTitle( )
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   def saveFile( self ):
      try:
         #if self._project.modified:
            #self._project.backup()
         
         self._commitDocument( )
         
         self._project.validate( )
         data = self._project.getPersistentData( )
         filename = self._project.filename( fullName=True )
         self._archiver.write( data, filename )
         
         self.updateWindowTitle( )
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   def saveFileAs( self ):
      try:
         #if self._project.modified:
            #self._project.backup( )
         
         self._commitDocument( )
         
         self._project.validate( )
         data = self._project.getPersistentData( )
         self._archiver.write( data )
         
         self.updateWindowTitle( )
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   def importFile( self, anArchiver ):
      try:
         self._closeCurrentProject( )
         
         filename, data = anArchiver.read( )
         self._project = self._makeProject( filename, data )
         
         if self._project is None:
            return False
         
         # Setup the project directory
         self._project.activateProjectDir( )
         
         # Install the Model
         self._setupModelInView( )
         self.updateWindowTitle( )
      except OperationCanceled:
         pass
      except:
         exceptionPopup( )
   
   
   def exportFile( self, anArchiver ):
      try:
         #if self._project.modified:
            #self._project.backup( )
         
         self._commitDocument( )
         
         self._project.validate( )
         data = self._project.getPersistentData( )
         anArchiver.write( data )
         
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
   
   # Helper Methods
   def _closeCurrentProject( self ):
      if self._project:
         if self._project.modified:
            if self._project.projectDir():
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
      appName = RES.get( 'Application', 'Name' )
      filename = self._project.filename()
      
      theTitle = '{0} - [{1}]'.format(appName, filename)
      
      if self._project.modified:
         theTitle += ' *'
      
      self._updateWindowTitle( theTitle ) 

   # Contract
   def _makeProject( self, filename=None, data=None ):
      pass
   
   def _setupModelInView( self ):
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
            if pluginClass and (not RES.has_section( pluginClass.NAME )):
               RES.add_section( pluginClass.NAME )
            if pluginClass:
               configuredOptions = RES.options( pluginClass.NAME )
               for opt,val in pluginClass.DEFAULT_SETTINGS.iteritems( ):
                  if opt.lower() not in configuredOptions:
                     RES.set( pluginClass.NAME, opt, val )

   def _importPlugin( self, pluginName ):
      try:
         moduleInfo  = imp.find_module( pluginName )
         module      = imp.load_module( pluginName, *moduleInfo )
         pluginClass = module.pluginClass
      except ImportError:
         print( 'The Plugin %s cannot be imported' % pluginName )
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
         RES.write( )
         f.close( )

   def pluginLib( self ):
      pluginLib = { }
      for nm,cls in self._plugins.iteritems():
         bases = [ base.__name__ for base in cls.__bases__ ]
         pluginLib[ nm ] = bases
      return pluginLib

   def pluginNames( self, baseClassName=None ):
      if baseClassName is None:
         return self._plugins.keys( )
      else:
         names = [ ]
         for nm, cls in self._plugins.iteritems():
            for base in cls.__bases__:
               if base.__name__ == baseClassName:
                  names.append( nm )
         
         return names

   def makePlugin( self, pluginName, *args, **opts ):
      return self._plugins[ pluginName ]( *args, **opts )


class Plugin( object ):
   def __init__( self ):
      self.name = self.NAME

   def setOption( self, key, value ):
      RES.set( self.NAME, key, value )

   def getOption( self, key ):
      return RES.get( self.NAME, key )


# Plugin __init__.py files should have the following format
"""
from PluginFramework import Plugin

class MyPlugin( Plugin ):
   NAME             = 'Build'
   VERSION          = ( 1, 5 )
   BUILD_DATE       = ( 2008, 11, 26 )
   
   DEFAULT_SETTINGS = {
                         option : value,
                         ...
                      }

   def __init__( self ):
      Plugin.__init__( self )
   
pluginClass = MyPlugin
"""

class ImporterPlugin( Plugin, Archiver ):
   def __init__( self, aView, fileTypes, defaultExtension, initialDir ):
      Plugin.__init__( self )
      Archiver.__init__( self, aView, fileTypes, defaultExtension, initialDir )
   
   def _readFile( self, aFilename ):
      """Read the file and return a document object.  If an error occurs,
      raise an exception.
      """
      import pickle
      return pickle.load( open( aFilename, 'rb' ) )


class ExporterPlugin( Plugin, Archiver ):
   def __init__( self, aView, fileTypes, defaultExtension, initialDir ):
      Plugin.__init__( self )
      Archiver.__init__( self, aView, fileTypes, defaultExtension, initialDir )

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
   def __init__( self ):
      Plugin.__init__( self )

   def buildGUI( self, parent, *args, **options ):
      pass
   
   def getMenu( self, menuParent ):
      return None
   
   def getToolbar( self, toolbarParent ):
      return None
   
   def onActivate( self ):
      raise NotImplementedError
   
   def onDeactivate( self ):
      raise NotImplementedError

