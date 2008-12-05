from __future__ import print_function, unicode_literals
from OutlineModel import OutlineModel, TreeNode
from PyQt4 import QtCore, QtGui
from ApplicationFramework import ExporterPlugin, RES

class HtmlExporter( ExporterPlugin ):
   NAME              = 'HTML'
   VERSION           = ( 1, 1 )
   BUILD_DATE        = ( 2008, 12, 4 )

   DEFAULT_SETTINGS = {
                      # File Information
                      'fileTypes':     'HTML Web Page (*.htm);;All Files (*.*)',
                      'fileExtension': 'htm',
                      
                      # Images
                      'imageDir':      'img',
                      'lineImageSize': '16:22',   # All line images must have this size
                      'iconImageSize': '24:22',   # All icons must have this size
                      'lineVertical':  '%(imageDir)s/ftv2vertline.png',
                      'lineEmpty':     '%(imageDir)s/ftv2blank.png',
                      'lineLeaf':      '%(imageDir)s/ftv2node.png',
                      'lineLeafLast':  '%(imageDir)s/ftv2lastnode.png',
                      'lineNode':      '%(imageDir)s/ftv2pnode.png',
                      'lineNodeLast':  '%(imageDir)s/ftv2plastnode.png',
                      'iconLeaf':      '%(imageDir)s/ftv2doc.png',
                      'iconNodeClosed':'%(imageDir)s/ftv2folderclosed.png',
                      
                      # Source Templates
                      #'treeSrcHead':      HtmlExporter.OUTLINE_HEAD,
                      #'treeSrcTail':      HtmlExporter.OUTLINE_TAIL,
                      #'frameSrc':         HtmlExporter.FRAME_FILE_FORMAT,
                      #'articleSrcStyles': HtmlExporter.STYLES
                      }

   OUTLINE_HEAD   = '''<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
   <meta http-equiv="Content-Type" content="text/xhtml;charset="iso-8859-1" />
   <meta http-equiv="Content-Style-Type" content="text/css" />
   <meta http-equiv="Content-Language" content="en" />
   <link rel="stylesheet" href="doxygen.css">
   <title>TreeView</title>
   <style type="text/css">
   <!--
   BODY,H1,H2,H3,H4,H5,H6,P,CENTER,TD,TH,UL,DL,DIV,PRE
      {{
      font-family: Lucida Sans Unicode, Geneva, Arial, Helvetica, sans-serif;
      }}
   .directory {{ font-size: 10pt; font-weight: bold; }}
   .directory h3 {{ margin: 0px; margin-top: 1em; font-size: 11pt; }}
   .directory p {{ margin: 0px; white-space: nowrap; }}
   .directory div {{ display: none; margin: 0px; }}
   .directory img {{ vertical-align: middle; }}
   -->
   </style>
   <script type="text/javascript">
   <!-- // Hide script from old browsers

   function findChildNode(node, name)
      {{
      var temp;

      if (node == null)
         return null;

      node = node.firstChild;

      while (node != null)
         {{
         if (node.nodeName == name)
            return node;

         temp = findChildNode(node, name);

         if (temp != null)
            return temp;

         node = node.nextSibling;
         }}

      return null;
      }}

   function toggleFolder(id, imageNode)
      {{
      var folder = document.getElementById(id);
      var l = 0;
      var vl = "img/ftv2vertline.png";

      if ( imageNode.nodeName != "IMG" )
         {{
         imageNode = findChildNode(imageNode, "IMG");

         l = imageNode.src.length;
         }}

      if ( folder.style.display == "block" )
         {{
         while ( imageNode.src.substring(l-vl.length,l) == vl )
            {{
            imageNode = imageNode.nextSibling;
            l = imageNode.src.length;
            }}

         l = imageNode.src.length;
         imageNode.nextSibling.src = "img/ftv2folderclosed.png";

         if ( imageNode.src.substring(l-13,l) == "img/ftv2mnode.png" )
            imageNode.src = "img/ftv2pnode.png";
         else if ( imageNode.src.substring(l-17,l) == "img/ftv2mlastnode.png" )
            imageNode.src = "img/ftv2plastnode.png";

         folder.style.display = "none";
         }}
      else
         {{
         while ( imageNode.src.substring(l-vl.length,l) == vl )
            {{
            imageNode = imageNode.nextSibling;
            l = imageNode.src.length;
            }}

         l = imageNode.src.length;
         imageNode.nextSibling.src = "img/ftv2folderopen.png";

         if ( imageNode.src.substring(l-13,l) == "img/ftv2pnode.png" )
            imageNode.src = "img/ftv2mnode.png";
         else if ( imageNode.src.substring(l-17,l) == "img/ftv2plastnode.png" )
            imageNode.src = "img/ftv2mlastnode.png";

         folder.style.display = "block";
         }}
      }}

   // End script hiding -->
   </script>
</head>

<body>
   <div class="directory">
      <h3>{title}</h3>
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

   STYLES = '''
