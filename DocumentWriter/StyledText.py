'''
Class Hierarchy
===============

    ^  Subclass
    *  Contains

           +------+
           | Text |
           +------+
              ^
              |
       +--------------+
       | EnhancedText |
       +--------------+
              ^
              |
        +------------+
        | StyledText |*------------+-------------+
        +------------+             |             |
              |                +-------+      +------+
              |                | Style |*-----| Font |
              |                +-------+      +------+
              |                    |             |
              |                    *             *
      +----------------+          +---------------+
      | DocumentWriter |*---------|  StyleEditor  |
      +----------------+          +---------------+

Overview of the Classes
=======================

EnhancedText (and support classes)
   A drop-in replacement for the Text widget which fixes some weird cursor
   movement problems.  It's a subclass of Text and the superclass of
   StyledText.

Font
   A class to encapsulate StyledText's definition of a font object.

Style
   StyledText's object which holds styling information.

StyledText
   The main widget of this small library.

DocumentWriter
   A mini Python word processor with toolbars all thrown into a Frame --
   primarily intended for use as a demo of StyledText.

StyleEditor
   A dialog box for allowing a user to edit and create custom Style objects.


Description
===========

Indices

Indices are identical to those of the Text widget.

Attributes & Styles

StyledText has two kinds of styling objects.  An attribute is a single styling
entity such as font family, foreground color or tab settings.  StyledText
recognizes the following attributes:

 * Font attributes:  family, size, weight, slant, offset, bold, italic

 * Pen attributes:   foreground, background, fgstipple, bgstipple, underline,
                     overstrike, borderwidth, relief

 * Layout attributes:  justify, wrap, tags, lmargin1, lmargin2,
                       spacing1, spacing2, spacing3

Most are identical to those of the Text object with the same name.  However,
there are some differences.  bold, and italic are alternative ways to express
the same thing expressed by slant and weight.

There are two new attributes:

   bold, boolean.   (alternative to 'weight')
   italic, boolean. (alternative to 'slant')

There are some new values:

   offset can have any of the values acceptable by Text's offset.
   It can also take 'normal', 'superscript' or 'subscript'.

   spacing options can have any of the values acceptable by the Text's
   widgets options of the same name.  They can also have one of the following
   values: 'None', 'Half Line', 'One Line' or 'Two Lines'.

Style is a class whose instances have the complete set of styling attributes.
Style contains a value DEFAULT_STYLE which contains the complete styling of the
Text widget right after it's created.  A Style instance is guaranteed to have a
value assigned to each attribute.  It is possible to define an empty Style
instance, Style(), or one with just a few values Style(foreground='blue'), in
these cases, if client software requests styling for an attribute not
explicitly assigned, Style will get the value from the DEFAULT_STYLE object.

StyledText maintains a style library (accessible via the styles() method)
which maps style names to Style objects.  The style library is guaranteed to
contain at least one object named "default" whose value is DEFAULT_STYLE.

Styling Layers

StyledText takes advantage of the Text widget's tags and stacking to form a
logical arrangement of styling in three layers.  In the layering scheme, values
assigned in higher layers obscure those in lower layers.  If a value is later
removed from a higher layer, the one in the lower layer then comes back into
effect.

On the bottom layer is the Global style layer.  There is exactly one Style
instance in this layer and it applies to the entire document.  Its
defined in the style library with the name "default".

Next is the Local style layer.  In this layer a Style may be assigned to a
region.  Only one Style may occupy any given region.  Later style assignments
will delete previous assignments.  If a new style assignment partially overlaps
a previous assignment, then the old style will only be deleted from the
overlapping region.  So, if region '1.0' to '10.6' is assigned Style "AA", then
then region '5.5' to '20.0' is assigned Style "BB", then "AA" now only covers
region '1.0' to '5.5'.  It gets removed from whereever style "BB" overlaps.
This is to prevent there being unused styles obscured by more recently applied
styles (a problem with Text's tag stack).

The third (and top) layer is the attribute layer.  In this layer, any region
may be assigned an individual attribute, being the top layer, they effectively
override those in the global and local layers.

Implementation
==============
To make the widget react more naturally when changing the value of 'offset'
across a region, I found it convenient to make 'offset' A sub-option of the
font object rather than a full option.  In this way if we have some text which
has (Ariel, 12, bold, superscript), the original size is preserved in the font.
The actual tag in the text widget gets configured with
{{{ {font:('Ariel',5,bold), offset='10p'} }}}.
Now if the user decides to remove the superscript styling, the information of
the original size (12) is still available in the font object so it's easily
restored.  To implement this I defined my own class Font to use with the
StyledText in place of tkFont.  This class includes the very useful method
{{{tagOptions()}}} which returns a dictionary of options suitable for passing
to Text's tag_config() to produce the desired appearance.  class Font manages
the options: family, size, weight, slant and offset.  Underline and Overstrike
can be set independently via tag_config(), so they are not managed by Font.

The primary attribute styling class is class Style.  This class is a subclass
of dict which is intended to hold values for all the style options not part of
class Font.  class Style also contains a _font member and like class Font has
the very useful {{{tagOptions()}}} method.  This tagOptions will combine its
own values with any it gets from calling {{{self._font.tagOptions()}}} to form
a complete set of values suitable for {{{tag_config()}}}.

To simplify the seeming chaos of layered tags and overlapping tagged regions
of Tkinter's Text widget, I decided to first define some restrictions on how
tags can be used.

 1.  The widget has a default styling (which assigns a value to every style
     attribute).

 2.  A non-StylerFont tag may configure exactly one styling attribute.

 3.  For any index in the underlying text widget, there may be at most one tag
     for any given non-StylerFont attribute.

 4.  For any index in the underlying text widget, there may be at most one tag
     handling a StylerFont.

 5.  For any unique attribute configuration in use there should exist exactly
     one tag.

These restrictions eliminate "Infinite depth tag stack" (criteria 2, 3 & 4)
and "tagName redundancy" (criteria 5).  Conceptually we now have just two
styling layers: default styling on the bottom, custom styling on top.  So, for
example if I call
{{{applyStyleAttribute( begin, end, 'underline', Tkinter.TRUE )}}}, any
existing tags in the region (begin,end) which assign to 'underline', are first
deleted if the new styling is something other than the default for the
attribute being set, the new styling is applied.

With the tag chaos of the Text widget under control, it's now possible to
design an algorithm which provides {{{applyStyleAttribute()}}} with a "map" of
the current styling of a region to which we want to make a styling change.
This map actually splits the region at every point that any tag in the region
begins or ends.  Here's an example to illustrate:

{{{
Sample Text:      Sample text to illustrate a styling map of a region of text.
Indecies:                   1         2         3         4         5         6
                  0123456789012345678901234567890123456789012345678901234567890

tag1:                  |<---------------->|          |<--------------->|
tag2:                            |<----------->|

Region to map:     |<-------------------------------------->|
Resulting map:     |<->|<------->|<------>|<-->|<--->|<---->|

}}}
So here we have some Sample Text.  tag1 spans regions 1.5 - 1.24 and
1.35 - 1.53, and tag2 spans 1.15 - 1.29.  {{{iterRegion()}}} slices the region
at any tag begin or tag end; this results in a map with six segments.  For each
segment in the map, the list of active tags is also given.  So
{{{iterRegion()}}} in the above example yieldse the following tuples:
{{{
   ( '1.1',  '1.5',  [ ] )                 # No tags in this region
   ( '1.5',  '1.15', [ 'tag1' ] )          # tag1 in this region
   ( '1.15', '1.24', [ 'tag1', 'tag2' ] )  # etc.
   ( '1.24', '1.29', [ 'tag2' ] )
   ( '1.29', '1.35', [ ] )
   ( '1.35', '1.42', [ 'tag1' ] )
}}}

Next is to determine which attributes and values are set in each segment.
The obvious way is to have a dict mapping a tagName to a Style object, but
it's not the only way.  Criterion 5 requires that we avoid tagName redundancy
(E.g. We don't want to define a new tag for underline every time the user
selects a bit of text and applies the underline style.  We should use the
same underline tag for all cases of underline).  To handle this I use a
standard naming convention for tags such that the name of the tag ''encodes''
the tag's configuration.  Because of criterion 2, this is actually reasonable
(the names won't get ''too'' long).  This also eliminates the need for the
dictionary since the name of each tag can also be ''decoded'' to get its
configuration.  Any tag which sets an attribute of class Font (family, size,
weight, slant or offset) has the tagName pattern:
{{{"_font_%(family)s_%(size)d_%(weight)s_%(slant)s_%(offset)"}}}.  The
remaining attributes have tagName patterns:
{{{"_attribute_%(attributeName)s_%(attributeValue)s"}}}.

The general algorithm that {{{applyStylAttribute()}}} uses is to iterate over
the segments of the map returned by {{{iterRegion()}}}.  For each segment,
determine the current styling settings, delete any current stying tags from the
segment which set a value to the same attribute, use the current styling
settings to derive a new set of settings with the new values, call
{{{tag_add()}}} and {{{tag_config()}}} to install the new styling.  The cases
for setting a new font attribute (family,size,weight,slant or offset) is
handled separately from that of any other attribute.)

So if {{{applyStyleAttribute()}}} gets an assignment to any class Font
attribute, it iterates throught the subregions returned by {{{iterRegion()}}}
if it there's a tag that begins {{{"_font_..."}}} (and there can be only one per
criterion 3), then it asks class Font to decode the tagName and create a new
Font instance, then it deletes the tag from the segment.  Next it call's the
Font's {{{deriveFont(attributeName,newAttributeValue)}}} which returns a new
Font object.  On this new font object it calls {{{tagOptions()}}} and
{{{fontName()}}} to get what's needed to define and configure a new
{{{"_font_..."}}} tag for the subregion.

Similarly, if {{{applyStyleAttribute()}}} gets an assignment to any other
attribute, it iterates through the subregions returned by {{{iterRegion()}}},
if there's a tag that begins {{{"_attribute_%(attributeName)s_"}}} (and there
can be only one per criterion 4), then it decodes the tagName, then deletes
the tag from the segment.  Next a new tagName and Style instance are creatd
which are used to define and configure the new tag in the underlying text
widget.

In the cases where {{{applyStyleAttribute()}}} is iterating over the segments
returned by mapRegion, and a segment is empty or does not contain any styling
on attributeName, then the default styling is assumed (criterion 1).
'''




