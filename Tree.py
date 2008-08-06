import copy
import uuid

class InvalidPathError( Exception ):
   def __init__( self, msg=None ):
      Exception.__init__( self, msg )


class TreePath( object ):
   SEPARATOR   =   '.'
   
   def __init__( self, aPath=[] ):
      assert isinstance( aPath, (str,unicode,list,uuid.UUID,TreePath) )
      
      if isinstance( aPath, list ):
         self._path = copy.copy( aPath )
      elif isinstance( aPath, uuid.UUID ):
         self._path = [ aPath ]
      elif isinstance( aPath, (str,unicode) ):
         if aPath == '':
            self._path = [ ]
         else:
            self._path = [ uuid.UUID( val ) for val in aPath.split( TreePath.SEPARATOR ) ]
      elif isinstance( aPath, TreePath ):
         self._path = copy.copy( aPath._path )
      else:
         raise Exception, 'Bad type'
   
   def __str__( self ):
      assert isinstance( self._path, list )
      return TreePath.SEPARATOR.join( [ str(val) for val in self._path ] )
   
   def __repr__( self ):
      assert isinstance( self._path, list )
      return TreePath.SEPARATOR.join( [ str(val) for val in self._path ] )
   
   def __eq__( self, other ):
      assert isinstance( self._path, list )
      return isinstance(other,TreePath) and (self._path == other._path)
   
   def __ne__( self, other ):
      assert isinstance( self._path, list )
      return not isinstance(other,TreePath) or (self._path != other._path)
   
   def __copy__( self ):
      assert isinstance( self._path, list )
      return TreePath( copy.copy( self._path ) )
   
   def __len__( self ):
      assert isinstance( self._path, list )
      
      return len( self._path )
   
   def __add__( self, other ):
      assert isinstance( other, (TreePath,list,uuid.UUID) )
      #assert isinstance( other, (TreePath,str,unicode,list,uuid.UUID) )
      assert isinstance( self._path, list )
      
      if isinstance( other, TreePath ):
         return TreePath( self._path + other._path )
      elif isinstance( other, list ):
         return TreePath( self._path + other )
      elif isinstance( other, uuid.UUID ):
         newPath = copy.copy( self._path )
         newPath.append( other )
         return TreePath( newPath )
      else:
         raise Exception( 'Bad Type' )
      #if isinstance( other, TreePath ):
         #return TreePath( self._path + other._path )
      #elif isinstance( other, (str,unicode) ):
         #return TreePath( self._path + other.split( TreePath.SEPARATOR ) )
      #elif isinstance( other, list ):
         #return TreePath( self._path + other )
      #elif isinstance( other, uuid.UUID ):
         #newPath = copy.copy( self._path )
         #newPath.append( other )
         #return TreePath( newPath )
      #else:
         #raise Exception( 'Bad Type' )
   
   def __getitem__( self, idx ):
      assert isinstance( idx, int )
      assert isinstance( self._path, list )
      
      return self._path[ idx ]
   
   def __getslice__( self, fromIdx, toIdx ):
      assert isinstance( fromIdx,  int )
      assert isinstance( toIdx,    int )
      
      assert isinstance( self._path, list )
      
      return TreePath(self._path[fromIdx : toIdx])

   def parentPath( self ):
      assert isinstance( self._path, list )
      if len(self._path) == 0:
         raise InvalidPathError( "Can't get a parent path of an empty path." )
      
      return TreePath( self._path[0:-1] )
   
   def child( self ):
      assert isinstance( self._path, list )
      
      if len(self._path) == 0:
         raise InvalidPathError( "Can't get child path of empty path." )
      
      return self._path[-1]
   
   def isChildOf( self, aPath ):
      assert isinstance( aPath,   TreePath )
      
      if len(self) <= len(aPath):
         return False
      
      return self[ : len(aPath) ] == aPath

   def append( self, branchName ):
      assert isinstance( branchName, uuid.UUID )
      
      if branchName is None:
         return
      
      self._path.append( branchName )

   def pop( self, index=None ):
      assert isinstance( self._path, list )
      
      if index is None:
         return self._path.pop( )
      else:
         return self._path.pop( index )


