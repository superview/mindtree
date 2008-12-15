from __future__ import print_function, unicode_literals


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

   SINGULAR_TAGS = {
      'ADDRESS':    (  1, TagDefinition( 'ADDRESS' )    ),
      'B':          (  2, TagDefinition( 'B' )          ),
      'BLINK':      (  3, TagDefinition( 'BLINK' )      ),
      'BLOCKQUOTE': (  4, TagDefinition( 'BLOCKQUOTE' ) ),
      'CENTER':     (  5, TagDefinition( 'CENTER' )     ),
      'CITE':       (  6, TagDefinition( 'CITE' )       ),
      'CODE':       (  7, TagDefinition( 'CODE' )       ),
      'DEL':        (  8, TagDefinition( 'DEL' )        ),
      'EM':         (  9, TagDefinition( 'EM' )         ),
      'I':          ( 10, TagDefinition( 'I' )          ),
      'INS':        ( 11, TagDefinition( 'INS' )        ),
      'KBD':        ( 12, TagDefinition( 'KBD' )        ),
      'PRE':        ( 13, TagDefinition( 'PRE' )        ),
      'Q':          ( 14, TagDefinition( 'Q' )          ),
      'S':          ( 15, TagDefinition( 'S' )          ),
      'SAMP':       ( 16, TagDefinition( 'SAMP' )       ),
      'STRIKE':     ( 17, TagDefinition( 'STRIKE' )     ),
      'STRONG':     ( 18, TagDefinition( 'STRONG' )     ),
      'SUB':        ( 19, TagDefinition( 'SUB' )        ),
      'SUP':        ( 20, TagDefinition( 'SUP' )        ),
      'U':          ( 21, TagDefinition( 'U' )          )
      }
   
   TAG_ID_COUNT = 1000
   
   def __init__( self ):
      self._htmlHead    = None
      self._tagDefs     = None
      self._elements    = None
      
      self.clear( )

   def clear( self ):
      '''Initialize the document.'''
      self._htmlHead = ''
      self._tagDefs  = { }   # map tag id to tag definition
      self._elements = [ HTMLSegment('') ]
      
      for tagId,tagDef in HTMLDocument.SINGULAR_TAGS:
         self._tagDefs[ tagId ] = tagDef

   def setContent( self, html ):
      '''Parse html in a string and set the content of the document.'''
      pass

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

   # Content Manipulateion
   def insertText( self, text, pos ):
      assert isinstance( text, (str,unicode) )
      assert isinstance( pos,  int           )
      
      elementNum,offset = self._elementAndOffset( pos )
      
      if elementNum is None:
         # We're just appending text
         lastEle = self._elements[ -1 ]
         if isinstance( lastEle, HTMLSegment ):
            lastEle.insertText( text )
         else:
            tags = copy.copy( lastEle.tags() )
            element = HTMLSegment( text, tags )
            self._elements.append( segment )
      
      else:
         self._elements[elementNum].insertText( text, offset )
   
   def insertObject( self, obj, pos ):
      assert isinstance( obj, HTMLEntity )
      assert isinstance( pos, int        )
      
      elementNum,offset = self._elementAndOffset( pos )
      
      if element is None:
         # We're just appending
         lastEle = self._elements[ -1 ]
         tags = copy.copy( lastEle.tags() )
         obj.setTags( tags )
         self._elements.append( obj )
      
      else:
         element = self._elements[ elementNum ]
         
         objectTags = copy.copy( element.tags() )
         obj.setTags( objectTags )
         
         self._splitElement( elementNum, offset )
         
         objElementNum = elementNum + 1
         self._elements.insert( objElementNum, obj )

   def delete( self, pos1, pos2=None ):
      firstElementNum, lastElementNum = self.slice( pos1, pos2 )
      
      if lastElementNum is None:
         self._elements = self._elements[ : firstElementNum ]
      else:
         self._elements = self._elements[ firstElementNum : lastElementNum ]

   # Tag Operations
   def defineTag( self, name, options=None ):
      name = name.upper()
      
      if name in HTMLDocument.SINGULAR_TAGS:
         return HTMLDocument.SINGULAR_TAGS[ name ][ 0 ]
      
      if options is None:
         options = { }
      
      assert isinstance( name,    (str,unicode) )
      assert isinstance( options, dict          )
      
      assert isinstance( self._tagDefs, dict )
      
      tagDef = TagDefinition( name, options )
      tagId  = HTMLDocument.TAG_ID_COUNT
      HTMLDocument.TAG_ID_COUNT += 1
      
      assert isinstance( tagDef, TagDefinition )
      assert isinstance( tagId,  int           )
      
      self._tagDefs[ tagId ] = tagDef
      
      return tagId

   def applyTag( self, tagId, pos1=None, pos2=None ):
      '''Apply the tag indicated by tagId to the region indicated by pos1 & pos2.
      If pos1 and pos2 are None, the tag is begun at the point that is currently
      the end of the document.
      '''
      if pos1 is None:
         last = self._elements[ -1 ]
         if (last is HTMLSegment) and (len(last) == 0):
            last.addTag( tagId )
         else:
            last = HTMLSegment( '', copy.copy(last.tags()) )
            last.addTag( tagId )
            self._elements.append( last )
         
         return
      
      firstElementNum, lastElementNum = self.slice( pos1, pos2 )
      
      if lastElementNum is None:
         for element in self._elements[ firstElementNum : ]:
            element.addTag( tagId )
      else:
         for element in self._elements[ firstElementNum : lastElementNum ]:
            element.addTag( tagId )
   
   def removeTag( self, tagId, pos1=None, pos2=None ):
      '''Remove the tag indicated by tagId from the region indicated by pos1 & pos2.
      If pos1 and pos2 are None, the tag is terminated at the point that is currently
      the end of the document.
      '''
      if pos1 is None:
         last = self._elements[ -1 ]
         if (last is HTMLSegment) and (len(last) == 0):
            last.removeTag( tagId )
         else:
            last = HTMLSegment( '', copy.copy(last.tags()) )
            last.removeTag( tagId )
            self._elements.append( last )
         
         return
      
      firstElementNum, lastElementNum = self.slice( pos1, pos2 )
      
      if lastElementNum is None:
         for element in self._elements[ firstElementNum : ]:
            element.removeTag( tagId )
      else:
         for element in self._elements[ firstElementNum : lastElementNum ]:
            element.removeTag( tagId )

   def tagsAt( self, pos, order=False ):
      '''For the position indicated by pos, this method returns a list of
      tuples of the form (tagId,tagDef).  Which lists all the tags active
      at pos.
      '''
      element,offset = self._elementAndOffset( pos )
      tagIds = element.tags( )
      
      result = [ ]
      for tagId in tagIds:
         result.append( (tagId, self._tagDefs[tagId]) )
      
      if order:
         orderedResult = [ ]
         for eleNum in range( element, -1, -1 ):
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

   # Implementation
   def _elementAndOffset( self, pos ):
      '''Return the tuple ( elementNum, offset ) indicating the index of the 
      element in self._elements and offset into that element of pos.
      
      if pos is past the end of the document, the elementNum returned is None,
      and offset is the number of characters past the end of the document.
      '''
      assert isinstance( pos,            int  )
      assert isinstance( self._elements, list )
      
      # All other cases
      segPos = 0
      for elementNum, element in enumerate(self._elements):
         eleLen = len(element)
         if pos < (segPos + eleLen):
            return elementNum, pos - segPos
         else:
            segPos += eleLen
      
      return None, None

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


   def slice( self, pos1, pos2=None ):
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
         elif key == QtCore.Qt.Key_Enter:
            self.insertText( '\n' )
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



doc = HTMLDocument( )
doc.insertText( 'Here\'s some sample text.', 0 )
tagid = doc.defineTag( 'B' )
doc.applyTag( tagid, 10, 15 )

# HTML Contents
print( doc.toHTML() )

# Elements
for num,element in enumerate(iter(doc)):
   tagList = element.tags()
   
   if isinstance( element, HTMLSegment ):
      elementType  = 'Text'
      elementValue = element.text()
   elif isinstance( element, HTMLEntity ):
      elementType  = 'Entity'
      elementValue = element.entity().makeBeginTag()
   
   print( '{0:>3}. {1}'.format( num, elementType ) )
   print( '     value:' )
   print( '        -', elementValue )
   print( '     tags:' )

   for tagId in tagList:
      tagDef = doc.tag( tagId )
      print( '        -', doc.tag(tagId).makeBeginTag() )