'''
Kinds of Tags:
- Styles           "_style_<name>"
- Attributes       "_attribute_<rest>"
- ToolHighlight    "_<toolName>_<rest>"
- Objects          "_<className>_<rest>"
  - Priority?      (Global,Local,Attribute,Exclusive)
  - Interactive?   (None,Sequence)
  - Persistent?    (True,False)
'''


import Tix
import tkFont
import copy
from EnhancedText import *
from resources import RES
import os
import os.path

TAG_NAME_SPLITTER = '_'

class Font( object ):
   ATTRIBUTE_NAMES = [ 'family', 'size', 'weight', 'slant', 'offset', 'bold', 'italic' ]
   NAME_FORMAT     = '_font_%(family)s_%(size)s_%(weight)s_%(slant)s_%(offset)s'
   NAME_PREFIX     = '_font_'
   
   DEFAULT_FONT = None
   FONT_LIBRARY = { }
   
   def __init__( self, **options ):
      try:
         del options[ 'underline' ]
      except:
         pass
      
      try:
         del options[ 'overstrike' ]
      except:
         pass
      
      self._fontOpts = options
   
   def __setitem__( self, key, value ):
      if key == 'bold':
         self._fontOpts[ 'weight' ] = 'bold' if value else 'normal'
      elif key == 'italic':
         self._fontOpts[ 'slant'  ] = 'italic' if value else 'roman'
      else:
         self._fontOpts[ key ] = value
   
   def __getitem__( self, key ):
      try:
         return self._fontOpts[ key ]
      except:
         if key == 'bold':
            try:
               return self._fontOpts[ 'weight' ] == 'bold'
            except:
               return self.DEFAULT_FONT[ 'weight' ] == 'bold'
         elif key == 'italic':
            try:
               return self._fontOpts[ 'slant' ] == 'italic'
            except:
               return self.DEFAULT_FONT[ 'slant' ] == 'italic'
         else:
            return self.DEFAULT_FONT[ key ]
   
   def opts( self ):
      opts = copy.copy( self._fontOpts )
      try:
         opts[ 'bold'   ] = opts['weight'] == 'bold'
      except:
         pass
      
      try:
         opts[ 'italic' ] = opts['slant' ] == 'italic'
      except:
         pass
      
      return opts
   
   def tagOptions( self ):
      options = { }
      
      styleList = [ ]
      if self._fontOpts['weight'] == 'bold':
         styleList.append( 'bold' )
      if self._fontOpts['slant'] == 'italic':
         styleList.append( 'italic' )
      
      if self._fontOpts['offset'] != 'normal':
         # If the region includes an offset, we need to reestablish that
         baseSize = self._fontOpts['size']
         size = int(baseSize * (3.0 / 5.0) + 0.5)
         
         if self._fontOpts['offset'] == 'superscript':
            options[ 'offset' ] = '%dp'  % int(baseSize / 2.0 + 0.5)
         else:
            options[ 'offset' ] = '-%dp' % int(baseSize / 5.0 + 0.5)
      else:
         size = self._fontOpts['size']
      
      options[ 'font' ] = ( self._fontOpts['family'], size, ' '.join(styleList) )
      
      return options
   
   def fontName( self ):
      return Font.NAME_FORMAT % self._fontOpts

   def deriveFont( self, **newOpts ):
      newFont = copy.deepcopy( self )
      for key,val in newOpts.iteritems():
         newFont[ key ] = val
      
      fontName = newFont.fontName( )
      
      if fontName not in Font.FONT_LIBRARY:
         Font.FONT_LIBRARY[ fontName ] = newFont
      return Font.FONT_LIBRARY[ fontName ]
   
   def tkFont( self ):
      return tkFont.Font( family=self._fontOpts['family'], size=self._fontOpts['size'], weight=self._fontOpts['weight'], slant=self._fontOpts['slant'] )

   @staticmethod
   def getFont( font=None, **options ):
      '''font     Font name, tkfont spec, font tuple
         family   font family name
         size     size
         weight   bold or normal
         bold     boolean
         slant    roman or italic
         italic   boolean
      '''
      fontOpts = { }
      fontStyling = ''
      
      if font:
         if isinstance( font, (str,unicode) ):
            try:
               return Font.FONT_LIBRARY[ font ]
            except:
               if font.startswith( Font.NAME_PREFIX ):
                  # We have a font name
                  for key,val in zip( ['family','size','weight','slant','offset'], font.split( TAG_NAME_SPLITTER )[2:] ):
                     fontOpts[ key ] = val
                  fontOpts['size'] = int(fontOpts['size'])
               else:
                  # We need to decode a tkinter font string
                  fontOpts = tkFont.Font( font=font ).actual( )
                  fontOpts['offset'] = 'normal'
               
               fontName = Font.NAME_FORMAT % fontOpts
               Font.FONT_LIBRARY[ fontName ] = Font( **fontOpts )
               return Font.FONT_LIBRARY[ fontName ]
         
         elif isinstance( font, (list,tuple) ):
            # We need to decode a tkinter font tuple
            offset = 'normal'
            if len(font) == 3:
               style = font[2].split( )
               if 'superscript' in style:
                  offset = 'superscript'
                  style.remove( 'superscript' )
               elif 'subscript' in style:
                  offset = 'subscript'
                  style.remove( 'subscript' )
               
               style = ' '.join( style )
               font = ( font[0], font[1], style )
            else:
               font = ( font[0], font[1] )
            
            fontOpts = tkFont.Font( font=font ).actual( )
            if offset:
               fontOpts[ 'offset' ] = offset
            
            fontName = Font.NAME_FORMAT % fontOpts
            
            try:
               return Font.FONT_LIBRARY[ fontName ]
            except:
               Font.FONT_LIBRARY[ fontName ] = Font( **fontOpts )
               return Font.FONT_LIBRARY[ fontName ]
      
      elif options:
         try:
            options[ 'weight' ] = 'bold' if options['bold'] else 'normal'
            del options[ 'bold' ]
         except:
            options[ 'weight' ] = 'normal'
         
         try:
            options[ 'slant' ] = 'italic' if options['italic'] else 'roman'
            del options[ 'italic' ]
         except:
            options[ 'slant' ] = 'roman'
         
         fontName = Font.NAME_FORMAT % options
         
         try:
            return Font.FONT_LIBRARY[ fontName ]
         except:
            Font.FONT_LIBRARY[ fontName ] = Font( **options )
            return Font.FONT_LIBRARY[ fontName ]
      
      else:
         return Font.FONT_LIBRARY[ 'default' ]

   @staticmethod
   def setupDefaults( aTextWidget ):
      Font.DEFAULT_FONT = Font.getFont( aTextWidget['font'] )
      Font.FONT_LIBRARY[ 'default' ] = Font.DEFAULT_FONT


