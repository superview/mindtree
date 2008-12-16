from __future__ import print_function, unicode_literals


import copy

class TagDefinition( object ):
   def __init__( self, name, **options ):
      assert isinstance( name,    (str,unicode) )
      assert isinstance( options, dict          )
      
      self._name    = name
      self._options = options

   def makeBeginTag( self ):
      assert isinstance( self._name,    (str,unicode) )
      assert isinstance( self._options, dict          )
      
      htmlOpenTagString = '<{0}'.format(self._name)
      
      for optName in self._options:
         assert isinstance( optName, (str,unicode) )
         optVal = self._options[ optName ]
         assert isinstance( optVal,  (str,unicode) )
         htmlOpenTagString += ' {0}={1}'.format(optName, optVal)
      
      htmlOpenTagString += '>'
      
      return htmlOpenTagString
   
   def makeEndTag( self ):
      return '</{0}>'.format( self._name )

   def name( self ):
      return self._name
   
   def options( self ):
      return self._options

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
      self._tags.discard( tag )

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
   
   def entity( self ):
      return self._entityDef

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

   def appendText( self, text ):
      self._text += text
   
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
   END = None
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

   SINGULAR_TAGS = {
      # Basic Styles
      'B':          (  1, TagDefinition( 'B' )          ),
      'I':          (  2, TagDefinition( 'I' )          ),
      'U':          (  3, TagDefinition( 'U' )          ),
      'STRIKE':     (  4, TagDefinition( 'STRIKE' )     ),
      'SUB':        (  5, TagDefinition( 'SUB' )        ),
      'SUP':        (  6, TagDefinition( 'SUP' )        ),
      'BLINK':      (  7, TagDefinition( 'BLINK' )      ),
      
      # Abstract Styles
      'ADDRESS':    ( 11, TagDefinition( 'ADDRESS' )    ),
      'BLOCKQUOTE': ( 12, TagDefinition( 'BLOCKQUOTE' ) ),
      'CENTER':     ( 13, TagDefinition( 'CENTER' )     ),
      'CITE':       ( 14, TagDefinition( 'CITE' )       ),
      'CODE':       ( 15, TagDefinition( 'CODE' )       ),
      'DEL':        ( 16, TagDefinition( 'DEL' )        ),
      'EM':         ( 17, TagDefinition( 'EM' )         ),
      'INS':        ( 18, TagDefinition( 'INS' )        ),
      'KBD':        ( 19, TagDefinition( 'KBD' )        ),
      'PRE':        ( 20, TagDefinition( 'PRE' )        ),
      'Q':          ( 21, TagDefinition( 'Q' )          ),
      'S':          ( 22, TagDefinition( 'S' )          ),
      'SAMP':       ( 23, TagDefinition( 'SAMP' )       ),
      'STRONG':     ( 24, TagDefinition( 'STRONG' )     )
      }
   
   TAG_ID_COUNT = 100
   
   def __init__( self ):
      self._tagDefs     = None
      self._elements    = None
      
      self.clear( )

   def clear( self ):
      '''Initialize the document.'''
      self._htmlHead = ''
      self._tagDefs  = { }   # map tag id to tag definition
      self._elements = [ HTMLSegment('') ]
      
      for tagName in HTMLDocument.SINGULAR_TAGS.keys():
         tagId, tagDef = HTMLDocument.SINGULAR_TAGS[ tagName ]
         self._tagDefs[ tagId ] = tagDef

   def setHtml( self, html ):
      '''Parse html in a string and set the content of the document.'''
      self.clear( )
      
      parser = HTMLDocumentParser( self )
      parser.feed( html )
      parser.close( )
   
   def setText( self, text ):
      self.clear( )
      
      self.insertText( 0, text )

   def __iter__( self ):
      return iter(self._elements)
   
   # Content Extraction
   def toHTML( self, fullDocument=True ):
      body = ''
      
      activeTags = set( )
      for element in self._elements:
         assert isinstance( element, HTMLElement )
         
         if isinstance( element, HTMLEntity ):
            body += element.toHTML( )
         else:
            body += self._segmentHtml( element, activeTags )
      
      for tagId in activeTags:
         body += self._tag[ tagId ].makeEndTag()
      
      if fullDocument:
         return HTMLDocument.HTML_FORMAT.format( head=self._htmlHead, body=body )
      else:
         return body

   def _segmentHtml( self, segment, activeTags ):
      assert isinstance( segment,    HTMLSegment )
      assert isinstance( activeTags, set         )
      
      result = ''
      
      segmentTags = segment.tags( )
      assert isinstance( segmentTags, set )
      
      # Close tags not in this segment
      closedTags = [ ]
      for tagId in activeTags:
         if tagId not in segmentTags:
            result += self._tagDefs[ tagId ].makeEndTag()
            closedTags.append( tagId )
      
      for tagId in closedTags:
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
      
      return result

   # Content Manipulation
   def insertText( self, pos, text ):
      '''Insert text at the position indicated by pos.  If pos is None,
      the text is appended to the document.
      '''
      assert isinstance( text, (str,unicode) )
      assert isinstance( pos,  int           ) or ( pos is None )
      
      elementNum,offset = self._elementAndOffset( pos )
      
      if offset == 0:
         # Special Case:  The inserted text should have the
         # tags of the previous element.  If the previous element is
         # just text, we'll just append that element.  If it's something
         # else, we'll insert a new text element with the same set of
         # tags as the previous element.
         if elementNum is None:
            previousElement = self._elements[ -1 ]
         else:
            previousElement = self._elements[ elementNum - 1 ]
         
         if isinstance( previousElement, HTMLSegment ):
            previousElement.appendText( text )
         else:
            newElement = HTMLSegment( text, previousElement.tags() )
            if elementNum is None:
               self._elements.append( newElement )
            else:
               self._elements.insert( elementNum, newElement )
      
      else:
         self._elements[elementNum].insertText( text, offset )
   
   def insertObject( self, pos, obj, setTagsFromContext=True ):
      '''Insert an HTMLElement at the position indicated by pos.  If pos
      is None, the element is appended to the document.
      '''
      assert isinstance( pos, int        ) or ( pos is None )
      
      elementNum,offset = self._elementAndOffset( pos )
      
      if offset == 0:
         # Special Case:  The inserted obj should have the
         # tags of the previous element.
         if elementNum is None:
            previousElement = self._elements[ -1 ]
         else:
            previousElement = self._elements[ elementNum - 1 ]
         
         if setTagsFromContext:
            obj.setTags( copy.copy(previousElement.tags()) )
         
         if elementNum is None:
            self._elements.append( obj )
         else:
            self._elements.insert( elementNum, obj )
      
      else:
         if setTagsFromContext:
            element = self._elements[ elementNum ]
            obj.setTags( copy.copy(element.tags()) )
         
         self._splitElement( elementNum, offset )
         
         objElementNum = elementNum + 1
         self._elements.insert( objElementNum, obj )
      
      # Compact the elements
      if elementNum is None:
         startCompact = len(self._elements) - 2
         stopCompact  = None
      else:
         startCompact = elementNum - 1
         stopCompact  = elementNum + 1
         
         if stopCompact >= len(self._elements):
            stopCompact = None
      
      if startCompact < 0:
         startCompact = 0
      
      self._compact( startCompact, stopCompact )

   def delete( self, pos1, pos2=None ):
      firstElementNum, lastElementNum = self._slice( pos1, pos2 )
      
      if lastElementNum is None:
         self._elements = self._elements[ : firstElementNum ]
      else:
         self._elements = self._elements[ firstElementNum : lastElementNum ]
      
      self._joinIfPossible( firstElementNum )

   # Tag Operations
   def defineTag( self, name, **options ):
      name = name.upper()
      
      if name in HTMLDocument.SINGULAR_TAGS:
         return HTMLDocument.SINGULAR_TAGS[ name ][ 0 ]
      
      assert isinstance( name,    (str,unicode) )
      assert isinstance( options, dict          )
      
      assert isinstance( self._tagDefs, dict )
      
      tagDef = TagDefinition( name, **options )
      tagId  = HTMLDocument.TAG_ID_COUNT
      HTMLDocument.TAG_ID_COUNT += 1
      
      assert isinstance( tagDef, TagDefinition )
      assert isinstance( tagId,  int           )
      
      self._tagDefs[ tagId ] = tagDef
      
      return tagId

   def applyTag( self, tagId, pos1, pos2=None ):
      '''Apply the tag indicated by tagId to the region indicated by pos1 & pos2.
      '''
      firstElementNum, lastElementNum = self._slice( pos1, pos2 )
      
      if lastElementNum is None:
         for element in self._elements[ firstElementNum : ]:
            element.addTag( tagId )
      else:
         for element in self._elements[ firstElementNum : lastElementNum ]:
            element.addTag( tagId )
      
      self._compact( firstElementNum, lastElementNum )
   
   def removeTag( self, tagId, pos1=None, pos2=None ):
      '''Remove the tag indicated by tagId from the region indicated by pos1 & pos2.
      If pos1 and pos2 are None, the tag is terminated at the point that is currently
      the end of the document.
      '''
      firstElementNum, lastElementNum = self._slice( pos1, pos2 )
      
      if lastElementNum is None:
         for element in self._elements[ firstElementNum : ]:
            element.removeTag( tagId )
      else:
         for element in self._elements[ firstElementNum : lastElementNum ]:
            element.removeTag( tagId )
      
      self._compact( firstElementNum, lastElementNum )

   def tagsAt( self, pos, ordered=False ):
      '''For the position indicated by pos, this method returns a list of
      tuples of the form (tagId,tagDef).  Which lists all the tags active
      at pos.
      
      If ordered is True, the list is returned such that tags at the beginning
      of the list are openned closer to pos than those later in the list.
      '''
      elementNum,offset = self._elementAndOffset( pos )
      
      if elementNum is None:
         result = list(self._elements[-1].tags())
      else:
         result = list(self._elements[elementNum].tags( ))
      
      if ordered:
         orderedResult = [ ]
         if len(self._elements) == 1:
            return result
         for eleNum in range( elementNum, -1, -1 ):
            ele = self._elements[eleNum]
            for tagId in ele.tags():
               if tagId in result:
                  orderedResult.append( tagId )
                  result.remove( tagId )
         return orderedResult
      else:
         return result

   def tag( self, tagId ):
      return self._tagDefs[ tagId ]

   def addTag( self, pos1, pos2=None, name=None, **options ):
      tagId = self.defineTag( name, **options )
      self.applyTag( tagId, pos1, pos2 )
      return tagId

   # Implementation
   def _elementAndOffset( self, pos ):
      '''Return the tuple ( elementNum, offset ) indicating the index of the 
      element in self._elements and offset into that element of pos.
      
      if pos is None or past the end of the document, ( None, 0 ) is returned.
      '''
      assert isinstance( pos,            int  ) or ( pos is None )
      assert isinstance( self._elements, list )
      
      if pos is None:
         return None, 0
      
      # All other cases
      segPos = 0
      for elementNum, element in enumerate(self._elements):
         eleLen = len(element)
         if pos < (segPos + eleLen):
            return elementNum, pos - segPos
         else:
            segPos += eleLen
      
      return None, 0

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
      try:
         first    = self._elements[elementNum]
         second   = self._elements[elementNum+1]
      except:
         return
      
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

   def _slice( self, pos1, pos2=None ):
      '''Return two element nums such that pos1 is the first position in
      the first element and pos2 is the first position after the second element.
      '''
      if pos2 is None:
         pos2 = pos1 + 1
      
      # Split at pos1
      firstElementNum,firstElementOffset = self._elementAndOffset( pos1 )
      
      if firstElementNum is None:
         raise Exception
      
      if firstElementOffset > 0:
         self._splitElement( firstElementNum, firstElementOffset )
         firstElementNum += 1
      
      # Split at pos2
      lastElementNum, lastElementOffset  = self._elementAndOffset( pos2 )
      if lastElementNum is not None:
         if lastElementOffset > 0:
            self._splitElement( lastElementNum, lastElementOffset )
            lastElementNum += 1
      
      return firstElementNum, lastElementNum
   
   def _compact( self, first, last=None ):
      '''Attempt to join adjacent elements within the range first,last inclusive.
      If last is None, the last element in the document is assumed.
      '''
      if last is None:
         last = len(self._elements) - 1
      
      if first >= last:
         return
      
      if first < 0:
         first = 0
      
      for idx in range( last, first-1, -1 ):
         self._joinIfPossible( idx )

   def debug( self ):
      # Elements
      for num,element in enumerate(iter(self)):
         tagList = element.tags()
         
         if isinstance( element, HTMLSegment ):
            elementType  = 'Txt'
            elementValue = element.text()
         elif isinstance( element, HTMLEntity ):
            elementType  = 'Img'
            elementValue = element.entity().makeBeginTag()
         
         print( '{0:>3}. {1}: {2}'.format( num, elementType, elementValue ) )
      
         for tagId in tagList:
            tagDef = self.tag( tagId )
            print( '     - ', self.tag(tagId).makeBeginTag() )


