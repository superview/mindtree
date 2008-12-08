from PyQt4 import QtCore, QtGui
from ApplicationFramework import RES
from uuid import uuid4
import os.path


class InvalidIndexError( Exception ):
   def __init__( self, msg=None ):
      Exception.__init__( self, msg )


class InvalidRowError( Exception ):
   def __init__( self, msg=None ):
      Exception.__init__( self, msg )


class TreeNode( object ):
   def __init__(self, title, parent=None, article=None):
      assert isinstance( title,   (str,unicode) )
      assert isinstance( parent,  TreeNode) or (parent is None)
      assert isinstance( article, (str,unicode) ) or (article is None)
      
      # Contents
      self._id         = uuid4().hex
      self._data       = [ title ]
      self._article    = article if article is not None else ''
      
      # Structure
      self._parentNode = parent
      self._childNodes = []

   def appendChild(self, node):
      assert isinstance( node, TreeNode )
      
      node._parentNode = self
      self._childNodes.append(node)

   def id( self ):
      return self._id
   
   def data( self, column ):
      assert isinstance( column, int )
      
      return self._data[ column ]

   def title( self ):
      return self._data[0]

   def article( self ):
      return self._article

   def row(self):
      if self._parentNode:
         return self._parentNode._childNodes.index(self)
      
      return 0

   def setTitle( self, aTitle ):
      assert isinstance( aTitle, (str,unicode) )
      
      self._data = [ aTitle ]

   def setArticle( self, article ):
      assert isinstance( article, (str,unicode) )
      
      self._article = article
   
   def validate( self, parent=None ):
      if (not isinstance(parent, TreeNode)) and (parent is not None):
         return False
      
      members = self.__dict__.keys()
      if len(members) != 5:
         return False
      
      # Validate _id
      if not isinstance(self._id,(str,unicode)):
         return False
      if len(self._id) != 32:
         return False
      for ch in self._id:
         if ch not in '0123456789abcdefABCDEF':
            return False
      
      # Validate _data
      if self._data is not None:
         if isinstance( self._data, list ):
            for element in self._data:
               if not isinstance( element, (str,unicode) ):
                  return False
         
         elif not isinstance( self._data, (str,unicode) ):
            return False
      
      # Validate _article
      if self._article is not None:
         if not isinstance( self._article, (str,unicode) ):
            return False
      
      # validate _parentNode
      if self._parentNode is not parent:
         return False
      
      # Validate _childNodes
      if not isinstance( self._childNodes, list ):
         return False
      
      for child in self._childNodes:
         if not isinstance( child, TreeNode ):
            return False
         
         if not child.validate( parent=self ):
            return False
      
      return True

   def hasChildren( self ):
      return len(self._childNodes) > 0
   
   def child( self, which ):
      return self._childNodes[ which ]
   
   def childList( self ):
      return self._childNodes

   def parent( self ):
      return self._parentNode
   
   def __iter__( self ):
      return TreeNodeIterator( self )


