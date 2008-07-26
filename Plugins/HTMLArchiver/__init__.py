__all__ = [ 'hgen' ]


from tkApplicationFramework import ExporterPlugin


class HTMLArchiver( ExporterPlugin ):
   NAME                   = 'HTML Generation...'
   DEFAULT_SETTINGS       = { }
   
   FILE_TYPES             = [ ( 'HTML file', '*.htm' ), ( 'All Files', '*.*' ) ]
   FILE_EXTENSION         = '.htm',
   
   HTML_DIR               = r''
   IMAGE_DIR              = r'img'

   def __init__( self, aView ):
      ExporterPlugin.__init__( self, aView, HTMLArchiver.FILE_TYPES, HTMLArchiver.FILE_EXTENSION, self.CONFIG.get( 'Workspace', 'directory' ) )
   
   def _writeFile( self, aDocument, aFilename=None, promptFilename=False ):
      import tkFileDialog
      rootDir = tkFileDialog.askdirectory( )
      if (rootDir is None) or (rootDir == ''):
         return
      
      import tkSimpleDialog
      name = tkSimpleDialog.askstring( 'Name', 'Web page title' )
      if (name is None) or (name == ''):
         return
      
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


pluginClass = HTMLArchiver