class Tree( object ):
   BEFORE = 0
   AFTER  = 1
   CHILD  = 2

   def __init__( self, title = None, article = None, subtrees = None ):
      assert (title is None) or isinstance( title, (str,unicode) )
      assert (subtrees is None) or isinstance( subtrees, list )
      
      self.id       = uuid.uuid4()
      self.title    = None
      self.article  = None
      self.subtrees = None
      
      if title is not None:
         self.title = title
      else:
         self.title = ''
      
      if article is not None:
         self.article = article
      else:
         self.article = ''
      
      if subtrees is None:
         self.subtrees = []
      else:
         self.subtrees = subtrees

   def __str__( self ):
      assert isinstance( self.id,       uuid.UUID ) or ( self.id is None )
      assert isinstance( self.title,    (str,unicode) ) or ( self.title is None )
      assert isinstance( self.subtrees, list          )
      
      result = '(self.title ### self.article ### '
      if len( self.subtrees ) > 0:
         result += repr( self.subtrees )
      result += ')'
      return result

   def __iter__( self ):
      return iter( self.subtrees )
   
   def insert( self, aTree, aRefPath, aRelation=BEFORE ):
      """Insert aTree before, after or as a child of the node named by aRefPath.
      If a subtree with the same id as aTree already exists in the target
      location, an exception is raised.
      
      If 'aParentPath' is not found, KeyError is raised.
      """
      assert isinstance( aTree,     Tree     )
      assert isinstance( aRefPath,  TreePath )
      assert isinstance( aRelation, int      )
      
      assert isinstance( self.id,       uuid.UUID ) or ( self.id is None )
      assert isinstance( self.title,    (str,unicode) ) or ( self.title is None )
      assert isinstance( self.subtrees, list          )
      
      # Verify that aRefPath exists
      if self.subtree( aRefPath ) is None:
         raise InvalidPathError( )
      
      # Determine the new parent path
      if aRelation in ( Tree.BEFORE, Tree.AFTER ):
         newParentPath = aRefPath.parentPath( )
      else:
         newParentPath = aRefPath
      
      newParent = self.subtree( newParentPath )
      
      # Verify that the tree doesn't already exist
      if self.exists( newParentPath + aTree.id ):
         raise Exception( )
      
      # Perform the insertion
      if aRelation == Tree.BEFORE:
         siblingId = aRefPath.child()
         for idx in xrange(len(newParent.subtrees)):
            if newParent.subtrees[idx].id == siblingId:
               newParent.subtrees.insert( idx, aTree )
               return
      elif aRelation == Tree.AFTER:
         siblingId = aRefPath.child()
         if newParent.subtrees[-1].id == siblingId:
            newParent.subtrees.append( aTree )
         else:
            for idx in xrange(len(newParent.subtrees)-1):
               if newParent.subtrees[idx].id == siblingId:
                  newParent.subtrees.insert( idx+1, aTree )
                  return
      elif aRelation == Tree.CHILD:
         if len(newParent.subtrees) == 0:
            newParent.subtrees.append( aTree )
         else:
            newParent.subtrees.insert( 0, aTree )

   def remove( self, path, silent=True ):
      """Remove the item specified by aPath.  If the item is not in the
      tree, ValueError is raised.
      """
      assert isinstance( path, TreePath )
      
      assert isinstance( self.id,       uuid.UUID ) or ( self.id is None )
      assert isinstance( self.title,    (str,unicode) ) or ( self.title is None )
      assert isinstance( self.subtrees, list          )
      
      parentTree = self.subtree( path.parentPath( ) )
      childId    = path.child( )
      for idx in xrange( len(parentTree.subtrees) ):
         if parentTree.subtrees[ idx ].id == childId:
            del parentTree.subtrees[ idx ]
            return
      
      if silent:
         return
      else:
         raise InvalidPathError( )

   def subtree( self, path ):
      """Return the subtree specified by path.  If the subtree is not
      a member of the tree, None is returned.
      """
      assert isinstance( path, TreePath )
      
      assert isinstance( self.id,       uuid.UUID ) or ( self.id is None )
      assert isinstance( self.title,    (str,unicode) ) or ( self.title is None )
      assert isinstance( self.subtrees, list          )
      
      if len(path) == 0:
         return self
      else:
         soughtId = path[0]
         for sub in self.subtrees:
            if soughtId == sub.id:
               return sub.subtree( path[1:] )
         else:
            raise InvalidPathError( )

   #def subtree( self, path ):
      #"""Return the subtree specified by path.  If the subtree is not
      #a member of the tree, None is returned.
      #"""
      #assert isinstance( path, TreePath )
      
      #assert isinstance( self.id,       (str,unicode) ) or ( self.id is None )
      #assert isinstance( self.title,    (str,unicode) ) or ( self.title is None )
      #assert isinstance( self.subtrees, list          )
      
      #pathCopy = copy.copy( path )
      #return self._subtree( pathCopy )
   
   #def _subtree( self, path ):
      #"""Implementation of subtree( )."""
      #assert isinstance( self.id,       (str,unicode) ) or ( self.id is None )
      #assert isinstance( self.title,    (str,unicode) ) or ( self.title is None )
      #assert isinstance( self.subtrees, list          )
      
      #if len(path) == 0:
         #return self
      #else:
         #soughtId = path.pop( 0 )
         #for sub in self.subtrees:
            #if soughtId == sub.id:
               #return sub.subtree( path )
      
      #raise InvalidPathError( )

   def previousSiblingPath( self, path ):
      """Find and return the sibling that preceeds path."""
      assert isinstance( path, TreePath )
      
      assert isinstance( self.id,       (str,unicode,uuid.UUID) ) or ( self.id is None )
      assert isinstance( self.title,    (str,unicode) ) or ( self.title is None )
      assert isinstance( self.subtrees, list          )
      
      parentPath = path.parentPath( )
      soughtId  = path.child( )
      parentSubtree = self.subtree( parentPath )
      for idx in xrange( 1, len(parentSubtree.subtrees) ):
         if parentSubtree.subtrees[idx].id == soughtId:
            return parentPath + parentSubtree.subtrees[idx - 1].id
      
      raise InvalidPathError( 'The named path does not exist, or has no predecessor' )
   
   def nextSiblingPath( self, path ):
      """Find and return the sibling that follows that named by path."""
      assert isinstance( path, TreePath )
      
      assert isinstance( self.id,       (str,unicode,uuid.UUID) ) or ( self.id is None )
      assert isinstance( self.title,    (str,unicode) ) or ( self.title is None )
      assert isinstance( self.subtrees, list          )
      
      parentPath = path.parentPath( )
      soughtId  = path.child( )
      parentSubtree = self.subtree( parentPath )
      for idx in xrange( len(parentSubtree.subtrees) - 1 ):
         if parentSubtree.subtrees[idx].id == soughtId:
            return parentPath + parentSubtree.subtrees[idx + 1].id
      
      raise InvalidPathError( 'The named path does not exist, or has no sucessor' )
   
   def hasChildren( self ):
      return len(self.subtrees) > 0

   def children( self ):
      return self.subtrees
   
   def exists( self, path ):
      try:
         self.subtree( path )
         return True
      except:
         return False

   # Unused & Untested
   def branchInsert( self, parentPath, childIndex, newSubtree ):
      try:
         tree = self.subtree( parentPath )
         tree.subtrees.insert( childIndex, newSubtree )
      except:
         pass

   def branchRemove( self, parentPath, childIndex ):
      try:
         tree = self.subtree( parentPath )
         del tree.subtrees[ childIndex ]
      except:
         pass

   def branchLocation( self, path ):
      parentPath = path.parentPath()
      tree = self.subtree( parentPath )
      soughtId = path.child( )
      for idx in xrange( len(tree.subtrees) ):
         if tree.subtrees[idx].id == soughtId:
            return ( parentPath, idx )
      
      return None


