from unittest import *
from HtmlDocument import *


class EmptyDocumentTests( TestCase ):
   def setUp( self ):
      self._doc = HTMLDocument( )
   
   def testEmptyDocContents( self ):
      for ct,element in enumerate(self._doc):
         self.assertEqual( ct, 0 )
         self.assert_( isinstance(element, HTMLSegment) )

   def testToText( self ):
      self.assertEqual( self._doc.toText( ), '' )
   
   def testDelete( self ):
      self._doc.delete( 0 )
      self.testEmptyDocContents( )
   
   def testElementAndOffset( self ):
      eleNum, offset = self._doc._elementAndOffset( 0 )
      
      self.assert_( eleNum is None )
      self.assert_( offset is None )
      
      eleNum, offset = self._doc._elementAndOffset( 10 )
      
      self.assert_( eleNum is None )
      self.assert_( offset is None )


class StringContentTests( TestCase ):
   def setUp( self ):
      self._doc = HTMLDocument( )
   
   def testInsert( self ):
      self._doc.clear( )
      
      self._doc.insertText( 'one two three', 0 )
      self.assertEqual( len(self._doc._elements), 1 )
      self.assert_( isinstance(self._doc._elements[0],HTMLSegment) )
      self.assertEqual( len(self._doc._elements[0].tags()), 0 )
      
      self._doc.insertText( '1 ', 4 )
      self.assertEqual( len(self._doc._elements), 1 )
      self.assert_( isinstance(self._doc._elements[0],HTMLSegment) )
      self.assertEqual( len(self._doc._elements[0].tags()), 0 )
      
      self.assertEqual( self._doc.toText(), 'one 1 two three' )
   
   def testTagBeginning( self ):
      self._doc.clear( )
      
      self._doc.insertText( 'one two three', 0 )
      
      tagId = self._doc.defineTag( 'B' )
      self._doc.applyTag( tagId, 0, 3 )
      
      self.assertEqual( self._doc.toHTML(False), '<B>one</B> two three' )
   
   def testTagEnding( self ):
      self._doc.clear( )
      
      self._doc.insertText( 'one two three', 0 )
      
      tagId = self._doc.defineTag( 'B' )
      self._doc.applyTag( tagId, 8, 13 )
      
      self.assertEqual( self._doc.toHTML(False), 'one two <B>three</B>' )
