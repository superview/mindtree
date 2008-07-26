"""
Standard Tags
=============

   Document Structure

      {{document( "Title" ): ... }}
      
      {{article( "id", "title", "location" ): ... }}
         ;;; Articles must appear contextually within the 'document' markup.
      
      {{section( "title", "style" ): ... }}
         ;;; Sections must appear contextually within the 'article' markups.
      
      {{item: ... }}
         ;;; Items must appear contextually within the 'section' markups.
         
         From these four markup tags, documents appear as follows:
         
            {{document( "title" ):
               {{article( "Title", "id", "Path" ):
                  {{section( "Title", "type" ):
                     {{Item:
                        {{style( "Style" ):
                           text
                        }}
                     }}
                     
                     ...
                  }}
               }}
            }}

   Links

      {{bookmark( "bookmarkName" )}}
         ;;; Bookmarks provide global names for the most recent 'article'
         anchor.

      {{see( "URL" ): clickableText }}

         where URL is,
            "mailto:emailaddress", a link to email
            "http://website",      a link to an external site.
            "bookmarkName",        a link to a bookmark

   Styles

      {{B: ... }}
      {{I: ... }}
      {{U: ... }}
      {{PRE: ... }}
      {{SUPER: ... }}
      {{OFFSET: ... }}

   Misc

      {{BR}}
      {{date}}


Sections & Items
================

   Synopsis:

      Section and Item tags are very common.  For this reason, there are
      abbreviated notations to allow for a more readable outline.

      [[ title ]]: style ...

         is shorthand for:

            {{section( "title", "style" ): ... }}

         The ... implicitly terminates at the next section or the end of
         the article.

         style is:

            For Paragraphs:

               text

            For Unordered Lists:

               unordered   bulletized with closed circles
               bullet      bulletized with closed circles
               circle      bulletized with open circles
               square      bulletized with closed circles

            For Ordered Lists:

               ordered     Numbered with decimal numbers
               A           Numbered with capital letters
               a           Numbered with lower case letters
               I           Numbered with capital roman numerals
               i           Numbered with lower case roman numerals
               1           Numbered with decimal numbers

      [[ title ]] ...

         is shorthand for:

            {{section( "title", "text" ): ... }}

      @@ ...

         is shorthand for:

            {{item: ... }}

         the ... implicitly terminates at the next item, or at the end of
         the section.


   Defaults:

      If <style> is not specified, then 'text' is assumed.

"""

from Tree import Tree


from MacroProcessor import Macro
from MacroProcessor import MacroProcessor
from MacroProcessor import BasicMacroEvaluator


