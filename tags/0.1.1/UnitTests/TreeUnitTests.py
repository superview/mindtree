from unittest import *
from Tree import *


class EmptyTreeTests( TestCase ):
   def setUp( self ):
      self.tree = Tree( )

   def test__iter__( self ):
      itr = iter(self.tree)
      self.assertRaises( StopIteration, itr.next )

   def testSubtree( self ):
      self.assertRaises( InvalidPathError, self.tree.subtree, TreePath('a') )

   def testPreviousSiblingPath( self ):
      self.assertRaises( InvalidPathError, self.tree.previousSiblingPath, TreePath('x') )

   def testNextSiblingPath( self ):
      self.assertRaises( InvalidPathError, self.tree.nextSiblingPath, TreePath('x') )

   def testHasChildren( self ):
      self.assertFalse( self.tree.hasChildren() )

   def testSubtrees( self ):
      self.assertEqual( self.tree.children(), [ ] )
   
   def testRemove( self ):
      self.assertRaises( InvalidPathError, self.tree.remove, TreePath('x.y.z') )
   
   def testInsert( self ):
      # Invalid Paths
      self.assertRaises( InvalidPathError, self.tree.insert, Tree(), TreePath( 'x.y.z'), Tree.BEFORE )
      self.assertRaises( InvalidPathError, self.tree.insert, Tree(), TreePath( 'x.y.z'), Tree.AFTER  )
      self.assertRaises( InvalidPathError, self.tree.insert, Tree(), TreePath( 'x.y.z'), Tree.CHILD  )
      
      # Invalid Relation
      self.assertRaises( InvalidPathError, self.tree.insert, Tree(), TreePath(), Tree.BEFORE )
      self.assertRaises( InvalidPathError, self.tree.insert, Tree(), TreePath(), Tree.AFTER  )
      
      # Good Insertion - Child
      try:
         child1     = Tree()
         self.tree.insert( child1, TreePath(), Tree.CHILD )
      except:
         self.fail( )
      
      # Good Insertion - After
      try:
         child2 = Tree()
         self.tree.insert( child2, TreePath( child1.id ), Tree.AFTER )
      except:
         self.fail( )
      
      # Good Insertion - Before
      try:
         child3 = Tree()
         self.tree.insert( child3, TreePath( child1.id ), Tree.BEFORE )
      except:
         self.fail( )
      
      # Test constructed tree
      children = self.tree.children()
      self.assertEqual( len(children), 3 )
      self.assertTrue( isinstance( children[0], Tree ) )
      self.assertTrue( isinstance( children[1], Tree ) )
      self.assertTrue( isinstance( children[2], Tree ) )
      
      self.assertTrue( children[0] is child3 )
      self.assertTrue( children[1] is child1 )
      self.assertTrue( children[2] is child2 )

