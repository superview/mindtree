"""
Macro Usage
===========

   Syntax:

      Simple & parameterized directives

      {{name}}                                  ;; simple macro
      {{name( arg1, arg2, ... )}}               ;; parameterized macro
      {{name: ... }}                            ;; block macro
      {{name( arg1, arg2, ... ): ... }}         ;; parameterized block macro

      where,
         name,  is the name of the macro.
         arg1,  arg2, ..., are various arguments to the macro.
         ...,   is arbitrary text which constitutes the object delimited by
                the macro.

   Arguments:

      Arguments may take one of the following forms:

      Quoted String

         A group of characters surrounded by " and ".

      Triple Quoted String

         A group of characters surrounded by triple quotes (\"\"\" and \"\"\").
         A triple quoted string can span multiple lines.  Line breaks are
         preserved.

      Tuple

         A list of comma-separated objects (Quoted String, Triple Quoted String,
         or Tupel) enclosed in parenthesis; ( and ).


Macro Definition
================

   There's only one built-in macro:  'define'.  It's used for defining new
   macros.  It has the following form:

      {{define( name, params, value )}}

   name

      A quoted or triple-quoted string which is the name of the new macro.

   params

      A tuple of quoted or triple-quoted strings listing the names of the
      parameters.  If value passed as params is ( ), an empty tuple, then the
      macro being defined takes no arguments.  Thus it's either a simple macro
      or an unparameterized block macro.

   value

      Two kinds of values are possible.  To define a simple macro, the value
      must be a quoted or triple-quoted string.  To define a block macro, the
      value must be a tuple of two quoted or triple-quoted strings.

   When a macro is actually used, the parameters get turned into new macros of
   the name {{macroName.parameterName}}.  These values stay in effect until
   the macro is used again at which time the parameter macros get redefined.

   example:

      {{define( "document", ( "name" ), ( "<HTML>", "</HTML>" ) )}}

      {{document( "My Home Page" ):
         Once this second macro is evaluated, a new macro is created with the
         name {{document.name}} whose value is set to "My Home Page".
      }}


Evaluation Order
================

   Macros may be considered in terms of segments.  Simple and Parameterized
   macros are complete segments in themselves.  However, block macros are
   composed of two segments;  {{name: or {{name(args): and }}

   Generally evaluation of a macro occurs as soon as parsing of a segment is
   completed.  This includes macros that happen to occur within quotes.  For

   example:

      {{section( "Last Updated: {{date}}", "text" ):

      Here, {{date}} will be evaluated first, because the parser will reach
      the end of that macro before it reaches the end of the {{section...:
      macro.

   These so called 'nested macros' may appear anywhere within a macro segment.

      {{define( "style", ( ), "Text" )}}
      {{blockOf{{style}}:...}}

      Here, the {{define...}} macro will get evaluated, which creates a new
      macro called {{style}}.  In evaluating the second macro, first the
      {{style}} macro is evaluated, resuling in

      {{blockOfText:...}}

      Then the resulting macro is evaluated.

   It is possible to change the evaluation order by prepending a $ to a quoted
   or triple-quoted string, you suspend evaluation through one pass of the
   parser.  This is particularly useful for using 'define', where you don't
   want the value to be evaluated until the macro is actually used.

   example:

      {{define( "article", ( "title" ), $"<H4>{{article.title}}</H4>")}}

   If this macro were evaluated using the normal evaluation order then the
   first thing that would happen is an attempt to evaluate the submacro
   {{article.title}}.  But it doesn't exist yet.  The $ forces the parser to
   take the entire quoted string as-is for the value of "article".  Here are
   the steps of evaluation laid out:

   After evaluation of the above define, we have

      "article" ( "title" )   mapped to  "<H4>{{article.title}}</H4>"

   Later we encounter:

      {{article( "I Like Cats Too!" ):

   Which expands to:

      <H4>{{article.title}}</H4>

   At the same time, it defines a new macro:

      "article.title"         mapped to  "I Like Cats Too!"

   The parser continues along the string, and eventually encounters
   {{article.title}} which gets expanded so that we have:

      <H4>I Like Cats Too!</H4>
"""

class Macro:
   PREFIX     =   0
   POSTFIX    =   1

   def __init__( self, params, value ):
      assert isinstance( params, ( str, unicode, tuple ) ) or ( params is None )
      assert isinstance( value,  ( str, unicode, tuple ) )
      
      if params is None:
         params = ( )
      elif isinstance( params, ( str, unicode ) ):
         params = tuple( [ params ] )
      elif isinstance( params, tuple ):
         for entry in params:
            assert isinstance( entry, ( str, unicode ) )
      
      if isinstance( value, tuple ):
         assert len( value ) == 2
         assert isinstance( value[0], ( str, unicode ) )
         assert isinstance( value[1], ( str, unicode ) )
      
      self._params = params
      self._value  = value

   def hasParams( self ):
      return self._params is not None

   def wrapsBlock( self ):
      return isinstance( self._value, tuple )

   def params( self ):
      return self._params

   def value( self, ord = PREFIX ):
      if isinstance( self._value, tuple ):
         return self._value[ ord ]
      else:
         return self._value


