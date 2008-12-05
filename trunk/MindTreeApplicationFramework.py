from ApplicationFramework import *
#from OutlineView import *
from OutlineModel import *
from utilities import *
from PyQt4.QtCore import QObject


class MindTreeProject( Project, QObject ):
   '''emit: resourceChange()'''
   IMAGE_RES       = 'Image'
   BOOKMARK_RES    = 'Bookmark'
   LINK_RES        = 'Link'

   def __init__( self, data=None, workspace=None, filename=None, name=None ):
      self._outline   = None
      self._resources = None
      
      Project.__init__( self, data, workspace, filename, name )
      QObject.__init__( self )

   def outline( self ):
      return self._outline
   
   def resources( self ):
      return self._resources

   # Resource Manipulation
   def res_add( self, name, resType, url ):
      if resType in ( MindTreeProject.IMAGE_RES ):
         linkString = '<IMG SRC="{0}">'.format( url )
      else:
         linkString = ( '<A HREF="{0}">'.format(url), '</A>' )
      
      self._resources[ name ] = [ url, resType, linkString, 0 ]
                           # URL, type,    usage,      usageCount
      
      self._res_announceChange( name )
   
   def res_del( self, name ):
      del self._resources[ name ]
      self._res_announceChange( name )

   def res_names( self ):
      return list(self._resources.keys())

   def res_info( self, name ):
      return self._resources[ name ]
   
   def res_incrementUsageCount( self ):
      self._resources[ name ][3] += 1
      self._res_announceChange( name )
   
   def res_decrementUsageCount( self ):
      self._resources[ name ][3] -= 1
      self._res_announceChange( name )
   
   def _res_announceChange( self, name ):
      self.emit( QtCore.SIGNAL( 'resourceChange(QString)' ), name )

   # Required Overrides
   def validate( self ):
      Project.validate( self )
      self._outline.validate( )
   
   def setDefaultData( self ):
      Project.setDefaultData( self )
      
      self._outline   = OutlineModel( )
      self._resources = { }

   def setPersistentData( self, data ):
      baseClassData, rootNode, resources = data
      Project.setPersistentData( self, baseClassData )
      
      self._outline   = OutlineModel( rootNode )
      self._resources = resources
      
      try:
         self.validate( )
      except:
         self.setDefaultData( )

   def getPersistentData( self ):
      self.validate( )
      rootNode = self._outline.root()
      
      baseClassData = Project.getPersistentData( self )
      return ( baseClassData, rootNode, self._resources )

   def _defaultFileExtension( self ):
      return RES.get('Application','fileExtension')


class MindTreePluggableTool( PluggableTool ):
   def __init__( self, parent, app, outlineView ):
      PluggableTool.__init__( self )
      
      self._parent      = parent
      self._app         = app
      self._outlineView = outlineView
      
      self._outlineWidget = self._outlineView.outlineWidget()
      self._articleWidget = self._outlineView.articleWidget()
      
      self._textSelectors = { }
   
   # Tool Selection Cursors
   def defineTextSelector( self, format, name=None ):
      if name is None:
         name = self.NAME
      
      specialSelection = QtGui.QTextEdit.ExtraSelection( )
      specialSelection.format = format
      self._textSelectors[ name ] = specialSelection

   def applyTextSelector( self, beginPos, endPos, moveUserCursor=True, name=None ):
      if name is None:
         name = self.NAME
      
      # Mark the text
      cursor = self._articleWidget.textCursor()
      cursor.setPosition( beginPos )
      cursor.setPosition( endPos, QtGui.QTextCursor.KeepAnchor )
      self._textSelectors[ name ].cursor = cursor
      self._articleWidget.setExtraSelections( [ self._textSelectors[name] ] )
      
      # Advance the cursor
      if moveUserCursor:
         cursor = self._articleWidget.textCursor()
         cursor.setPosition( endPos )
         self._articleWidget.setTextCursor( cursor )

   def specialSelection( self, name=None ):
      if name is None:
         name = self.NAME
      
      return self._textSelectors[name]

   def showSelection( self, index, fromPos=None, toPos=None, moveUserCursor=True, name=None ):
      self._outlineWidget.setCurrentIndex( index )
      
      if fromPos and toPos and name:
         self.applyTextSelector( fromPos, toPos, moveUserCursor, name )

