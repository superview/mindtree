from PyQt4 import QtCore, QtGui
from ApplicationFramework import RES
import os.path


class InvalidIndexError( Exception ):
   def __init__( self, msg=None ):
      Exception.__init__( self, msg )


class InvalidRowError( Exception ):
   def __init__( self, msg=None ):
      Exception.__init__( self, msg )


class TreeNode( object ):
   def __init__(self, title, parent=None, article=None, articleType='text'):
      # Contents
      self._data        = None
      self._article     = None
      
      # Structure
      self._parentNode = parent
      self._childNodes = []
      
      # Initialization
      self.setContents( title, article, articleType )

   def appendChild(self, node):
      node._parentNode = self
      self._childNodes.append(node)

   def data( self, column ):
      return self._data[ column ]

   def article( self ):
      return self._article

   def row(self):
      if self._parentNode:
         return self._parentNode._childNodes.index(self)
      
      return 0

   def setTitle( self, aTitle ):
      self._data = [ aTitle ]

   def setArticle( self, article, articleType='text' ):
      if article is None:
         article = ''
      
      self._article = [ articleType, article ]
   
   def setContents( self, title, article, articleType ):
      if article is None:
         article = ''
      
      self._data        = [ title ]
      self._article     = [ articleType, article  ]


class OutlineModel(QtCore.QAbstractItemModel):
   def __init__(self, rootNode=None, parent=None):
      QtCore.QAbstractItemModel.__init__(self, parent)
      self._rootNode    = None
      
      if rootNode is None:
         rootNode = TreeNode( 'Untitled' )
         rootNode.appendChild( TreeNode( '', rootNode, '', 'text' ) )
      
      self._rootNode       = rootNode
      
      self.emptyArticleIcon = QtCore.QVariant(RES.getIcon( 'OutlineView', 'emptyArticleIcon' ))
      self.fullArticleIcon  = QtCore.QVariant(RES.getIcon( 'OutlineView', 'fullArticleIcon'  ))

   def validateModel( self ):
      pass

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
      
      # Get the parent node
      theParentNode = parentIndex.internalPointer()
      if theParentNode is None:
         theParentNode = self._rootNode
      
      # Validate the row
      children = theParentNode._childNodes
      if (row < 0) or (row > len(children)):
         return False
         #raise InvalidRowError( )
      
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
   
   def mimifyNode( self, index ):
      # Since nodes contain refs to their parents, it's importnat to
      # first set that ref to None to prevent the whole tree from being
      # pickled.  After pickling, the ref to the parent is restored.
      import pickle
      node = index.internalPointer()
      nodeParent = node._parentNode
      node._parentNode = None
      encodedData = pickle.dumps( node )
      node._parentNode = nodeParent
      
      mimeObject = QtCore.QMimeData( )
      mimeObject.setData( RES.get('OutlineView','nodeMimeType'), encodedData )
      return mimeObject

   def demimifyNode( self, mimeObject ):
      import pickle
      encodedData = mimeObject.data( RES.get('OutlineView','nodeMimeType') )
      return pickle.loads( encodedData )

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
         
         if (article[1] is None) or (article[1] == ''):
            return self.emptyArticleIcon
         else:
            return self.fullArticleIcon
         
         #pic = QtGui.QPicture()
         #x = pic.load(iconFilename)
         #return QtCore.QVariant(pic)
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
      return [ RES.get('OutlineView','nodeMimeType') ]

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
