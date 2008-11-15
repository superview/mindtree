from PyQt4 import QtCore, QtGui
from OutlineModel import OutlineModel, TreeNode
from ApplicationFramework import RES

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

class OutlineViewWidget( QtGui.QTreeView ):
   '''Emits: entryRightClicked(QPoint,QModelIndex)'''
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
         if theRow == (len(nodeIndex.internalPointer()._parentNode._childNodes)-1):
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
      outlineFont = RES.getFont( 'OutlineView', 'Font' )
      articleFont = RES.getFont( 'ArticleView', 'Font' )
      
      self._outlineView = OutlineViewWidget(self)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 0 )
      self._outlineView.setSizePolicy(sizePolicy)
      self._outlineView.setMinimumSize(QtCore.QSize(100, 100))
      self._outlineView.setSizeIncrement(QtCore.QSize(1, 1))
      self._outlineView.setFont( outlineFont )
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
      self._articleView.setFont( articleFont )
      self._articleView.setObjectName("articleView")
      
      QtCore.QObject.connect( self._outlineView, QtCore.SIGNAL('entryRightClicked(QPoint,QModelIndex)'), self.entryRightClicked )

   def _defineActions( self ):
      self.editUndoAction         = RES.installAction( 'editUndo',         self._outlineView, self )
      self.editRedoAction         = RES.installAction( 'editRedo',         self._outlineView, self )
      self.articleCutAction       = RES.installAction( 'articleCut',       self._outlineView, self )
      self.articleCopyAction      = RES.installAction( 'articleCopy',      self._outlineView, self )
      self.articlePasteAction     = RES.installAction( 'articlePaste',     self._outlineView, self )
      self.articleSelectAllAction = RES.installAction( 'articleSelectAll', self._outlineView, self )
      self.cutNodeAction          = RES.installAction( 'cutNode',          self._outlineView, self )
      self.copyNodeAction         = RES.installAction( 'copyNode',         self._outlineView, self )
      self.pasteNodeBeforeAction  = RES.installAction( 'pasteNodeBefore',  self._outlineView, self )
      self.pasteNodeAfterAction   = RES.installAction( 'pasteNodeAfter',   self._outlineView, self )
      self.pasteNodeChildAction   = RES.installAction( 'pasteNodeChild',   self._outlineView, self )
      self.expandAllAction        = RES.installAction( 'expandAll',        self._outlineView, self )
      self.collapseAllAction      = RES.installAction( 'collapseAll',      self._outlineView, self )
      self.expandNodeAction       = RES.installAction( 'expandNode',       self._outlineView, self )
      self.collapseNodeAction     = RES.installAction( 'collapseNode',     self._outlineView, self )
      self.moveNodeUpAction       = RES.installAction( 'moveNodeUp',       self._outlineView, self )
      self.moveNodeDownAction     = RES.installAction( 'moveNodeDown',     self._outlineView, self )
      self.indentNodeAction       = RES.installAction( 'indentNode',       self._outlineView, self )
      self.dedentNodeAction       = RES.installAction( 'dedentNode',       self._outlineView, self )
      self.insertNewNodeBeforeAction = RES.installAction( 'insertNewNodeBefore', self._outlineView, self )
      #self.insertNewNodeAfterAction  = RES.installAction( 'insertNewNodeAfter',  self._outlineView, self )
      self.insertNewChildAction   = RES.installAction( 'insertNewChild',   self._outlineView, self )
      self.deleteNodeAction       = RES.installAction( 'deleteNode',       self._outlineView, self )
      
      self.insertNewNodeAfterAction = defAction( 'insertNewNodeAfter', self._outlineView, self,
                                                 text='New Node After',
                                                 shortcuts=[ 'Return', 'Enter' ] )

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