class OutlineModel(QtCore.QAbstractItemModel):
   EmptyArticleIcon = None
   FullArticleIcon  = None
   
   def __init__(self, rootNode=None, parent=None):
      QtCore.QAbstractItemModel.__init__(self, parent)
      self._rootNode    = None
      
      if rootNode is None:
         rootNode = TreeNode( 'Untitled' )
         rootNode.appendChild( TreeNode( '', rootNode, '' ) )
      
      self._rootNode       = rootNode
      
      global EmptyArticleIcon, FullArticleIcon
      OutlineModel.EmptyArticleIcon = QtCore.QVariant(RES.getIcon( 'OutlineView', 'emptyArticleIcon' ))
      OutlineModel.FullArticleIcon  = QtCore.QVariant(RES.getIcon( 'OutlineView', 'fullArticleIcon'  ))

   def root( self ):
      return self._rootNode

   def validate( self ):
      members = self.__dict__.keys()
      if len(members) != 1:
         return False
      
      # Validate _rootNode
      return self._rootNode.validate( parent=None )
   
   def insertNode( self, newParentIndex, newRow, newNode=None ):
      '''Insert newNode as a new child node of parent.  It becomes the
      nth child node (determined by newRow).  Existing child nodes are pushed up (e.g. the current
      nth child becomes the (n+1)th child).  If newRow == -1If newRow >= num children, newNode is
      added at the end of the list of child nodes.'''
      # Get the parent Node
      theParentNode = newParentIndex.internalPointer()
      if theParentNode is None:
         theParentNode = self._rootNode
      
      # Validate the row
      children = theParentNode._childNodes
      if (newRow < 0) or (newRow > len(children)):
         return False
      
      # Get the node to be inserted
      if newNode is None:
         newNode = TreeNode( '', theParentNode )
      else:
         newNode._parentNode = theParentNode
      
      # Insert the Node
      self.beginInsertRows( newParentIndex, newRow, newRow )
      children.insert( newRow, newNode )
      self.endInsertRows( )
      
      return True
   
   def removeNode( self, index ):
      parentIndex = index.parent()
      row         = index.row()
      
      # We cannot delete the root node
      if index.internalPointer() is self._rootNode:
         return False
      
      # We cannot delete the only node of a tree with only once node
      parentNode = index.internalPointer().parent()
      if parentNode is self._rootNode:
         if len(parentNode.childList()) == 1:
            return False
      
      # Get the parent node
      theParentNode = parentIndex.internalPointer()
      if theParentNode is None:
         theParentNode = self._rootNode
      
      # Validate the row
      children = theParentNode._childNodes
      if (row < 0) or (row > len(children)):
         return False
      
      # Remove the node
      self.beginRemoveRows( parentIndex, row, row )
      del children[ row ]
      self.endRemoveRows( )
      
      return True

   def moveNode( self, theNodeIndex, newParentIndex, newRow ):
      if not theNodeIndex.isValid():
         raise InvalidIndexError()
      
      theNode = theNodeIndex.internalPointer()
      
      self.removeNode( theNodeIndex )
      self.insertNode( newParentIndex, newRow, theNode )

   def serializeNode( self, index=None ):
      '''Return a serialized version of the entires subtree starting from the
      node indicated by index.  If index is None, the entire tree is serialized.
      '''
      import pickle
      
      if index is None:
         node = self._rootNode
      else:
         node = index.internalPointer()
      
      # Since nodes contain refs to their parents, it's importnat to
      # first set that ref to None to prevent the whole tree from being
      # pickled.  After pickling, the ref to the parent is restored.
      nodeParent = node._parentNode
      node._parentNode = None
      encodedData = pickle.dumps( node )
      node._parentNode = nodeParent
      
      return encodedData

   def deserialize( self, encodedData ):
      import pickle
      return pickle.loads( encodedData )

   def mimifyNode( self, index ):
      encodedData = self.serializeNode( index )
      
      mimeObject = QtCore.QMimeData( )
      mimeObject.setData( RES.get('Mime','mindTreeOutline'), encodedData )
      return mimeObject

   def demimifyNode( self, mimeObject ):
      encodedData = mimeObject.data( RES.get('Mime','mindTreeOutline') )
      return self.deserialize( encodedData )

   # Basic Overrides
   def index(self, row, column, parentIndex):
      if row < 0 or column < 0 or row >= self.rowCount(parentIndex) or column >= self.columnCount(parentIndex):
         return QtCore.QModelIndex()
      
      if not parentIndex.isValid():
         parentNode = self._rootNode
      else:
         parentNode = parentIndex.internalPointer()
      
      childNode = parentNode._childNodes[row]
      if childNode:
         return self.createIndex(row, column, childNode)
      else:
         return QtCore.QModelIndex()

   def parent(self, index):
      if not index.isValid():
         return QtCore.QModelIndex()
      
      childItem = index.internalPointer()
      parentNode = childItem._parentNode
      
      if parentNode == self._rootNode:
         return QtCore.QModelIndex()
      
      return self.createIndex(parentNode.row(), 0, parentNode)

   def rowCount(self, parent):
      if parent.column() > 0:
         return 0
      
      if not parent.isValid():
         parentItem = self._rootNode
      else:
         parentItem = parent.internalPointer()
      
      return len(parentItem._childNodes)

   def columnCount(self, parent):
      return 1

   def data(self, index, role):
      if not index.isValid():
         return QtCore.QVariant()
      
      item = index.internalPointer()
      
      if role == QtCore.Qt.DisplayRole:
         return QtCore.QVariant(item.data(index.column()))
      elif role == QtCore.Qt.DecorationRole:
         article = item.article()
         
         if article == '':
            return OutlineModel.EmptyArticleIcon
         else:
            return OutlineModel.FullArticleIcon
      else:
         return QtCore.QVariant()

   # Editing Overrides
   def setData( self, index, value, role ):
      if not index.isValid():
         return False
      
      if role == QtCore.Qt.DisplayRole:
         if isinstance(value,(str,unicode,QtCore.QString)):
            value = unicode(value)
         elif value.type() != QtCore.QVariant.String:
            value = unicode(value.toString())
         else:
            return True
         
         theTreeNode = index.internalPointer()
         if theTreeNode.data( 0 ) != value:
            theTreeNode.setTitle( value )
            self.emit( QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)'), index, index )
      
      return True

   def flags(self, index):
      if not index.isValid():
         return QtCore.Qt.ItemIsEnabled
      
      return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.QAbstractItemModel.flags( self, index )

   def headerData(self, section, orientation, role):
      if (orientation == QtCore.Qt.Horizontal) and (role == QtCore.Qt.DisplayRole):
         data = self._rootNode.data(section)
         if isinstance( data, (str,unicode) ):
            data = QtCore.QVariant( data )
         return data
      
      return QtCore.QVariant()

   def insertRows( self, rowNum, count, parentIndex ):
      return self.insertNode( parentIndex, rowNum )
   
   def removeRows( self, rowNum, count, parentIndex ):
      return self.removeNode( self.index( rowNum, 0, parentIndex ) )
   
   # Drag and Drop Overrides
   def mimeTypes( self ):
      return [ RES.get('Mime','mindTreeOutline') ]

   def supportedDropActions( self ):
      return QtCore.Qt.MoveAction

   # Convenience Methods
   def relativeInsertNode( self, refIndex, relation, newNode=None ):
      '''Given a refernce index (an index to a node already in the outline),
      and a relation ('before', 'after', 'child') insert the new node in
      the indicated location.  'child' indicates the newNode will be inserted
      as the first child of the node indicated by refIndex.
      '''
      if relation == 'child':
         self.insertNode( refIndex, 0, newNode )
      else:
         # The new node is to be a sibling of the node indicated by refIndex
         # so we need to get the parent.
         newParentIndex = refIndex.parent()
         if newParentIndex is None:
            newParentIndex = QtCore.QModelIndex()
         
         # Now determine the insertion row
         insertionRow = refIndex.row()
         if relation == 'after':
            insertionRow += 1
         
         # Do the insertion
         self.insertNode( refIndex, insertionRow, newNode )

   def __iter__( self ):
      return OutlineModelIterator( self.index(0,0,QtCore.QModelIndex()) )
   
   def indexForNode( self, aNode ):
      if aNode.parent() is None:
         return self.index( 0, 0, QtCore.QModelIndex() )
      else:
         return self.index( aNode.row(), 0, self.makeIndexForNode( aNode.parent() ) )