class HTMLDocumentCursor( object ):
   def __init__( self, document, pos ):
      assert isinstance( document, HTMLDocument )
      assert isinstance( pos,      int          ) or ( pos is None )
      
      self._doc           = document
      
      self._pos           = None
      self._anchor        = None
      
      self._activeTags    = None
      
      self.moveTo( pos )

   def document( self ):
      return self._doc
   
   def position( self ):
      return self._pos
   
   def moveTo( self, pos, moveAnchor=True ):
      '''Move the cursor to the specified location.  A pos of None indicates
      the end of the document.
      '''
      # Move the cursor
      self._pos = pos
      
      if moveAnchor:
         self._anchor = pos
      
      self._activeTags = self._doc.tagsAt( self._pos, ordered=True )

   def openTag( self, tagId ):
      '''Open the tag with the specified tagId.  If there is a selection,
      (i.e. anchor != pos) the tag is applied to the selection.
      '''
      if tagId not in self.activeTags:
         self._activeTags.append( tagId )
   
   def openNewTag( self, tagName, **options ):
      '''Convenience function for openNewTag.  This method first defines
      the tag then does an openTag().  The id of the newly created tag is
      returned.
      '''
      tagId = self._doc.defineTag( tagName, **options )
      
      if tagId not in self._activeTags:
         self._activeTags.insert( 0, tagId )
      
      return tagId
   
   def closeTag( self, tagId ):
      '''Close the specified tag.'''
      self._activeTags.remove( tagId )
   
   def closeAllTags( self ):
      self._activeTags = [ ]
   
   def insertText( self, text ):
      '''Insert text into the document at the point of the cursor using
      the active tags.  If there is a selection (anchor != pos), the
      selected text is first deleted.
      '''
      obj = HTMLSegment( text, self._activeTags )
      self.insertObject( obj, setTagsFromContext=False )
   
   def insertParagraph( self, closePreviousTags=True ):
      if closePreviousTags:
         self.closeAllTags( )
      
      obj = HTMLEntity( 'P' )
      self.insertObject( obj, setTagsFromContext=False )

   def insertObject( self, obj, setTagsFromContext=True ):
      if self._anchor != self._pos:
         self.delete( )
      
      self._doc.insertObject( self._pos, obj, setTagsFromContext )
      
      if isinstance( self._pos, int ):
         self._pos += len(obj)
   
   def backspace( self ):
      if self._anchor != self._pos:
         self._deleteSection( )
      elif self._pos is None:
         lastPos = len(self._doc) - 1
         self._doc.delete( lastPos )
      elif self._pos == 0:
         return
      else:
         self._pos -= 1
         self._doc.delete( self._pos )
         self._anchor = self._pos
   
   def delete( self ):
      if self._anchor != self._pos:
         self._deleteSection( )
      elif self._pos is None:
         return
      else:
         self._doc.delete( self._pos )

   def _deleteSection( self ):
      if self._anchor is None:
         fromPos = self._pos
         toPos   = None
      elif self._pos is None:
         fromPos = self._anchor
         toPos   = None
      else:
         fromPos = min( self._anchor, self._pos )
         toPos   = max( self._anchor, self._pos )
      
      self._doc.delete( fromPos, toPos )
      
      self.moveTo( fromPos )

   def activeTags( self ):
      '''Return the active tags ordered by locality of activation.
      (i.e. tags openned closest to the cursor are listed first)
      '''
      return copy.copy(self._activeTags)
   
   
