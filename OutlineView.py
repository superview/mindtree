from PyQt4 import QtCore, QtGui
from OutlineModel import OutlineModel, TreeNode
from ApplicationFramework import RES

from utilities import *


class OutlineView_Delegate( QtGui.QItemDelegate ):
   def __init__( self, parent ):
      QtGui.QItemDelegate.__init__( self, parent )
   
   def createEditor( self, parent, option, index ):
      editor = QtGui.QItemDelegate.createEditor( self, parent, option, index )
      editor.installEventFilter( self.parent() )
      return editor
   
   def setEditorData( self, editor, index ):
      editor.setText( index.internalPointer().data(0) )
   
   def setModelData( self, editor, model, index ):
      model.setData( index, editor.text(), QtCore.Qt.DisplayRole )
   

class OutlineViewWidget( QtGui.QTreeView ):
   '''Emits: entryRightClicked(QPoint,QModelIndex)'''
   def __init__( self, parent ):
      QtGui.QTreeView.__init__( self, parent )
      
      alternatingRowColors = RES.getboolean('OutlineView','alternatingRowColors')
      
      # Drag and Drop
      self.setDragEnabled( True )
      self.setAcceptDrops( True )
      #self.setDropIndicatorShown( True )
      self.setDragDropMode( QtGui.QAbstractItemView.InternalMove )
      
      # Entry Editing
      self.setItemDelegate( OutlineView_Delegate(self) )
      self.setEditTriggers( QtGui.QAbstractItemView.SelectedClicked |
                            QtGui.QAbstractItemView.CurrentChanged )
      
      # Appearance
      self.setAlternatingRowColors( alternatingRowColors )
      self.setUniformRowHeights(True)
      
      # Behavior Settings
      self.setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
      self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
      self.setSortingEnabled(False)
      self.setTabKeyNavigation(False)
      
      # Drag and Drop Cursors
      self.insertBefore_cursor  = RES.getDragCursor('OutlineView','DnD_insertBeforeCursor')
      self.insertAfter_cursor   = RES.getDragCursor('OutlineView','DnD_insertAfterCursor')
      self.insertChild_cursor   = RES.getDragCursor('OutlineView','DnD_insertChildCursor')

   def eventFilter( self, obj, event ):
      if isinstance(obj,QtGui.QLineEdit) and (event.type() == QtCore.QEvent.KeyPress):
         keyEvent = event
         if keyEvent.key() == QtCore.Qt.Key_Tab:
            if keyEvent.modifiers() == QtCore.Qt.ShiftModifier:
               self.parent().dedentNode()
            else:
               self.parent().indentNode()
            
            return True  # disallow target from handling the event.
         
         elif keyEvent.key() == QtCore.Qt.Key_Left:
            if keyEvent.modifiers() == QtCore.Qt.ControlModifier:
               self.parent().dedentNode()
               return True
      
         elif keyEvent.key() == QtCore.Qt.Key_Right:
            if keyEvent.modifiers() == QtCore.Qt.ControlModifier:
               self.parent().indentNode()
               return True
      
         elif keyEvent.key() == QtCore.Qt.Key_Up:
            if keyEvent.modifiers() == QtCore.Qt.ControlModifier:
               self.parent().moveNodeUp()
               return True
      
         elif keyEvent.key() == QtCore.Qt.Key_Down:
            if keyEvent.modifiers() == QtCore.Qt.ControlModifier:
               self.parent().moveNodeDown()
               return True
      
      return False
   
   def keyboardPressEvent( self, keyEvent ):
      if keyEvent.key() == QtCore.Qt.Key_Tab:
         if keyEvent.modifiers() == QtCore.Qt.ShiftModifier:
            self.parent().dedentNode()
         else:
            self.parent().indentNode()

   def _buildGui( self ):
      pass
   
   def _buildWidgets( self ):
      pass

   def _defineActions( self ):
      pass
   
   def _buildMenus( self ):
      pass
   
   def _buildToolbars( self ):
      pass
   
   # Drag and Drop
   def mousePressEvent( self, event ):
      if event.button() == QtCore.Qt.RightButton:
         point = event.pos()
         index = self.indexAt( point )
         self.emit( QtCore.SIGNAL('entryRightClicked(QPoint,QModelIndex)'), event.globalPos(), index )
      else:
         import copy
         if event.button() == QtCore.Qt.LeftButton:
            self._dragStartPosition = copy.copy( event.pos() )
            print( 'Clicked {0}'.format(self._dragStartPosition) )
         
         QtGui.QTreeView.mousePressEvent( self, event )

   def mouseMoveEvent( self, event ):
      # Are we doing a drag?
      if not (event.buttons() & QtCore.Qt.LeftButton):
         return
      
      if (event.pos() - self._dragStartPosition).manhattanLength() < QtGui.QApplication.startDragDistance():
         return
      
      # Encode the node and stuff it into a drag object
      dragStartIndex = self.indexAt( self._dragStartPosition )
      mimeData = self.model().mimifyNode( dragStartIndex )
      self.drag = QtGui.QDrag( self )
      self.drag.setMimeData( mimeData )
      
      # Execute the drag (this is blocking)
      dropAction = self.drag.exec_( QtCore.Qt.MoveAction )
      
      # If the drag was successful, remove the node
      if dropAction == QtCore.Qt.MoveAction:
         self.model().removeNode( dragStartIndex )

   def dragMoveEvent( self, event ):
      index,relation = self._dnd_insertionPos( event )
      self.setSelection( QtCore.QRect( event.pos(), event.pos() ), QtGui.QItemSelectionModel.ClearAndSelect )
      self._selectCursor( relation )

   def dragEnterEvent( self, event ):
      print( 'Entered' )
      if event.mimeData().hasFormat( RES.get('OutlineView','nodeMimeType') ):
         event.acceptProposedAction( )

   def dragLeaveEvent( self, event ):
      QtGui.QTreeView.dragLeaveEvent( self, event )

   def dropEvent( self, event ):
      if event.source() is self:
         if event.possibleActions() & QtCore.Qt.MoveAction:
            event.acceptProposedAction()
            
            print( 'Dropping' )
            # Determine the drop location
            point = event.pos()
            index = self.indexAt( point )
            
            newParent = index.parent()
            if newParent is None:
               newParent = QtCore.QModelIndex()
            
            newRow = index.row()
            
            # Extract the node
            mimeData = event.mimeData()
            if not mimeData.hasFormat( RES.get('OutlineView','nodeMimeType') ):
               return
            
            node = self.model().demimifyNode(mimeData)
            
            # Insert the node
            self.model().insertNode( newParent, newRow, node )

   def _dnd_insertionPos( self, evt ):
      # Find the closest entry to the mouse
      mousePos               = evt.pos()
      indexOfentryUnderMouse = self.indexAt( mousePos )
      
      # Is the cursur above or below the midpoint of this entry
      rectOfEntryUnderMouse  = self.visualRect( indexOfentryUnderMouse )
      min_y = rectOfEntryUnderMouse.y()
      max_y = min_y + rectOfEntryUnderMouse.height()
      mid_y = (min_y + max_y) / 2
      if mousePos.y() <= mid_y:
         # Before
         return ( indexOfentryUnderMouse, 'before' )
      else:
         # After (may be sibling or child)
         if mousePos.x() >= rectOfEntryUnderMouse.x() + RES.getint('OutlineView','DnD_siblingChildBound'):
            return ( indexOfentryUnderMouse, 'child' )
         else:
            return ( indexOfentryUnderMouse, 'after' )

   def _selectCursor( self, rel ):
      if rel == 'before':
         cursor = self.insertBefore_cursor
         statusTip = 'Drop before'
      elif rel == 'after':
         cursor = self.insertAfter_cursor
         statusTip = 'Drop after'
      else:
         cursor = self.insertChild_cursor
         statusTip = 'Drop as child'
      
      self.setStatusTip( statusTip )
      self.drag.setDragCursor( cursor[0], QtCore.Qt.CopyAction + QtCore.Qt.MoveAction )
      self.drag.setHotSpot( cursor[1] )
      print( 'Updatable: {0}'.format(self.updatesEnabled()) )
      self.repaint()
      self.update()
      self.window().repaint()
      self.window().update()


