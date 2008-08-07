"""
TASKS - Basic Functionality

- Figure out how to implement undo/redo

FEATURE

- Improve drag n drop so that it works across multiple TreeEditor instances.

- Find some way to number the tree entries.

- Need to figure out a better way to do drag-and-drop.  Currently,
  _dnd_insertionPos must have access to the TreeViewEntry widgets
  to be able to fully implement drag-and-drop.  This makes TixTreeDnDInterface
  too dependent upon TreeEditor.
"""

import Tix
from Tree import *
from Outline import Outline
from TkTools import menuItem, CALLBACK, EVTCALLBACK, EVTCALLBACK2, splitFilePath, exceptionPopup
import Tkdnd
import tkFont
from DocumentWriter.DocumentWriter import DocumentWriter
from Project import Project
from tkMessageBox import *
import sys
import os.path

from resources import RES


class ArticleEditor( DocumentWriter ):
   CONFIG = None
   
   def __init__( self, parent, **options ):
      DocumentWriter.__init__( self, parent, **options )

   def onInsertImage( self, filename=None ):
      if filename is None:
         import tkFileDialog
         filename = tkFileDialog.askopenfilename( parent=self, filetypes=[ ( 'GIF Image', '*.gif' ) ] )
         if not filename or (filename == ''):
            return
      
      disk,path,name,extension = splitFilePath( filename )
      imagePath = os.path.join( ArticleEditor.CONFIG.get( 'Editor', 'imageDir' ), name + extension )
      if not os.path.exists( imagePath ):
         import shutil
         shutil.copy( filename, imagePath )
      
      DocumentWriter.onInsertImage( self, imagePath )


class Dragable:
   def __init__( self, path ):
      assert isinstance( path,  TreePath )
      
      self.path = path
   
   def dnd_end( self, targetObject, evt ):
      assert isinstance( self.path, TreePath )
      pass


class TixTreeDnDInterface( object ):
   __onCompletion = None

   INSERT_BEFORE_CURSOR = 'arrow_insertBefore'
   INSERT_AFTER_CURSOR  = 'arrow_insertAfter'
   INSERT_CHILD_CURSOR  = 'arrow_insertChild'

   def __init__( self, tixTreeInstance, childWidgetMap ):
      self._tixTreeInstance = tixTreeInstance
      self.mainWidget        = childWidgetMap
      
      tixTreeInstance._dndInterface = self
      tixTreeInstance.dnd_start  = self.dnd_start
      tixTreeInstance.dnd_accept = self.dnd_accept
      tixTreeInstance.dnd_enter  = self.dnd_enter
      tixTreeInstance.dnd_motion = self.dnd_motion
      tixTreeInstance.dnd_leave  = self.dnd_leave
      tixTreeInstance.dnd_commit = self.dnd_commit

   def dnd_start( self, evt, source, dropHandler ):
      self._dropHandler    = dropHandler
      dndHandler  = Tkdnd.dnd_start( source, evt )
      self._tixTreeInstance.bind_all( '<KeyPress-Escape>', dndHandler.cancel )
      self._theWidget = evt.widget

   def dnd_accept( self, source, evt ):
      return self
   
   def dnd_enter( self, source, evt ):
      self._originalCursor = self._tixTreeInstance.cget( 'cursor' )
      self._tixTreeInstance.dnd_motion( source, evt )
   
   def dnd_motion( self, source, evt ):
      dragSite, rel = self._dnd_insertionPos( evt )
      self._selectCursor( rel )
      
      #self._tixTreeInstance.anchor_set( dragSite )
      #self._tixTreeInstance.selection_clear( )
      #self._tixTreeInstance.selection_set( dragSite )
   
   def dnd_leave( self, source, evt ):
      self._tixTreeInstance.selection_clear( )
      self._tixTreeInstance.config( cursor=self._originalCursor )
   
   def dnd_commit( self, source, evt ):
      self._tixTreeInstance.unbind_all( '<KeyPress-Escape>' )
      self._tixTreeInstance.config( cursor=self._originalCursor )
      self._tixTreeInstance.selection_clear( )
      
      dropSitePath, rel = self._dnd_insertionPos( evt )
      dropSitePath = TreePath(dropSitePath)
      
      if dropSitePath.isChildOf( source.path ):
         return
      
      self._dropHandler( source.path, dropSitePath, rel )

   def _dnd_insertionPos( self, evt ):
      htree = self._tixTreeInstance
      
      # First find the closest entry to the cursor
      dragSitex = htree.winfo_pointerx( ) - self._tixTreeInstance.winfo_rootx( )
      dragSitey = htree.winfo_pointery( ) - self._tixTreeInstance.winfo_rooty( )
      dragSite  = htree.nearest( dragSitey )
      
      # Next find out if the cursor is above or below the midpoint
      dragSiteBBox = htree.info_bbox( dragSite )
      min_y = dragSiteBBox[1]
      max_y = dragSiteBBox[3]
      mid_y = ( min_y + max_y ) / 2
      if dragSitey <= mid_y:
         # Before
         return ( dragSite, Tree.BEFORE )
      else:
         # After
         # Is it a sibling or child position?
         entryWidget = self.mainWidget._entryWidget[ TreePath(dragSite).child( ) ]
         mid_x = entryWidget.winfo_x( ) + 15
         if dragSitex < mid_x:
            return ( dragSite, Tree.AFTER )
         else:
            return ( dragSite, Tree.CHILD )

   def _selectCursor( self, rel ):
      if rel == Tree.BEFORE:
         self._theWidget.config( cursor=RES.DnD_INSERT_BEFORE_CURSOR )
      elif rel == Tree.AFTER:
         self._theWidget.config( cursor=RES.DnD_INSERT_AFTER_CURSOR  )
      else:
         self._theWidget.config( cursor=RES.DnD_INSERT_CHILD_CURSOR  )


