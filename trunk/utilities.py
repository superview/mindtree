import os
import os.path
import traceback
from PyQt4 import QtGui, QtCore


def exceptionPopup( ):
   msgBox = QtGui.QMessageBox( )
   msgBox.setWindowTitle( 'Exception' )
   msgBox.setText( traceback.format_exc( ) )
   msgBox.setIcon( QtGui.QMessageBox.Critical )
   msgBox.exec_( )


def dirPath( *parts ):
   if isinstance( parts, str ):
      return parts
   
   return os.path.join( *parts ) + os.sep


def filePath( *parts ):
   if isinstance( parts, str ):
      return parts
   
   return os.path.join( *parts )


def splitFilePath( path ):
   if path is None or (path == ''):
      return '','','',''
   
   fixedPath = os.path.normpath( os.path.normcase( path ) )
   disk, pathRest = os.path.splitdrive( fixedPath )
   path, pathRest = os.path.split( pathRest )
   filename, extension = os.path.splitext( pathRest )
   return disk, path, filename, extension


def defAction( name, parent, handlerObj=None, handlerFn=None, text=None, statustip=None, tooltip=None, icon=None, shortcuts=None, font=None ):
   if handlerFn is None:
      if handlerObj is None:
         handlerObj = parent
      
      handlerFn = handlerObj.__getattribute__( name )
   
   # Create the action
   theAction = QtGui.QAction( parent )
   theAction.setObjectName( name )
   QtCore.QObject.connect( theAction, QtCore.SIGNAL('triggered()'), handlerFn )
   
   # Populate the resources
   if text is not None:
      theAction.setText( QtGui.QApplication.translate("MainWindow", text, None, QtGui.QApplication.UnicodeUTF8) )
   
   if statustip is not None:
      theAction.setStatusTip( QtGui.QApplication.translate("MainWindow", statustip, None, QtGui.QApplication.UnicodeUTF8) )
   
   if tooltip is not None:
      theAction.setToolTip( QtGui.QApplication.translate("MainWindow", tooltip, None, QtGui.QApplication.UnicodeUTF8) )

   if icon is not None:
      theAction.setIcon( QtGui.QIcon(icon) )

   if shortcuts is not None:
      theAction.setShortcuts( shortcuts )
   
   if font is not None:
      theAction.setFont( font )
   
   return theAction


class Action( object ):
   def __init__( self, actionName, **options ):
      self._name = actionName
      self._def  = options
      self._obj  = None

   def install( self, parent, handlerObj=None, handlerFn=None ):
      actionName = self._name
      
      if handlerFn is None:
         if handlerObj is None:
            handlerObj = parent
         
         handlerFn = handlerObj.__class__.__dict__[ self._name ]
      
      self._obj = QtGui.QAction( parent )
      self._obj.setObjectName( self._name )
      QtCore.QObject.connect( theAction, QtCore.SIGNAL('triggered()'), handlerFn )
      
      theResources = self._defs[ self._name ]
      shortcuts    = [ ]
      fontFamily   = None
      fontSize     = None
      fontWeight   = None
      fontItalic   = False
      
      for resourceName, resourceValue in theResources.iteritems():
         if resourceName == 'text':
            theAction.setText( QtGui.QApplication.translate("MainWindow", resourceValue, None, QtGui.QApplication.UnicodeUTF8) )
         elif resourceName == 'statustip':
            theAction.setStatusTip( QtGui.QApplication.translate("MainWindow", resourceValue, None, QtGui.QApplication.UnicodeUTF8) )
         elif resourceName == 'tooltip':
            theAction.setToolTip( QtGui.QApplication.translate("MainWindow", resourceValue, None, QtGui.QApplication.UnicodeUTF8) )
         elif resourceName == 'icon':
            theAction.setIcon( QtGui.QIcon(resourceValue) )
         elif resourceName == 'shortcut':
            shortcuts.append( resourceValue )
         elif resourceName == 'fontfamily':
            fontFamily = resourceValue
         elif resourceName == 'fontsize':
            fontSize   = int(resourceValue)
         elif resourceName == 'fontweight':
            fontWeight = int(resourceValue)
         elif resourceName == 'fontitalic':
            if resourceValue in ( '1', 'True', 'Yes', 'true', 'yes' ):
               fontItalic = True
      
      if len(shortcuts) > 0:
         theAction.setShortcuts( shortcuts )
      
      font = None
      if fontFamily is not None:
         font = QtGui.QFont( fontFamily )
         if fontSize is not None:
            font.setPointSize( fontSize )
         if fontWeight is not None:
            font.setWeight( fontWeight )
         if fontItalic is not None:
            font.setItalic( fontItalic )
      
      if font is not None:
         theAction.setFont( font )
      
      return self._obj

