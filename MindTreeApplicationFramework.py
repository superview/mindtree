from ApplicationFramework import *
from OutlineModel import *
from ArticleResourceModel import *
from PyQt4.QtCore import QObject
from uuid import uuid4


class TreeEntryIconSelector( object ):
   EmptyArticleIcon = None
   FullArticleIcon  = None
   FlagRedIcon      = None
   FlagGreenIcon    = None
   FlagBlueIcon     = None
   FlagYellowIcon   = None
   FlagBlackIcon    = None
   FlagWhiteIcon    = None

   def __init__( self ):
      TreeEntryIconSelector.EmptyArticleIcon = QtCore.QVariant(RES.getIcon('OutlineEdit','emptyArticleIcon'  ))
      TreeEntryIconSelector.FullArticleIcon  = QtCore.QVariant(RES.getIcon('OutlineEdit','fullArticleIcon'   ))
      TreeEntryIconSelector.FlagRedIcon      = QtCore.QVariant(RES.getIcon('OutlineEdit','redBookmarkIcon'   ))
      TreeEntryIconSelector.FlagGreenIcon    = QtCore.QVariant(RES.getIcon('OutlineEdit','greenBookmarkIcon' ))
      TreeEntryIconSelector.FlagBlueIcon     = QtCore.QVariant(RES.getIcon('OutlineEdit','blueBookmarkIcon'  ))
      TreeEntryIconSelector.FlagYellowIcon   = QtCore.QVariant(RES.getIcon('OutlineEdit','yellowBookmarkIcon'))
      TreeEntryIconSelector.FlagBlackIcon    = QtCore.QVariant(RES.getIcon('OutlineEdit','blackBookmarkIcon' ))
      TreeEntryIconSelector.FlagWhiteIcon    = QtCore.QVariant(RES.getIcon('OutlineEdit','whiteBookmarkIcon' ))
      
      self._outlineResManager = None

   def setResourceManager( self, resMgr ):
      self._outlineResManager = res

   def iconForIndex( self, index ):
      item = index.internalPointer()
      
      if item.id() in self._bookmarkedIds:
         return TreeEntryIconSelector.FlagBlueIcon
      elif item.article() == '':
         return TreeEntryIconSelector.EmptyArticleIcon
      else:
         return TreeEntryIconSelector.FullArticleIcon


class MindTreeProject( Project, QObject ):
   def __init__( self, data=None, workspace=None, filename=None, name=None ):
      self._outline   = None
      self._resources = None
      
      Project.__init__( self, data, workspace, filename, name )
      QObject.__init__( self )

   def outline( self ):
      return self._outline
   
   def resources( self ):
      return self._resources

   # Required Overrides
   def validate( self ):
      Project.validate( self )
      self._outline.validate( )
      self._resources.validate( )
   
   def setDefaultData( self ):
      Project.setDefaultData( self )
      
      self._outline   = OutlineModel( )
      self._resources = ArticleResourcesModel( )

   def setPersistentData( self, data ):
      baseClassData, rootNode, resources = data
      Project.setPersistentData( self, baseClassData )
      
      assert isinstance( rootNode, TreeNode )
      assert isinstance( resources, ArticleResources )
      
      self._outline   = OutlineModel( rootNode )
      self._resources = ArticleResourcesModel( resources )
      
      try:
         self.validate( )
      except:
         self.setDefaultData( )

   def getPersistentData( self ):
      self.validate( )
      rootNode = self._outline.root()
      resources = self._resources.rawResourceObject()
      
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

