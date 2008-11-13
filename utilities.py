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
   
class ActionLib( object ):
   def_lib = { }          # Action definitions
   act_lib = { }          # Action objects
   
   @staticmethod
   def readDefinitions( self, filename ):
      from ConfigParser import SafeConfigParser
      config = SafeConfigParser( )
      config.read( filename )
      
      for actionName in config.sections( ):
         options = config.options( actionName )
         ActionLib.defineAction( actionName, options )

   @staticmethod
   def defineAction( self, actionName, **options ):
      ActionLib.def_lib[ actionName ] = options
   
   @staticmethod
   def installAction( self, parent, actionName, handlerObj=None ):
      if handlerObj is None:
         handlerObj = parent
      
      handlerFn = handlerObj.__dict__[ actionName ]
      
      theAction = QtGui.QAction( widget )
      theAction.setObjectName( actionName )
      QtCore.QObject.connect( theAction, QtCore.SIGNAL('triggered()'), handlerFn )
      ActionLib.act_lib[ actionName ] = theAction
      
      theResources = ActionLib.def_lib[ actionName ]
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
   
   @staticmethod
   def action( self, actionName ):
      return ActionLib.act_lib[ actionName ]

