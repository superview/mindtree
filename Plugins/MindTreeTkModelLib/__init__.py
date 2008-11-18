# Read and Convert a MindTree v1.0 Project file

from OutlineModel import OutlineModel, TreeNode
from PyQt4 import QtCore

from ApplicationFramework import ImporterPlugin, RES

class MT1ImportingArchiver( ImporterPlugin ):
   NAME              = 'MindTree1Importer'
   VERSION           = ( 1, 0 )
   BUILD_DATE        = ( 2008, 11, 15 )
   
   FILE_TYPES        = 'MindTree Data File (*.mt);;All Files (*.*)'
   FILE_EXTENSION    = 'mt'
   
   DEFAULT_SETTINGS = {
                      'fileTypes':     'MindTree Data File (*.mt);;All Files (*.*)',
                      'fileExtension': 'mt'
                      }

   def __init__( self, parentWidget ):
      workingDir = RES.get( 'Project',  'directory'     )
      
      ImporterPlugin.__init__( self, parentWidget, self.FILE_TYPES, self.FILE_EXTENSION, workingDir )
   
   def _readFile( self, aFilename ):
      from utilities import splitFilePath
      disk,path,filename,extension = splitFilePath( aFilename )
      documentName = filename[0].upper() + filename[1:]
      
      import pickle
      data = pickle.load( open( aFilename, 'rb' ) )
      
      theConvertedProject = self.convertProject( data._tree, documentName )
      theModel = OutlineModel( theConvertedProject )
      
      return theModel

   def convertProject( self, model, title ):
      newModelOutline = self._convertProject( model )
      newModelOutline.setTitle( unicode(title) )
      return newModelOutline
   
   def _convertProject( self, oldModelTreeNode, newModelParentNode=None ):
      title   = unicode(oldModelTreeNode.title)
      article = ''
      
      if isinstance( oldModelTreeNode.article, list ):
         for key,val,index in oldModelTreeNode.article:
            if key == 'text':
               article += val
      
      newModelTreeNode = TreeNode( title, newModelParentNode, article )
      for oldChildNode in oldModelTreeNode.children( ):
         newModelTreeNode.appendChild( self._convertProject(oldChildNode, newModelTreeNode) )
      return newModelTreeNode
   




pluginClass = MT1ImportingArchiver

