class WordProcWidget:
   def __init__( self ):
      pass
   
   # Parent UI Components
   def getMenus( self ):
      pass
   
   def getToolbars( self ):
      pass
   
   # Contents - Text
   def setHtml( self, text ):
      pass

   def getHtml( self ):
      pass
   
   def getText( self ):
      pass
   
   # Contents - Resources
   def defineResource( self, url, spec ):
      pass
   
   def getResourceList( self ):
      pass
   
   def insertResource( self, resName ):
      pass
   
   def isModified( self ):
      pass
   
   def setModified( self, newVal ):
      pass

   # Cursors
   def defineSpecialCursor( self, name, spec ):
      pass
   
   def moveSpecialCursor( self, name, fromPos, toPos=None, moveEditCursor=True ):
      pass
   
   def hideSpecialCursor( self, name ):
      pass
   
   def getSpecialCursor( self ):
      pass
   
   def getEditCursor( self ):
      pass
   
   def setEditCursor( self, newCursor ):
      pass
   
   def moveEditCursor( self, where ):
      pass
   
   # Widget Construction
   def _buildGui( self, parent ):
      self._buildWidgets( )
      self._defineActions( )
      self._buildMenus( )
      self._buildToolbars( )
   
   def _buildWidgets( self ):
      pass
   
   def _defineActions( self ):
      pass
   
   def _buildMenus( self ):
      pass
   
   def _buildToolbars( self ):
      pass
   
   # Slots
   def _editCursorMoved( self ):
      pass
   
   def _documentChanged( self ):
      pass
   
   def _modifiedFlagChanged( self ):
      pass

