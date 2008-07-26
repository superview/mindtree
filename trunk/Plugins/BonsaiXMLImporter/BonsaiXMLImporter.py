import xml.sax
import copy


from Tree import Tree


class OutlineBuilder:
   def __init__( self, anOutlineName=None ):
      self._stack   =  []
      self._top     =  None
      self._depth   =  -1
      self.beginNested( anOutlineName )

   def beginNested( self, name = None ):
      newItem = Tree( )
      self._stack.append( newItem )
      self._depth += 1
      self._top = self._stack[ self._depth ]
      
      newItem.location = copy.copy( self._stack )
      if name != None:
         assert isinstance( name, (str,unicode) )
         self._top.title = name

   def endNested( self ):
      item = self._stack.pop( )
      self._depth -= 1
      self._top = self._stack[ self._depth ]
      self.addItem( item )

   def setTitle( self, title ):
      assert isinstance( title, (unicode,str) )
      
      self._top.title = title

   def setArticle( self, article ):
      assert isinstance( article, (unicode,str) )
      
      self._top.article = article

   def setItems( self, items ):
      assert isinstance( items, list )
      
      self._top.subtrees = list

   def addItem( self, item ):
      assert isinstance( item, Tree )
      
      self._top.subtrees.append( item )

   def top( self ):
      return self._stack[ self.depth ]

   def isDone( self ):
      return self._depth == 1

   def get( self ):
      return self._stack[ 0 ]


from Translator import Translator


class OutlineParserHandler( xml.sax.ContentHandler ):
   def __init__( self, outlineBuilder ):
      self._text   = ''
      self._builder = outlineBuilder
      self._trans   = Translator( )

   def startElement( self, tag, attrs ):
      if tag == 'item':
         self._builder.beginNested( )
      elif tag == 'text':
         self._text = ''
      elif tag == 'note':
         self._text  = ''
      elif tag == 'items':
         pass
      else:
         pass

   def endElement( self, tag ):
      if tag == 'item':
         self._builder.endNested( )
      elif tag == 'text':
         self._builder.setTitle( self._trans.translate( self._text ) )
      elif tag == 'note':
         self._builder.setArticle( self._trans.translate( self._text ) )
      elif tag == 'items':
         pass
      else:
         pass

   def characters( self, data ):
      self._text += data

   def get( self ):
      return self._builder.get( )

class Parser:
   @staticmethod
   def parseXML( aFileName, anOutlineName=None ):
      builder = OutlineBuilder( anOutlineName )
      handler = OutlineParserHandler( builder )
      xml.sax.parse( aFileName, handler )
      return handler.get( )

