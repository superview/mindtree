from StyledText import StyledText, Font, Style

class STObject( object ):
   NAME_SEP    = '_'
   NAME        = 'Object'
   FORMAT      = '_%s_%s'
   COUNT       = 0
   _text       = None
   
   INVALIDATED = [ ]
   
   def __init__( self, name=None ):
      if name:
         self._name = name
      else:
         self._name = STObject.FORMAT % ( self.NAME, str(STObject.COUNT) )
      
      self._id   = STObject.COUNT
      STObject.COUNT += 1

   def rename( self, name ):
      self._name = STObject.FORMAT % ( self.NAME, name )
   
   def name( self ):
      return self._name

   def actions( self ):
      return [ ]
   
   def paint( self, context ):
      pass
   
   def invalidate( self ):
      STObject.INVALIDATED.append( self )

class Attribute_STObject( STObject ):
   NAME = 'Attribute'
   
   def __init__( self, attributeName=None, attributeValue=None ):
      self._attributeName  = attributeName
      self._attributeValue = attributeValue
      
      if attributeName:
         STObject.__init__( self, '%s_%s' % (attributeName, attributeValue) )
      else:
         STObject.__init__( self )

   def paint( self, context ):
      context.setAttribute( self._attributeName, self._attributeValue )

class Font_STObject( STObject ):
   NAME = 'Font'
   
   def __init__( self, tagName ): #family, size, weight, slant, offset ):
      self._style = Style.getStyle( tagName )
   
   def paint( self, context ):
      pass

class Bookmark_STObject( STObject ):
   NAME   = 'Bookmark'
   
   BOOKMARKS = { }
   
   def __init__( self, name=None, location=None ):
      STObject.__init__( self, name )
      self._location = location
      
      if name:
         Bookmark_STObject.BOOKMARKS[ name ] = self
   
   def paint( self, context ):
      pass


class CursorLocation_STObject( STObject ):
   NAME = 'insert'
   
   def __init__( self ):
      STObject.__init__( self )
   
   def actions( self ):
      pass
   
   def paint( self, context ):
      raise Exception( "Cannot realize the selection object." )

class Dump_STObject( STObject ):
   NAME = 'Dump'
   
   def __init__( self, dump ):
      STObject.__init__( self )
      self._dump = dump
   
   def paint( self, context ):
      '''Slave routine for insert.  This method handles inserting dumps.'''
      context.markDrawingIndex( '__insert__' )
      
      tags = { }
      for element in self._dump:
         action = element[0]
         value  = element[1]
         index  = context.getDrawingIndex( '__insert__' )
         
         if action == 'tagon':
            tags[ value ] = index
         elif action == 'tagoff':
            try:
               regionBegin = tags[ value ]
               del tags[ value ]
            except:
               raise Exception( 'tagoff not preceded by tagon.' )
            
            regionEnd   = context.getDrawingIndex( '__insert__' )
            tagName     = value
            
            obj = context.objectFactory().getObjectByName( tagName )
            context.insertObject( obj, regionBegin, regionEnd )
         elif action == 'text':
            obj = context.objectFactory().makeObject( 'Text', value )
            context.insertObject( obj )
         elif action == 'mark':
            if value in ( 'insert', 'current', 'anchor' ):
               continue
            obj = context.objectFactory().makeObject( 'Bookmark', value )
            context.insertObject( obj )
         elif action == 'image':
            obj = context.objectFactory().makeObject( 'Image', value )
            context.insertObject( obj )
         elif action == 'window':
            self.insert( 'insertHere', value, 'widget' )
         else:
            raise Exception( 'Unknown Action: ' + str(action) )
      
      context.unmarkDrawingIndex( '__insert__' )

class Image_STObject( STObject ):
   NAME   = 'Image'
   
   IMAGES = { }
   
   def __init__( self, filename=None ):
      STObject.__init__( self, filename )
      self._filename = filename
      self._image    = None
   
   def paint( self, context ):
      if not self._filename:
         import tkFileDialog
         self._filename = tkFileDialog.askopenfilename( parent=self, filetypes=[ ( 'GIF Image', '*.gif' ) ] )
         if not self._filename or (self._filename == ''):
            return
         
         self.rename( self._filename )
      
      try:
         image = Image_STObject.IMAGES[ self._filename ]
      except:
         image = PhotoImage( file=self._filename )
         Image_STObject.IMAGES[ self._filename ] = image
      
      context.drawImage( self._filename, image )

