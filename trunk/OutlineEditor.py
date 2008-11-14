from PyQt4 import QtCore, QtGui
from OutlineModel import OutlineModel, TreeNode
import MTresources as RES

from utilities import *

# TODO
# - Implement Ctrl-Right to Indent a node
# - Implement Ctrl-Left to Dedent a node
# - Modify OutlineEntryEditor_Delegate to display icon.

class EntryEditor( QtGui.QWidget ):
   def __init__( parent ):
      pass
   
   def setText( self, text ):
      pass
   
   def setIcon( self, anIcon ):
      pass
   
   def getText( self ):
      pass


class OutlineEntryEditor_Delegate( QtGui.QItemDelegate ):
   def __init__( self, parent, outlineEditor ):
      self._entryEditor     = None
      self._outlineEditor   = outlineEditor
      
      QtGui.QItemDelegate.__init__( self, parent )

   def createEditor( self, parent, option, index ):
      if index.column() != 0:
         return None
      
      # Original
      #self._entryEditor = QtGui.QLineEdit( parent )
      #self._entryEditor.setFrame( False )
      #return self._entryEditor
      
      # New
      self.widget = QtGui.QWidget( parent )
      #self.box = QtGui.QHBoxLayout( self.widget )
      
      #self._label       = QtGui.QToolButton( self.widget )
      #self._label.setAutoRaise( True )
      
      self._entryEditor = QtGui.QLineEdit( self.widget )
      #self._entryEditor.setFrame( False )
      
      #self.box.addWidget( self._label       )
      #self.box.addWidget( self._entryEditor )
      #self.widget.setLayout( self.box )
      
      self.indentNodeAction            = QtGui.QAction( self._entryEditor )
      self.indentNodeAction.setObjectName( 'actionIndentNode' )
      self.indentNodeAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Right, QtCore.Qt.Key_Tab ] )
      QtCore.QObject.connect( self.indentNodeAction, QtCore.SIGNAL('triggered()'), self._outlineEditor.indentNode )
      
      self.dedentNodeAction            = QtGui.QAction( self._entryEditor )
      self.dedentNodeAction.setObjectName( 'actionDedentNode' )
      self.dedentNodeAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Left, QtCore.Qt.SHIFT + QtCore.Qt.Key_Tab ] )
      QtCore.QObject.connect( self.dedentNodeAction, QtCore.SIGNAL('triggered()'), self._outlineEditor.dedentNode )
      
      self.widget.setFocusProxy( self._entryEditor )
      return self.widget

   def setEditorData( self, editor, index ):
      # New
      #icon = index.model().data( index, QtCore.Qt.DecorationRole ).toPyObject()
      #self._label.setIcon( icon )
      
      # Original
      dataToEdit = index.internalPointer( ).data( 0 )
      self._entryEditor.setText( dataToEdit )

   def setModelData( self, editor, model, index ):
      newDataValue = self._entryEditor.text( )
      model.setData( index, newDataValue, QtCore.Qt.DisplayRole )

   def updateEditorGeometry( self, editor, option, index ):
      self._entryEditor.setGeometry( option.rect )

   def returnPressed( self ):
      self._outlineEditor.insertNewNodeAfter( )

class OutlineEditorWidget( QtGui.QTreeView ):
   def __init__( self, parent ):
      QtGui.QTreeView.__init__( self, parent )
      self.setAcceptDrops( True )

   def mousePressEvent( self, event ):
      if event.button() == QtCore.Qt.RightButton:
         point = event.pos()
         index = self.indexAt( point )
         self.emit( QtCore.SIGNAL('entryRightClicked(QPoint,QModelIndex)'), event.globalPos(), index )
      else:
         if event.button() == QtCore.Qt.LeftButton:
            self._dragStartPosition = event.pos()
            self._dragStartIndex    = self.indexAt( event.pos() )
         
         QtGui.QTreeView.mousePressEvent( self, event )

   def mouseMoveEvent( self, event ):
      if event.button() != QtCore.Qt.LeftButton:
         return
      
      if (event.pos() - self._dragStartPosition) < QtGui.QApplication.startDragDistance():
         return
      
      drag = QtGui.QDrag( self )
      mimeData = QtCore.QMimeData( )
      mimeData.setText( 'x' )
      drag.setMimeData( mimeData )
      
      dropAction = drag.exec_( )

   def dragEnterEvent( self ):
      pass

   def dropEvent( self ):
      pass


