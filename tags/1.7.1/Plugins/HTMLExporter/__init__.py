from OutlineModel import OutlineModel, TreeNode
from PyQt4 import QtCore, QtGui

from ApplicationFramework import ExporterPlugin, RES

class HtmlExporter( ExporterPlugin ):
   NAME              = 'HTML Exporter'
   VERSION           = ( 1, 0 )
   BUILD_DATE        = ( 2008, 11, 15 )
   
   FILE_TYPES        = 'HTML Web Page (*.htm);;All Files (*.*)'
   FILE_EXTENSION    = 'htm'
   
   DEFAULT_SETTINGS = { }

   HTML_DIR               = r''
   IMAGE_DIR              = r'img'

   def __init__( self, parentWidget ):
      workingDir = RES.get( 'Project',  'workspace'     )
      
      ExporterPlugin.__init__( self, parentWidget, self.FILE_TYPES, self.FILE_EXTENSION, workingDir )
   
   def _writeFile( self, aDocument, aFilename=None, promptFilename=False ):
      rootDir = self.askdir( 'Target Location...' )
      
      name = 'Logic'
      
      import os
      if not os.path.exists( rootDir ):
         os.mkdir( rootDir )
      
      rootDir = rootDir.replace( '/', os.sep )
      htmlDir = os.path.join( rootDir, HTMLArchiver.HTML_DIR  )
      imgDir  = os.path.join( rootDir, HTMLArchiver.IMAGE_DIR )
      
      import hgen as HtmlGen
      builder = HtmlGen.HTMLBuilder( )
      
      if isinstance( aDocument, (list,tuple) ):
         builder.buildHTML( aDocument[0], rootDir, htmlDir, imgDir, name )
      else:
         builder.buildHTML( aDocument, rootDir, htmlDir, imgDir, name )
   
pluginClass = HtmlExporter
