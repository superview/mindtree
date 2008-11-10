from PyQt4 import QtCore, QtGui
import mt2resources as RES


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
      
      if rootNode is None:
         rootNode = TreeNode( [ 'OutlineName' ] )
         rootNode.appendChild( TreeNode( '', rootNode, '', 'text' ) )
      
      self._rootNode       = rootNode

   def updateModel( self ):
      pass
   
   def validateModel( self ):
      pass

   def insertNode( self, newParentIndex, newRow, newNode=None ):
      # Get the parent Node
      theParentNode = newParentIndex.internalPointer()
      if theParentNode is None:
         theParentNode = self._rootNode
      
      # Validate the row
      children = theParentNode._childNodes
      if (newRow < 0) or (newRow > len(children)):
         raise InvalidRowError( )
      
      # Get the node to be inserted
      if newNode is None:
         newNode = TreeNode( '', theParentNode )
      else:
         newNode._parentNode = theParentNode
      
      # Insert the Node
      self.beginInsertRows( newParentIndex, newRow, newRow )
      children.insert( newRow, newNode )
      self.endInsertRows( )
   
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
         raise InvalidRowError( )
      
      # Remove the node
      self.beginRemoveRows( parentIndex, row, row )
      del children[ row ]
      self.endRemoveRows( )

   def moveNode( self, theNodeIndex, newParentIndex, newRow ):
      if not theNodeIndex.isValid():
         raise InvalidIndexError()
      
      theNode = theNodeIndex.internalPointer()
      
      self.removeNode( theNodeIndex )
      self.insertNode( newParentIndex, newRow, theNode )
   
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
            iconFilename = RES.emptyArticleIcon
         else:
            iconFilename = RES.fullArticleIcon
         
         return QtCore.QVariant( QtGui.QIcon(iconFilename) )
         #pic = QtGui.QPicture()
         #x = pic.load(iconFilename)
         #return QtCore.QVariant(pic)
      else:
         return QtCore.QVariant()

   # Editing Overrides
   def setData( self, index, value, role ):
      if not index.isValid():
         raise InvalidIndexError()
      
      if role == QtCore.Qt.DisplayData:
         index.internalPointer().setTitle( value )

   def flags(self, index):
      if not index.isValid():
         return QtCore.Qt.ItemIsEnabled
      
      return QtCore.Qt.ItemIsEditable | QtCore.QAbstractItemModel.flags( self, index )

   def headerData(self, section, orientation, role):
      if (orientation == QtCore.Qt.Horizontal) and (role == QtCore.Qt.DisplayRole):
         return QtCore.QVariant( self._rootNode.data(section) )
      
      return QtCore.QVariant()

   def insertRows( self, rowNum, count, parentIndex ):
      self.insertNode( parentIndex, rowNum, 1 )
   
   def removeRows( self, rowNum, count, parentIndex ):
      self.removeNode( self.index( rowNum, 0, parentIndex ) )
      #parentNode     = parentIndex.internalPointer( )
      #firstRowNum    = rowNum
      #lastRowNum     = firstRowNum + count - 1
      
      #self.beginRemoveRows( parentIndex, firstRowNum, lastRowNum )
      
      #del parentNode._childNodes[ firstRowNum : lastRowNum ]
      
      #self.endRemoveRows( )
   

