from unittest import *

from Tree import *


class TreePathTests( object ):
   def __init__( self ):
      pass
   
   def setupTestValues( self, elementList ):
      self.elements = elementList
      self.strVal   = TreePath.SEPARATOR.join( elementList )
      self.length   = len(elementList)
   
   def test__str__( self ):
      self.assertEqual( str(self.path), self.strVal )
   
   def test__repr__( self ):
      self.assertEqual( str(self.path), self.strVal )
   
   def test__eq__( self ):
      self.assertTrue( self.path == TreePath( self.elements ) )
   
   def test__ne__( self ):
      self.assertFalse( self.path != TreePath(self.elements) )
   
   def test__len__( self ):
      self.assert_( len(self.path) == self.length )
   
   def test__getitem__( self ):
      if len(self.elements) == 0:
         self.assertRaises( IndexError, self.path.__getitem__, 0 )
         self.assertRaises( IndexError, self.path.__getitem__, 1 )
         self.assertRaises( IndexError, self.path.__getitem__, -1 )
      else:
         for idx in range( self.length ):
            self.assertEqual( self.path[idx], self.elements[idx] )
   
   def test__getslice__( self ):
      result = TreePath.SEPARATOR.join( self.elements[ 0:10 ] )
      self.assertEqual( str(self.path.__getslice__( 0, 10 )), result )
   
   def testGetParentPath( self ):
      if self.length == 0:
         self.assertRaises( Exception, self.path.parentPath )
      else:
         result = TreePath.SEPARATOR.join( self.elements[ 0: -1 ] )
         self.assertEqual( str(self.path.parentPath()), result )
   
   def testGetChildName( self ):
      if self.length == 0:
         self.assertRaises( Exception, self.path.child )
      else:
         self.assertEqual( self.path.child(), self.elements[-1] )
   
   def testIsChildOf( self ):
      if self.length == 0:
         self.assertFalse( self.path.isChildOf( TreePath() ) )
      else:
         self.assertTrue( self.path.isChildOf( TreePath() ) )
   
   def testPop( self ):
      if self.length == 0:
         self.assertRaises( IndexError, self.path.pop )
      else:
         self.assertEqual( self.path.pop(), self.elements[-1] )
   
   def test__add__( self ):
      newList = self.path + TreePath()
      self.assertEqual( str(newList), TreePath.SEPARATOR.join(self.elements) )

   def test__append__( self ):
      self.path.append( '' )
      self.assertEqual( str(self.path), TreePath.SEPARATOR.join(self.elements) )

class NullArgTreePathUnitTest( TestCase, TreePathTests ):
   def __init__( self, *args, **kwargs ):
      TreePathTests.__init__( self )
      TestCase.__init__( self, *args, **kwargs )

   def setUp( self ):
      TreePathTests.setupTestValues( self, [ ] )
      self.path = TreePath( )

class EmptyStringTreePathUnitTest( TestCase, TreePathTests ):
   def __init__( self, *args, **kwargs ):
      TreePathTests.__init__( self )
      TestCase.__init__( self, *args, **kwargs )

   def setUp( self ):
      TreePathTests.setupTestValues( self, [ ] )
      self.path = TreePath( '' )

class EmptyUnicodeTreePathUnitTest( TestCase, TreePathTests ):
   def __init__( self, *args, **kwargs ):
      TreePathTests.__init__( self )
      TestCase.__init__( self, *args, **kwargs )

   def setUp( self ):
      TreePathTests.setupTestValues( self, [ ] )
      self.path = TreePath( u'' )

class EmptyListTreePathUnitTest( TestCase, TreePathTests ):
   def __init__( self, *args, **kwargs ):
      TreePathTests.__init__( self )
      TestCase.__init__( self, *args, **kwargs )

   def setUp( self ):
      TreePathTests.setupTestValues( self, [ ] )
      self.path = TreePath( [] )

class SingleElementStringTreePathUnitTest( TestCase, TreePathTests ):
   def __init__( self, *args, **kwargs ):
      TreePathTests.__init__( self )
      TestCase.__init__( self, *args, **kwargs )

   def setUp( self ):
      TreePathTests.setupTestValues( self, [ 'abc' ] )
      self.path = TreePath( 'abc' )

class SingleElementUnicodeTreePathUnitTest( TestCase, TreePathTests ):
   def __init__( self, *args, **kwargs ):
      TreePathTests.__init__( self )
      TestCase.__init__( self, *args, **kwargs )

   def setUp( self ):
      TreePathTests.setupTestValues( self, [ 'abc' ] )
      self.path = TreePath( u'abc' )

class SingleElementListTreePathUnitTest( TestCase, TreePathTests ):
   def __init__( self, *args, **kwargs ):
      TreePathTests.__init__( self )
      TestCase.__init__( self, *args, **kwargs )

   def setUp( self ):
      TreePathTests.setupTestValues( self, [ 'abc' ] )
      self.path = TreePath( [ 'abc' ] )


class MultiElementListTreePathUnitTest( TestCase, TreePathTests ):
   def __init__( self, *args, **kwargs ):
      TreePathTests.__init__( self )
      TestCase.__init__( self, *args, **kwargs )

   def setUp( self ):
      TreePathTests.setupTestValues( self, [ 'abc', 'xyz' ] )
      self.path = TreePath( [ 'abc', 'xyz' ] )

class MultiElementStringTreePathUnitTest( TestCase, TreePathTests ):
   def __init__( self, *args, **kwargs ):
      TreePathTests.__init__( self )
      TestCase.__init__( self, *args, **kwargs )

   def setUp( self ):
      TreePathTests.setupTestValues( self, [ 'abc', 'xyz' ] )
      self.path = TreePath( 'abc.xyz' )

class MultiElementUnicodeTreePathUnitTest( TestCase, TreePathTests ):
   def __init__( self, *args, **kwargs ):
      TreePathTests.__init__( self )
      TestCase.__init__( self, *args, **kwargs )

   def setUp( self ):
      TreePathTests.setupTestValues( self, [ 'abc', 'xyz' ] )
      self.path = TreePath( u'abc.xyz' )



