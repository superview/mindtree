from uuid import uuid4, UUID
import copy

class TagDefinition( object ):
   def __init__( self, name, options=None ):
      if options is None:
         options = { }
      
      assert isinstance( name,    (str,unicode) )
      assert isinstance( options, dict          )
      
      self._name    = name
      self._options = options

   def makeBeginTag( self ):
      assert isinstance( self._name,    (str,unicode) )
      assert isinstance( self._options, dict          )
      
      htmlOpenTagString += '<{0}'.format(self._name)
      
      for optName in self._options:
         assert isinstance( optName, (str,unicode) )
         optVal = self._options[ optName ]
         assert isinstance( optVal,  (str,unicode) )
         htmlOpenTagString += ' {0}={1}'.format(optName, optVal)
      
      htmlOpenTagString += '>'
      
      return htmlOpenTagString
   
   def makeEndTag( self ):
      return '</{0}>'.format( self._name )


class HTMLElement( object ):
   def __init__( self, tags=None ):
      self.setTags( tags )
   
   def tags( self ):
      return self._tags

   def __len__( self ):
      return 0

   def addTag( self, tag ):
      self._tags.add( tag )

   def removeTag( self, tag ):
      self._tag.discard( tag )

   def setTags( self, tags=None ):
      if tags is None:
         tags = set( )
      else:
         tags = set( tags )
      
      self._tags = tags


class HTMLEntity( HTMLElement ):
   def __init__( self, name, options=None, tags=None ):
      HTMLElement.__init__( self, tags )
      self._entityDef = TagDefinition( name, options )
   
   def __len__( self ):
      return 1

class HTMLSegment( HTMLElement ):
   def __init__( self, text='', tags=None ):
      HTMLElement.__init__( self, tags )
      
      self._text = text

   def __len__( self ):
      return len( self._text )

   def text( self ):
      return self._text

   def setText( self, text ):
      self._text = text

   def insertText( self, text, offset=None ):
      assert isinstance( text,   (str,unicode) )
      assert isinstance( offset, int           ) or ( offset is None )
      
      if offset is None:
         self._text += text
      else:
         self._text = self._text[ : offset ] + text + self._text[ offset : ]

   def deleteText( self, pos1, pos2=None ):
      if pos2 is None:
         pos2 = pos1 + 1
      
      assert isinstance( pos1, int )
      assert isinstance( pos2, int )
      
      self._text = self._text[ : pos1 ] + self._text[ pos2 : ]

   def split( self, offset ):
      '''Split this segment such that the text in this segment include
      all the text up to (but not including) offset.  The new HTMLSegment
      then includes everything from offset to the end of the segment.
      
      The two resulting segment objects are returned as a tuple.  If one
      of the segment objects is not created None is returned in its place.
      '''
      assert isinstance( offset, int )
      
      if offset >= len(self):
         return self, None
      
      if offset == 0:
         return None, self
      
      newNodeText = self._text[ offset : ]
      newNodeTags = copy.copy( self._tags )
      
      self._text = self._text[ : offset ]
      
      return self, HTMLSegment( newNodeText, newNodeTags )

class HTMLDocument( object ):
   HTML_FORMAT = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
   <head>
      {head}
   </head>

   <body>
      {body}
   </body>
