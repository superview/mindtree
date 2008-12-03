from __future__ import print_function, unicode_literals
from Tree import Tree


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

   OUTLINE_HEAD    = '''<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
   <meta http-equiv="Content-Type" content="text/xhtml;charset="iso-8859-1" />
   <meta http-equiv="Content-Style-Type" content="text/css" />
   <meta http-equiv="Content-Language" content="en" />
   <link rel="stylesheet" href="doxygen.css">
   <title>TreeView</title>
   <style type="text/css">
   <!--
   BODY,H1,H2,H3,H4,H5,H6,P,CENTER,TD,TH,UL,DL,DIV,PRE
      {
      font-family: Lucida Sans Unicode, Geneva, Arial, Helvetica, sans-serif;
      }
   .directory { font-size: 10pt; font-weight: bold; }
   .directory h3 { margin: 0px; margin-top: 1em; font-size: 11pt; }
   .directory p { margin: 0px; white-space: nowrap; }
   .directory div { display: none; margin: 0px; }
   .directory img { vertical-align: middle; }
   -->
   </style>
   <script type="text/javascript">
   <!-- // Hide script from old browsers

   function findChildNode(node, name)
      {
      var temp;

      if (node == null)
         return null;

      node = node.firstChild;

      while (node != null)
         {
         if (node.nodeName == name)
            return node;

         temp = findChildNode(node, name);

         if (temp != null)
            return temp;

         node = node.nextSibling;
         }

      return null;
      }

   function toggleFolder(id, imageNode)
      {
      var folder = document.getElementById(id);
      var l = 0;
      var vl = "img/ftv2vertline.png";

      if ( imageNode.nodeName != "IMG" )
         {
         imageNode = findChildNode(imageNode, "IMG");

         l = imageNode.src.length;
         }

      if ( folder.style.display == "block" )
         {
         while ( imageNode.src.substring(l-vl.length,l) == vl )
            {
            imageNode = imageNode.nextSibling;
            l = imageNode.src.length;
            }

         l = imageNode.src.length;
         imageNode.nextSibling.src = "img/ftv2folderclosed.png";

         if ( imageNode.src.substring(l-13,l) == "img/ftv2mnode.png" )
            imageNode.src = "img/ftv2pnode.png";
         else if ( imageNode.src.substring(l-17,l) == "img/ftv2mlastnode.png" )
            imageNode.src = "img/ftv2plastnode.png";

         folder.style.display = "none";
         }
      else
         {
         while ( imageNode.src.substring(l-vl.length,l) == vl )
            {
            imageNode = imageNode.nextSibling;
            l = imageNode.src.length;
            }

         l = imageNode.src.length;
         imageNode.nextSibling.src = "img/ftv2folderopen.png";

         if ( imageNode.src.substring(l-13,l) == "img/ftv2pnode.png" )
            imageNode.src = "img/ftv2mnode.png";
         else if ( imageNode.src.substring(l-17,l) == "img/ftv2plastnode.png" )
            imageNode.src = "img/ftv2mlastnode.png";

         folder.style.display = "block";
         }
      }

   // End script hiding -->
   </script>
</head>

<body>
   <div class="directory">
      <h3>{{outline.name}}</h3>
'''

   OUTLINE_TAIL = '''   </div>
   </body>
</html>
'''
   
   FRAME_FILE_FORMAT = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
   <head>
      <META NAME="keywords" CONTENT="logic, deduction, fallacies, fallacy, induction, reasoning, argumentation">
      <META NAME="description" CONTENT="A comprehensive outline of the science of logic.">
      <META NAME="author" CONTENT="Ronald H. Provost">
      <title>{frameName}</title>
   </head>

   <frameset cols="30%%,*">
      <frame src="{frameTreename}" name="sidemenu">
      <frame src="{frameNotesname}" name="baseframe">
   </frameset>
</html>
'''


   def __init__( self ):
      self.frame         = None
      self.outline       = None
      self.articles      = None
      
      self._articleCount = 0

   def buildTreeElementStr( self, element, id = None ):
      if ( id is not None ):
         return "<img src=%s width=%d height=%d onclick=\"toggleFolder(\'folder%s\', this)\" />" % ( element[0], element[1], element[2], id )
      else:
         return "<img src=%s width=%d height=%d />" % element

   def buildTreeEntryStr( self, item, isLastInSubtree ):
      result = ""
      
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
         
         self.outline.write( '<p>' )
         
         # Build the Outline Tree
         self.outline.write( self.buildTreeEntryStr( item, item == last ) )
         
         # Item
         if item.article:
            if isinstance( item.article, unicode ):
               item.article += ' '
            
            self._articleCount += 1
            
            articleName = item.title = self.procAndTrans( item.title )
            
            try:
               anchor = '<a href="%s#%s" target="baseframe">%s</a>' % (notesName, self._articleCount, articleName )
               anchorStr = str( anchor )
               self.outline.write( anchorStr )
            except:
               pass
            
         else:
            self.outline.write( item.title )
         
         self.outline.write( '</p>\n' )
         
         # subtrees
         if len(item.subtrees) > 0:
            self.outline.write( '<div id="folder%s">\n' % (item.id) )
            self.nestingStack.append( item == last )
            self._buildTree( item.subtrees, notesName )
            self.nestingStack.pop( )
            self.outline.write( '</div>\n' )

   def buildTree( self, outline, name, notesName ):
      print( "Generating tree..." )
      self.nestingStack = []
      self.outline.write( HTMLBuilder.OUTLINE_HEAD )
      self._articleCount = 0
      self._buildTree( outline.subtrees, notesName )
      self.outline.write( HTMLBuilder.OUTLINE_TAIL )
   
   def _buildArticles( self, items ):
      for item in items:
         self.current = item
         
         # Construct the location string
         self.location.append( item.title )
         
         # Item
         if item.article:
            if isinstance( item.article, unicode ):
               item.article += ' '
            
            self._articleCount += 1
            try:
               self.articles.write( '<HR><HR><H2>{0}</H2>\n'.format( item.title() ) )
               self.articles.write( item.article() )
            except:
               print( 'Problem in writing article: %s' % item.title )
         
         self._buildArticles( item.subtrees )
         
         self.location.pop( )

   def buildArticles( self, outline ):
      self.articles.write( '<HTML><HEAD><TITLE>{0}</TITLE>{{STYLES}}</HEAD><BODY>'.format(name) )
      self._buildArticles( outline.subtrees )
      self.articles.write( '</BODY></HTML>' )

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
      
      try:
         self.frame.write( HTMLBuilder.FRAME_FILE_FORMAT.format( frameName=name, frameTreename=outlineName, frameNotesname=articlesName ) )
         self.buildTree( outline, name, articlesName )
         self.buildArticles( outline )
      
      except Exception, (msg):
         print( 'Exception raised while processing article \'%s\' (%s)\n%s' % ( self.current.title, self.current.id, msg ) )
         raise
      
      self.frame.close()
      self.outline.close()
      self.articles.close()