class Link_STObject( STObject ):
   STYLE = Style( family='Ariel',
                        size  =12,
                        foreground ='blue',
                        underline  = True )

   NAME   = 'Link'
   
   POPUP = None
   
   def __init__( self, url='' ):
      STObject.__init__( self, url )
      self._url = url
      
      if Link_STObject.POPUP is None:
         Link_STObject.POPUP = Menu( self._text, tearoff=False, cursor='hand2' )
         Link_STObject.POPUP.add_command( )
      
      if 'link' not in self._text.styles():
         self._text.styles()[ 'link' ] = Link_STObject.STYLE

   def onEnter( self, aLinkItem ):
      self._timer = self._text.after( 1000, self.popup )
      self._text[ 'cursor' ] = 'hand2'

   def onLeave( self, aLinkItem ):
      self._text.after_cancel( self._timer )
      self._text[ 'cursor' ] = 'xterm'
   
   def popup( self, event=None ):
      try:
         #self._index = self._text.index( '@%d,%d' % self._text.winfo_pointerxy() )
         
         self.POPUP.entryconfig( 0, label=self._url, command=self.editURL )
         pos = self._text.winfo_pointerxy( )
         Link_STObject.POPUP.post( *pos )
      except:
         pass
   
   def editURL( self, event=None ):
      import tkSimpleDialog
      newValue = tkSimpleDialog.askstring( 'Link to', 'URL', parent=self._text, initialvalue=self._url )
      
      if newValue is not None:
         self._url = newValue

   def paint( self, context ):
      if not isinstance( context, RegionContext ):
         raise Exception( 'There must be a selection to make a link.' )
      
      context.defineStyle( self.name(), Link_STObject.STYLE )
      context.setStyle( self.name() )
      context.bind( self.name(), '<Enter>', self.onEnter )
      context.bind( self.name(), '<Leave>', self.onLeave )
      
      self.editURL( )

class List_STObject( STObject ):
   NAME   = 'List'
   
   def __init__( self ):
      STObject.__init__( self )

   def paint( self, context ):
      pass


class Selection_STObject( STObject ):
   NAME  = 'sel'
   
   def __init__( self ):
      STObject.__init__( self )
   
   def actions( self ):
      return [ ( 'Delete', None ),
               ( 'Cut',    None ),
               ( 'Copy',   None ) ]
   def paint( self, context ):
      raise Exception( "Cannot realize the selection object." )

class Style_STObject( STObject ):
   NAME   = 'Style'
   
   def __init__( self, name=None ):
      STObject.__init__( self, name )
   
   def paint( self, context ):
      context.setStyle( self.name() )

class Table_STObject( STObject ):
   NAME   = 'Table'
   
   def __init__( self ):
      STObject.__init__( self )

   def paint( self, context ):
      pass


class Text_STObject( STObject ):
   NAME = 'Text'
   
   def __init__( self, string=None ):
      STObject.__init__( self )
      self._string = string
   
   def paint( self, context ):
      context.drawText( self._string )


class STObjectFactory( object ):
   STObjectClasses = [ Attribute_STObject, Bookmark_STObject,
                       CursorLocation_STObject, Dump_STObject, Image_STObject,
                       Link_STObject, List_STObject, Selection_STObject,
                       Style_STObject, Table_STObject, Text_STObject ]

   objectTypeLib = { }

   for STObjectClass in STObjectClasses:
      objectTypeLib[ STObjectClass.NAME ] = STObjectClass

   objectNamePrefixLib = { }

   def __init__( self, objects=None ):
      if objects:
         self._objectLib = objects
      else:
         self._objectLib = { }

   def defineObject( self, name, instance ):
      self._objectLib[ name ] = instance
   
   def ObjectTypes( self ):
      return stObject_ClassLib.keys( )

   def getObjectByName( self, instanceName ):
      try:
         return self._objectLib[ instanceName ]
      except:
         nameParts = instanceName.split( '-' )
         instance  = self.makeObject( *nameParts )
         instance.rename( instanceName )
         self._objectLib[ instanceName ] = instance
         return instance

   def makeObject( self, ClassName, *args, **kwargs ):
      if ClassName == 'Attribute':
         if len( args ) != 2:
            raise Exception( 'attribute values and name required to make an attribute object.' )
         elif len( kwargs ) != 0:
            raise Exception( 'Key arguments not allowed when making an attribute object.' )
         
         attributeName, attributeValue = args
         
         tagName = Attribute_STObject.FORMAT % ( attributeName, attributeValue )
         
         try:
            objectInstance = self._objectLib[ tagName ]
         except:
            objectInstance = Attribute_STObject( attributeName, attributeValue )
            self._objectLib[ objectInstance.name( ) ] = objectInstance
         
         return objectInstance
      
      elif ClassName == 'Style':
         if len(args) != 1:
            raise Exception( 'Name required to make a style object.' )
         elif len(kwargs) == 0:
            raise Exception( 'At least one key argument required to make a style object.' )
         
         styleName = args[0]
         
         try:
            objectInstance = self._objectLib[ styleName ]
         except:
            objectInstance = Style_STObject( styleName, **kwargs )
            self._objectLib[ objectInstance.name( ) ] = objectInstance
         
         return objectInstance
      
      else:
         return self.objectTypeLib[ ClassName ]( *args )


from Tkinter import *