class ArticleViewWidget( QtGui.QTextEdit ):
   def __init__( self, parent ):
      QtGui.QTextEdit.__init__( self, parent )
      self._buildGui( )

   def getFixedMenus( self ):
      return [ self.menuArticle ]
   
   def getToolbars( self ):
      return [ self._articletoolbar, self._edittoolbar, self._styleToolbar ]
   
   def editUndo( self ):
      pass
   
   def editRedo( self ):
      pass

   def articleCut( self ):
      pass
   
   def articleCopy( self ):
      pass
   
   def articlePaste( self ):
      pass
   
   def articleSelectAll( self ):
      pass

   def textStyleBold( self ):
      isBold = self._articleView.fontWeight()
      if isBold == QtGui.QFont.Bold:
         self._articleView.setFontWeight( QtGui.QFont.Normal )
      else:
         self._articleView.setFontWeight( QtGui.QFont.Bold )
   
   def textStyleItalic( self ):
      isItalic = self._articleView.fontItalic()
      self._articleView.setFontItalic( not isItalic )
   
   def textStyleUnderline( self ):
      isUnderlined = self._articleView.fontUnderline()
      self._articleView.setFontUnderline( not isUnderlined )
   
   def textStyleOverstrike( self ):
      pass
   
   def _buildGui( self ):
      self._buildWidgets( )
      self._defineActions( )
      self._buildMenus( )
      self._buildToolbars( )
   
   def _buildWidgets( self ):
      pass

   def _defineActions( self ):
      self.editUndoAction            = RES.installAction( 'editUndo',          self )
      self.editRedoAction            = RES.installAction( 'editRedo',          self )
      self.articleCutAction          = RES.installAction( 'articleCut',        self )
      self.articleCopyAction         = RES.installAction( 'articleCopy',       self )
      self.articlePasteAction        = RES.installAction( 'articlePaste',      self )
      self.articleSelectAllAction    = RES.installAction( 'articleSelectAll',  self )
      self.textBoldAction            = RES.installAction( 'textStyleBold',     self )
      self.textItalicAction          = RES.installAction( 'textStyleItalic',   self )
      self.textUnderlineAction       = RES.installAction( 'textStyleUnderline',self )
      self.textOverstrikeAction      = RES.installAction( 'textStyleOverstrike',self )
   
   def _buildMenus( self ):
      self.menuArticle = QtGui.QMenu(self)
      self.menuArticle.setObjectName("menuArticle")
      self.menuArticle.setTitle(QtGui.QApplication.translate("MainWindow", "Article", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuArticle.addAction( self.articleCutAction )
      self.menuArticle.addAction( self.articleCopyAction )
      self.menuArticle.addAction( self.articlePasteAction )
      self.menuArticle.addSeparator()
      self.menuArticle.addAction( self.articleSelectAllAction )
   
   def _buildToolbars( self ):
      self._articletoolbar = QtGui.QToolBar( 'articleEditingToolbar', self )
      self._articletoolbar.addAction( self.articleCutAction )
      self._articletoolbar.addAction( self.articleCopyAction )
      self._articletoolbar.addAction( self.articlePasteAction )
     
      self._edittoolbar = QtGui.QToolBar( 'editToolbar', self )
      self._edittoolbar.addAction( self.editUndoAction )
      self._edittoolbar.addAction( self.editRedoAction )
      
      self._styleToolbar = QtGui.QToolBar( 'textStyleToolbar', self )
      self._fontCombo = QtGui.QFontComboBox( self )
      self._styleToolbar.addWidget( self._fontCombo )
      self._styleToolbar.addAction( self.textBoldAction )
      self._styleToolbar.addAction( self.textItalicAction )
      self._styleToolbar.addAction( self.textUnderlineAction )
      self._styleToolbar.addAction( self.textOverstrikeAction )


class OutlineView(QtGui.QSplitter):
   '''Emits: QtCore.SIGNAL("modelChanged()")'''
   def __init__( self, parent ):
      QtGui.QSplitter.__init__( self, parent )
      
      self._outlineView            = None      # The TreeView widget
      self._articleView            = None      # The TextEdit widget
      self._model                  = None      # The model for the data
      self._currentArticleModified = False     # Has the article currently being edited been modified?
      
      self._buildGui( )

   def getFixedMenus( self ):
      menus = [ self.menuTree ]
      menus.extend( self._articleView.getFixedMenus() )
      return menus

   def getToolbars( self ):
      toolbars = [ self._treetoolbar ]
      toolbars.extend( self._articleView.getToolbars() )
      return toolbars
   
   # Basic Operations
   def setModel( self, aModel ):
      self._model = aModel
      self.swappingArticle = False
      
      self._articleView.clear( )
      
      try:
         # Update and Validate the new model
         aModel.validate( )
         
         self._outlineView.setModel( aModel )
         
         QtCore.QObject.connect( self._outlineView.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged )
         QtCore.QObject.connect( self._model, QtCore.SIGNAL( 'dataChanged(QModelIndex,QModelIndex)' ), self.onModelChanged )
         QtCore.QObject.connect( self._articleView, QtCore.SIGNAL( 'textChanged()' ), self.onArticleChanged )
      
      except:
         exceptionPopup( )
      
      indexOfFirst = aModel.index( 0, 0, QtCore.QModelIndex() )
      self.selectionChanged( indexOfFirst )

   def getModel( self ):
      return self._model

   def commitChanges( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex( )
      
      if self._currentArticleModified:
         theDocument = self._articleView.document()
         
         if theDocument.isEmpty():
            article     = ''
         else:
            article     = unicode( theDocument.toHtml() )
         
         index.internalPointer().setArticle( article )

   def insertNode( self, newParentIndex, newRow, newNode=None ):
      try:
         self._model.insertNode( newParentIndex, newRow, newNode )
         self._outlineView.setCurrentIndex( self._model.index(newRow, 0, newParentIndex) )
         self.onModelChanged()
      except:
         exceptionPopup( )
   
   def deleteNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self._model.removeNode( index )
         self.onModelChanged()
      except:
         exceptionPopup()

   def moveNode( self, index, newParentIndex, newRow ):
      try:
         self._model.moveNode( index, newParentIndex, newRow )
         self._outlineView.setCurrentIndex( self._model.index(newRow, 0, newParentIndex) )
         self.onModelChanged()
      except:
         exceptionPopup()

   def expandAll( self ):
      try:
         self._outlineView.expandAll( )
      except:
         exceptionPopup()

   def expandNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self._outlineView.expand( self._outlineView.currentIndex() )
      except:
         exceptionPopup()

   def collapseAll( self ):
      try:
         self._outlineView.collapseAll( )
      except:
         exceptionPopup()

   def collapseNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self._outlineView.collapse( self._outlineView.currentIndex() )
      except:
         exceptionPopup()

   # Advanced Operations (built on top of Basic Operations)
   def selectionChanged( self, newSelection, oldSelection=None ):
      # Save the currently active article
      self.swappingArticle = True
      
      if oldSelection:
         if isinstance( oldSelection, QtCore.QModelIndex ):
            index = oldSelection
         else:
            indexes = oldSelection.indexes()
            if indexes and (len(indexes) > 0):
               index = indexes[0]
            else:
               index = None
         
         if index:
            self.commitChanges( index )
      
      # Reinitialize the article widget
      self._articleView.clear( )
      
      # Display the newly selected article
      if newSelection:
         self._currentArticleModified = False
         if isinstance( newSelection, QtCore.QModelIndex ):
            index = newSelection
         else:
            indexes = newSelection.indexes()
            if indexes and (len(indexes) > 0):
               index = indexes[0]
            else:
               index = None
         
         if index:
            outlineNode = index.internalPointer( )
            
            if outlineNode is not None:
               self._articleView.setHtml( outlineNode.article() )
      
      self.swappingArticle = False

   def insertNodeBefore( self, index=None, node=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self.insertNode( index.parent(), index.row(), node )
      except:
         exceptionPopup()

   def insertNodeAfter( self, index=None, node=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self.insertNode( index.parent(), index.row() + 1, node )
      except:
         exceptionPopup()

   def insertNodeAsChild( self, index=None, node=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self.insertNode( index, 0, node )
      except:
         exceptionPopup()

   def indentNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         theNodeRow = index.row()
         if theNodeRow == 0:
            return
         
         theNewParent = index.sibling( index.row() - 1, 0 )
         if len(theNewParent.internalPointer()._childNodes) == 0:
            self.moveNode( index, theNewParent, 0 )
      except:
         exceptionPopup()

   def dedentNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         if len(index.parent().internalPointer()._childNodes) != 1:
            return
         
         newParent = index.parent().parent()
         newRow    = index.parent().row() + 1
         self.moveNode( index, newParent, newRow )
      except:
         exceptionPopup()

   def moveNodeUp( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         theRow = index.row()
         if theRow == 0:
            return
         
         self.moveNode( index, index.parent(), theRow - 1 )
      except:
         exceptionPopup()

   def moveNodeDown( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         theRow = index.row()
         if theRow == (len(index.internalPointer()._parentNode._childNodes)-1):
            return
         
         self.moveNode( index, index.parent(), theRow + 1 )
      except:
         exceptionPopup()

   def cutNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         mimeObject = self._model.mimifyNode( index )
         
         try:
            QtGui.QApplication.clipboard().setMimeData( mimeObject )
         except:
            return
         
         self.deleteNode( index )
      except:
         exceptionPopup()

   def copyNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         mimeObject = self._model.mimifyNode( index )
         
         QtGui.QApplication.clipboard().setMimeData( mimeObject )
      
      except:
         exceptionPopup()
   
   def pasteNodeBefore( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         mimeObject = QtGui.QApplication.clipboard().mimeData()
         if not mimeObject.hasFormat( RES.get('OutlineView','nodeMimeType') ):
            return
         
         node = self._model.demimifyNode( mimeObject )
         self.insertNodeBefore( index, node )
      except:
         exceptionPopup( )

   def pasteNodeAfter( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         mimeObject = QtGui.QApplication.clipboard().mimeData()
         if not mimeObject.hasFormat( RES.get('OutlineView','nodeMimeType') ):
            return
         
         node = self._model.demimifyNode( mimeObject )
         self.insertNodeAfter( index, node )
      except:
         exceptionPopup( )
   
   def pasteNodeAsChild( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         mimeObject = QtGui.QApplication.clipboard().mimeData()
         if not mimeObject.hasFormat( RES.get('OutlineView','nodeMimeType') ):
            return
         
         node = self._model.demimifyNode( mimeObject )
         self.insertNodeAsChild( index, node )
      except:
         exceptionPopup( )
   
   # Slots
   def onArticleChanged( self ):
      if not self.swappingArticle:
         self._currentArticleModified = True
         self.onModelChanged( )

   def onModelChanged( self, index1=None, index2=None ):
      self.emit( QtCore.SIGNAL('modelChanged()') )

   def entryRightClicked( self, point, index ):
      self._outlineView.setCurrentIndex( index )
      self.menuTree.popup(point)

   # GUI Construction
   def _buildGui( self ):
      self._buildWidgets( )
      
      self._defineActions( )
      
      self._buildMenus( )
      self._buildToolbars( )

   def _buildWidgets( self ):
      outlineFont = RES.getFont( 'OutlineView', 'Font' )
      articleFont = RES.getFont( 'ArticleView', 'Font' )
      
      self._outlineView = OutlineViewWidget(self)
      self._outlineView.setObjectName("outlineView")
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 0 )
      self._outlineView.setSizePolicy(sizePolicy)
      self._outlineView.setMinimumSize(QtCore.QSize(100, 100))
      self._outlineView.setSizeIncrement(QtCore.QSize(1, 1))
      self._outlineView.setFont( outlineFont )
      
      self._articleView = ArticleViewWidget(self)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 1 )
      self._articleView.setSizePolicy(sizePolicy)
      self._articleView.setMinimumSize(QtCore.QSize(100, 100))
      self._articleView.setFont( articleFont )
      self._articleView.setObjectName("articleView")
      
      QtCore.QObject.connect( self._outlineView, QtCore.SIGNAL('entryRightClicked(QPoint,QModelIndex)'), self.entryRightClicked )

   def _defineActions( self ):
      self.cutNodeAction             = RES.installAction( 'cutNode',           self )
      self.copyNodeAction            = RES.installAction( 'copyNode',          self )
      self.pasteNodeBeforeAction     = RES.installAction( 'pasteNodeBefore',   self )
      self.pasteNodeAfterAction      = RES.installAction( 'pasteNodeAfter',    self )
      self.pasteNodeAsChildAction    = RES.installAction( 'pasteNodeAsChild',  self )
      self.expandAllAction           = RES.installAction( 'expandAll',         self )
      self.collapseAllAction         = RES.installAction( 'collapseAll',       self )
      self.expandNodeAction          = RES.installAction( 'expandNode',        self )
      self.collapseNodeAction        = RES.installAction( 'collapseNode',      self )
      self.moveNodeUpAction          = RES.installAction( 'moveNodeUp',        self )
      self.moveNodeDownAction        = RES.installAction( 'moveNodeDown',      self )
      self.indentNodeAction          = RES.installAction( 'indentNode',        self )
      self.dedentNodeAction          = RES.installAction( 'dedentNode',        self )
      self.insertNewNodeBeforeAction = RES.installAction( 'insertNodeBefore',  self )
      self.insertNewNodeAfterAction  = RES.installAction( 'insertNodeAfter',   self )
      self.insertNewChildAction      = RES.installAction( 'insertNodeAsChild', self )
      self.deleteNodeAction          = RES.installAction( 'deleteNode',        self )
      

   def _buildMenus( self ):
      self.menuTree = QtGui.QMenu(self)
      self.menuTree.setObjectName("menuTree")
      self.menuTree.setTitle(QtGui.QApplication.translate("MainWindow", "Tree", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuTree.addAction( self.cutNodeAction )
      self.menuTree.addAction( self.copyNodeAction )
      self.menuTree.addAction( self.pasteNodeBeforeAction )
      self.menuTree.addAction( self.pasteNodeAfterAction )
      self.menuTree.addAction( self.pasteNodeAsChildAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self.expandAllAction )
      self.menuTree.addAction( self.collapseAllAction )
      self.menuTree.addAction( self.expandNodeAction )
      self.menuTree.addAction( self.collapseNodeAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self.insertNewNodeBeforeAction )
      self.menuTree.addAction( self.insertNewNodeAfterAction )
      self.menuTree.addAction( self.insertNewChildAction )
      self.menuTree.addAction( self.deleteNodeAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self.indentNodeAction )
      self.menuTree.addAction( self.dedentNodeAction )
      self.menuTree.addAction( self.moveNodeUpAction )
      self.menuTree.addAction( self.moveNodeDownAction )

   def _buildToolbars( self ):
      self._treetoolbar = QtGui.QToolBar( 'treeToolbar', self )
      self._treetoolbar.addAction( self.expandAllAction )
      self._treetoolbar.addAction( self.collapseAllAction )
