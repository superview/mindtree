from PyQt4 import QtCore, QtGui

from MindTreeApplicationFramework import *

class MT1ImportingArchiver( ImporterPlugin ):
   NAME              = 'MindTree1.x'
   VERSION           = ( 1, 1 )
   BUILD_DATE        = ( 2008, 12, 4 )

   DEFAULT_SETTINGS = {
                      'fileTypes':     'MindTree Data File (*.mt);;All Files (*.*)',
                      'fileExtension': 'mt',
                      'defaultFont':   'Lucida Sans Unicode:10'
                      }

   def __init__( self, parentWidget ):
      workingDir     = RES.get('Project',    'workspace', default='' )
      fileTypes      = RES.get('MindTree1.x','fileTypes')
      fileExtensions = RES.get('MindTree1.x','fileExtension')
      
      ImporterPlugin.__init__( self, parentWidget, fileTypes, fileExtensions, workingDir )
      self._document = QtGui.QTextDocument( )  # for converting text to html

   def _read( self, aFilename ):
      from utilities import splitFilePath
      disk,path,filename,extension = splitFilePath( aFilename )
      documentName = filename[0].upper() + filename[1:]
      
      import pickle
      data = pickle.load( open( aFilename, 'rb' ) )
      
      theConvertedProject = self.convertProject( data._tree, documentName )
      theRootNode     = theConvertedProject
      
      return documentName, theRootNode

   def convertProject( self, model, title ):
      return self._convertProject( model )

   def _convertProject( self, oldModelTreeNode, newModelParentNode=None ):
      # Extract the article title from the old tree model node
      title   = unicode(oldModelTreeNode.title)
      
      # Extract the article text from the old tree model node
      plainTextArticle = u''
      if isinstance( oldModelTreeNode.article, list ):
         for key,val,index in oldModelTreeNode.article:
            if key == 'text':
               try:
                  plainTextArticle += val
               except:
                  # If there are any characters in val which have codes > 127,
                  # the concatenation will fail.  This code will take care of that
                  for character in val:
                     plainTextArticle += unichr(ord(character))
      
      elif isinstance( oldModelTreeNode.article, (str,unicode) ):
         plainTextArticle = unicode(oldModelTreeNode.article)
      
      # Convert the article to HTML
      if len(plainTextArticle) > 0:
         self._document.clear( )
         self._document.setDefaultFont( RES.getFont('MindTree1.x','defaultFont') )
         self._document.setPlainText( plainTextArticle )
         htmlArticle = unicode(self._document.toHtml( 'utf-8' ))
      else:
         htmlArticle = ''
      
      # Construct a new model node
      newModelTreeNode = TreeNode( title, parent=newModelParentNode, article=htmlArticle )
      
      # Iterate over the children nodes converting them
      for oldChildNode in oldModelTreeNode.children( ):
         newModelTreeNode.appendChild( self._convertProject(oldChildNode, newModelTreeNode) )
      
      # Return the newly created tree
      return newModelTreeNode


pluginClass = MT1ImportingArchiver


   