class TreeViewEntry( Tix.Frame ):
   FONT = ''
   
   def __init__( self, parent, treeEntry ):
      self.label      = None         # the label widget (to hold the icon)
      self.entry      = None         # the entry widget (to hold the title)
      self._treeEntry = treeEntry    # reference to the associated outline entry
      
      Tix.Frame.__init__( self, parent, relief=Tix.FLAT, bd=0, bg='white', highlightbackground='white', highlightthickness=0, background='white' )
      
      # Create the label
      self.label = Tix.Label( self )
      self.label.pack( side=Tix.LEFT )
      
      # Create the entry
      self.entry = Tix.Entry( self, relief=Tix.FLAT, bd=0, width=200, font=TreeViewEntry.FONT )
      self.entry.pack( side=Tix.LEFT )#, padx=10 )
      
      # Set the entry widget's text
      self.entry.insert( 'end', self._treeEntry.title )
      
      # update the icon
      if self._treeEntry.article and (len(self._treeEntry.article) > 0):
         self.label.config( image=RES.TEXTFILE_IMG )
      else:
         self.label.config( image=RES.FILE_IMG )
   
   def commit( self, articleWidget ):
      modified = False
      
      # Collect the data to commit
      title    = self.entry.get( )
      article  = articleWidget.stext.dump( )
      
      if article and (len(article) == 0):
         article = None
      
      # If the entry title has changed, save it.
      if title != self._treeEntry.title:
         modified = True
         self._treeEntry.title = title
      
      # If the entry article has changed, save it.
      if article != self._treeEntry.article:
         modified = True
         self._treeEntry.article = article
         
         # update the icon
         if self._treeEntry.article and (len(self._treeEntry.article) > 0):
            self.label.config( image=RES.TEXTFILE_IMG )
         else:
            self.label.config( image=RES.FILE_IMG )
      
      return modified

   def update( self, articleWidget, grabFocus=False ):
      # update the icon
      if self._treeEntry.article and (len(self._treeEntry.article) > 0):
         self.label.config( image=RES.TEXTFILE_IMG )
      else:
         self.label.config( image=RES.FILE_IMG )
      
      # update the articleWidget
      try:
         articleWidget.stext.reinitialize( )
      except:
         print 'Update failed to reinitialize StyledText widget.'
         raise
      
      data = self._treeEntry.article
      dataType = 'text' if isinstance( self._treeEntry.article, (str,unicode) ) else 'dump'
      
      try:
         #if dataType == 'dump':
            #obj = articleWidget.stext.objectFactory().makeObject( 'Dump', data )
         #else:
            #obj = articleWidget.stext.objectFactory().makeObject( 'Text', data )
         
         #articleWidget.stext.insertObject( obj ) 
         articleWidget.stext.insert( 'end', self._treeEntry.article, dataType )
      except:
         print 'Error displaying new article.'
         raise
      
      articleWidget.stext.edit_reset( )
   
   def focus_set( self ):
      self.entry.focus_set( )
      self.entry.icursor( 'end' )


