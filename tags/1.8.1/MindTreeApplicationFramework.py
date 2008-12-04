from ApplicationFramework import *
from OutlineView import *
from OutlineModel import *
from utilities import *


class MindTreeProject( Project ):
   def __init__( self, data=None, workspace=None, filename=None, name=None ):
      self.data = None
      Project.__init__( self, data, workspace, filename, name )

   # Required Overrides
   def validate( self ):
      Project.validate( self )
      
      outlineModel,resources = self.data
      outlineModel.validate( )
   
   def setDefaultData( self ):
      Project.setDefaultData( self )
      
      outlineModel = OutlineModel( )
      resources    = { }
      self.data = outlineModel,resources

   def setPersistentData( self, data=None ):
      baseClassData, rootNode, resources = data
      Project.setPersistentData( self, baseClassData )
      
      outlineModel = OutlineModel( rootNode )
      self.data = outlineModel,resources
      
      try:
         self.validate( )
      except:
         self.setDefaultData( )

   def getPersistentData( self ):
      self.validate( )
      outlineModel,resources = self.data
      rootNode = outlineModel.root()
      
      baseClassData = Project.getPersistentData( self )
      return ( baseClassData, rootNode, resources )

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