class MacroEvaluator:
   def __init__( self ):
      self._envStack = [ ]

   # Extension
   def beginMacro( self, macroName, macroArgs = None ):
      assert isinstance( macroName, (str,unicode) )
      assert isinstance( macroArgs, (list,tuple)  ) or ( macroArgs is None )
      
      if macroArgs is None:
         macroArgs = ( )
      
      self._envStack.append( ( macroName, macroArgs ) )
      return self.evalBeginMacro( macroName, macroArgs )

   def endMacro( self ):
      macroName, macroArgs = self._envStack.pop( )
      return self.evalEndMacro( macroName, macroArgs )

   def simpleMacro( self, macroName, macroArgs = None ):
      assert isinstance( macroName, (str,unicode) )
      assert isinstance( macroArgs, (list,tuple)  ) or ( macroArgs is None )
      
      if macroArgs is None:
         macroArgs = ( )
      
      return self.evalSimpleMacro( macroName, macroArgs )

   def assertContext( self, aContext ):
      if len( self._envStack ) > 0:
         if self._envStack[ -1 ][ 0 ] != aContext:
            raise SyntaxError, "Invalid context asserted.  Problems matching {{ with }}."

   # Contract
   def evalBeginMacro( self, macroName, macroArgs = None ):
      """This method should return the expansion for the beginning of a block macro."""
      raise NotImplementedError

   def evalEndMacro( self, macroName, macroArgs = None ):
      """This method should return the expansion for the ending of a block macro."""
      raise NotImplementedError

   def evalSimpleMacro( self, macroName, macroArgs = None ):
      """This method should return the expansion for a simple macro."""
      raise NotImplementedError


class Buffer:
   def __init__( self, buf ):
      assert isinstance( buf, (str,unicode) )
      
      self.buf   = buf
      self.point = 0

   def substitute( self, aNewSubstring, aMark ):
      assert isinstance( aNewSubstring, (str,unicode) )
      assert isinstance( aMark,         int           )
      
      newVal = self.buf[ : aMark ] + aNewSubstring + self.buf[ self.point : ]
      self.buf = newVal

   def getSubString( self, aMark ):
      assert isinstance( aMark, int )
      
      return self.buf[ aMark : self.point ]

   def more( self ):
      return self.point < len( self.buf )

   def peek( self ):
      return self.buf[ self.point ]

   def consumeString( self, aStr ):
      assert isinstance( aStr, (str,unicode) )
      
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


class MacroProcessor:
   import re
   whiteSpace       = re.compile( r'\s' )
   delimiter        = re.compile( r'\{\{|\}\}' )
   nameRegEx        = re.compile( r'[a-zA-Z0-9\.\-\_]+' )
   stringRegEx      = re.compile( r'\"([^"]|\\.)*\"' )
   tqstringRegEx    = re.compile( r'\"\"\"((?!\"\"\").|\\.)*\"\"\"', re.DOTALL )

   # Standard Methods
   def __init__( self, handler ):
      assert isinstance( handler, MacroEvaluator )
      
      self._handler = handler

   # Extension
   def process( self, string ):
      assert isinstance( string, (str,unicode) )
      
      buf = Buffer( string )
      
      while buf.consumeUpTo( self.delimiter ):
         macroPos = buf.point
         self.processMacro( buf )
         buf.point = macroPos
      
      return buf.buf

   def processMacro( self, buf ):
      assert isinstance( buf, Buffer )
      
      macroPos = buf.point
      if buf.consumeString( '}}' ):
         buf.substitute( self._handler.endMacro( ), macroPos )
      
      elif buf.consumeString( '{{' ):
         name = self.processMacroName( buf )
         
         if buf.consumeString( '}}' ):
            buf.substitute( self._handler.simpleMacro( name, None ), macroPos )
         elif buf.consumeString( ':' ):
            buf.substitute( self._handler.beginMacro( name, None ), macroPos )
         elif buf.peek( ) == '(':
            args = self.processTuple( buf )
            
            if buf.consumeString( ':' ):
               buf.substitute( self._handler.beginMacro( name, args ), macroPos )
            elif buf.consumeString( '}}' ):
               buf.substitute( self._handler.simpleMacro( name, args ), macroPos )
            else:
               raise SyntaxError, "Invalid macro termnation, ':' or '}}' expected."
         else:
            raise SyntaxError, "Invalid macro, '}}', ':' or '(' expected."
      else:
         raise SyntaxError, "Invalid macro intro, '{{' or '}}' expected."

   def processMacroName( self, buf ):
      assert isinstance( buf, Buffer )
      
      nameBeginPos = buf.point
      buf.consumeRegEx( self.nameRegEx )
      
      while buf.peek( ) == '{':
         savePos = buf.point
         self.processMacro( buf )
         buf.point = savePos
         
         buf.consumeRegEx( self.nameRegEx )
      
      if buf.peek( ) not in ( ':', '(', '}' ):
         raise SyntaxError, "Macro name must be followed by ':', '(' or '}'."
      
      return buf.getSubString( nameBeginPos )

   def processTuple( self, buf ):
      assert isinstance( buf, Buffer )
      
      args = [ ]
      
      buf.consumeString( '(' )
      
      buf.consumePast( self.whiteSpace )
      if buf.peek( ) != ')':
         args.append( self.processTupleItem( buf ) )
      
      buf.consumePast( self.whiteSpace )
      while buf.consumeString( ',' ):
         buf.consumePast( self.whiteSpace )
         
         args.append( self.processTupleItem( buf ) )
         buf.consumePast( self.whiteSpace )
      
      if not buf.consumeString( ')' ):
         raise SyntaxError, "Tuple not terminated, ')' expected."
      
      return tuple( args )

   def processTupleItem( self, buf ):
      assert isinstance( buf, Buffer )
      
      evalSubMacros = not buf.consumeString( '$' )
      
      if buf.peek( ) == '"':
         strMark = buf.point
         if buf.consumeRegEx( self.tqstringRegEx ):
            subStr = buf.getSubString( strMark )
            subStr = subStr[ 3 : -3 ]
         elif buf.consumeRegEx( self.stringRegEx ):
            subStr = buf.getSubString( strMark )
            subStr = subStr[ 1 : -1 ]
         else:
            raise SyntaxError, "Invalid string literal."
         
         if evalSubMacros:
            subStr = self.process( subStr )
         
         return subStr
      
      elif buf.peek( ) == '(':   # ( ... )
         return self.processTuple( buf )
      
      else:
         raise SyntaxError, "Invalid tuple item; \" or ( expected."

   @staticmethod
   def splice( aBaseStr, aBeginPos, anEndPos, newSubstr ):
      assert isinstance( aBaseStr,  (str,unicode) )
      assert isinstance( aBeginPos, int           )
      assert isinstance( anEndPos,  int           )
      assert isinstance( newSubstr, (str,unicode) )
      
      return ''.join( ( aBaseStr[ : aBeginPos ], newSubstr, aBaseStr[ anEndPos : ] ) )


