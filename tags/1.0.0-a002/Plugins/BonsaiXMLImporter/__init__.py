from tkApplicationFramework import ImporterPlugin


class BonsaiXMLArchiver( ImporterPlugin ):
   NAME                   = 'Bonsai XML...'
   DEFAULT_SETTINGS       = { }
   
   FILE_TYPES             = [ ( 'Bonzai XML File', '*.xml' ), ( 'All Files', '*.*' ) ]
   FILE_EXTENSION         = '.xml',

   def __init__( self, aView ):
      ImporterPlugin.__init__( self, aView, BonsaiXMLArchiver.FILE_TYPES, BonsaiXMLArchiver.FILE_EXTENSION, self.CONFIG.get( 'Workspace', 'directory' ) )
   
   def _readFile( self, filename ):
      import BonsaiXMLImporter
      return BonsaiXMLImporter.Parser.parseXML(filename)


pluginClass = BonsaiXMLArchiver

