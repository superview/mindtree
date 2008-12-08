from ApplicationFramework import *
from OutlineModel import *
from PyQt4.QtCore import QObject
from uuid import uuid4


class Resource( object ):
   def __init__( self, name, resType, resVal, resId=None ):
      self.name      = name    # User Defined Name
      self.resType   = resType # Type of the resource
      self.resVal    = resVal  # String or URL of the resource


class ResourceManager( object ):
   def __init__( self ):
      self._res      = { }     # map id to Resource instance
      self._names    = { }     # map name to id
   
   def define( self, name, resType, resVal ):
      self._res[ name ] = Resource( name, resType, resVal )
   
   def undefine( self, name ):
      del self._res[ name ]

   def resource( self, name ):
      return self._res[ name ]


class MindTreeProject( Project, QObject ):
   '''emit: resourceChange(int,QString)'''
   IMAGE_RES       = 'Image'
   BOOKMARK_RES    = 'Bookmark'
   LINK_RES        = 'Link'
   STRING_RES      = 'String'
   
   ADD_ACTION      = 0
   REM_ACTION      = 1
   MOD_ACTION      = 2

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
   def res_add( self, name, resType, value ):
      self._resources[ name ] = [ resType, value ]
                                # type,   resource (url, string, etc.)
      
      self._res_announceChange( )
   
   def res_del( self, name ):
      del self._resources[ name ]
      self._res_announceChange( )

   def res_names( self ):
      return list(self._resources.keys())

   def res_info( self, name ):
      return self._resources[ name ]
   
   def _res_announceChange( self ):
      self.emit( QtCore.SIGNAL( 'resourceChange()' ) )

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