class BasicMacroEvaluator( MacroEvaluator ):
   def __init__( self, aDict = None ):
      assert isinstance( aDict, dict ) or ( aDict is None )
      MacroEvaluator.__init__( self )
      if aDict is None:
         self._macros = { }
      else:
         self._macros = aDict
      
      from datetime import date
      self._macros[ 'define' ] = Macro( ( 'name', 'params', 'value' ), '' )
      self._macros[ 'date'   ] = Macro( None, date.today( ).isoformat( ) )
      
      self.bookmarkReport = {}

   def define( self, macroName, definition ):
      assert isinstance( macroName, ( str, unicode ) )
      assert isinstance( definition, Macro ) or (definition is None)
      
      if definition is None:
         del self._macros[ macroName ]
      else:
         self._macros[ macroName ] = definition

   def isDefined( self, macroName ):
      assert isinstance( macroName, ( str, unicode ) )
      return macroName in self._macros

   def resetDefs( self ):
      self._macros = { }

   def evalBeginMacro( self, macroName, macroArgs ):
      assert isinstance( macroName, (str,unicode) )
      assert isinstance( macroArgs, (list,tuple)  )
      
      if macroName not in self._macros:
         raise KeyError, "Attempted to used an undefined macro: %s" % macroName
      
      if not self._macros[ macroName ].wrapsBlock( ):
         raise SyntaxError, "Attempted to use a simple macro to wrap a block: %s." % macroName
      
      self.storeArgs( macroName, macroArgs )
      
      return self._macros[ macroName ].value( Macro.PREFIX )

   def evalEndMacro( self, macroName, macroArgs ):
      assert isinstance( macroName, (str,unicode) )
      assert isinstance( macroArgs, (list,tuple)  )
      
      return self._macros[ macroName ].value( Macro.POSTFIX )

   def evalSimpleMacro( self, macroName, macroArgs ):
      assert isinstance( macroName, (str,unicode) )
      assert isinstance( macroArgs, (list,tuple)  )
      
      if macroName not in self._macros:
         raise KeyError, "Attempted to used an undefined macro: %s" % macroName
      
      if self._macros[ macroName ].wrapsBlock( ):
         raise SyntaxError, "Attempted to use a block macro as simple: %s." % macroName
      
      self.storeArgs( macroName, macroArgs )
      
      if macroName == 'define':
         self._macros[ macroArgs[0] ] = Macro( macroArgs[1], macroArgs[2] )
      
      return self._macros[ macroName ].value( )

   def storeArgs( self, macroName, macroArgs ):
      assert isinstance( macroName, (str,unicode) )
      assert isinstance( macroArgs, (list,tuple)  )
      
      if macroName == 'define':
         return
      elif macroName not in self._macros:
         raise KeyError, "Attempted to use an undefined macro: %s" % macroName

      params = self._macros[ macroName ].params( )

      for param, arg in zip( params, macroArgs ):
         self._macros[ macroName + '.' + param ] = Macro( None, arg )

