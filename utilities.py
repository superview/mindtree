import os
import os.path
import traceback
from PyQt4 import QtGui, QtCore


def fatalErrorPopup( msg ):
   msgBox = QtGui.QMessageBox( )
   msgBox.setWindowTitle( 'Fatal Error' )
   msgBox.setText( traceback.format_exc( ) )
   msgBox.setDetailedText( msg )
   msgBox.setInformativeText( msg )
   msgBox.setIcon( QtGui.QMessageBox.Critical )
   msgBox.exec_( )
   exit( )


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


def defAction( name, parent, handlerObj=None, handlerFn=None, **resources ):
   if handlerFn is None:
      if handlerObj is None:
         handlerObj = parent
      
      handlerFn = handlerObj.__getattribute__( name )
   
   # Create the action
   theAction = QtGui.QAction( parent )
   theAction.setObjectName( name )
   QtCore.QObject.connect( theAction, QtCore.SIGNAL('triggered()'), handlerFn )
   
   shortcuts    = [ ]
   font         = None
   fontFamily   = None
   fontSize     = None
   fontWeight   = None
   fontItalic   = False
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
      
      elif resName == 'shortcuts':
         if isinstance( shortcuts, (list,tuple) ):
            translated = [ ]
            for entry in resValue:
               if isinstance( entry, (str,unicode) ):
                  shortcut = QtGui.QApplication.translate("MainWindow", entry, None, QtGui.QApplication.UnicodeUTF8)
               else:
                  shortcut = entry
               
               translated.append( entry )
         
         theAction.setShortcuts( translated )
      
      elif resName == 'fontfamily':
         fontFamily = resourceValue
      elif resName == 'fontsize':
         fontSize   = int(resourceValue)
      elif resName == 'fontweight':
         fontWeight = int(resourceValue)
      elif resName == 'fontitalic':
         if resValue in ( '1', 'True', 'Yes', 'true', 'yes' ):
            fontItalic = True
   
   if len(shortcuts) > 0:
      theAction.setShortcuts( shortcuts )
   
   if fontFamily is not None:
      font = QtGui.QFont( *(fontFamily, fontSize, fontWeight, fontItalic) )
      theAction.setFont( font )
   
   return theAction