class ForewardFinder( object ):
   NOT_STARTED      = 10
   SCANNING_TITLE   = 20
   SCANNING_ARTICLE = 30
   
   def __init__( self, tree, regEx, treeTitles=True, treeData=True ):
      assert isinstance( tree,        Tree )
      assert isinstance( treeTitles,  bool )
      assert isinstance( treeData,    bool )
      assert treeTitles or treeData
      
      self._tree           = tree
      self._pattern        = regEx
      self._iter           = None
      self._currentTree    = None
      self._currentPath    = None
      self._currentLineSet = [ ]
      self._currentLineNo  = None
      self._currentColumn  = 0
      self._searchTitles   = treeTitles
      self._searchArticles = treeData
      
      self._iter    = ForewardTreeIterator( self._tree )
      
      self._currentTree, self._currentPath = self._iter.next( )
      
      if self._searchTitles:
         self._subject = ForewardFinder.SCANNING_TITLE
         self._currentLineSet = self._currentTree.title.splitlines( )
      elif self._searchArticles:
         self._subject = ForewardFinder.SCANNING_ARTICLE
         self._currentLineSet = self._currentTree.article.splitlines( )
      
      self._currentLineNo = 0
      self._currentColumn = 0
   
   def __iter__( self ):
      return self
   
   def next( self ):
      while True:
         try:
            slice = self._scan( )
            return ( self._currentPath, self._subject, self._currentLineNo, slice[0], slice[1] )
         except:
            if (self._subject == ForewardFinder.SCANNING_TITLE) and self._searchArticles:
               self._subject = ForewardFinder.SCANNING_ARTICLE
            else:
               self._currentTree, self._currentPath = self._iter.next( )
               if self._searchTitles:
                  self._subject = ForewardFinder.SCANNING_TITLE
               else:
                  self._subject = ForewardFinder.SCANNING_ARTICLE
            
            if self._subject == ForewardFinder.SCANNING_TITLE:
               self._currentLineSet = self._currentTree.title.splitlines( )
            else:
               self._currentLineSet = self._currentTree.article.splitlines( )
            
            self._currentLineNo = 0
            self._currentColumn = 0
   
   def _scan( self ):
      while True:
         match = self._pattern.search( self._currentLineSet[ self._currentLineNo ], self._currentColumn )
         if match is not None:
            slice = match.span( )
            self._currentColumn = slice[1]
            return slice
         
         self._currentLineNo += 1