class HTMLBuilder( object ):
                   # ( icon file,                   width, height )
   LINE_VERT       = ( "img/ftv2vertline.png",     16,    22     )
   LINE_EMPTY      = ( "img/ftv2blank.png",        16,    22     )
   DOC_LINE_NODE   = ( "img/ftv2node.png",         16,    22     )
   DOC_LINE_LAST   = ( "img/ftv2lastnode.png",     16,    22     )
   FLD_LINE_NODE   = ( "img/ftv2pnode.png",        16,    22     )
   FLD_LINE_LAST   = ( "img/ftv2plastnode.png",    16,    22     )
   DOC_ICON        = ( "img/ftv2doc.png",          24,    22     )
   FLD_ICON        = ( "img/ftv2folderclosed.png", 24,    22     )

   def __init__( self ):
      self.frame         = None
      self.outline       = None
      self.articles      = None
      
      self._msp          = None
      
      self.location      = [ ]
      
      self._articleCount = 0
      
      self.nestingStack  = None
         # list of tuple: ( entryName, isLast )

   def locationStr( self, aSeparator = u' :: ' ):
      return aSeparator.join( self.location )
      if len( self.location ) <= 1:
         return u''
      
      locationStr = self.location[1]
      for locIdx in xrange( len( self.location ) - 2 ):
         locationStr += aSeparator + self.location[ locIdx+2 ]
      
      return locationStr

   def loadMacroFile( self, macroDefs = None ):
      macroFile = open( macroDefs, "r" )
      macroDefsStr = ""
      for line in macroFile:
         macroDefsStr += line
      self._msp.process( macroDefsStr )
      macroFile.close( )

   def procAndTrans( self, aString ):
      # Expand Macros
      string = self._msp.process( aString )
      
      # Translate unicode characters
      outStr = ''
      for char in string:
         charOrd = ord(char)
         if charOrd >= 128:
            outStr += '&#%d;' % charOrd
         else:
            outStr += char
      
      return outStr

   def buildTreeElementStr( self, element, id = None ):
      if ( id is not None ):
         return u"<img src=%s width=%d height=%d onclick=\"toggleFolder(\'folder%s\', this)\" />" % ( element[0], element[1], element[2], id )
      else:
         return u"<img src=%s width=%d height=%d />" % element

   def buildTreeEntryStr( self, item, isLastInSubtree ):
      result = u""
      
      # Scope Lines
      # -----------
      for scope in self.nestingStack:
         if scope == False:
            result += self.buildTreeElementStr( HTMLBuilder.LINE_VERT )
         else:
            result += self.buildTreeElementStr( HTMLBuilder.LINE_EMPTY )
      
      # open/close & icon
      # -----------------
      if len( self.nestingStack ) > -1:
         if isLastInSubtree:
            if len(item.subtrees) == 0:
               # Doc Last Node
               result += self.buildTreeElementStr( HTMLBuilder.DOC_LINE_LAST )
               result += self.buildTreeElementStr( HTMLBuilder.DOC_ICON )
            else:
               # Folder Last Node
               result += self.buildTreeElementStr( HTMLBuilder.FLD_LINE_LAST, item.id )
               result += self.buildTreeElementStr( HTMLBuilder.FLD_ICON, item.id )
         else:
            if len(item.subtrees) == 0:
               # Doc Node
               result += self.buildTreeElementStr( HTMLBuilder.DOC_LINE_NODE )
               result += self.buildTreeElementStr( HTMLBuilder.DOC_ICON )
            else:
               # Folder Node
               result += self.buildTreeElementStr( HTMLBuilder.FLD_LINE_NODE, item.id )
               result += self.buildTreeElementStr( HTMLBuilder.FLD_ICON, item.id )
      
      return result

   def _buildTree( self, items, notesName ):
      last = items[-1]
      for item in items:
         self.current = item
         
         self.outline.write( u'<p>' )
         
         # Build the Outline Tree
         self.outline.write( self.buildTreeEntryStr( item, item == last ) )
         
         # Item
         if item.article:
            if isinstance( item.article, (str,unicode) ):
               item.article += u' '
            
            self._articleCount += 1
            
            articleName = item.title = self.procAndTrans( item.title )
            
            try:
               anchor = u'<a href="%s#%s" target="baseframe">%s</a>' % (notesName, self._articleCount, articleName )
               anchorStr = str( anchor )
               self.outline.write( anchorStr )
            except:
               pass
            
            self.procAndTrans( u'{{article( "%s", """ %s """, """ %s """ ):\n' % ( self._articleCount, articleName, self.locationStr( ) ) )
            if isinstance( item.article, (str,unicode) ):
               for line in item.article.splitlines( True ):
                  self.procAndTrans( line )
            else:
               result = u''
               for key,val,index in item.article:
                  if key == 'text':
                     result += val
               self.procAndTrans( result )
            self.procAndTrans( u'}}' )
         
         else:
            self.outline.write( self.procAndTrans( item.title ) )
         
         self.outline.write( u'</p>\n' )
         
         # subtrees
         if len(item.subtrees) > 0:
            self.outline.write( u'<div id="folder%s">\n' % (item.id) )
            self.nestingStack.append( item == last )
            self._buildTree( item.subtrees, notesName )
            self.nestingStack.pop( )
            self.outline.write( u'</div>\n' )

   def buildTree( self, outline, name, notesName ):
      print "Generating tree..."
      self.nestingStack = []
      self.outline.write( self.procAndTrans( u'{{outline( "%s" ):' % name ) )
      self._articleCount = 0
      self._buildTree( outline.subtrees, notesName )
      self.outline.write( self.procAndTrans( u'}}' ) )
   
   def writeArticle( self, item ):
      articleName = item.title
      
      if isinstance( item.article, (list,tuple) ):
         import TkTools
         result = u''
         
         for key,val,index in item.article:
            if key == 'tagon':
               result += '<%s>' % val
            elif key == 'tagoff':
               result += '</%s>' % val
            elif key == 'text':
               result += val
            elif key == 'image':
               disk,path,filename,extension = TkTools.splitFilePath( val )
               newFilename = filename + extension
               result += '<img SRC=\"%s\">' % newFilename
         
         self.articles.write( result )
         return
      
      begin = u'{{article( "%s", """ %s """, """ %s """ ):\n' % ( self._articleCount, articleName, self.locationStr( ) )
      self.articles.write( self.procAndTrans( begin ) )
      
      sectionBegun = False
      itemBegun    = False
      
      lineList     = item.article.splitlines( True )
      item.article    = u""
      for line in lineList:
         if line.lstrip( )[0:2] == '[[':
            # Parse the delimiters
            begPos   = line.find( '[[' )
            stylePos = line.find( ']]' )
            
            if stylePos == -1:
               raise Exception, "Invalid section specification."
            
            title = line[ begPos + 2 : stylePos ]
            
            if title == 'Definition':
               icon = u'{{icon.def}}'
            else:
               icon = u''
            
            if line[ stylePos + 2 ] != ':':
               style = u'text'
               endPos = stylePos + 2
            else:
               stylePos += 3
               while line[ stylePos ] in ( ' ', '\t' ):
                  stylePos += 1
               
               match = MacroProcessor.nameRegEx.match( line, stylePos )
               styleSlice = match.span( )
               style = line[ styleSlice[0] : styleSlice[1] ]
               endPos = styleSlice[1]
            
            # splice the new substring
            if itemBegun:
               line = MacroProcessor.splice( line, begPos, endPos, u'}} }} {{section( "%s%s", "%s" ):' % ( icon, title, style ) )
            elif sectionBegun:
               line = MacroProcessor.splice( line, begPos, endPos, u'}} {{section( "%s%s", "%s" ):' % ( icon, title, style ) )
            else:
               line = MacroProcessor.splice( line, begPos, endPos, u'{{section( "%s%s", "%s" ):' % ( icon, title, style ) )
            
            sectionBegun = True
            itemBegun    = False
         elif line.lstrip( )[0:2] == '@@':
            # Parse the delimiters
            begPos   = line.find( '@@' )
            endPos   = begPos + 2
            
            #splice the new substring
            if itemBegun:
               line = MacroProcessor.splice( line, begPos, endPos, u'}} {{item:' )
            else:
               line = MacroProcessor.splice( line, begPos, endPos, u'{{item:' )
            
            itemBegun = True
         
         # Process the line
         item.article += line
      
      item.article += u'\n\n }}'
      if itemBegun:
         item.article += u' }}'
      if sectionBegun:
         item.article += u' }}'
      item.article += u'\n'
      
      self.articles.write( self.procAndTrans( item.article ) )

   def _buildArticles( self, items ):
      for item in items:
         self.current = item
         
         # Construct the location string
         self.location.append( item.title )
         
         # Item
         if item.article:
            if isinstance( item.article, (str,unicode) ):
               item.article += u' '
            
            self._articleCount += 1
            try:
               self.writeArticle( item )
            except:
               print 'Problem in writing article: %s' % item.title
         
         self._buildArticles( item.subtrees )
         
         self.location.pop( )

   def buildArticles( self, outline ):
      self._articleCount = 0
      self._buildArticles( outline.subtrees )

   def buildHTML( self, outline, rootPath, htmDir, imgDir, name ):
      import os
      
      htmPath = os.path.join( rootPath, htmDir )
      imgPath = os.path.join( rootPath, imgDir )
      
      extension           = 'html'
      frameName           = ''.join( ( "welcome", os.extsep, extension ) )
      outlineName         = ''.join( ( "outline", os.extsep, extension ) )
      articlesName        = ''.join( ( "articles", os.extsep, extension ) )
      
      framePathName       = os.path.join( htmPath, frameName )
      outlinePathName     = os.path.join( htmPath, outlineName )
      articlesPathName    = os.path.join( htmPath, articlesName )
      
      self.frame          = open( framePathName, "w" )
      self.outline        = open( outlinePathName, "w" )
      self.articles       = open( articlesPathName, "w" )
      
      eval                = BasicMacroEvaluator( )
      self._msp           = MacroProcessor( eval )
      
      self.loadMacroFile( "Plugins\\HTMLArchiver\\articles.mac" )
      
      try:
         #count = outline.count( )
         count = 1000
         self.articles.write( self.procAndTrans( u'{{document("%s", "%d"):' % ( name, count ) ) )
         
         # Construct the Frame
         self.frame.write( self.procAndTrans( u'{{frame( "%s", "%s", "%s" )}}' % ( name, outlineName, articlesName ) ) )
         
         # Construct the bodies
         if len( outline.subtrees) > 0:
            # Tree
            self.buildTree( outline, name, articlesName )
            
            self.procAndTrans( u"""{{define( "see", ( "name" ), ( $\"\"\"<A HREF="#{{bookmark.{{see.name}}}}" TARGET="baseframe">\"\"\", $"</A>") )}}""" )
            
            # Articles
            print "Generating articles..."
            self.buildArticles( outline )
         
         self.articles.write( self.procAndTrans( u'}}' ) )
         
         for key,val in self._msp._handler._macros.items( ):
            if key.startswith( 'bookmark.' ):
               print '%-40s:%6s' % ( key,val._value )
         
      except Exception, (msg):
         print 'Exception raised while processing article \'%s\' (%s)\n%s' % ( self.current.title, self.current.id, msg )
         raise
      
      self.frame.close()
      self.outline.close()
      self.articles.close()