class OutlineEditor(QtGui.QSplitter):
   '''Emits: QtCore.SIGNAL("modelChanged()")'''
   def __init__( self, parent ):
      QtGui.QSplitter.__init__( self, parent )
      
      self._outlineView            = None      # The TreeView widget
      self._articleView            = None      # The TextEdit widget
      self._model                  = None      # The model for the data
      self._currentArticleModified = False     # Has the article currently being edited been modified?
      
      self._buildGui( )

   def getFixedMenus( self ):
      return ( self.menuTree, self.menuArticle )

   # Basic Operations
   def setModel( self, aModel ):
      self._model = aModel
      self.swappingArticle = False
      
      self._articleView.clear( )
      
      try:
         # Update and Validate the new model
         aModel.validateModel( )
         
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
            articleType = 'text'
         else:
            article     = unicode( theDocument.toHtml() )
            articleType = 'html'
         
         index.internalPointer().setArticle( article, articleType )

   def insertNode( self, newParentIndex, newRow, newNode=None ):
      try:
         self._model.insertNode( newParentIndex, newRow, newNode )
         self._outlineView.setCurrentIndex( self._model.index(newRow, 0, newParentIndex) )
         self.onModelChanged()
      except:
         exceptionPopup( )
   
   def deleteNode( self, nodeIndex=None ):
      try:
         if nodeIndex is None:
            nodeIndex = self._outlineView.currentIndex()
         
         self._model.removeNode( nodeIndex )
         self.onModelChanged()
      except:
         exceptionPopup()

   def moveNode( self, nodeIndex, newParentIndex, newRow ):
      try:
         self._model.moveNode( nodeIndex, newParentIndex, newRow )
         self._outlineView.setCurrentIndex( self._model.index(newRow, 0, newParentIndex) )
         self.onModelChanged()
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
            OutlineNode = index.internalPointer( )
            
            if OutlineNode is not None:
               articleType, articleText = OutlineNode.article( )
               
               if articleType == 'text':
                  self._articleView.setText( articleText )
               elif articleType == 'html':
                  self._articleView.setHtml( articleText )
      
      self.swappingArticle = False

   def expandAll( self ):
      try:
         self._outlineView.expandAll( )
      except:
         exceptionPopup()

   def expandNode( self ):
      try:
         self._outlineView.expand( self._outlineView.currentIndex() )
      except:
         exceptionPopup()

   def collapseAll( self ):
      try:
         self._outlineView.collapseAll( )
      except:
         exceptionPopup()

   def collapseNode( self ):
      try:
         self._outlineView.collapse( self._outlineView.currentIndex() )
      except:
         exceptionPopup()

   def insertNewNodeBefore( self ):
      try:
         index = self._outlineView.currentIndex()
         self.insertNode( index.parent(), index.row() )
      except:
         exceptionPopup()

   def insertNewNodeAfter( self ):
      try:
         index = self._outlineView.currentIndex()
         self.insertNode( index.parent(), index.row() + 1 )
      except:
         exceptionPopup()

   def insertNewChild( self ):
      try:
         index = self._outlineView.currentIndex()
         self.insertNode( index, 0 )
      except:
         exceptionPopup()

   def indentNode( self, nodeIndex=None ):
      try:
         if nodeIndex is None:
            nodeIndex = self._outlineView.currentIndex()
         
         theNodeRow = nodeIndex.row()
         if theNodeRow == 0:
            return
         
         theNewParent = nodeIndex.sibling( nodeIndex.row() - 1, 0 )
         if len(theNewParent.internalPointer()._childNodes) == 0:
            self.moveNode( nodeIndex, theNewParent, 0 )
      except:
         exceptionPopup()

   def dedentNode( self, nodeIndex=None ):
      try:
         if nodeIndex is None:
            nodeIndex = self._outlineView.currentIndex()
         
         if len(nodeIndex.parent().internalPointer()._childNodes) != 1:
            return
         
         newParent = nodeIndex.parent().parent()
         newRow    = nodeIndex.parent().row() + 1
         self.moveNode( nodeIndex, newParent, newRow )
      except:
         exceptionPopup()

   def moveNodeUp( self, nodeIndex=None ):
      try:
         nodeIndex = nodeIndex
         if nodeIndex is None:
            nodeIndex = self._outlineView.currentIndex()
         
         theRow = nodeIndex.row()
         if theRow == 0:
            return
         
         self.moveNode( nodeIndex, nodeIndex.parent(), theRow - 1 )
      except:
         exceptionPopup()

   def moveNodeDown( self, nodeIndex=None ):
      try:
         if nodeIndex is None:
            nodeIndex = self._outlineView.currentIndex()
         
         theRow = nodeIndex.row()
         if theRow >= len(nodeIndex.internalPointer()._parentNode._childNodes):
            return
         
         self.moveNode( nodeIndex, nodeIndex.parent(), theRow + 1 )
      except:
         exceptionPopup()

   def cutNode( self ):
      pass
   
   def copyNode( self ):
      pass
   
   def pasteNodeBefore( self ):
      pass
   
   def pasteNodeAfter( self ):
      pass
   
   def pasteNodeChild( self ):
      pass
   
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

   # Implementation
   def _buildGui( self ):
      self._buildWidgets( )
      
      self._defineActions( )
      
      self._buildMenus( )

   def _buildWidgets( self ):
      self._outlineView = OutlineEditorWidget(self)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 0 )
      self._outlineView.setSizePolicy(sizePolicy)
      self._outlineView.setMinimumSize(QtCore.QSize(100, 100))
      self._outlineView.setSizeIncrement(QtCore.QSize(1, 1))
      self._outlineView.setFont( RES.articleFont )
      self._outlineView.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
      #self._outlineView.setDragEnabled(True)
      #self._outlineView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
      self._outlineView.setAlternatingRowColors(True)
      #self._outlineView.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
      self._outlineView.setUniformRowHeights(True)
      self._outlineView.setSortingEnabled(False)
      self._outlineView.setObjectName("outlineView")
      self._outlineView.setItemDelegate( OutlineEntryEditor_Delegate(self._outlineView, self) )
      
      self._articleView = QtGui.QTextEdit(self)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 1 )
      self._articleView.setSizePolicy(sizePolicy)
      self._articleView.setMinimumSize(QtCore.QSize(100, 100))
      self._articleView.setFont( RES.articleFont )
      self._articleView.setObjectName("articleView")
      
      QtCore.QObject.connect( self._outlineView, QtCore.SIGNAL('entryRightClicked(QPoint,QModelIndex)'), self.entryRightClicked )

   def _defineActions( self ):
      # Undo
      self.editUndoAction = QtGui.QAction( self._outlineView )
      self.editUndoAction.setObjectName( 'actionEditUndo' )
      self.editUndoAction.setText(QtGui.QApplication.translate("MainWindow", RES.ACTION_EDIT_UNDO_TEXT, None, QtGui.QApplication.UnicodeUTF8))
      self.editUndoAction.setIcon( QtGui.QIcon(RES.ACTION_EDIT_UNDO_ICON) )
      self.editUndoAction.setStatusTip( RES.ACTION_EDIT_UNDO_STATUSTIP )
      #self.editUndoAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.editUndoAction, QtCore.SIGNAL('triggered()'), self.editUndo )
      
      # Redo
      self.editRedoAction = QtGui.QAction( self._outlineView )
      self.editRedoAction.setObjectName( 'actionEditRedo' )
      self.editRedoAction.setText(QtGui.QApplication.translate("MainWindow", RES.ACTION_EDIT_REDO_TEXT, None, QtGui.QApplication.UnicodeUTF8))
      self.editRedoAction.setIcon( QtGui.QIcon(RES.ACTION_EDIT_REDO_ICON) )
      self.editRedoAction.setStatusTip( RES.ACTION_EDIT_REDO_STATUSTIP )
      #self.editRedoAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.editRedoAction, QtCore.SIGNAL('triggered()'), self.editRedo )
      
      # Cut Text
      self.articleCutAction = QtGui.QAction( self._outlineView )
      self.articleCutAction.setObjectName( 'actionArticleCut' )
      self.articleCutAction.setText(QtGui.QApplication.translate("MainWindow", RES.ACTION_ARTICLE_CUT_TEXT, None, QtGui.QApplication.UnicodeUTF8))
      self.articleCutAction.setIcon( QtGui.QIcon(RES.ACTION_ARTICLE_CUT_ICON) )
      self.articleCutAction.setStatusTip( RES.ACTION_ARTICLE_CUT_STATUSTIP )
      #self.articleCutAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.articleCutAction, QtCore.SIGNAL('trigger()'), self.articleCut )
      
      # Copy Text
      self.articleCopyAction = QtGui.QAction( self._outlineView )
      self.articleCopyAction.setObjectName( 'actionArticleCopy' )
      self.articleCopyAction.setText(QtGui.QApplication.translate("MainWindow", RES.ACTION_ARTICLE_COPY_TEXT, None, QtGui.QApplication.UnicodeUTF8))
      self.articleCopyAction.setIcon( QtGui.QIcon(RES.ACTION_ARTICLE_COPY_ICON) )
      self.articleCopyAction.setStatusTip( RES.ACTION_ARTICLE_COPY_STATUSTIP )
      #self.articleCopyAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.articleCopyAction, QtCore.SIGNAL('trigger()'), self.articleCopy )
      
      # Paste Text
      self.articlePasteAction = QtGui.QAction( self._outlineView )
      self.articlePasteAction.setObjectName( 'actionArticlePaste' )
      self.articlePasteAction.setText(QtGui.QApplication.translate("MainWindow", RES.ACTION_ARTICLE_PASTE_TEXT, None, QtGui.QApplication.UnicodeUTF8))
      self.articlePasteAction.setIcon( QtGui.QIcon(RES.ACTION_ARTICLE_PASTE_ICON) )
      self.articlePasteAction.setStatusTip( RES.ACTION_ARTICLE_PASTE_STATUSTIP )
      #self.articlePasteAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.articlePasteAction, QtCore.SIGNAL('trigger()'), self.articlePaste )
      
      # Select All Text
      self.articleSelectAllAction = QtGui.QAction( self._outlineView )
      self.articleSelectAllAction.setObjectName( 'actionSelectAll' )
      self.articleSelectAllAction.setText(QtGui.QApplication.translate("MainWindow", "Select All Text", None, QtGui.QApplication.UnicodeUTF8))
      #self.articleSelectAllAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.articleSelectAllAction, QtCore.SIGNAL('trigger()'), self.articleSelectAll )
      
      # Cut Node
      self.cutNodeAction           = QtGui.QAction( self._outlineView )
      self.cutNodeAction.setObjectName( 'actionCutNode' )
      self.cutNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Cut Node", None, QtGui.QApplication.UnicodeUTF8))
      #self.cutNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.cutNodeAction, QtCore.SIGNAL('triggered()'), self.cutNode )
      
      # Copy Node
      self.copyNodeAction          = QtGui.QAction( self._outlineView )
      self.copyNodeAction.setObjectName( 'actionCopyNode' )
      self.copyNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Copy Node", None, QtGui.QApplication.UnicodeUTF8))
      #self.copyNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.copyNodeAction, QtCore.SIGNAL('triggered()'), self.copyNode )
      
      # Paste Node Before
      self.pasteNodeBeforeAction   = QtGui.QAction( self._outlineView )
      self.pasteNodeBeforeAction.setObjectName( 'actionPasteNodeBefore' )
      self.pasteNodeBeforeAction.setText(QtGui.QApplication.translate("MainWindow", "Paste Node Before", None, QtGui.QApplication.UnicodeUTF8))
      #self.pasteNodeBeforeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.pasteNodeBeforeAction, QtCore.SIGNAL('triggered()'), self.pasteNodeBefore )
      
      # Paste Node After
      self.pasteNodeAfterAction    = QtGui.QAction( self._outlineView )
      self.pasteNodeAfterAction.setObjectName( 'actionPasteNodeAfter' )
      self.pasteNodeAfterAction.setText(QtGui.QApplication.translate("MainWindow", "Paste Node After", None, QtGui.QApplication.UnicodeUTF8))
      #self.pasteNodeAfterAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.pasteNodeAfterAction, QtCore.SIGNAL('triggered()'), self.pasteNodeAfter )
      
      # Past Node as Child
      self.pasteNodeChildAction    = QtGui.QAction( self._outlineView )
      self.pasteNodeChildAction.setObjectName( 'actionPasteNodeChild' )
      self.pasteNodeChildAction.setText(QtGui.QApplication.translate("MainWindow", "Paste Node Child", None, QtGui.QApplication.UnicodeUTF8))
      #self.pasteNodeChildAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.pasteNodeChildAction, QtCore.SIGNAL('triggered()'), self.pasteNodeChild )
      
      # Expand All Nodes
      self.expandAllAction         = QtGui.QAction( self._outlineView )
      self.expandAllAction.setObjectName( 'actionExpandAll' )
      self.expandAllAction.setText(QtGui.QApplication.translate("MainWindow", RES.ACTION_TREE_EXPANDALL_TEXT, None, QtGui.QApplication.UnicodeUTF8))
      self.expandAllAction.setIcon( QtGui.QIcon(RES.ACTION_TREE_EXPANDALL_ICON) )
      self.expandAllAction.setStatusTip( RES.ACTION_TREE_EXPANDALL_STATUSTIP )
      #self.expandAllAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.expandAllAction, QtCore.SIGNAL('triggered()'), self.expandAll )
      
      # Expand Node
      self.expandNodeAction            = QtGui.QAction( self._outlineView )
      self.expandNodeAction.setObjectName( 'actionExpandNode' )
      self.expandNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Expand Node", None, QtGui.QApplication.UnicodeUTF8))
      #self.expandNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.expandNodeAction, QtCore.SIGNAL('triggered()'), self.expandNode )
      
      # Collapse All Nodes
      self.collapseAllAction       = QtGui.QAction( self._outlineView )
      self.collapseAllAction.setObjectName( 'actionCollapseAll' )
      self.collapseAllAction.setText(QtGui.QApplication.translate("MainWindow", RES.ACTION_TREE_COLLAPSEALL_TEXT, None, QtGui.QApplication.UnicodeUTF8))
      self.collapseAllAction.setStatusTip( RES.ACTION_TREE_COLLAPSEALL_STATUSTIP )
      self.collapseAllAction.setIcon( QtGui.QIcon(RES.ACTION_TREE_COLLAPSEALL_ICON) )
      #self.collapseAllAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.collapseAllAction, QtCore.SIGNAL('triggered()'), self.collapseAll )
      
      # Collapse Node
      self.collapseNodeAction          = QtGui.QAction( self._outlineView )
      self.collapseNodeAction.setObjectName( 'actionCollapseNode' )
      self.collapseNodeAction.setText(QtGui.QApplication.translate("MainWindow", "CollapseNode", None, QtGui.QApplication.UnicodeUTF8))
      #self.collapseNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.collapseNodeAction, QtCore.SIGNAL('triggered()'), self.collapseNode )
      
      # Move Node Up
      self.moveNodeUpAction            = QtGui.QAction( self._outlineView )
      self.moveNodeUpAction.setObjectName( 'actionMoveNodeUp' )
      self.moveNodeUpAction.setText(QtGui.QApplication.translate("MainWindow", "Move Node Up", None, QtGui.QApplication.UnicodeUTF8))
      self.moveNodeUpAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Up ] )
      QtCore.QObject.connect( self.moveNodeUpAction, QtCore.SIGNAL('triggered()'), self.moveNodeUp )
      
      # Move Node Down
      self.moveNodeDownAction          = QtGui.QAction( self._outlineView )
      self.moveNodeDownAction.setObjectName( 'actionMoveNodeDown' )
      self.moveNodeDownAction.setText(QtGui.QApplication.translate("MainWindow", "Move Node Down", None, QtGui.QApplication.UnicodeUTF8))
      self.moveNodeDownAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Down ] )
      QtCore.QObject.connect( self.moveNodeDownAction, QtCore.SIGNAL('triggered()'), self.moveNodeDown )
      
      # Indent Node
      self.indentNodeAction            = QtGui.QAction( self._outlineView )
      self.indentNodeAction.setObjectName( 'actionIndentNode' )
      self.indentNodeAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Right, QtCore.Qt.Key_Tab ] )
      self.indentNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Indent Node", None, QtGui.QApplication.UnicodeUTF8))
      QtCore.QObject.connect( self.indentNodeAction, QtCore.SIGNAL('triggered()'), self.indentNode )
      
      # Dedent Node
      self.dedentNodeAction            = QtGui.QAction( self._outlineView )
      self.dedentNodeAction.setObjectName( 'actionDedentNode' )
      self.dedentNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Dedent Node", None, QtGui.QApplication.UnicodeUTF8))
      self.dedentNodeAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Left, QtCore.Qt.SHIFT + QtCore.Qt.Key_Tab ] )
      QtCore.QObject.connect( self.dedentNodeAction, QtCore.SIGNAL('triggered()'), self.dedentNode )
      
      # Insert New Node Before
      self.insertNewNodeBeforeAction   = QtGui.QAction( self._outlineView )
      self.insertNewNodeBeforeAction.setObjectName( 'actionInsertNewNodeBefore' )
      self.insertNewNodeBeforeAction.setText(QtGui.QApplication.translate("MainWindow", "New Node Before", None, QtGui.QApplication.UnicodeUTF8))
      #self.insertNewNodeBeforeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.insertNewNodeBeforeAction, QtCore.SIGNAL('triggered()'), self.insertNewNodeBefore )
      
      # Insert New Node After
      self.insertNewNodeAfterAction    = QtGui.QAction( self._outlineView )
      self.insertNewNodeAfterAction.setObjectName( 'actionInsertNewNodeAfter' )
      self.insertNewNodeAfterAction.setText(QtGui.QApplication.translate("MainWindow", "New Node After", None, QtGui.QApplication.UnicodeUTF8))
      self.insertNewNodeAfterAction.setShortcuts( [ QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter ] )
      QtCore.QObject.connect( self.insertNewNodeAfterAction, QtCore.SIGNAL('triggered()'), self.insertNewNodeAfter )
      
      # Insert New Child Node
      self.insertNewChildAction        = QtGui.QAction( self._outlineView )
      self.insertNewChildAction.setObjectName( 'actionInsertNewChild' )
      self.insertNewChildAction.setText(QtGui.QApplication.translate("MainWindow", "New Child", None, QtGui.QApplication.UnicodeUTF8))
      #self.insertNewChildAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.insertNewChildAction, QtCore.SIGNAL('triggered()'), self.insertNewChild )
      
      # Delete Node
      self.deleteNodeAction            = QtGui.QAction( self._outlineView )
      self.deleteNodeAction.setObjectName( 'actionDeleteNode' )
      self.deleteNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Delete Subtree", None, QtGui.QApplication.UnicodeUTF8))
      #self.deleteNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.deleteNodeAction, QtCore.SIGNAL('triggered()'), self.deleteNode )

   def _buildMenus( self ):
      # Tree Menu
      self.menuTree = QtGui.QMenu(self)
      self.menuTree.setObjectName("menuTree")
      self.menuTree.setTitle(QtGui.QApplication.translate("MainWindow", "Tree", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuTree.addAction( self.cutNodeAction )
      self.menuTree.addAction( self.copyNodeAction )
      self.menuTree.addAction( self.pasteNodeBeforeAction )
      self.menuTree.addAction( self.pasteNodeAfterAction )
      self.menuTree.addAction( self.pasteNodeChildAction )
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
      
      # Article Menu
      self.menuArticle = QtGui.QMenu(self)
      self.menuArticle.setObjectName("menuArticle")
      self.menuArticle.setTitle(QtGui.QApplication.translate("MainWindow", "Article", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuArticle.addAction( self.articleCutAction )
      self.menuArticle.addAction( self.articleCopyAction )
      self.menuArticle.addAction( self.articlePasteAction )
      self.menuArticle.addSeparator()
      self.menuArticle.addAction( self.articleSelectAllAction )