class OutlineModelIterator( object ):
   def __init__( self, index=None, recurse=True ):
      self._rootIndex = index
      self._nextIndex = index
      self._recurse   = recurse
   
   def __iter__( self ):
      return self
   
   def next( self ):
      if self._nextIndex is None:
         raise StopIteration
      
      result = self._nextIndex
      
      if not self._recurse:
         self._nextIndex = None
      elif len(self._nextIndex.internalPointer()._childNodes) > 0:
         self._nextIndex = self._nextIndex.child(0,0)
         return result
      else:
         while self._nextIndex.isValid() and (self._nextIndex != self._rootIndex):
            siblingRow = self._nextIndex.row() + 1
            siblingNode = self._nextIndex.sibling(siblingRow,0)
            
            if siblingNode.isValid():
               self._nextIndex = siblingNode
               return result
            else:
               self._nextIndex = self._nextIndex.parent()
      
      self._nextIndex = None
      return result

 
class NoMoreSubstrings( Exception ):
   pass


class ArticleSubstringIterator( object ):
   '''ArticleIterator iterates over the articles in an Outline

   A textIterator must be an iterator class (provide a next() function which
   returns the next item in the sequence or raises StopIteration if there are
   no items left in the sequence.  textIterator must also supply a restart(text)
   which takes a string as an argument.  This function should reinit the
   iterator to begin scanning the text passed in.  TextIterator may be used as
   a base class to provide some of the implementation.

   When textIterator is passed into this constructor, it may be ready to iterate
   OR it can raise StopIteration and allow ArticleTextIterator to initialize it.
   '''
   def __init__( self, outlineInter ):
      self._outlineIter      = outlineInter
      self._text             = None
      self._currentNodeIndex = None
      
      self._document = QtGui.QTextDocument( )  # used to convert html to text
   
   def __iter__( self ):
      return self
   
   def next( self ):
      try:
         fromPos,toPos = self._nextSubstringOfInterest( )
      except NoMoreSubstrings:
         # We are now ready to iterate through a new article
         
         while True:
            # Get the contents of the new article
            self._currentNodeIndex = self._outlineIter.next( )
            articleText = self._currentNodeIndex.internalPointer().article()
            
            # Convert the article to plain text
            self._document.setHtml( articleText )
            articleText = unicode(self._document.toPlainText( ))
            
            # Reinitialize the iteration over the article segments
            self._setTextToParse( articleText )
            try:
               fromPos,toPos = self._nextSubstringOfInterest( )
               break
            except NoMoreSubstrings:
               pass
      
      return self._currentNodeIndex, fromPos, toPos

   def _setTextToParse( self, newText ):
      'Derived class implementation should call this method before doing anything.'
      self._text = newText

   def _nextSubstringOfInterest( self ):
      '''Derived class implementation should call this method before doing anything.
      
      If there are no substrings to return, raise NoMoreSubstrings.
      '''
      if self._text is None:
         raise NoMoreSubstrings