</html>
'''

   def __init__( self ):
      self._htmlHead    = ''
      
      self._tagDefs     = { }   # map tag id to tag definition
      self._elements    = [ ]

   def setContent( self, html ):
      pass

   def toHTML( self ):
      body = ''
      
      activeTags = set( )
      for element in self._elements:
         assert isinstance( element, HTMLElement )
         
         if isinstance( element, HTMLEntity ):
            body += element.toHTML( )
         else:
            body += self._segmentHtml( element, activeTags )
      
      return HTMLDocument.HTML_FORMAT.format( head=self._htmlHead, body=body )

   def _segmentHtml( self, segment, activeTags ):
      assert isinstance( segment,    HTMLSegment )
      assert isinstance( activeTags, set         )
      
      result = ''
      
      segmentTags = segment.tags( )
      assert isinstance( segmentTags, set )
      
      # Close tags not in this segment
      for tagId in activeTags:
         if tagId not in segmentTags:
            result += self._tagDefs[ tagId ].makeEndTag()
            activeTags.remove( tagId )
      
      # Open tags in this segment
      for tagId in segmentTags:
         if tagId not in activeTags:
            result += self._tagDefs[ tagId ].makeBeginTag()
            activeTags.add( tagId )
      
      # Insert the text
      return result + segment.text()
   
   def toText( self ):
      result = ''
      
      for segment in self._elements:
         if isinstance( segment, HTMLSegment ):
            result += segment.text()

   def insertText( self, text, pos ):
      assert isinstance( text, (str,unicode) )
      assert isinstance( pos,  int           )
      
      elementNum,offset = self._elementAndOffset( pos )
      
      if elementNum is None:
         if offset == 1:
            # We're just appending text
            lastEle = self._elements[ -1 ]
            if isinstance( lastEle, HTMLSegment ):
               insertText( text )
            else:
               tags = copy.copy( lastEle.tags() )
               element = HTMLSegment( text, tags )
               self._elements.append( segment )
         
         else:
            raise Exception
      
      else:
         self._elements[elementNum].insertText( text, offset )
   
   def insertObject( self, obj, pos ):
      assert isinstance( obj, HTMLEntity )
      assert isinstance( pos, int        )
      
      elementNum,offset = self._elementAndOffset( pos )
      
      if element is None:
         if offset == 1:
            # We're just appending
            lastEle = self._elements[ -1 ]
            tags = copy.copy( lastEle.tags() )
            obj.setTags( tags )
            self._elements.append( obj )
         
         else:
            raise Exception
      
      else:
         element = self._elements[ elementNum ]
         
         objectTags = copy.copy( element.tags() )
         obj.setTags( objectTags )
         
         self._splitElement( elementNum, offset )
         
         objElementNum = elementNum + 1
         self._elements.insert( objElementNum, obj )

   def delete( self, pos1, pos2=None ):
      if pos2 is None:
         pos2 = pos1 + 1
      
      assert isinstance( pos1, int )
      assert isinstance( pos2, int )
      
      from_elementNum,from_offset = self._elementAndOffset( pos1 )
      to_elementNum,to_offset     = self._elementAndOffset( pos2 )
      
      # delete all intermediate elements
      numIntermediateElements = to_elementNum - (from_elementNum+1)
      if numIntermediateElements >= 1:
         for ct in range( 0, numIntermediateElements ):
            del self._elements[ from_elementNum + 1 ]
      
      # Any text remaining to be deleted is in the adjacent
      # elements from_elementNum and from_elementNum+1
      to_elementNum = from_elementNum + 1
      
      # Delete the text from the second element
      toElement = self._elements[to_elementNum]
      toElement.deleteText( 0, to_offset )
      
      # Delete the text from the first element
      fromElement = self._elements[from_elementNum]
      fromElement.deleteText( from_offset, len(fromElement) )
      
      # Try to merge elements
      self._joinIfPossible( from_elementNum, to_elementNum )

   def applyTag( self, tag, pos1, pos2=None ):
      if pos2 is None:
         pos2 = pos1 + 1
      
      assert isinstance( pos1, int )
      assert isinstance( pos2, int )
      
      from_elementNum,from_offset = self._elementAndOffset( pos1 )
      to_elementNum,to_offset     = self._elementAndOffset( pos2 )
      
      # Apply the tag to all intermediate elements
      numIntermediateElements = to_elementNum - (from_elementNum+1)
      if numIntermediateElements >= 1:
         for ct in range( 0, numIntermediateElements ):
            self._elements[ from_elementNum + ct ].addTag( tag )
      
      # Apply to the last element (splitting if necessary)
      if tag not in self._elements[ to_elementNum ].tags():
         # Split the toElement and apply the tag to the first element
         result = self._splitElement( to_elementNum, to_offset )
         if result:
            result[0].addTag( tag )
      
      # Apply to the first element (splitting if necessary)
      if tag not in self._elements[ from_elementNum ].tags():
         result = self._splitElement( from_elementNum, from_offset )
         if result:
            result[1].addTag( tag )
      
      # Of all the segments touched, see what can be joined.
      for ct in range( 0, to_elementNum - from_elementNum ):
         self._joinIfPossible( to_elementNum - ct )
      
      self._joinIfPossible( from_elementNum - 1 )

   def removeTag( self, tag, pos1, pos2=None ):
      if pos2 is None:
         pos2 = pos1 + 1
      
      assert isinstance( pos1, int )
      assert isinstance( pos2, int )
      
      from_elementNum,from_offset = self._elementAndOffset( pos1 )
      to_elementNum,to_offset     = self._elementAndOffset( pos2 )
      
      # Remove the tag from all intermediate elements
      numIntermediateElements = to_elementNum - (from_elementNum+1)
      if numIntermediateElements >= 1:
         for ct in range( 0, numIntermediateElements ):
            self._elements[ from_elementNum + ct ].removeTag( tag )
      
      # Remove from the last element (splitting if necessary)
      if tag in self._elements[ to_elementNum ].tags():
         # Split the toElement and apply the tag to the first element
         result = self._splitElement( to_elementNum, to_offset )
         if result:
            result[0].removeTag( tag )
      
      # Remove from the first element (splitting if necessary)
      if tag in self._elements[ from_elementNum ].tags():
         # Split the fromElement and apply the tag to the second element
         result = self._splitElement( from_elementNum, from_offset )
         if result:
            result[1].removeTag( tag )
      
      # Of all the segments touched, see what can be joined.
      for ct in range( 0, to_elementNum - from_elementNum ):
         self._joinIfPossible( to_elementNum - ct )
      
      self._joinIfPossible( from_elementNum - 1 )

   def defineTag( self, name, options=None ):
      if option is None:
         options = { }
      
      assert isinstance( name,    (str,unicode) )
      assert isinstance( options, dict          )
      
      assert isinstance( self._tagDefs, dict )
      
      tagDef = TagDefinition( name, options )
      tagId  = uuid4( ).bytes
      
      assert isinstance( tagDef, TagDefinition )
      assert isinstance( tagId,  bytes         )
      
      self._tagDefs[ tagId ] = tagDef
      
      return tagId

   def undefTag( self, tagId ):
      assert isinstance( tagId, bytes )
      
      assert isinstance( self._tagDefs, dict )
      
      del self._tagDefs[ tagId ]
   
   def _elementAndOffset( self, pos ):
      '''Return the tuple ( elementNum, offset ) indicating the index of the 
      element in self._elements and offset into that element of pos.
      
      if pos is past the end of the document, the elementNum returned is None,
      and offset is the number of characters past the end of the document.
      '''
      assert isinstance( pos,            int  )
      assert isinstance( self._elements, list )
      
      segPos = 0
      for elementNum, element in enumerate(self._elements):
         eleLen = len(element)
         if pos < (segPos + eleLen):
            return elementNum, pos - segPos
         else:
            segPos += eleLen
      
      return None, pos - segPos

   def _splitElement( self, elementNum, offset ):
      '''Split this element at offset.  Insert the two new elements into the
      list in sequence in the location where elementNum was originally.
      
      Return the two new elements as a tuple.  If the split was unsuccessful
      None will be returned.
      '''
      element = self._elements[ elementNum ]
      
      assert isinstance( element, HTMLSegment )
      
      first,second = element.split( offset )
      
      if (first is not None) and (second is not None):
         newElementNum = elementNum + 1
         self._elements.insert( newElementNum, second )
         return first,second
      
      return None

   def _joinIfPossible( self, elementNum ):
      '''Attempt to join the element indicated by elementNum with its successor.
      
      Return True if the join succeeded otherwise False.
      
      If one or both of the elements is empty, the element will be deleted and
      the join will be considered successful.
      '''
      first    = self._elements[elementNum]
      second   = self._elements[elementNum+1]
      
      # If one of the elements is not a segment return False
      if not isinstance( first, HTMLSegment ):
         return False
      
      if not isinstance( second, HTMLSegment ):
         return False
      
      # If one of the segments is empty delete it and return True
      result = False
      
      if len(second) == 0:
         del self._elements[elementNum+1]
         result = True
      
      if len(first) == 0:
         del self._elements[elementNum]
         result = True
      
      if result:
         return True
      
      # If the tags of the two elements are identical, merge the text into
      # the first and delete the second.
      if first.tags() == second.tags():
         first.setText( first.text() + second.text() )
         del self._elements[elementNum + 1]
         return True
      
      return False


