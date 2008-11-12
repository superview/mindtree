from PyQt4 import QtCore, QtGui
from OutlineModel import OutlineModel, TreeNode
import MTresources as RES

def exceptionPopup( self ):
   import traceback
   
   msgBox = QtGui.QMessageBox( )
   msgBox.setWindowTitle( 'Exception' )
   msgBox.setText( traceback.format_exc( ) )
   msgBox.setIcon( QtGui.QMessageBox.Critical )
   msgBox.exec_( )

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

class OutlineEditor(QtGui.QSplitter):
   '''Emits: QtCore.SIGNAL("modelChanged()")'''
   def __init__( self, parent ):
      QtGui.QSplitter.__init__( self, parent )
      
      self._outlineView            = None      # The TreeView widget
      self._articleView            = None      # The TextEdit widget
      self._model                  = None      # The model for the data
      self._currentArticleModified = False     # Has the article currently being edited been modified?
      
      self._outlineView = QtGui.QTreeView(self)
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
      
      # Define Actions
      self.expandAllAction         = QtGui.QAction( self._outlineView )
      self.expandAllAction.setObjectName( 'actionExpandAll' )
      #self.expandAllAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.expandAllAction, QtCore.SIGNAL('triggered()'), self.expandAll )
      
      self.expandNodeAction            = QtGui.QAction( self._outlineView )
      self.expandNodeAction.setObjectName( 'actionExpandNode' )
      #self.expandNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.expandNodeAction, QtCore.SIGNAL('triggered()'), self.expandNode )
      
      self.collapseAllAction       = QtGui.QAction( self._outlineView )
      self.collapseAllAction.setObjectName( 'actionCollapseAll' )
      #self.collapseAllAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.collapseAllAction, QtCore.SIGNAL('triggered()'), self.collapseAll )
      
      self.collapseNodeAction          = QtGui.QAction( self._outlineView )
      self.collapseNodeAction.setObjectName( 'actionCollapseNode' )
      #self.collapseNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.collapseNodeAction, QtCore.SIGNAL('triggered()'), self.collapseNode )
      
      self.moveNodeUpAction            = QtGui.QAction( self._outlineView )
      self.moveNodeUpAction.setObjectName( 'actionMoveNodeUp' )
      self.moveNodeUpAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Up ] )
      QtCore.QObject.connect( self.moveNodeUpAction, QtCore.SIGNAL('triggered()'), self.moveNodeUp )
      
      self.moveNodeDownAction          = QtGui.QAction( self._outlineView )
      self.moveNodeDownAction.setObjectName( 'actionMoveNodeDown' )
      self.moveNodeDownAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Down ] )
      QtCore.QObject.connect( self.moveNodeDownAction, QtCore.SIGNAL('triggered()'), self.moveNodeDown )
      
      self.indentNodeAction            = QtGui.QAction( self._outlineView )
      self.indentNodeAction.setObjectName( 'actionIndentNode' )
      self.indentNodeAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Right, QtCore.Qt.Key_Tab ] )
      QtCore.QObject.connect( self.indentNodeAction, QtCore.SIGNAL('triggered()'), self.indentNode )
      
      self.dedentNodeAction            = QtGui.QAction( self._outlineView )
      self.dedentNodeAction.setObjectName( 'actionDedentNode' )
      self.dedentNodeAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Left, QtCore.Qt.SHIFT + QtCore.Qt.Key_Tab ] )
      QtCore.QObject.connect( self.dedentNodeAction, QtCore.SIGNAL('triggered()'), self.dedentNode )
      
      self.insertNewNodeBeforeAction   = QtGui.QAction( self._outlineView )
      self.insertNewNodeBeforeAction.setObjectName( 'actionInsertNewNodeBefore' )
      #self.insertNewNodeBeforeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.insertNewNodeBeforeAction, QtCore.SIGNAL('triggered()'), self.insertNewNodeBefore )
      
      self.insertNewNodeAfterAction    = QtGui.QAction( self._outlineView )
      self.insertNewNodeAfterAction.setObjectName( 'actionInsertNewNodeAfter' )
      self.insertNewNodeAfterAction.setShortcuts( [ QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter ] )
      QtCore.QObject.connect( self.insertNewNodeAfterAction, QtCore.SIGNAL('triggered()'), self.insertNewNodeAfter )
      
      self.insertNewChildAction        = QtGui.QAction( self._outlineView )
      self.insertNewChildAction.setObjectName( 'actionInsertNewChild' )
      #self.insertNewChildAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.insertNewChildAction, QtCore.SIGNAL('triggered()'), self.insertNewChild )
      
      self.deleteNodeAction            = QtGui.QAction( self._outlineView )
      self.deleteNodeAction.setObjectName( 'actionDeleteNode' )
      #self.deleteNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.deleteNodeAction, QtCore.SIGNAL('triggered()'), self.deleteNode )

   # Basic Operations
   def setModel( self, aModel ):
      self._model = aModel
      self.swappingArticle = False
      
      self._articleView.clear( )
      
      try:
         # Update and Validate the new model
         aModel.validateModel( )
         aModel.updateModel( )
         
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

   # Slots
   def onArticleChanged( self ):
      if not self.swappingArticle:
         self._currentArticleModified = True
         self.onModelChanged( )

   def onModelChanged( self, index1=None, index2=None ):
      self.emit( QtCore.SIGNAL('modelChanged()') )