class PopulatedTreeTests( TestCase ):
   def setUp( self ):
      Tree._nextId = 1
      tree01 = Tree('one')
      tree02 = Tree('two')
      tree03 = Tree('three')
      tree04 = Tree('four')
      tree05 = Tree('five')
      tree06 = Tree('six', '6', [tree01,tree02,tree03,tree04,tree05])
      tree07 = Tree('seven')
      tree08 = Tree('eight', '8', [tree07])
      tree09 = Tree('nine')
      tree10 = Tree('ten', '10', [tree08,tree09])
      self.tree = Tree('eleven', '11', [tree06,tree10])
   
   def testSubtree( self ):
      self.assertEqual( self.tree.subtree( TreePath('6.1') ).id,  '1'  )
      self.assertEqual( self.tree.subtree( TreePath('6.2') ).id,  '2'  )
      self.assertEqual( self.tree.subtree( TreePath('6.3') ).id,  '3'  )
      self.assertEqual( self.tree.subtree( TreePath('6.4') ).id,  '4'  )
      self.assertEqual( self.tree.subtree( TreePath('6.5') ).id,  '5'  )
      self.assertEqual( self.tree.subtree( TreePath('6') ).id,    '6'  )
      self.assertEqual( self.tree.subtree( TreePath('10.8.7') ).id, '7'  )
      self.assertEqual( self.tree.subtree( TreePath('10.8') ).id, '8'  )
      self.assertEqual( self.tree.subtree( TreePath('10.9') ).id, '9'  )
      self.assertEqual( self.tree.subtree( TreePath('10') ).id,   '10' )
      self.assertEqual( self.tree.subtree( TreePath() ).id,       '11' )

   def testPreviousSiblingPath( self ):
      self.assertRaises( InvalidPathError, self.tree.previousSiblingPath, TreePath('6.1') )
      self.assertEqual( str(self.tree.previousSiblingPath( TreePath('6.2') )), '6.1' )
      self.assertEqual( str(self.tree.previousSiblingPath( TreePath('6.3') )), '6.2' )
      self.assertEqual( str(self.tree.previousSiblingPath( TreePath('6.4') )), '6.3' )
      self.assertEqual( str(self.tree.previousSiblingPath( TreePath('6.5') )), '6.4' )
      self.assertRaises( InvalidPathError, self.tree.previousSiblingPath, TreePath('6') )
      self.assertRaises( InvalidPathError, self.tree.previousSiblingPath, TreePath('10.8.7') )
      self.assertRaises( InvalidPathError, self.tree.previousSiblingPath, TreePath('10.8') )
      self.assertEqual( str(self.tree.previousSiblingPath( TreePath('10.9') )), '10.8' )
      self.assertEqual( str(self.tree.previousSiblingPath( TreePath('10') )), '6' )
      self.assertRaises( InvalidPathError, self.tree.previousSiblingPath, TreePath() )
      
      # Bad input tree path
      self.assertRaises( InvalidPathError, self.tree.previousSiblingPath, TreePath('10.8.4') )

   def testNextSiblingPath( self ):
      self.assertEqual( str(self.tree.nextSiblingPath( TreePath('6.1') )), '6.2' )
      self.assertEqual( str(self.tree.nextSiblingPath( TreePath('6.2') )), '6.3' )
      self.assertEqual( str(self.tree.nextSiblingPath( TreePath('6.3') )), '6.4' )
      self.assertEqual( str(self.tree.nextSiblingPath( TreePath('6.4') )), '6.5' )
      self.assertRaises( InvalidPathError, self.tree.nextSiblingPath, TreePath('6.5') )
      self.assertEqual( str(self.tree.nextSiblingPath( TreePath('6') )), '10' )
      self.assertRaises( InvalidPathError, self.tree.nextSiblingPath, TreePath('10.8.7') )
      self.assertEqual( str(self.tree.nextSiblingPath( TreePath('10.8') )), '10.9' )
      self.assertRaises( InvalidPathError, self.tree.nextSiblingPath, TreePath('10.9') )
      self.assertRaises( InvalidPathError, self.tree.nextSiblingPath, TreePath('10') )
      self.assertRaises( InvalidPathError, self.tree.nextSiblingPath, TreePath() )
      
      # Bad input tree path
      self.assertRaises( InvalidPathError, self.tree.nextSiblingPath, TreePath('10.8.4') )

   def testHasChildren( self ):
      self.assertFalse( self.tree.subtree(TreePath('6.1')).hasChildren( ) )
      self.assertFalse( self.tree.subtree(TreePath('6.2')).hasChildren( ) )
      self.assertFalse( self.tree.subtree(TreePath('6.3')).hasChildren( ) )
      self.assertFalse( self.tree.subtree(TreePath('6.4')).hasChildren( ) )
      self.assertFalse( self.tree.subtree(TreePath('6.5')).hasChildren( ) )
      self.assertTrue(  self.tree.subtree(TreePath('6')).hasChildren( )   )
      self.assertFalse( self.tree.subtree(TreePath('10.8.7')).hasChildren( ) )
      self.assertTrue(  self.tree.subtree(TreePath('10.8')).hasChildren( ) )
      self.assertFalse( self.tree.subtree(TreePath('10.9')).hasChildren( ) )
      self.assertTrue(  self.tree.subtree(TreePath('10')).hasChildren( )  )
      self.assertTrue(  self.tree.subtree(TreePath()).hasChildren( ) )

   def subtreeIdsOfPath( self, path, subtreeIdList ):
      sub = [ tree.id for tree in self.tree.subtree(TreePath(path)).children() ]
      self.assertEqual( len(sub), len(subtreeIdList) )
      for id1,id2 in zip(sub,subtreeIdList):
         self.assertEqual( id1, id2 )
   
   def testSubtrees( self ):
      self.subtreeIdsOfPath( '6.1',    [] )
      self.subtreeIdsOfPath( '6.2',    [] )
      self.subtreeIdsOfPath( '6.3',    [] )
      self.subtreeIdsOfPath( '6.4',    [] )
      self.subtreeIdsOfPath( '6.5',    [] )
      self.subtreeIdsOfPath( '6',      ['1','2','3','4','5'] )
      self.subtreeIdsOfPath( '10.8.7', [] )
      self.subtreeIdsOfPath( '10.8',   ['7'] )
      self.subtreeIdsOfPath( '10.9',   [] )
      self.subtreeIdsOfPath( '10',     ['8','9'] )
      self.subtreeIdsOfPath( '',       ['6','10'] )

   def testInsert( self ):
      # Test Inserting before in a well populated subtree
      self.tree.insert( Tree(), TreePath('6.1'), Tree.BEFORE )
      self.subtreeIdsOfPath( '6', ['12','1','2','3','4','5'] )
      
      self.tree.insert( Tree(), TreePath('6.3'), Tree.BEFORE )
      self.subtreeIdsOfPath( '6', ['12','1','2','13','3','4','5'] )
      
      self.tree.insert( Tree(), TreePath('6.5'), Tree.BEFORE )
      self.subtreeIdsOfPath( '6', ['12','1','2','13','3','4','14','5'] )
      
      # Test Inserting after in a well populated subtree
      self.tree.insert( Tree(), TreePath('6.12'), Tree.AFTER )
      self.subtreeIdsOfPath( '6', ['12','15','1','2','13','3','4','14','5'] )
      
      self.tree.insert( Tree(), TreePath('6.3'), Tree.AFTER )
      self.subtreeIdsOfPath( '6', ['12','15','1','2','13','3','16','4','14','5'] )
      
      self.tree.insert( Tree(), TreePath('6.5'), Tree.AFTER )
      self.subtreeIdsOfPath( '6', ['12','15','1','2','13','3','16','4','14','5','17'] )
      
      # Test inserting child in well populated subtree
      self.tree.insert( Tree(), TreePath('6'), Tree.CHILD )
      self.subtreeIdsOfPath( '6', ['18','12','15','1','2','13','3','16','4','14','5','17'] )
      
      # Test inserting child in an empty subtree
      self.tree.insert( Tree(), TreePath('6.15'), Tree.CHILD )
      self.subtreeIdsOfPath( '6.15', ['19'] )
      
      # Test inserting child into the root
      self.tree.insert( Tree(), TreePath(), Tree.CHILD )
      self.subtreeIdsOfPath( '',       ['20','6','10'] )
      
      # Test inserting child into invalid reference path
      self.assertRaises( InvalidPathError, self.tree.insert, Tree(), TreePath('6.15.8'), Tree.CHILD )
      self.assertRaises( InvalidPathError, self.tree.insert, Tree(), TreePath('6.15.8'), Tree.AFTER )
      self.assertRaises( InvalidPathError, self.tree.insert, Tree(), TreePath('6.15.8'), Tree.BEFORE )

   def testRemove( self ):
      # Try removing invalid path
      self.assertRaises( InvalidPathError, self.tree.remove, TreePath('6.3.12'), False )
      
      # Try removing empty tree
      try:
         self.tree.remove( TreePath('10.8'), False )
         self.subtreeIdsOfPath( '10', ['9'] )
      except:
         self.fail( )
      
      # Try removing tree with children
      try:
         self.tree.remove( TreePath('10'), False )
         self.subtreeIdsOfPath( '', ['6'] )
      except:
         self.fail( 'failed' )
      
      # Try removing only child of root
      try:
         self.tree.remove( TreePath('6'), False )
         self.subtreeIdsOfPath( '', [] )
      except:
         self.fail( 'failed' )
      
      # Try removing root
      self.assertRaises( InvalidPathError, self.tree.remove, TreePath(''), False )


if __name__ == '__main__':
   main()