<STYLE>
   BODY,H1,H2,H3,H4,H5,H6,P,CENTER,TD,TH,UL,DL,DIV,PRE
      {
      font-family: Lucida Sans Unicode, Geneva, Arial, Helvetica, sans-serif;
      }
   
   DIV.BLOCK
      {
      color:black;
      border:solid thin black;
      padding:1.0em 1.8em;
      }
   
   DIV.BLOCK DIV.BLOCK
      {
      color:black;
      border:solid thin black;
      padding:1.0em 1.8em;
      margin:1.5em
      }
   
   DIV.GRAYBLOCK
      {
      background:#E0E0E0;
      color:black;
      border:solid thin black;
      padding:1.0em 1.8em;
      }
   
   DIV.GRAYBLOCK DIV.GRAYBLOCK
      {
      background:#E0E0E0;
      color:black;
      border:solid thin black;
      padding:1.0em 1.8em;
      margin:1.5em
      }
   </STYLE>
'''

   def __init__( self, parentWidget ):
      workingDir    = RES.get('Project', 'workspace' )
      fileTypes     = RES.get('HTML',    'fileTypes' )
      fileExtension = RES.get('HTML',    'fileExtension' )
      
      ExporterPlugin.__init__( self, parentWidget, fileTypes, fileExtension, workingDir )
      
      # Output Files
      self.frame         = None
      self.outline       = None
      self.articles      = None
      
      # Tree Walking
      self._currentNode  = None
      self._nestingStack = None
      
      # Tree images and icons
      lineImgSz     = RES.getMultipartResource('HTML','lineImageSize')
      imgWd,imgHt   = [ int(val) for val in lineImgSz ]
      
      iconImgSz     = RES.getMultipartResource('HTML','iconImageSize')
      iconWd,iconHt = [ int(val) for val in iconImgSz ]
      
      self.lineVertial    = ( RES.get('HTML','lineVertical'),  imgWd, imgHt )
      self.lineEmpty      = ( RES.get('HTML','lineEmpty'),     imgWd, imgHt )
      self.lineLeaf       = ( RES.get('HTML','lineLeaf'),      imgWd, imgHt )
      self.lineLeafLast   = ( RES.get('HTML','lineLeafLast'),  imgWd, imgHt )
      self.lineNode       = ( RES.get('HTML','lineNode'),      imgWd, imgHt )
      self.lineNodeLast   = ( RES.get('HTML','lineNodeLast'),  imgWd, imgHt )
      self.iconLeaf       = ( RES.get('HTML','iconLeaf'),      iconWd, iconHt )
      self.iconNodeClosed = ( RES.get('HTML','iconNodeClosed'),iconWd, iconHt )

   def write( self, aDocument, aFilename=None, promptFilename=False ):
      rootDir = self.askdir( 'Target Location...' )
      
      name, rootNode, resources = aDocument
      
      import os
      if not os.path.exists( rootDir ):
         os.mkdir( rootDir )
      
      rootDir = rootDir.replace( '/', os.sep )
      htmlDir = rootDir
      imgDir  = os.path.join( rootDir, RES.get('HTML','imageDir') )
      
      self.buildHTML( rootNode, rootDir, htmlDir, imgDir, name )
   
   def buildTreeElementStr( self, element, id = None ):
      if ( id is not None ):
         return "<img src=%s width=%d height=%d onclick=\"toggleFolder(\'folder%s\', this)\" />" % ( element[0], element[1], element[2], id )
      else:
         return "<img src=%s width=%d height=%d />" % element

   def buildTreeEntryStr( self, node, isLastInSubtree ):
      assert isinstance( node,            TreeNode )
      assert isinstance( isLastInSubtree, bool     )
      
      result = ""
      
      # Scope Lines
      # -----------
      for scope in self._nestingStack:
         if scope == False:
            result += self.buildTreeElementStr( self.lineVertial )
         else:
            result += self.buildTreeElementStr( self.lineEmpty )
      
      # open/close & icon
      # -----------------
      if len( self._nestingStack ) > -1:
         if isLastInSubtree:
            if len(node.childList()) == 0:
               # Doc Last Node
               result += self.buildTreeElementStr( self.lineLeafLast )
               result += self.buildTreeElementStr( self.iconLeaf )
            else:
               # Folder Last Node
               result += self.buildTreeElementStr( self.lineNodeLast, node.id().hex )
               result += self.buildTreeElementStr( self.iconNodeClosed, node.id().hex )
         else:
            if len(node.childList()) == 0:
               # Doc Node
               result += self.buildTreeElementStr( self.lineLeaf )
               result += self.buildTreeElementStr( self.iconLeaf )
            else:
               # Folder Node
               result += self.buildTreeElementStr( self.lineNode, node.id().hex )
               result += self.buildTreeElementStr( self.iconNodeClosed, node.id().hex )
      
      return result

   def _buildTree( self, node, notesName, isLastSubNode ):
      self._currentNode  =  node
      self.writeTree( '<p>' )
      
      # Build the Outline Tree
      self.writeTree( self.buildTreeEntryStr( node, isLastSubNode ) )
      
      # Item
      title   = node.title()
      article = node.article()
      if article and (len(article) > 0):
         text = u'<a href="{0}#{1}" target="baseframe">{2}</a>'.format(notesName, node.id().hex, title )
         self.writeTree( text )
      
      else:
         self.writeTree( title )
      
      # subtrees
      if len(node.childList()) > 0:
         self.writeTree( '<div id="folder{0}">\n'.format(node.id().hex) )
         self._nestingStack.append( isLastSubNode )
         lastSubNode = node.childList()[-1]
         for subNode in node.childList():
            self._buildTree( subNode, notesName, subNode is lastSubNode )
         self._nestingStack.pop( )
         self.writeTree( '</div>\n' )

   def buildTree( self, rootNode, articlesName, name ):
      self._currentNode  = rootNode
      self._nestingStack = [ ]
      
      self.writeTree( self.OUTLINE_HEAD.format(title=name) )
      lastSubNode = rootNode.childList()[-1]
      for subNode in rootNode.childList():
         self._buildTree( subNode, articlesName, subNode is lastSubNode )
      self.writeTree( self.OUTLINE_TAIL )
   
   def _buildArticles( self, node ):
      self._currentNode   = node
      
      # Item
      title   = node.title()
      article = node.article()
      if article and (len(article) > 0):
         self.writeArticle( '<A NAME="{0}">'.format(node.id().hex) )
         self.writeArticle( u'<HR><HR><H2>{0}</H2>\n'.format(title) )
         self.writeArticle( article )
      else:
         self.writeArticle( u'<HR><HR><H2>{0}</H2>\n'.format(title) )
      
      for subNode in node.childList():
         self._buildArticles( subNode )

   def buildArticles( self, rootNode, name ):
      self._currentNode  = rootNode
      
      self.writeArticle( '<HTML><HEAD><TITLE>{title}</TITLE>{styles}</HEAD><BODY>'.format(title=name,styles=self.STYLES) )
      for node in rootNode.childList():
         self._buildArticles( node )
      self.writeArticle( '</BODY></HTML>' )

   def buildHTML( self, rootNode, rootPath, htmDir, imgDir, name ):
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
         self.frame.write( self.FRAME_FILE_FORMAT.format( frameName=name, frameTreename=outlineName, frameNotesname=articlesName ) )
         self.buildTree( rootNode, articlesName, name )
         self.buildArticles( rootNode, name )
      
      except Exception:
         print( 'Exception raised while processing article: {0}' % ( self._currentNode.title() ) )
         raise
      
      self.frame.close()
      self.outline.close()
      self.articles.close()

   # Helper Functions
   def writeFrame( self, string ):
      self.frame.write( self.encode(string) )
   
   def writeTree( self, string ):
      self.outline.write( self.encode(string) )
   
   def writeArticle( self, string ):
      self.articles.write( self.encode(string) )
   
   @staticmethod
   def encode( string ):
      result = ''
      for ch in string:
         chOrd = ord(ch)
         
         if 0 < chOrd <= 0x7f:
            result += ch
         else:
            result += '&#{0};'.format(chOrd)
      
      return result

pluginClass = HtmlExporter