import HTMLParser

class HTMLDocumentParser( HTMLParser.HTMLParser ):
   TAGS = {
      # Tag Name:    ( Supported, Block, Nest  )
      'A':           ( True,      True,  True ),
      'ADDRESS':     ( True,      True,  True ),
      'APPLET':      ( False,     True   ),
      'AREA':        ( False,     True   ),
      'B':           ( True,      True,  True ),
      'BASE':        ( False,     False  ),
      'BASEFONT':    ( False,     False  ),
      'BGSOUND':     ( False,     False  ),
      'BIG':         ( True,      True   ),
      'BLINK':       ( False,     True   ),
      'BLOCKQUOTE':  ( True,      True   ),
      'BODY':        ( True,      True   ),
      'BR':          ( True,      False  ),
      'BUTTON':      ( False,     False  ),
      'CAPTION':     ( False,     True   ),
      'CENTER':      ( True,      True  ),
      'CITE':        ( True,      True  ),
      'CODE':        ( True,      True  ),
      'COL':         ( False,     False ),
      'COLGROUP':    ( False,     False ),
      'DD':          ( True,      True , False ),
      'DEL':         ( False     ),
      'DFN':         ( True      ),
      'DIV':         ( True      ),
      'DL':          ( True      ),
      'DT':          ( True      ),
      'EM':          ( True      ),
      'EMBED':       ( False     ),
      'FIELDSET':    ( False     ),
      'FONT':        ( True      ),
      'FORM':        ( False     ),
      'FRAME':       ( False     ),
      'FRAMESET':    ( False     ),
      'H1':          ( True      ),
      'H2':          ( True      ),
      'H3':          ( True      ),
      'H4':          ( True      ),
      'H5':          ( True      ),
      'H6':          ( True      ),
      'HEAD':        ( True      ),
      'HR':          ( True      ),
      'HTML':        ( True      ),
      'I':           ( True      ),
      'IFRAME':      ( False     ),
      'IMG':         ( True      ),
      'INPUT':       ( False     ),
      'INS':         ( False     ),
      'KBD':         ( True      ),
      'LABEL':       ( False     ),
      'LAYER':       ( False     ),
      'LEGEND':      ( False     ),
      'LI':          ( True      ),
      'LINK':        ( False     ),
      'MAP':         ( False     ),
      'MARQUEE':     ( False     ),
      'META':        ( True      ),
      'NOBR':        ( True      ),
      'NOFRAMES':    ( False     ),
      'NOSCRIPT':    ( False     ),
      'OBJECT':      ( False     ),
      'OL':          ( True      ),
      'OPTGROUP':    ( False     ),
      'P':           ( True      ),
      'PRE':         ( True      ),
      'Q':           ( False     ),
      'S':           ( True      ),
      'SAMP':        ( True      ),
      'SCRIPT':      ( False     ),
      'SELECT':      ( False     ),
      'SMALL':       ( True      ),
      'SPAN':        ( True      ),
      'STRIKE':      ( False     ),
      'STRONG':      ( True      ),
      'STYLE':       ( False     ),
      'SUB':         ( True      ),
      'SUP':         ( True      ),
      'TABLE':       ( True      ),
      'TBODY':       ( True      ),
      'TD':          ( True      ),
      'TH':          ( True      ),
      'TEXTAREA':    ( False     ),
      'TFOOT':       ( True      ),
      'THEAD':       ( True      ),
      'TITLE':       ( True      ),
      'TR':          ( True      ),
      'TT':          ( True      ),
      'U':           ( True      ),
      'UL':          ( True      ),
      'WBR':         ( False     ),
      'VAR':         ( True      )
      }
   
   def __init__( self, htmlDoc ):
      HTMLParser.HTMLParser.__init__( self )
      
      self._doc            = htmlDoc
      self._cursor         = HTMLDocumentCursor( htmlDoc, None )

   def close( self ):
      HTMLParser.HTMLParser.close( self )
      self._doc._compact( 0 )

   def handle_starttag( self, tag, attrs ):
      print( 'Parsing begin tag:', tag )
      self._cursor.openNewTag( tag, **dict(attrs) )
   
   def handle_startendtag( self, tag, attrs ):
      print( 'Parsing begin/end tag:', tag )
      self._cursor.insertObject( HTMLEntity( tag, dict(attrs) ) )
   
   def handle_endtag( self, tag ):
      print( 'Parsing end tag:', tag )
      
      activeTags = self._cursor.activeTags()
      for idx in range( len(activeTags)-1, -1, -1 ):
         tagId = activeTags[ idx ]
         tagDef = self._doc.tag( tagId )
         if tagDef.name() == tag.upper():
            self._cursor.closeTag( tagId )
            break
      else:
         raise Exception( 'Unmatched end tag \'{0}\'.'.format(tag) )

   def handle_data( self, data ):
      print( 'Parsing data:', data )
      self._cursor.insertText( unicode(data) )
   
   def handle_charref( self, name ):
      pass
   
   def handle_entityref( self, name ):
      pass
   
   def handle_decl( self, decl ):
      pass
   
   def handle_pi( self, pi ):
      pass
   