class Style( object ):
   ATTRIBUTE_NAMES = [ 'justify', 'wrap', 'tabs', 'lmargin1', 'lmargin2',
                     'rmargin', 'spacing1', 'spacing2', 'spacing3',
                     'foreground', 'background', 'fgstipple', 'bgstipple',
                     'underline', 'overstrike', 'borderwidth', 'relief' ]
   NAME_FORMAT     = '_style_%(name)s'
   NAME_PREFIX     = '_style_'
   
   ATTRIBUTE_NAME_FORMAT = '_attribute_%(name)s_%(value)s'
   ATTRIBUTE_NAME_PREFIX = '_attribute_'
   
   DEFAULT_STYLE = None
   OFF_VALUES    = None
   
   def __init__( self, **options ):
      self._styleOpts = { }
      self._font      = Font( )
      
      for key,value in options.iteritems( ):
         if key in Font.ATTRIBUTE_NAMES:
            self._font[ key ] = value
         
         elif key == 'font':
               if isinstance( value, Font ):
                  self._font = value
               else:
                  self._font = Font.getFont( value )
         
         else:
            self._styleOpts[ key ] = value

   def __setitem__( self, key, value ):
      if key in Font.ATTRIBUTE_NAMES:
         self._font[ key ] = value
      
      elif key == 'font':
            if isinstance( value, Font ):
               self._font = value
            else:
               self._font = Font.getFont( value )
      
      else:
         if (value in Style.OFF_VALUES[key]) or (value == Style.DEFAULT_STYLE[key]):
            if key in self:
               del self._styleOpts[ key ]
         else:
            self._styleOpts[ key ] = value
   
   def __getitem__( self, key ):
      if key in Font.ATTRIBUTE_NAMES:
         return self._font[ key ]
      elif key == 'font':
         return self._font
      elif key in self._styleOpts:
         return self._styleOpts[ key ]
      else:
         return Style.DEFAULT_STYLE[ key ]

   def opts( self ):
      opts = copy.copy( self._styleOpts )
      opts.update( self._font.opts() )
      return opts
   
   def tagOptions( self ):
      options  = { }
      options.update( self._styleOpts )
      try:
         options.update( self._font.tagOptions( ) )
         lineHeight = self._font.tkFont().metrics('linespace')
      except:
         lineHeight = Style.DEFAULT_STYLE._font.tkFont().metrics('linespace')
      
      # Adjust fields with non-tk options
      for spacingKind in [ 'spacing1', 'spacing2', 'spacing3' ]:
         try:
            selectedSpacing = options[ spacingKind ]
            if selectedSpacing == 'None':
               options[ spacingKind ] = '0'
            elif selectedSpacing == 'Half Line':
               options[ spacingKind ] = '%dp' % int(float(lineHeight * 0.5 + 0.5))
            elif selectedSpacing == 'One Line':
               options[ spacingKind ] = '%dp' % int(lineHeight)
            elif selectedSpacing == 'Two Lines':
               options[ spacingKind ] = '%dp' % int(lineHeight * 2)
            else:
               options[ spacingKind ] = selectedSpacing
         except:
            pass
      
      if 'background' in options:
         del options[ 'background' ]
      
      return options
   
   def deriveStyle( self, attribName, attribValue ):
      if attribuName in Font.ATTRIBUTE_NAMES:
         return self._font.deriveFont( attribName, attribValue )
      else:
         opts = copy.copy( self._styleOpts )
         opts[ attribName ] = attribValue
         return Style( **opts )
   
   @staticmethod
   def getStyle( aSpec=None, **options ):
      if aSpec:
         if isinstance( aSpec, str ):
            if aSpec.startswith(Font.NAME_PREFIX):
               return Font.getFont( aSpec )
            elif aSpec.startswith(Style.ATTRIBUTE_NAME_PREFIX):
               key,value = aSpec.split(TAG_NAME_SPLITTER)[2:]
               theStyle = Style( )
               theStyle[ key ] = value
               return theStyle
      if options:
         return Style( **options)

   @staticmethod
   def setupDefaults( aTextWidget ):
      Font.setupDefaults( aTextWidget )
      Style.DEFAULT_STYLE = Style( font        = Font.DEFAULT_FONT,
                                   underline   = False,
                                   overstrike  = False,
                                   foreground  = aTextWidget[ 'foreground' ],
                                   background  = aTextWidget[ 'background' ],
                                   fgstipple   = '',
                                   bgstipple   = '',
                                   borderwidth = 0,
                                   relief      = 'flat',
                                   justify     = 'left',
                                   wrap        = aTextWidget[ 'wrap' ],
                                   lmargin1    = 0,
                                   lmargin2    = 0,
                                   rmargin     = 0,
                                   spacing1    = aTextWidget[ 'spacing1' ],
                                   spacing2    = aTextWidget[ 'spacing2' ],
                                   spacing3    = aTextWidget[ 'spacing3' ],
                                   tabs        = aTextWidget[ 'tabs' ]
                                 )
      
      Style.OFF_VALUES = {
                          # Font Attributes
                          'family':     [ Font.DEFAULT_FONT['family'] ],
                          'size':       [ Font.DEFAULT_FONT['size'  ] ],
                          'weight':     [ 'normal', None          ],
                          'slant':      [ 'roman',  None          ],
                          'offset':     [ 'normal', '0', '0p', '0i', '0c', '0m', '', None          ],
                           
                          # Paragraph Attributes
                          'justify':    [ 'left', '', None ],
                          'wrap':       [ 'char', '', None ],
                          'lmargin1':   [ '0', '0p', '0i', '0c', '0m', '', None ],
                          'lmargin2':   [ '0', '0p', '0i', '0c', '0m', '', None ],
                          'rmargin':    [ '0', '0p', '0i', '0c', '0m', '', None ],
                          'spacing1':   [ '0', '0p', '0i', '0c', '0m', 'None', '', None ],
                          'spacing2':   [ '0', '0p', '0i', '0c', '0m', 'None', '', None ],
                          'spacing3':   [ '0', '0p', '0i', '0c', '0m', 'None', '', None ],
                          'tabs':       [ '', None ],
                           
                          # Other Attributes
                          'underline':  [ Tix.FALSE, '0', 'false', 'False', False, '', None ],
                          'overstrike': [ Tix.FALSE, '0', 'false', 'False', False, '', None ],
                          'foreground': [ aTextWidget[ 'foreground' ], '', None ],
                          'background': [ aTextWidget[ 'background' ], '', None ],
                          'fgstipple':  [ '', 'none', None ],
                          'bgstipple':  [ '', 'none', None ],
                          'borderwidth':[ '0', '0p', '0i', '0c', '0m', '', None ],
                          'relief':     [ 'flat', '', None ]
                          }