class ActionLib( object ):
   def_lib = { }          # Action definitions
   act_lib = { }          # Action objects
   
   def ActionLib( self ):
      self._defs = { }
      self._acts = { }

   def readDefinitions( self, filename ):
      from ConfigParser import SafeConfigParser
      config = SafeConfigParser( )
      config.read( filename )
      
      for actionName in config.sections( ):
         options = config.options( actionName )
         self.defineAction( actionName, options )

   def define( self, actionName, **options ):
      self._defs[ actionName ] = options
   
   def install( self, actionName, parent, handlerObj=None, handlerFn=None ):
      if handlerFn is None:
         if handlerObj is None:
            handlerObj = parent
         
         handlerFn = handlerObj.__class__.__dict__[ actionName ]
      
      theAction = QtGui.QAction( parent )
      theAction.setObjectName( actionName )
      QtCore.QObject.connect( theAction, QtCore.SIGNAL('triggered()'), handlerFn )
      self._acts[ actionName ] = theAction
      
      theResources = self._defs[ actionName ]
      shortcuts    = [ ]
      fontFamily   = None
      fontSize     = None
      fontWeight   = None
      fontItalic   = False
      
      for resourceName, resourceValue in theResources.iteritems():
         if resourceName == 'text':
            theAction.setText( QtGui.QApplication.translate("MainWindow", resourceValue, None, QtGui.QApplication.UnicodeUTF8) )
         elif resourceName == 'statustip':
            theAction.setStatusTip( QtGui.QApplication.translate("MainWindow", resourceValue, None, QtGui.QApplication.UnicodeUTF8) )
         elif resourceName == 'tooltip':
            theAction.setToolTip( QtGui.QApplication.translate("MainWindow", resourceValue, None, QtGui.QApplication.UnicodeUTF8) )
         elif resourceName == 'icon':
            theAction.setIcon( QtGui.QIcon(resourceValue) )
         elif resourceName == 'shortcut':
            shortcuts.append( resourceValue )
         elif resourceName == 'fontfamily':
            fontFamily = resourceValue
         elif resourceName == 'fontsize':
            fontSize   = int(resourceValue)
         elif resourceName == 'fontweight':
            fontWeight = int(resourceValue)
         elif resourceName == 'fontitalic':
            if resourceValue in ( '1', 'True', 'Yes', 'true', 'yes' ):
               fontItalic = True
      
      if len(shortcuts) > 0:
         theAction.setShortcuts( shortcuts )
      
      font = None
      if fontFamily is not None:
         font = QtGui.QFont( fontFamily )
         if fontSize is not None:
            font.setPointSize( fontSize )
         if fontWeight is not None:
            font.setWeight( fontWeight )
         if fontItalic is not None:
            font.setItalic( fontItalic )
      
      if font is not None:
         theAction.setFont( font )
   
   def action( self, actionName ):
      return self._acts[ actionName ]
   
   def __getitem__( self, actionName ):
      return self._acts[ actionName ]

actionLib = ActionLib( )