class TreeEditor( Tix.Frame ):
   CONFIG  = None

   def __init__( self, parent, application, **options ):
      Tix.Frame.__init__( self, parent, class_='TreeEditor' )
      
      # Initialize the instance data
      self._project          = None
      self._outline          = None
      self._treeDoc          = None
      self._currentEntry     = None
      
      self._treeView         = None
      self._articleView      = None
      self._entryWidget      = { }
      self._subtreePopup     = None
      
      self._application      = application
      self._clipboard        = application.getClipboard( )
      
      self._finder           = None
      
      self._drawWidget( ).pack( side=Tix.TOP, expand=1, fill=Tix.BOTH )

   @staticmethod
   def setupConfig( aConfig ):
      TreeEditor.CONFIG = aConfig
      ArticleEditor.CONFIG = aConfig
   
   # Content
   def clearModifiedFlag( self ):
      self._articleView.stext.text.edit_modified( False )

   def deleteTree( self ):
      try:
         if self._treeDoc is None:
            return
         
         self._fileName         = ''
         self._treeDoc          = None
         
         self._treeView.hlist.delete_all( )
         self._entryWidget      = { }
         self._currentEntry     = None
      except:
         exceptionPopup( )

   def setModel( self, aProject ):
      try:
         # Update and Validate the new model
         treeDoc, styles = aProject.data._tree, aProject.data._styles
         project = aProject
         outline = aProject.data
         
         outline.validateModel( )
         outline.updateModel( )
         
         # Remove the old
         self.deleteTree( )
         self._articleView.stext.reinitialize( styles )
         
         # install the new
         self._project = project
         self._outline = outline
         self._styles  = styles
         self._treeDoc = treeDoc
         
         if not treeDoc.hasChildren( ):
            self._treeDoc.insert( Tree(), TreePath(), Tree.CHILD )
         
         self._buildTreeView( )
         
         # Make the first tree entry the current
         pathToFirst = TreePath(self._treeDoc.children()[0].id)
         self.setCurrentSubtree( pathToFirst )
         
         self.collapse( )
      except:
         exceptionPopup( )

   def commit( self, entryPath=None ):
      # Get the path to the item to be committed
      if entryPath is None:
         if self._currentEntry:
            theListPath = self._currentEntry
         else:
            return
      else:
         theListPath = entryPath
      
      # Locate the relevant entry and article widgets
      entryWidget   = self._entryWidget[ theListPath.child( ) ]
      articleWidget = self._articleView
      
      # Commit the values
      try:
         modified = entryWidget.commit( articleWidget )
      except:
         print 'Error committing current article.'
         raise
      
      if modified:
         self.event_generate( '<<Modified>>' )
   
   # Primitive Operations
   def insertSubtree( self, aSubtree, refPath=None, relation=Tree.BEFORE ):
      assert isinstance( aSubtree,    Tree     )
      assert isinstance( refPath,     TreePath ) or ( refPath is None )
      assert isinstance( relation,    int      )
      
      try:
         if refPath is None:
            theRefPath = self._currentEntry
         else:
            theRefPath = refPath
         
         self._treeDoc.insert( aSubtree, theRefPath, relation )
         
         if relation in [ Tree.BEFORE, Tree.AFTER ]:
            newSubtreePath = theRefPath.parentPath( ) + aSubtree.id
         else:
            newSubtreePath = theRefPath + aSubtree.id
         
         self._buildSubtreeView( newSubtreePath )
         self.setCurrentSubtree( newSubtreePath )
      except:
         exceptionPopup( )
   
   def deleteSubtree( self, path=None ):
      try:
         if path is None:
            thePath = self._currentEntry
         else:
            thePath = path
         
         docEntry = self._treeDoc.subtree( thePath )
         if docEntry is self._treeDoc:
            raise Exception( "Cannot delete the root." )
         elif len(thePath.parentPath( )) == 0:   # If the parent is the root
            if len(self._treeDoc.children()) == 1:   # If we're the only subtree of root.
               raise Exception( "Cannot delete the only child of root." )
         
         # Determine the next subtree to be set as current
         if self._currentEntry and (thePath != self._currentEntry):
            newCurrent = self._currentEntry
         else:
            try:
               newCurrent = self._treeDoc.nextSiblingPath( thePath )
            except:
               try:
                  newCurrent = self._treeDoc.previousSiblingPath( thePath )
               except:
                  newCurrent = thePath.parentPath( )
         
         # Delete the subtree form the view
         self._treeView.hlist.delete_entry( thePath )
         
         # Delete the references to the TreeViewEntry widgets
         docEntry = self._treeDoc.subtree( thePath )
         for subtree, subtreePath in ForewardTreeIterator(docEntry):
            del self._entryWidget[ subtree.id ]
         
         # Delete the subtree from the document
         self._treeDoc.remove( thePath )
         
         # Adjust parent's indicator in the tree control
         parentPath = thePath.parentPath()
         parentTree = self._treeDoc.subtree( parentPath )
         if not parentTree.hasChildren( ):
            self._treeView.setmode( parentPath, 'none' )
         
         # Notify the app that the doc has been modified
         self.event_generate( '<<Modified>>' )
         
         # Make the new Current Path Active
         try:
            self.setCurrentSubtree( newCurrent )
         except:
            pass
      except:
         exceptionPopup( )
   
   def moveSubtree( self, itemPath, destRefPath=None, relation=Tree.BEFORE ):
      '''Where only one or neither of: before or after is specified.  Whichever is
      provided, it must provide a sibling id.  If neither is specified, the
      object is appended to parent's subtree list.
      '''
      try:
         # Get a reference to the subtree to be moved
         itemDoc = self._treeDoc.subtree( itemPath )
         
         # Create a copy of the itemPath entry with a new id.
         #newItemDoc = Tree( title=itemDoc.title, article=itemDoc.article, subtrees=itemDoc.subtrees )
            # Now there are two Tree instances that refer to the same tree but have differen id's.
         
         # Determine the subtree's new path
         if relation == Tree.CHILD:
            parentPath = destRefPath
         else:
            parentPath = destRefPath.parentPath()
         
         theNewPath = parentPath + itemDoc.id
         
         # Move the subtree
         self.commit( )
         
         self.deleteSubtree( itemPath )
         self.insertSubtree( itemDoc, destRefPath, relation )
      except:
         exceptionPopup( )

   def setCurrentSubtree( self, path ):
      assert isinstance( path, TreePath ) or ( path is None )
      
      try:
         self.commit( )
      except:
         pass
      
      # Set path as the new current entry
      if path is not None:
         # Insure entry is visible
         parentPath = path.parentPath( )
         while len(parentPath) > 0:
            self._treeView.open(parentPath)
            parentPath.pop( )
         
         self._treeView.hlist.see( path )
         
         # Move the selection to the new entry in the tree view
         self._treeView.hlist.selection_clear( )
         self._treeView.hlist.selection_set( path )
         self._treeView.hlist.anchor_set( path )
         entryWidget = self._entryWidget[ path.child( ) ]
         
         # Load the article into the article view
         try:
            self._articleView.stext.unbind( '<<Modified>>' )
         except:
            pass
         
         try:
            entryWidget.update( self._articleView, True )
         except:
            print 'Error while updating display.  Data integrity failure.'
            raise
         
         entryWidget.focus_set( )
         self._articleView.stext.bind( '<<Modified>>', self.onNoteModified )
      
      # Record the new current subtree path
      self._currentEntry = path
   
   def copySubtree( self, path=None, removeFromDocument=False ):
      try:
         if path is None:
            theCopy = copy.copy( self._treeDoc.subtree( self._currentEntry ) )
         else:
            theCopy = copy.copy( self._treeDoc.subtree( path ) )
         
         self._clipboard.set( theCopy )
         
         if removeFromDocument:
            self.deleteSubtree( path )
      except:
         exceptionPopup( )

   def pasteCopiedSubtree( self, refPath=None, relation=Tree.AFTER ):
      try:
         theCopy = self._clipboard.get()
         theCopy.fixIds()
         self.insertSubtree( theCopy, refPath, relation )
      except:
         exceptionPopup( )

   # Derived Editing Operations
   def newSubtree( self, refPath=None, relation=Tree.BEFORE ):
      assert isinstance( refPath,   TreePath ) or ( refPath is None )
      assert isinstance( relation,  int      )
      
      try:
         self.insertSubtree( Tree( ), refPath, relation )
      except:
         exceptionPopup( )

   def undo( self ):
      pass
   
   def redo( self ):
      pass
   
   def cut( self ):
      try:
         focusWidget  = self.focus_get( )
         focusWidget.event_generate('<Control-x>')
         #self.clipboard_append( 'test' )
      except:
         exceptionPopup( )

   def copy( self ):
      try:
         focusWidget  = self.focus_get( )
         focusWidget.event_generate('<Control-c>')
         #self.clipboard_append( 'test' )
      except:
         exceptionPopup( )

   def paste( self ):
      try:
         focusWidget  = self.focus_get( )
         focusWidget.event_generate('<Control-v>')
         #data = root.selection_get(selection="CLIPBOARD")
      except:
         exceptionPopup( )

   def selectAll( self ):
      try:
         self._articleView.text.focus_set( )
         self._articleView.text.tag_add( Tix.SEL, '1.0', Tix.END )
      except:
         exceptionPopup( )

   def replace( self, pattern, newStr, path, recursive ):
      assert isinstance( pattern,    (str,unicode) )
      assert isinstance( newStr,     (str,unicode) )
      assert isinstance( path,       TreePath      )
      assert isinstance( recursive,  bool          )
      pass
   
   def indentSubtree( self, path=None ):
      '''Make the entry indicated by path, the first child of path's
      predecessor sibling.  If such a sibling does not exist, do nothing.
      '''
      try:
         if path is None:
            thePath = self._currentEntry
         else:
            thePath = path
         
         entryMode = self._treeView.getmode( thePath )
         
         try:
            predPath = self._treeDoc.previousSiblingPath( thePath )
         except:
            return
         
         newParentPath        = predPath
         newParentDoc         = self._treeDoc.subtree(newParentPath)
         
         if len(newParentDoc.subtrees) == 0:
            self.moveSubtree( thePath, newParentPath, Tree.CHILD )
         
         if entryMode == 'open':
            newEntryPath = newParentPath + thePath.child( )
            self._treeView.close( newEntryPath )
      except:
         exceptionPopup( )
   
   def deindentSubtree( self, path=None ):
      '''Make the entry indicated by path, the successor sibling of path's
      parent.
      '''
      try:
         if path is None:
            thePath = self._currentEntry
         else:
            thePath = path
         
         entryMode = self._treeView.getmode( thePath )
         
         parentPath           = thePath.parentPath( )
         parentDoc            = self._treeDoc.subtree( parentPath )
         
         if len(parentDoc.subtrees) != 1:
            self.after( 1, CALLBACK( self.setCurrentSubtree, thePath ) )
            return
         
         newParentPath = parentPath.parentPath( )
         newPredPath   = parentPath
         
         self.moveSubtree( thePath, parentPath, Tree.AFTER )
         
         if entryMode == 'open':
            newEntryPath = newParentPath + thePath.child( )
            self._treeView.close( newEntryPath )
      except:
         exceptionPopup( )

   def moveSubtreeUp( self, path=None ):
      try:
         if path is None:
            thePath = self._currentEntry
         else:
            thePath = path
         
         try:
            predPath = self._treeDoc.previousSiblingPath( thePath )
         except:
            return
         
         self.moveSubtree( thePath, predPath, Tree.BEFORE )
      except:
         exceptionPopup( )
   
   def moveSubtreeDown( self, path=None ):
      try:
         if path is None:
            thePath = self._currentEntry
         else:
            thePath = path
         
         try:
            succPath = self._treeDoc.nextSiblingPath( thePath )
         except:
            return
         
         self.moveSubtree( thePath, succPath, Tree.AFTER )
      except:
         exceptionPopup( )
   
   def insertNewSubtreeAfterCurrent( self, pathToCurrent=None ):
      try:
         if pathToCurrent is None:
            pathToCurrent = self._currentEntry
         
         mode = self._treeView.getmode( pathToCurrent )
         
         if mode == 'close':
            self.newSubtree( pathToCurrent, Tree.CHILD )
         else:
            self.newSubtree( pathToCurrent, Tree.AFTER )
      except:
         exceptionPopup( )
   
   # Derived Non-Mutating Operations
   def moveUp( self ):
      try:
         x1,y1,x2,y2 = self._treeView.hlist.info_bbox( self._currentEntry )
         
         prevEntryY = y1 - 1
         
         if prevEntryY < 0:
            try:
               self._treeView.hlist.yview_scroll( -1, 'units' )
               
               x1,y1,x2,y2 = self._treeView.hlist.info_bbox( self._currentEntry )
               prevEntryY = y1 - 1
            except:
               pass
         
         if prevEntryY >= 0:
            prevEntryPath = self._treeView.hlist.nearest( prevEntryY )
            if len(prevEntryPath) > 0:
               self.setCurrentSubtree( TreePath(prevEntryPath) )
      except:
         exceptionPopup( )
   
   def moveDown( self ):
      try:
         x1,y1,x2,y2 = self._treeView.hlist.info_bbox( self._currentEntry )
         
         nextEntryY = y2 + 1
         maxY = self._treeView.winfo_height( )
         
         if nextEntryY > maxY:
            try:
               self._treeView.hlist.yview_scroll( 1, 'units' )
               
               x1,y1,x2,y2 = self._treeView.hlist.info_bbox( self._currentEntry )
               nextEntryY = y2 + 1
            except:
               pass
         
         if nextEntryY >= 0:
            nextEntryPath = self._treeView.hlist.nearest( nextEntryY )
            if len(nextEntryPath) > 0:
               self.setCurrentSubtree( TreePath(nextEntryPath) )
      except:
         exceptionPopup( )
   
   def setupFind( self, expr ):
      try:
         self._finder = ForewardFinder( self._treeDoc, expr )
      except:
         exceptionPopup( )

   def findNext( self ):
      try:
         return self._finder.next( )
      except:
         exceptionPopup( )

   def expand( self, path=None, depth=0 ):
      """Open one or more tree branches indicated by path. If depth is 0,
      the entry specified by path and its entire subtree is opened.  If depth
      is positive, the subtree is expanded to the given depth.
      """
      assert isinstance( path,     TreePath ) or ( path is None )
      assert isinstance( depth,    int      )
      
      try:
         if path is None:
            root = self._treeDoc
         else:
            root = self._treeDoc.subtree( path )
         
         if depth > 0:
            for subtree,iPath in ForewardTreeIterator( root ):
               if (len(iPath) <= depth) and (len(iPath) > 0) and subtree.hasChildren():
                  self._treeView.open( iPath )
         else:
            for subtree,iPath in ForewardTreeIterator( root ):
               if (len(iPath) > 0) and subtree.hasChildren():
                  self._treeView.open( iPath )
      except:
         exceptionPopup( )

   def collapse( self, path=None, depth=0 ):
      """Close one or more tree branches indicated by path.f depth is 0,
      the entry specified by path and its entire subtree is closed.  If depth
      is positive, the subtree is closed to the given depth.
      """
      assert isinstance( path,     TreePath ) or ( path is None )
      assert isinstance( depth,    int      )
      
      try:
         if path is None:
            root = self._treeDoc
            rootPath = TreePath()
         else:
            root = self._treeDoc.subtree( path )
            rootPath = path
         
         if depth > 0:
            for subtree,iPath in ForewardTreeIterator( root ):
               if (len(iPath) <= depth) and (len(iPath) > 0) and subtree.hasChildren():
                  self._treeView.close( iPath )
         else:
            for subtree,iPath in ForewardTreeIterator( root ):
               entryPath = rootPath + iPath
               if (len(entryPath) > 0) and subtree.hasChildren():
                  self._treeView.close( entryPath )
      except:
         exceptionPopup( )

   # GUI Rendering
   def subtreePopup( self, evt, path ):
      try:
         self.setCurrentSubtree( path )
         self._subtreePopup.post( evt.x_root, evt.y_root )
      except:
         exceptionPopup( )

   def menus( self, master, *args, **kwargs ):
      try:
         self._subtreePopup = Tix.Menu( master )
         menuItem( self._subtreePopup, 'Cu&t Branch',                   CALLBACK( self.copySubtree,        None, True         ) )
         menuItem( self._subtreePopup, '&Copy Branch',                  CALLBACK( self.copySubtree,        None, False        ) )
         menuItem( self._subtreePopup, 'Paste Branch &Before',          CALLBACK( self.pasteCopiedSubtree, None, Tree.BEFORE  ) )
         menuItem( self._subtreePopup, 'Paste Branch &After',           CALLBACK( self.pasteCopiedSubtree, None, Tree.AFTER   ) )
         menuItem( self._subtreePopup, 'Paste Branch As &Child',        CALLBACK( self.pasteCopiedSubtree, None, Tree.CHILD   ) )
         self._subtreePopup.add_separator( )
         menuItem( self._subtreePopup, 'E&xpand All',                   self.expand                                   )
         menuItem( self._subtreePopup, 'C&ollapse All',                 self.collapse                                 )
         self._subtreePopup.add_separator( )
         menuItem( self._subtreePopup, 'Indent',                        self.indentSubtree,   'Shift-Right, Tab'      )
         menuItem( self._subtreePopup, 'Unindent',                      self.deindentSubtree, 'Shift-Left, Shift-Tab' )
         menuItem( self._subtreePopup, 'Move Up',                       self.moveSubtreeUp,   'Shift-Up'              )
         menuItem( self._subtreePopup, 'Move Down',                     self.moveSubtreeDown, 'Shift-down'            )
         self._subtreePopup.add_separator( )
         menuItem( self._subtreePopup, 'Add Sibling Before',            CALLBACK( self.newSubtree,   None, Tree.BEFORE  ) )
         menuItem( self._subtreePopup, 'Add Sibling After',             CALLBACK( self.newSubtree,   None, Tree.AFTER   ) )
         menuItem( self._subtreePopup, 'Add Child',                     CALLBACK( self.newSubtree,   None, Tree.CHILD   ) )
         
         articleMenu = Tix.Menu( master )
         menuItem( articleMenu,    '&Undo',                         self.undo,            'Ctrl-Z'                )
         menuItem( articleMenu,    '&Redo',                         self.redo,            'Ctrl-Y'                )
         articleMenu.add_separator( )
         menuItem( articleMenu,    'Cu&t',                          self.cut,             'Ctrl-X'                )
         menuItem( articleMenu,    '&Copy',                         self.copy,            'Ctrl-C'                )
         menuItem( articleMenu,    '&Paste',                        self.paste,           'Ctrl-V'                )
         articleMenu.add_separator( )
         menuItem( articleMenu,    'Select &All',                   self.selectAll,       'Ctrl-A'                )
         
         return [ ('Tree', self._subtreePopup), ('Article', articleMenu) ]
      except:
         exceptionPopup( )

   def _drawWidget( self ):
      try:
         workPane = Tix.PanedWindow( self, orientation=Tix.HORIZONTAL )
         
         outlinePane = workPane.add( 'outline', min=100 )
         articlePane = workPane.add( 'article',  min=100 )
         
         self._treeView = Tix.Tree( outlinePane, width=300 )
         TreeViewEntry.FONT = tkFont.Font( font=self.CONFIG.get( 'Editor', 'treeFont' ) )
         self._treeView.hlist.config( separator=TreePath.SEPARATOR, 
                                      selectmode=Tix.SINGLE, borderwidth=0, bg='white', browsecmd=self._onBrowse, indicatorcmd=self._onOpenCloseSubtree )
         self._treeView.pack( expand=1, fill=Tix.BOTH, padx=5 )
         TixTreeDnDInterface( self._treeView.hlist, self )
         
         articleFont = self.CONFIG.get( 'Editor', 'defaultArticleFont' )
         wrap        = self.CONFIG.get( 'Editor', 'defaultWrap' )
         spacing1    = self.CONFIG.get( 'Editor', 'defaultSpacing1' )
         spacing2    = self.CONFIG.get( 'Editor', 'defaultSpacing2' )
         spacing3    = self.CONFIG.get( 'Editor', 'defaultSpacing3' )
         self._articleView = ArticleEditor( articlePane, height=15, font=articleFont, wrap=wrap, spacing1=spacing1, spacing2=spacing2, spacing3=spacing3, undo=True, maxundo=0, autoseparators=True, exportselection=1 )
         self._articleView.stext.bind( '<<Modified>>', self.onNoteModified )
         self._articleView.pack( expand=1, fill=Tix.BOTH, padx=5 )
         
         return workPane
      except:
         exceptionPopup( )
         raise

   def _buildTreeView( self ):
      try:
         self._treeView.hlist.delete_all( )
         self._entryWidget = { }
         self._buildSubtreeListView( self._treeDoc.children() )
      except:
         exceptionPopup( )
         raise

   def _buildSubtreeListView( self, aTreeList, path=None ):
      assert isinstance( aTreeList, list )
      assert isinstance( path, TreePath ) or ( path is None )
      
      try:
         if path is None:
            thePath = TreePath( )
         else:
            thePath = path
         
         for tree in aTreeList:
            subpath = thePath + tree.id
            self._buildTreeViewEntry( subpath, tree )
            self._buildSubtreeListView( tree.subtrees, subpath )
      except:
         exceptionPopup( )
         raise

   def _buildSubtreeView( self, subtreePath ):
      assert isinstance( subtreePath, TreePath )
      
      try:
         # Do some path algebra
         parentDoc       = self._treeDoc.subtree( subtreePath.parentPath( ) )
         subtreeId       = subtreePath.child( )
         entryDoc        = parentDoc.subtree( TreePath(subtreeId) )
         
         # Identify where to insert the new subtree within the parent
         beforePath = None
         if parentDoc.subtrees[-1].id != subtreeId:
            subtreeDocIdx   = -1
            for idx in xrange( len(parentDoc.subtrees) - 1 ):
               if parentDoc.subtrees[idx].id == subtreeId:
                  subtreeDocIdx = idx
                  break
            
            if subtreeDocIdx == -1:
               raise Exception, 'Subtree does not exist'
            
            beforePath = subtreePath.parentPath( ) + parentDoc.subtrees[subtreeDocIdx+1].id
         
         self._buildTreeViewEntry( subtreePath, entryDoc, beforePath )
         self._buildSubtreeListView( entryDoc.subtrees, subtreePath )
         
         parentPath = subtreePath.parentPath()
         if len(parentPath) > 0:
            if self._treeView.getmode( parentPath ) == 'none':
               self._treeView.setmode( parentPath, 'close' )
      
      except:
         exceptionPopup( )

   def _buildTreeViewEntry( self, path, docEntry, before=None ):
      try:
         treeEntry = TreeViewEntry( self._treeView.hlist, docEntry )
         self._entryWidget[ docEntry.id ] = treeEntry
         
         # Label Bindings
         treeEntry.label.bind( '<Button-1>',             EVTCALLBACK2( self._treeView.hlist.dnd_start, Dragable(path), self.moveSubtree ) )
         treeEntry.label.bind( '<ButtonRelease-3>',      EVTCALLBACK2( self.subtreePopup,    path ) )
         
         # Entry Bindings
         treeEntry.entry.bind( '<Button-1>',             EVTCALLBACK( self.setCurrentSubtree,  path ) )
         treeEntry.entry.bind( '<KeyPress-Tab>',         EVTCALLBACK( self.indentSubtree,      path ) )
         treeEntry.entry.bind( '<Shift-KeyPress-Right>', EVTCALLBACK( self.indentSubtree,      path ) )
         treeEntry.entry.bind( '<Shift-KeyPress-Tab>',   EVTCALLBACK( self.deindentSubtree,    path ) )
         treeEntry.entry.bind( '<Shift-KeyPress-Left>',  EVTCALLBACK( self.deindentSubtree,    path ) )
         treeEntry.entry.bind( '<Shift-KeyPress-Up>',    EVTCALLBACK( self.moveSubtreeUp,      path ) )
         treeEntry.entry.bind( '<Shift-KeyPress-Down>',  EVTCALLBACK( self.moveSubtreeDown,    path ) )
         treeEntry.entry.bind( '<KeyPress-Up>',          EVTCALLBACK( self.moveUp                   ) )
         treeEntry.entry.bind( '<KeyPress-Down>',        EVTCALLBACK( self.moveDown                 ) )
         treeEntry.entry.bind( '<KeyPress-Return>',      EVTCALLBACK( self.insertNewSubtreeAfterCurrent, path ) )
         treeEntry.entry.bind( '<Control-KeyPress-b>',   EVTCALLBACK( self.deleteSubtree,      path ) )
         
         if before is None:
            self._treeView.hlist.add( path, itemtype=Tix.WINDOW, window=treeEntry )
         else:
            self._treeView.hlist.add( path, itemtype=Tix.WINDOW, window=treeEntry, before=before )
         
         if self._treeDoc.subtree( path ).hasChildren( ):
            self._treeView.setmode( path, 'close' )
      except:
         exceptionPopup( )

   def _isHidden( self, aPath ):
      assert isinstance( aPath, TreePath )
      
      try:
         thePath = copy.deepcopy(aPath)
         
         while len(thePath) > 0:
            hidden = self._treeView.hlist.info_hidden( thePath )
            if  hidden =='1':
               return True
            
            thePath = thePath.parentPath( )
         
         return False
      except:
         exceptionPopup( )

   # Event Handlers
   def _onBrowse( self, entryPath ):
      self.setCurrentSubtree( TreePath(entryPath) )

   def _onMouseWheel( self, event ):
      try:
         if event.delta < 0:
            self._treeView.yview_scroll( 1, 'units' )
         else:
            self._treeView.yview_scroll( -1, 'units' )
      except:
         exceptionPopup( )

   def _onOpenCloseSubtree( self, entryPath ):
      clickPath = TreePath( entryPath )
      
      try:
         self._treeView.hlist.config( indicatorcmd='' )
         
         currentMode = self._treeView.getmode( clickPath )
         
         if currentMode == 'open':
            self._treeView.open( clickPath )
         else:
            self._treeView.close( clickPath )
         
         self.after( 350, self._registerOpenCloseCallback )
         self.setCurrentSubtree( clickPath )
      except:
         exceptionPopup( )

   def _registerOpenCloseCallback( self ):
      try:
         self._treeView.hlist.config( indicatorcmd=self._onOpenCloseSubtree )
      except:
         exceptionPopup( )

   def onNoteModified( self, event=None ):
      try:
         self.event_generate( '<<Modified>>' )
      except:
         exceptionPopup( )


