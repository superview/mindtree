from DocumentWriter import DocumentWriter


class ArticleEditor( DocumentWriter ):
   def __init__( self, parent, **options ):
      DocumentWriter.__init__( self, parent, **options )
      
      self._project = None
   
   def setProject( self, aProject ):
      self._project = aProject

