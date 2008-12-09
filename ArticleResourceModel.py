from PyQt4 import QtCore, QtGui
import os.path


from utilities import splitFilePath
from ApplicationFramework import RES


class ArticleResources( object ):
   IMAGE_RES       = 'Image'
   BOOKMARK_RES    = 'Bookmark'
   LINK_RES        = 'Link'
   STRING_RES      = 'String'

   def __init__( self, resDict=None ):
      self._res       = { }     # map id to Resource instance
      self._bookmarks = set( )
      
      if resDict is not None:
         self._res = resDict
   
   def define( self, name, resType, resVal ):
      self._res[ name ] = [ resType, resVal ]
      if resType == ArticleResources.BOOKMARK_RES:
         self._bookmarks.add( resVal )
   
   def undefine( self, name ):
      resType, resVal = self._res[ name ]
      if resType == ArticleResources.BOOKMARK_RES:
         self._bookmarks.remove( resVal )
      
      del self._res[ name ]

   def names( self ):
      return self._res.keys( )
   
   def info( self, name ):
      return self._res[ name ]
   
   def __iter__( self ):
      return iter(self._res)

   def isBookmarkedId( self, anId ):
      return anId in self._bookmarks

   def validate( self ):
      if not isinstance( self._res, dict ):
         return False
      
      for name in self._res:
         if not isinstance( name, (str,unicode) ):
            return False
         
         val = self._res[ name ]
         if not isinstance( val, (list,tuple) ):
            return False
         if not len(val) == 2:
            return False
         resType,resVal = val
         if resType not in ( ArticleResources.IMAGE_RES, ArticleResources.BOOKMARK_RES, ArticleResources.LINK_RES, ArticleResources.STRING_RES ):
            return False
         if not isinstance( resVal, (str,unicode) ):
            return False
      
      return True


class ArticleResourcesModel(QtCore.QAbstractItemModel):
   '''emit: resourceChange()'''
   def __init__( self, articleResources=None, parent=None ):
      QtCore.QAbstractItemModel.__init__(self, parent)
      
      self._res         = articleResources
      self._resNameList = [ ]
      
      if self._res is None:
         self._res = ArticleResources( )
         self._updateNameList( )
   
   # Qt Interface
   def columnCount( self, parent ):
      return 3    # [ name, type, value ]
   
   def data( self, index, role ):
      if not index.isValid( ):
         return QtCore.QVariant( )
      
      if role != QtCore.Qt.DisplayRole:
         return QtCore.QVariant( )
      
      row = index.row()
      resName = self._resNameList[ row ]
      
      if index.column() == 0:
         val = resName
      else:
         val = self._res.info(resName)[ index.column() - 1 ]
      
      return QtCore.QVariant(val)
   
   def flags( self, index ):
      if not index.isValid( ):
         return QtCore.Qt.ItemIsEnabled
      
      return QtCore.Qt.ItemIsEditable | QtCore.QAbstractItemModel.flags( self, index )
   
   def headerData(self, section, orientation, role):
      header = RES.getMultipartResource('ArticleResource','viewColumns',translate=True)
      
      if (orientation == QtCore.Qt.Horizontal) and (role == QtCore.Qt.DisplayRole):
         return QtCore.QVariant( header[section] )
      
      return QtCore.QVariant()

   def index(self, row, column, parentIndex):
      if row < 0 or column < 0 or row >= self.rowCount(parentIndex) or column >= self.columnCount(parentIndex):
         return QtCore.QModelIndex()
      
      return self.createIndex(row, column, None)

   def parent( self, index ):
      return QtCore.QModelIndex()
   
   def rowCount(self, parent):
      return len(self._resNameList)

   # Other Methods
   def isBookmarkedId( self, anId ):
      return self._res.isBookmarkedId( anId )

   def validate( self ):
      if not isinstance( self._resNameList, list ):
         return False
      for name in self._resNameList:
         if not isinstance( name, (str,unicode) ):
            return False
      
      return self._res.validate( )

   def rawResourceObject( self ):
      return self._res
   
   def define( self, name, resType, resVal ):
      self._res.define( name, resType, resVal )
      self._updateNameList( )
      self._announceChanges( )
   
   def undefine( self, name ):
      self._res.undefine( name )
      self._updateNameList( )
      self._announceChanges( )
   
   def info( self, name ):
      return self._res.info( name )

   def __iter__( self ):
      return iter(self._resNameList)

   # Helpers
   def installImageResource( self, filename ):
      IMAGE_DIR = RES.get( 'ArticleResource','imageDir' )
      
      disk,path,name,ext = splitFilePath( filename )
      
      # Copy the image to the resource folder if needed
      imagePath = os.path.join( IMAGE_DIR, name + ext )
      if not os.path.exists( imagePath ):
         if not os.path.exists( IMAGE_DIR ):
            os.mkdir( IMAGE_DIR )
         import shutil
         shutil.copy( filename, imagePath )
      
      resName = name + ext
      resUrl  = '{0}/{1}'.format( IMAGE_DIR, name )
      
      self.define( resName, ArticleResources.IMAGE_RES, resUrl )

   def _updateNameList( self ):
      self._resNameList = list(self._res.names())
      self._resNameList.sort( )
   
   def _announceChanges( self ):
      self.emit( QtCore.SIGNAL('resourceChange()') )

