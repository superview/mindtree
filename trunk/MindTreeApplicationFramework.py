from __future__ import print_function, unicode_literals
from PyQt4.QtCore import QObject
from uuid import uuid4

from ApplicationFramework import *
from OutlineModel import *


class MindTreeProject( Project, QObject ):
   def __init__( self, data=None, workspace=None, filename=None, name=None ):
      self._outline   = None
      self._bookmarks = { }    # map name to node id
      
      Project.__init__( self, data, workspace, filename, name )
      QObject.__init__( self )

   def outline( self ):
      return self._outline
   
   def bookmarks( self ):
      return self._bookmarks

   # Required Overrides
   def validate( self ):
      Project.validate( self )
      self._outline.validate( )
   
   def setDefaultData( self ):
      Project.setDefaultData( self )
      
      self._outline   = OutlineModel( )

   def setPersistentData( self, data ):
      baseClassData, rootNode = data
      Project.setPersistentData( self, baseClassData )
      
      assert isinstance( rootNode, TreeNode )
      
      self._outline   = OutlineModel( rootNode )
      
      try:
         self.validate( )
      except:
         self.setDefaultData( )

   def getPersistentData( self ):
      self.validate( )
      rootNode = self._outline.root()
      
      baseClassData = Project.getPersistentData( self )
      return ( baseClassData, rootNode )

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