class Context( object ):
   DRAW_INDEX = '__drawHere__'
   
   def __init__( self, textWidget ):
      self.widget    = textWidget

   def defineStyle( self, styleName, styleObject ):
      self.widget.styles()[ styleName ] = styleObject
   
   def insertObject( self, object, first=None, last=None ):
      self.widget.insertObject( object, first, last )
   
   def objectFactory( self ):
      return self.widget.objectFactory( )
   
   def drawingIndex( self ):
      return self.widget.index( Context.DRAW_INDEX )
   
   def markDrawingIndex( self, name, gravity='right' ):
      self.widget.mark_set( name, Context.DRAW_INDEX )
      self.widget.mark_gravity( name, gravity )
   
   def getDrawingIndex( self, name ):
      return self.widget.index( name )

   def unmarkDrawingIndex( self, name ):
      self.widget.mark_unset( name )
   
   def prePaint( self ):
      pass
   
   def postPaint( self ):
      self.widget.mark_unset( Context.DRAW_INDEX )
   
class InsertContext( Context ):
   def __init__( self, textWidget ):
      Context.__init__( self, textWidget )
   
   def bind( self, name, sequence, callback ):
      return
      self.defineStyle( name, Style( ) )
      self.widget.setInsertStyle( name )
      self.widget.tag_bind( name, sequence, callback )
   
   def setAttribute( self, attributeName, attributeValue ):
      self.widget.setInsertAttribute( attributeName, attributeValue )

   def setStyle( self, styleName ):
      self.widget.setInsertStyle( styleName )
   
   def setBookmark( self, bookmarkName ):
      self.widget.mark_set( bookmarkName, 'insert' )
   
   def drawImage( self, imageName, imageObject ):
      self.widget.image_create( 'insert', name=imageName, image=imageObject, padx=1 )
   
   def drawText( self, textString ):
      self.widget.insert( 'insert', textString )
   
   def drawWindow( self, widget ):
      self.widget.window_create( 'insert', window=widget, padx=1 )

   def prePaint( self ):
      self.widget.mark_set( Context.DRAW_INDEX, 'insert' )
      self.widget.mark_gravity( Context.DRAW_INDEX, 'right' )
   
class RegionContext( Context ):
   def __init__( self, textWidget, first, last ):
      Context.__init__( self, textWidget )
      self._first = first
      self._last  = last

   def bind( self, name, sequence, callback ):
      self.widget.tag_add( name, self._first, self._last )
      self.widget.tag_bind( name, sequence, callback )

   def setAttribute( self, attributeName, attributeValue ):
      self.widget.setAttribute( self._first, self._last, attributeName, attributeValue )
   
   def setStyle( self, styleName ):
      self.widget.setStyle( self._first, self._last, styleName )
   
   def setBookmark( self, bookmarkName ):
      self.widget.mark_set( bookmarkName, self._first )
   
   def drawImage( self, imageName, imageObject ):
      self.widget.delete( self._first, self._last )
      self.widget.image_create( self._first, name=imageName, image=imageObject, padx=1 )
   
   def drawText( self, textString ):
      self.widget.delete( self._first, self._last )
      self.widget.insert( self._first, textString )

   def drawWindow( self, widget ):
      self.widget.delete( self._first, self._last )
      self.widget.window_create( self._first, window=widget, padx=1 )

   def prePaint( self ):
      self.widget.mark_set( Context.DRAW_INDEX, self._first )
      self.widget.mark_gravity( Context.DRAW_INDEX, 'right' )
   
class OText( StyledText ):
   def __init__( self, parent, **options ):
      StyledText.__init__( self, parent, **options )
      
      self._objFactory = STObjectFactory( )
      self._objFactory.defineObject( 'sel',     Selection_STObject( ) )
      self._objFactory.defineObject( 'default', Style_STObject( 'default' ) )
      
      STObject._text = self
   
   def reinitialize( self, styleLibrary=None, objectLibrary=None ):
      if styleLibrary:
         for styleName in styleLibrary.keys():
            self._objFactory.defineObject( styleName, Style_STObject( styleName ) )
      
      StyledText.reinitialize( self, styleLibrary, objectLibrary )

   def insertObject( self, object, first=None, last=None ):
      if first:
         first = self.index( first )
         last  = self.index( last  )
         ctx   = RegionContext( self, first, last )
      else:
         try:
            first = self.index( 'sel.first' )
            last  = self.index( 'sel.last'  )
            ctx   = RegionContext( self, first, last )
         except:
            ctx   = InsertContext( self )
      
      ctx.prePaint( )
      object.paint( ctx )
      ctx.postPaint( )
   


if __name__=='__main__':
   from Tkinter import *
   
   def ADD_OBJ( objClassName ):
      def _doAdd( event=None ):
         obj = factory.makeObject( objClassName )
         text.insertObject( obj )
      
      return _doAdd

   root = Tk()
   
   addLinkBtn = Button( root, text='link', command=ADD_OBJ( Link_STObject.NAME ) )
   addLinkBtn.pack( )
   
   text = OText( root )
   text.pack( )
   
   factory = STObjectFactory( )
   
   t = Text_STObject( '012 something to link ' )
   text.insertObject( t )
   
   root.mainloop( )