doc = HTMLDocument( )
doc.setHtml( 'Here\'s <b>some<i> sample</B> text</i>.' )
doc.debug( )

#doc = HTMLDocument( )
#doc.insertText( None, 'Here\'s some sample text.' )
#boldTag   = doc.addTag(  7, 15, 'B' )
#italicTag = doc.addTag( 12, 20, 'I' )

#print( doc.toHTML(False) )
#doc.debug( )

#print( )
#print( 'Examining tags at 14' )
#tagList = doc.tagsAt( 14, ordered=True )
#for tagId in tagList:
   #tagDef = doc.tag(tagId)
   #print( tagDef.name( ) )

#print( )
#print( 'Removing bold from 12-15' )
#doc.removeTag( boldTag, 12, 15 )

#print( )
#print( doc.toHTML(False) )
#doc.debug( )


from PyQt4 import QtCore, QtGui

class HTMLEditor( object ):
   def __init__( self, parent ):
      self._editor = QtGui.QTextEdit( parent )
      self._document = HTMLDocument( )
      self._editor.installEventFilter( self )
      self._specialSelection = { }

   def setDocument( self, aDocument ):
      assert isinstance( aDocument, HTMLDocument )
      
      self._document = aDocument
      self.update( )

   def document( self ):
      return self._document

   def eventFilter( self, obj, event ):
      if isinstance(obj,QtGui.QLineEdit) and (event.type() == QtCore.QEvent.KeyPress):
         keyEvent = event
         key      = keyEvent.key()
         text     = keyEvent.text()
         if len(text) > 0:
            self.insertText( text )
         elif key == QtCore.Qt.Key_Tab:
            self.insertText( '\t' )
         elif key == QtCore.Qt.Key_Backspace:
            self.delete( back=True )
         elif key == QtCore.Qt.Key_Return:
            self.insertText( '\n' )
            insertParagraph( )
         elif key == QtCore.Qt.Key_Enter:
            self.insertText( '\n' )
            insertParagraph( )
         elif key == QtCore.Qt.Key_Delete:
            self.delete( )
         else:
            return False
      else:
         return False

   def textCursor( self ):
      return self._editor.textCursor()

   # Content Operations
   def insertText( self, text, cursor=None ):
      if cursor is None:
         cursor = self._editor.textCursor()
      
      assert isinstance( text,   (str,unicode)     )
      assert isinstance( cursor, QtGui.QTextCursor )
      
      anchor   = cursor.anchor()
      position = cursor.position()
      
      first = min(anchor,position)
      last  = max(anchor,position)
      
      if first != last:
         self._document.delete( first, last )
      
      self._document.insertText( text, first )
      
      self.update( )

   def delete( self, cursor, back=False ):
      if cursor is None:
         cursor = self._editor.textCursor()
      
      assert isinstance( text,   (str,unicode)     )
      assert isinstance( cursor, QtGui.QTextCursor )
      
      anchor   = cursor.anchor()
      position = cursor.position()
      
      first = min(anchor,position)
      last  = max(anchor,position)
      
      if first != last:
         self._document.delete( first, last )
      
      elif back:
         self._document.delete( first - 1, first )
      
      self.update( )

   # Tag Operations
   def applyTag( self, tag, options=None, cursor=None ):
      if cursor is None:
         cursor = self._editor.textCursor()
      
      assert isinstance( text,   (str,unicode)     )
      assert isinstance( cursor, QtGui.QTextCursor )
      
      anchor   = cursor.anchor()
      position = cursor.position()
      
      first = min(anchor,position)
      last  = max(anchor,position)
      
      tagId = self._document.defineTag( tag, options )
      
      self._document.applyTag( tagId, first, last )
      
      self.update( )
   
   def removeTag( self, tagId, cursor=None ):
      if cursor is None:
         cursor = self._editor.textCursor()
      
      assert isinstance( text,   (str,unicode)     )
      assert isinstance( cursor, QtGui.QTextCursor )
      
      anchor   = cursor.anchor()
      position = cursor.position()
      
      first = min(anchor,position)
      last  = max(anchor,position)
      
      if first != last:
         self._document.removeTag( tagId, first, last )
      else:
         self._document.removeTag( tagId, first )
   
   def tagsAt( self, cursor=None ):
      '''Returns a list of the active tag definitions at the cursor position.
      The anchor position is ignored.  The content returned is a list of tuples
      of the form (tagId,tagDef).
      
      These are the actual tag definitions in use.  Modifying them will change
      the underlying HTML document.
      '''
      if cursor is None:
         cursor = self._editor.textCursor()
      
      assert isinstance( text,   (str,unicode)     )
      assert isinstance( cursor, QtGui.QTextCursor )
      
      position = cursor.position()
      
      return self._document.tagsAt( position )
   
   # Special Selections
   def defineSpecialSelector( self, name, format ):
      specialSelection = QtGui.QTextEdit.ExtraSelection( )
      specialSelection.format = format
      self._selectors[ name ] = specialSelection

   def getSpecialSelector( self, name ):
      return self._textSelectors[name]

   def applySpecialSelector( self, name, cursor=None, moveUserCursor=True ):
      # Mark the text
      cursor = self._articleWidget.textCursor()
      cursor.setPosition( beginPos )
      cursor.setPosition( endPos, QtGui.QTextCursor.KeepAnchor )
      self._textSelectors[ name ].cursor = cursor
      self._articleWidget.setExtraSelections( [ self._textSelectors[name] ] )
      
      # Advance the cursor
      if moveUserCursor:
         cursor = self._articleWidget.textCursor()
         cursor.setPosition( endPos )
         self._articleWidget.setTextCursor( cursor )

   def showSelection( self, name, index, cursor=None, moveUserCursor=True ):
      self._outlineWidget.setCurrentIndex( index )
      
      if fromPos and toPos and name:
         self.applyTextSelector( fromPos, toPos, moveUserCursor, name )
   # Other Operations
   def update( self ):
      assert isinstance( self._editor, QtGui.QTextEdit )
      
      self._editor.setHtml( self._document.toHTML() )