class StyledText( EnhancedText ):
   PRIVATE_TAGS  = [ 'sel' ]
   PRIVATE_MARKS = [ 'insert', 'current', 'anchor' ]
   
   def __init__( self, parent, styleLibrary=None, objectLibrary=None, **options ):
      EnhancedText.__init__( self, parent, **options )
      self.bind( '<KeyPress-BackSpace>', self._updateInsertStylingInfo, '+' )
      self.bind( '<KeyPress-Up>',        self._updateInsertStylingInfo, '+' )
      self.bind( '<KeyPress-Down>',      self._updateInsertStylingInfo, '+' )
      self.bind( '<KeyPress-Left>',      self._updateInsertStylingInfo, '+' )
      self.bind( '<KeyPress-Right>',     self._updateInsertStylingInfo, '+' )
      self.bind( '<KeyPress-Home>',      self._updateInsertStylingInfo, '+' )
      self.bind( '<KeyPress-End>',       self._updateInsertStylingInfo, '+' )
      self.bind( '<KeyPress-Prior>',     self._updateInsertStylingInfo, '+' )
      self.bind( '<KeyPress-Next>',      self._updateInsertStylingInfo, '+' )
      self.bind( '<ButtonPress-1>',      self._updateInsertStylingInfo, '+' )
      self.bind( '<ButtonRelease-1>',    self._updateInsertStylingInfo, '+' )
      
      self._styleLib    = styleLibrary if styleLibrary else { }
      self._objectLib   = objectLibrary if objectLibrary else { }
      
      self._insertTags  = [ ]
      
      Style.setupDefaults( self )
      self.reinitialize( )

   def reinitialize( self, styleLibrary=None, objectLibrary=None ):
      try:
         if styleLibrary:
            self._styleLib  = styleLibrary
         
         if objectLibrary:
            self._objectLib = objectLibrary
         
         self.delete( '1.0', 'end' )
         self._insertTags = [ '_style_default', None ]
         
         self._styleLib[ 'default' ] = Style.DEFAULT_STYLE
         self.tag_config( '_style_default', **Style.DEFAULT_STYLE.tagOptions() )
         self.tag_lower( '_style_default' )
         
         self.event_generate( '<<Reinitialized>>' )
         self.edit_reset( )
      except:
         pass

   # Content
   def dump( self, first='1.0', last='end' ):
      return EnhancedText.dump( self, first, last,
                                omittedTags=StyledText.PRIVATE_TAGS,
                                omittedMarks=StyledText.PRIVATE_MARKS )
   
   def insert( self, index, object, type=None, **options ):
      '''Insert an object into the text.
         type             object
         'text' or None   The ascii or unicode string to be inserted.
         'dump'           a dump returned from get().
         'image'          The filename of a .gif image file.
         'widget'         a Tix widget.
      '''
      if type is None:
         if isinstance( object, (str,unicode) ):
            type = 'text'
         elif isinstance( object, (list,tuple) ):
            type = 'dump'
      
      if type == 'text':
         if self.compare( index, '==', 'insert' ):
            import copy
            tags = [ x for x in self._insertTags if x ]
         else:
            tags = self.tag_names( index )
         
         EnhancedText.insert( self, index, object, tuple(tags) )
      
      elif type == 'dump':
         self._load( index, object )
      
      elif type == 'image':
         filename = object
         
         try:
            image = self._makeImage( filename )
            self.image_create( index, name=filename, image=image, padx=1, **options )
         except:
            print 'Unable to create image: ', filename
            self.image_create( index, image=RES.IMAGE_NOT_FOUND )
      
      elif type == 'widget':
         widgetName = object
         widget = self._objectLib[ widgetName ]
         self.window_create( index, window=widget, **options )
         raise Exception( 'Unknown object type' )

   def objects( self ):
      '''Return the dictionary of objects (objectname to object instance).'''
      return self._objectLib
   
   # Attributes & Styles
   def styles( self ):
      '''Return the dictionary of styles (stylename to Style object).'''
      return self._styleLib
   
   def setStyle( self, index1, index2, styleName ):
      self.clearStyling( index1, index2 )
      
      theStyle = self._styleLib[ styleName ]
      tagName = Style.NAME_FORMAT % { 'name':styleName }
      
      options = theStyle.tagOptions()
      if len(options) > 0:
         self.tag_config( tagName, **options )
      
      self.tag_add( tagName, index1, index2 )
      if styleName != '_style_default':
         try:
            self.tag_raise( tagName, '_style_default' )
         except:
            pass
   
   def setInsertStyle( self, styleName ):
      if styleName != 'default':
         tagName = Style.NAME_FORMAT % { 'name':styleName }
         self._insertTags      = [ '_style_default', tagName ]
         try:
            self.tag_raise( tagName, '_style_default' )
         except:
            pass

   def setAttribute( self, index1, index2, attribName, attribValue ):
      '''Applies an attribute name:value pair to a given region indicated by
      index1, index2.  Index1 is part of the region, index2 is not.  Valid
      values for name and value are the same as those accepted by Style.__setitem__().
      '''
      try:
         index1 = self.index( index1 )
         index2 = self.index( index2 )
      except:
         return
      
      # Manipulate the styles and tags in the region
      if attribName in Font.ATTRIBUTE_NAMES:
         for beg,end,tagNameList in self.iterRegion( index1, index2 ):
            # Get the old font info (oldFontOpts) and delete the styling tag
            for oldTagName in tagNameList:
               if oldTagName.startswith( Font.NAME_PREFIX ):
                  currentFont = Font.getFont( oldTagName )
                  self.tag_remove( oldTagName, beg, end )
                  break
            
            else:
               currentFont = Font.getFont( )
            
            # Calculating & Install new values
            newFont = currentFont.deriveFont( **{ attribName:attribValue } )
            newTagName = newFont.fontName()
            
            self.tag_add( newTagName, beg, end )
            self.tag_config( newTagName, **newFont.tagOptions() )
            self.tag_raise( newTagName )
      
      else:
         for beg,end,tagNameList in self.iterRegion( index1, index2 ):
            # If the attribute already exists, remove it.
            for oldTagName in tagNameList:
               if oldTagName.startswith(Style.ATTRIBUTE_NAME_PREFIX) or oldTagName.startswith(Font.NAME_PREFIX):
                  if oldTagName.startswith( Style.ATTRIBUTE_NAME_PREFIX + attribName + TAG_NAME_SPLITTER ):
                     self.tag_remove( oldTagName, beg, end )
                     break
            
            # If we're just deactivating, then we're done
            if attribValue in Style.OFF_VALUES[ attribName ]:
               continue
            
            # Calculate the new values
            newTagName = Style.ATTRIBUTE_NAME_FORMAT % { 'name':attribName, 'value':str(attribValue) }
            styleObj   = Style( **{ attribName:attribValue } )
            
            # Install the new values
            self.tag_add( newTagName, beg, end )
            self.tag_config( newTagName, styleObj.tagOptions( ) )
            self.tag_raise( newTagName )
   
   def setInsertAttribute( self, attribName, attribVal ):
      if attribName in Font.ATTRIBUTE_NAMES:
         for oldTagName in self._insertTags:
            if oldTagName and oldTagName.startswith( Font.NAME_PREFIX ):
               theNewFont = Font.getFont( oldTagName ).deriveFont( **{attribName:attribVal} )
               self.tag_config( theNewFont.fontName(), **theNewFont.tagOptions() )
               try:
                  self._insertTags.append( theNewFont.fontName() )
               except:
                  pass
               
               try:
                  self._insertTags.remove( oldTagName )
               except:
                  pass
               break
         else:
            try:
               theOldFont = Font.getFont( self.tag_config(self._insertTags[1])['font'][-1] )
            except:
               theOldFont = Font.getFont( self.tag_config(self._insertTags[0])['font'][-1] )
            
            theNewFont = theOldFont.deriveFont( **{ attribName:attribVal } )
            
            self._insertTags.append( theNewFont.fontName() )
            self.tag_config( theNewFont.fontName(), **theNewFont.tagOptions() )
            self.tag_raise( theNewFont.fontName() )
      
      else:
         soughtAttribPrefix = Style.ATTRIBUTE_NAME_PREFIX + '%s_' % attribName
         for oldTagName in self._insertTags:
            if oldTagName and oldTagName.startswith( soughtAttribPrefix ):
               newAttrib = Style( **{ attribName : attribVal } )
               newTagName = Style.ATTRIBUTE_NAME_FORMAT % { 'name':attribName, 'value':attribVal }
               self.tag_config( newTagName, **newAttrib.tagOptions() )
               try:
                  self._insertTags.append( newTagName )
               except:
                  pass
               
               try:
                  self._insertTags.remove( oldTagName )
               except:
                  pass
               break
         else:
            newAttrib = Style( **{ attribName : attribVal } )
            newTagName = Style.ATTRIBUTE_NAME_FORMAT % { 'name':attribName, 'value':attribVal }
            self._insertTags.append( newTagName )
            self.tag_config( newTagName, **newAttrib.tagOptions() )
            self.tag_raise( newTagName )

   def effectiveStyling( self, index ):
      '''Return a dictionary of all the styling attributes mapped to values.
      This dictionary provides the effective styling at the given index.  That
      is, the styling values that text will apply to the character displayed
      at that index (hidden attributes, such as those further down on the tag-
      stack, will not appear).'''
      opts = copy.copy( Style.DEFAULT_STYLE.opts() )
      localStyleName = 'default'
      for name in self.tag_names( index ):
         if name == 'sel':
            continue
         
         if name.startswith( Style.ATTRIBUTE_NAME_PREFIX ):
            attribName, attribValue = name.split(TAG_NAME_SPLITTER)[2:]
            if attribName in ('bold','italic','underline','overstrike'):
               attribValue = bool(attribValue)
            elif attribName in ('size'):
               attribValue = int(attribValue)
            
            opts[ attribName ] = attribValue
         
         elif name.startswith( Style.NAME_PREFIX ):
            styleName = name.split('_')[2]
            opts.update( self._styleLib[styleName].opts() )
            localStyleName = styleName
         
         elif name.startswith( Font.NAME_PREFIX ):
            opts.update( Font.getFont(name).opts() )
         
      if 'font' in opts:
         opts.update( Font.getFont( opts['font'] ).opts( ) )
         del opts[ 'font' ]
      
      return opts, localStyleName
   
   def effectiveInsertStyling( self ):
      '''Return a dictionary of all the styling attributes mapped to values.
      This dictionary provides the effective styling at the given index.  That
      is, the styling values that will apply to the character displayed
      at that index (hidden attributes, such as those further down on the tag-
      stack, will not be included).'''
      opts = copy.copy( Style.DEFAULT_STYLE.opts() )
      if self._insertTags[1]:
         localStyleName = self._insertTags[1].split('_')[2]
         opts.update( self._styleLib[ localStyleName ].opts() )
      
      for name in self._insertTags[2:]:
         if name.startswith( Style.ATTRIBUTE_NAME_PREFIX ):
            attribName, attribValue = name.split(TAG_NAME_SPLITTER)[2:]
            if attribName in ('bold','italic','underline','overstrike'):
               attribValue = attribValue.lower() in ('1', 'yes', 'true')
            elif attribName in ('size'):
               attribValue = int(attribValue)
            
            opts[ attribName ] = attribValue
         
         elif name.startswith( Font.NAME_PREFIX ):
            opts.update( Font.getFont(name).opts() )
      
      if 'font' in opts:
         opts.update( Font.getFont( opts['font'] ).opts( ) )
         del opts[ 'font' ]
      
      return opts, self._insertTags[1]

   def clearStyling( self, index1, index2=None, attributes=True, style=True ):
      try:
         index1 = self.index( index1 )
         index2 = self.index( index2 )
      except:
         return
      
      for begin, end, tagNameList in self.iterRegion( index1, index2 ):
         for tagName in tagNameList:
            if tagName.startswith(Style.ATTRIBUTE_NAME_PREFIX) or tagName.startswith(Font.NAME_PREFIX):
               if attributes:
                  self.tag_remove( tagName, begin, end )
            else:
               if style and (tagName not in StyledText.PRIVATE_TAGS):
                  self.tag_remove( tagName, begin, end )

   # Implementation Only -- Not intended for use by client software
   def _load( self, index, dump ):
      '''Slave routine for insert.  This method handles inserting dumps.'''
      self.mark_set( 'insertHere', index )
      
      # Be sure that the 'img' subdirectory exists
      if not os.path.exists( 'img' ):
         os.mkdir( 'img' )
      
      tags = { }
      for element in dump:
         action = element[0]
         value  = element[1]
         index  = self.index( Tix.INSERT )
         
         if action == 'tagon':
            tags[ value ] = index
         elif action == 'tagoff':
            if value in StyledText.PRIVATE_TAGS:
               continue
            elif value[0] == '$':
               continue
            
            try:
               regionBegin = tags[ value ]
               del tags[ value ]
            except:
               raise Exception( 'tagoff not preceded by tagon.' )
            
            regionEnd   = index
            tagName     = value
            
            if tagName.startswith( Style.NAME_PREFIX ):
               styleName = tagName.split('_')[2]
            else:
               styleName = tagName
            
            try:
               newTagOpts = self._styleLib[ styleName ].tagOptions()
            except:
               newStyle = Style.getStyle( styleName )
               newTagOpts = newStyle.tagOptions()
            
            self.tag_add( tagName, regionBegin, regionEnd )
            self.tag_config( tagName, **newTagOpts )
            
            if tagName.startswith( Style.NAME_PREFIX ):
               try:
                  self.tag_raise( tagName, '_style_default' )
               except:
                  self.tag_lower( tagName )
            else:
               self.tag_raise( tagName )
         elif action == 'text':
            EnhancedText.insert( self, 'insertHere', value )
         elif action == 'mark':
            if value in StyledText.PRIVATE_MARKS:
               continue
            self.mark_set( index, value )
         elif action == 'image':
            self.insert( 'insertHere', value, 'image' )
         elif action == 'window':
            self.insert( 'insertHere', value, 'widget' )
         else:
            raise Exception( 'Unknown Action: ' + str(action) )
      
      self.mark_unset( 'insertHere' )

   def _makeImage( self, filename ):
      if filename not in self._objectLib:
         self._objectLib[ filename ] = Tix.PhotoImage( file=filename )
      
      return self._objectLib[ filename ]

   def _updateInsertStylingInfo( self, event=None ):
      self._insertTags  = [ '_style_default', None ]
      
      for name in self.tag_names( 'insert -1 chars' ):
         if name == 'sel':
            continue
         
         if name[0] == TAG_NAME_SPLITTER:
            self._insertTags.append( name )
         else:
            self._insertTags[1] = name