class ForewardTreeIterator( object ):
   def __init__( self, aTree ):
      assert isinstance( aTree,    Tree )
      
      self._stack    = [ ]
      self._currTree = aTree
      self._childIdx = 0
      self._trPath   = None
   
   def __iter__( self ):
      return self
   
   def next( self ):
      if self._trPath is None:
         self._trPath = TreePath( )
         return ( self._currTree, self._trPath )
      elif len(self._currTree.subtrees) > 0:
         self._stack.append( [ self._currTree, copy.copy(self._trPath), self._childIdx ] )
         
         self._currTree = self._currTree.subtrees[ self._childIdx ]
         self._childIdx = 0
         self._trPath.append( self._currTree.id )
         
         return ( self._currTree, self._trPath )
      else:
         while True:
            try:
               self._currTree, self._trPath, self._childIdx = self._stack.pop( )
               self._childIdx += 1
            
            except:
               raise StopIteration
            
            try:
               self._stack.append( [ self._currTree, copy.copy(self._trPath), self._childIdx ] )
               
               self._currTree = self._currTree.subtrees[ self._childIdx ]
               self._childIdx = 0
               self._trPath.append( self._currTree.id )
               
               return ( self._currTree, self._trPath )
            except:
               self._currTree, self._trPath, self._childIdx = self._stack.pop( )
               self._childIdx += 1
