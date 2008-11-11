from PyQt4 import QtCore, QtGui
from OutlineModel import OutlineModel, TreeNode
import MTresources as RES

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

class OutlineEditor(object):
   '''emits: modelChanged()'''
   def __init__( self, parent ):
      self.splitter    = None
      self.outlineView = None
      self.articleView = None
      self.delegate    = None
      self.model       = None
      
      self.splitter = QtGui.QSplitter(parent)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 0 )
      self.splitter.setSizePolicy(sizePolicy)
      self.splitter.setMinimumSize(QtCore.QSize(100, 100))
      self.splitter.setOrientation(QtCore.Qt.Horizontal)
      self.splitter.setChildrenCollapsible(False)
      self.splitter.setObjectName("splitter")
      
      self.outlineView = QtGui.QTreeView(self.splitter)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 0 )
      self.outlineView.setSizePolicy(sizePolicy)
      self.outlineView.setMinimumSize(QtCore.QSize(100, 100))
      self.outlineView.setSizeIncrement(QtCore.QSize(1, 1))
      self.outlineView.setFont( RES.articleFont )
      self.outlineView.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
      #self.outlineView.setDragEnabled(True)
      #self.outlineView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
      self.outlineView.setAlternatingRowColors(True)
      #self.outlineView.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
      #########self.outlineView.setUniformRowHeights(True)
      self.outlineView.setSortingEnabled(False)
      self.outlineView.setObjectName("outlineView")
      self.delegate = OutlineEntryEditor_Delegate(self.outlineView, self)
      self.outlineView.setItemDelegate( self.delegate )
      
      self.articleView = QtGui.QTextEdit(self.splitter)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 1 )
      self.articleView.setSizePolicy(sizePolicy)
      self.articleView.setMinimumSize(QtCore.QSize(100, 100))
      self.articleView.setFont( RES.articleFont )
      self.articleView.setObjectName("articleView")
      
      # Define Actions
      self.expandAllAction         = QtGui.QAction( self.outlineView )
      self.expandAllAction.setObjectName( 'actionExpandAll' )
      #self.expandAllAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.expandAllAction, QtCore.SIGNAL('triggered()'), self.expandAll )
      
      self.expandNodeAction            = QtGui.QAction( self.outlineView )
      self.expandNodeAction.setObjectName( 'actionExpandNode' )
      #self.expandNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.expandNodeAction, QtCore.SIGNAL('triggered()'), self.expandNode )
      
      self.collapseAllAction       = QtGui.QAction( self.outlineView )
      self.collapseAllAction.setObjectName( 'actionCollapseAll' )
      #self.collapseAllAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.collapseAllAction, QtCore.SIGNAL('triggered()'), self.collapseAll )
      
      self.collapseNodeAction          = QtGui.QAction( self.outlineView )
      self.collapseNodeAction.setObjectName( 'actionCollapseNode' )
      #self.collapseNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.collapseNodeAction, QtCore.SIGNAL('triggered()'), self.collapseNode )
      
      self.moveNodeUpAction            = QtGui.QAction( self.outlineView )
      self.moveNodeUpAction.setObjectName( 'actionMoveNodeUp' )
      self.moveNodeUpAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Up ] )
      QtCore.QObject.connect( self.moveNodeUpAction, QtCore.SIGNAL('triggered()'), self.moveNodeUp )
      
      self.moveNodeDownAction          = QtGui.QAction( self.outlineView )
      self.moveNodeDownAction.setObjectName( 'actionMoveNodeDown' )
      self.moveNodeDownAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Down ] )
      QtCore.QObject.connect( self.moveNodeDownAction, QtCore.SIGNAL('triggered()'), self.moveNodeDown )
      
      self.indentNodeAction            = QtGui.QAction( self.outlineView )
      self.indentNodeAction.setObjectName( 'actionIndentNode' )
      self.indentNodeAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Right, QtCore.Qt.Key_Tab ] )
      QtCore.QObject.connect( self.indentNodeAction, QtCore.SIGNAL('triggered()'), self.indentNode )
      
      self.dedentNodeAction            = QtGui.QAction( self.outlineView )
      self.dedentNodeAction.setObjectName( 'actionDedentNode' )
      self.dedentNodeAction.setShortcuts( [ QtCore.Qt.CTRL + QtCore.Qt.Key_Left, QtCore.Qt.SHIFT + QtCore.Qt.Key_Tab ] )
      QtCore.QObject.connect( self.dedentNodeAction, QtCore.SIGNAL('triggered()'), self.dedentNode )
      
      self.insertNewNodeBeforeAction   = QtGui.QAction( self.outlineView )
      self.insertNewNodeBeforeAction.setObjectName( 'actionInsertNewNodeBefore' )
      #self.insertNewNodeBeforeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.insertNewNodeBeforeAction, QtCore.SIGNAL('triggered()'), self.insertNewNodeBefore )
      
      self.insertNewNodeAfterAction    = QtGui.QAction( self.outlineView )
      self.insertNewNodeAfterAction.setObjectName( 'actionInsertNewNodeAfter' )
      self.insertNewNodeAfterAction.setShortcuts( [ QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter ] )
      QtCore.QObject.connect( self.insertNewNodeAfterAction, QtCore.SIGNAL('triggered()'), self.insertNewNodeAfter )
      
      self.insertNewChildAction        = QtGui.QAction( self.outlineView )
      self.insertNewChildAction.setObjectName( 'actionInsertNewChild' )
      #self.insertNewChildAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.insertNewChildAction, QtCore.SIGNAL('triggered()'), self.insertNewChild )
      
      self.deleteNodeAction            = QtGui.QAction( self.outlineView )
      self.deleteNodeAction.setObjectName( 'actionDeleteNode' )
      #self.deleteNodeAction.setShortcuts( [ ] )
      QtCore.QObject.connect( self.deleteNodeAction, QtCore.SIGNAL('triggered()'), self.deleteNode )

   # Basic Operations
   def setModel( self, aModel ):
      self.model = aModel
      self.ct    = 0
      self.swappingArticle = False
      
      self.articleView.clear( )
      
      try:
         # Update and Validate the new model
         aModel.validateModel( )
         aModel.updateModel( )
         
         self.outlineView.setModel( aModel )
         
         QtCore.QObject.connect( self.outlineView.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged )
         QtCore.QObject.connect( self.model, QtCore.SIGNAL( 'dataChanged(QModelIndex,QModelIndex)' ), self.onModelChanged )
         QtCore.QObject.connect( self.articleView, QtCore.SIGNAL( 'textChanged()' ), self.onModelChanged )
      
      except:
         exceptionPopup( )
      
      indexOfFirst = aModel.index( 0, 0, QtCore.QModelIndex() )
      self.selectionChanged( indexOfFirst )

   def insertNode( self, newParentIndex, newRow, newNode=None ):
      self.model.insertNode( newParentIndex, newRow, newNode )
      self.outlineView.setCurrentIndex( self.model.index(newRow, 0, newParentIndex) )
      self.onModelChanged()
   
   def deleteNode( self, nodeIndex=None ):
      if nodeIndex is None:
         nodeIndex = self.outlineView.currentIndex()
      
      self.model.removeNode( nodeIndex )
      self.onModelChanged()

   def moveNode( self, nodeIndex, newParentIndex, newRow ):
      self.model.moveNode( nodeIndex, newParentIndex, newRow )
      self.outlineView.setCurrentIndex( self.model.index(newRow, 0, newParentIndex) )
      self.onModelChanged()

   # Slots
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
            theDocument = self.articleView.document()
            
            if theDocument.isEmpty():
               article     = ''
               articleType = 'text'
            else:
               article     = unicode( theDocument.toHtml() )
               articleType = 'html'
            
            index.internalPointer().setArticle( article, articleType )
      
      # Reinitialize the article widget
      self.articleView.clear( )
      
      # Display the newly selected article
      if newSelection:
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
                  self.articleView.setText( articleText )
               elif articleType == 'html':
                  self.articleView.setHtml( articleText )
      
      self.swappingArticle = False

   def expandAll( self ):
      self.outlineView.expandAll( )

   def expandNode( self ):
      self.outlineView.expand( self.outlineView.currentIndex() )

   def collapseAll( self ):
      self.outlineView.collapseAll( )

   def collapseNode( self ):
      self.outlineView.collapse( self.outlineView.currentIndex() )

   def insertNewNodeBefore( self ):
      index = self.outlineView.currentIndex()
      self.insertNode( index.parent(), index.row() )

   def insertNewNodeAfter( self ):
      index = self.outlineView.currentIndex()
      self.insertNode( index.parent(), index.row() + 1 )

   def insertNewChild( self ):
      index = self.outlineView.currentIndex()
      self.insertNode( index, 0 )

   def indentNode( self, nodeIndex=None ):
      if nodeIndex is None:
         nodeIndex = self.outlineView.currentIndex()
      
      theNodeRow = nodeIndex.row()
      if theNodeRow == 0:
         return
      
      theNewParent = nodeIndex.sibling( nodeIndex.row() - 1, 0 )
      if len(theNewParent.internalPointer()._childNodes) == 0:
         self.moveNode( nodeIndex, theNewParent, 0 )

   def dedentNode( self, nodeIndex=None ):
      if nodeIndex is None:
         nodeIndex = self.outlineView.currentIndex()
      
      if len(nodeIndex.parent().internalPointer()._childNodes) != 1:
         return
      
      newParent = nodeIndex.parent().parent()
      newRow    = nodeIndex.parent().row() + 1
      self.moveNode( nodeIndex, newParent, newRow )

   def moveNodeUp( self, nodeIndex=None ):
      nodeIndex = nodeIndex
      if nodeIndex is None:
         nodeIndex = self.outlineView.currentIndex()
      
      theRow = nodeIndex.row()
      if theRow == 0:
         return
      
      self.moveNode( nodeIndex, nodeIndex.parent(), theRow - 1 )

   def moveNodeDown( self, nodeIndex=None ):
      if nodeIndex is None:
         nodeIndex = self.outlineView.currentIndex()
      
      theRow = nodeIndex.row()
      if theRow >= len(nodeIndex.internalPointer()._parentNode._childNodes):
         return
      
      self.moveNode( nodeIndex, nodeIndex.parent(), theRow + 1 )

   def onModelChanged( self, index1=None, index2=None ):
      if not self.swappingArticle:
         print 'model changed', self.ct
         self.ct += 1
