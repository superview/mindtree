from OutlineModel import OutlineModel, TreeNode
from PyQt4 import QtCore, QtGui

from ApplicationFramework import ExporterPlugin, RES

class HtmlExporter( ExporterPlugin ):
   NAME              = 'HTML Importer'
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
      
      ExporterPlugin.__init__( self, parentWidget, self.FILE_TYPES, self.FILE_EXTENSION, workingDir )
   
   def _readFile( self, aFilename ):
      # Manipulate the filename
      from utilities import splitFilePath
      disk,path,filename,extension = splitFilePath( aFilename )
      documentName = filename[0].upper() + filename[1:]
      
      # Read in the data
      import pickle
      data = pickle.load( open( aFilename, 'rb' ) )
      
      # Convert the data
      theConvertedProject = self.convertProject( data._tree, documentName )
      
      # Package the data for MindTree
      theModel = OutlineModel( theConvertedProject )
      return theModel, { }

   def convertProject( self, model, title ):
      pass
   
pluginClass = HtmlExporter
