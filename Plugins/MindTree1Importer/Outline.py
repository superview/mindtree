from __future__ import print_function, unicode_literals
from Tree import Tree
from uuid import UUID

class Outline( object ):
   def __init__( self, tree=None, anchors=None, styles=None ):
      self._tree    = tree
      self._anchors = anchors
      self._styles  = styles
      
      if tree is None:
         self._tree = Tree( )
      
      if anchors is None:
         self._anchors = { }
   
   def validateModel( self ):
      if self._tree:
         self._validateModel( self._tree )

   def updateModel( self ):
      if self._tree:
         self._updateModel( self._tree )

   def anchors( self ):
      return self._anchors

   def _validateModel( self, aTree ):
      verbose = False
      if verbose:
         try:
            print( "%s: %s" % (str(aTree.id), aTree.title) )
         except UnicodeEncodeError:
            print( "%s: ??" % (str(aTree.id)) )
      
      if not isinstance( aTree.id, (str,UUID) ):
         raise Exception( "[%s] Invalid tree id" % str(aTree.id) )
      
      try:
         str(aTree.id)
      except:
         raise Exception( "[%s] Tree id must be a UUID found %s" % ( str(aTree.id), type(aTree.id) ) )
      
      if not isinstance( aTree.title, (bytes,unicode) ):
         raise Exception( "[%s] Tree title must be a string, found %s" % ( str(aTree.id), type(aTree.title) ) )
      
      if not isinstance( aTree.article, (bytes,unicode,list,tuple) ):
         raise Exception( "[%s] Invalid article type, found %s" % (str(aTree.id), type(aTree.article) ) )
      elif isinstance( aTree.article, (list,tuple) ):
         from DocumentWriter.EnhancedText import EnhancedText
         EnhancedText.validateDump( aTree.article )
      
      if not isinstance( aTree.subtrees, list ):
         raise Exception( "[%s] Invalid subtree list, found %s" % (str(aTree.id), type(self.subtrees) ) )
      
      for child in aTree.subtrees:
         if not isinstance( child, Tree ):
            raise Exception( "[%s] Invalid child type, found %s" % (aTree.id, type(child)) )
         
         self._validateModel( child )

   def _updateModel( self, aTree ):
      if isinstance( aTree.title, str ):
         aTree.title = unicode( aTree.title )
      
      if isinstance( aTree.article, str ):
         aTree.article = unicode( aTree.article )
      
      if isinstance(aTree.article, (list,tuple) ):
         newArticle = [ ]
         
         for key,val,index in aTree.article:
            if key == 'image':
               import TkTools
               import os.path
               disk,path,name,extension = TkTools.splitFilePath( val )
               val = os.path.join( 'img', name + extension )
            
            #elif key == 'text':
               #if isinstance(val,str):
                  #val = unicode(val)
            
            #if key in ('tagon','tagoff'):
               #if val[0] == '$':
                  #continue
               #elif val[0] != '_':
                  #val = '_style_%s' % val
            
            newArticle.append( (key,val,index) )
         
         aTree.article = newArticle
      
      for child in aTree.subtrees:
         self._updateModel( child )


