import os


def stringSplice( aBaseString, aBegPos, anEndPos, aNewSubStr ):
   return ''.join( ( aBaseString[ : aBegPos ], aNewSubStr, aBaseString[ anEndPos : ] ) )


class Buffer:
   def __init__( self, buf ):
      self.buf   = buf
      self.point = 0

   def substitute( self, aNewSubstring, aMark ):
      self.buf = ''.join( ( self.buf[ : aMark ], aNewSubstring, self.buf[ self.point : ] ) )

   def getSubString( self, aMark ):
      return self.buf[ aMark : self.point ]

   def more( self ):
      return self.point < len( self.buf )

   def peek( self ):
      return self.buf[ self.point ]

   def consumeString( self, aStr ):
      if self.buf.startswith( aStr, self.point ):
         self.point += len( aStr )
         return True
      else:
         return False
       
   def consumeRegEx( self, regEx ):
      match = regEx.match( self.buf, self.point )
      if match:
         self.point = match.span( )[1]
         return True
      else:
         return False

   def consumeUpTo( self, regEx ):
      match = regEx.search( self.buf, self.point )
      if match:
         self.point = match.span( )[0]
         return True
      else:
         return False

   def consumePast( self, regEx ):
      while self.consumeRegEx( regEx ):
         pass


class Scanner:
   def __init__( self, tokenMap ):
      assert isinstance( tokenMap, dict )
      self._tokenMap = tokenMap
      self._buf      = None
      self._next     = None
   
   def prepare( self, aString ):
      assert isinstance( self._tokenMap, dict )
      assert isinstance( aString, ( str,unicode ) )
      self._buf = Buffer( aString )
      self.consume( )
   
   def peek( self ):
      assert isinstance( self._tokenMap, dict )
      assert isinstance( self._buf, Buffer )
      assert isinstance( self._next, int )
      return self._next
   
   def consume( self ):
      pass
   
   def expect( self, aTok ):
      pass


def matchOne( regExSeq, buffer ):
   return regExSeqIdx
   #additionally, buffer will have been mutated such that
      #[ buffer.mark : buffer.point ] is the slice containing the matched
      #substr.

def searchOne( regExSeq, buffer ):
   #Just like matchOne, but the matched substring need not be at the
   #beginning of the buffer.


