from Plugins import MindTree1Importer
from OutlineModel import OutlineModel, OutlineModelIterator, ArticleSubstringIterator, NoMoreSubstrings
from PyQt4 import QtCore, QtGui
import re
import sys

class FindSubstringIterator( ArticleSubstringIterator ):
   def __init__( self, outlineIterator, reObj ):
      ArticleSubstringIterator.__init__( self, outlineIterator )
      self._regexObj = reObj
      self._pos      = 0
   
   def _setTextToParse( self, newText ):
      ArticleSubstringIterator._setTextToParse( self, newText )
      self._pos      = 0
   
   def _nextSubstringOfInterest( self ):
      ArticleSubstringIterator._nextSubstringOfInterest( self )
      
      match = self._regexObj.search( self._text, self._pos )
      try:
         start, stop = match.span( )
      except:
         raise NoMoreSubstrings
      
      if start < 0:
         raise NoMoreSubstrings
      
      self._pos = stop
      
      return start,stop


if __name__=='__main__':
   import os.path
   sys.path.append( os.path.join( sys.path[0], 'Plugins', 'MindTree1Importer' ) )

   app = QtGui.QApplication( sys.argv )
   win = QtGui.QMainWindow( )
   
   imp = MindTree1Importer.MT1ImportingArchiver( win )
   filename, data = imp.read( )
   name,rootNode, res = data
   
   model = OutlineModel( rootNode )
   
   #index = model.index( 0, 0, QtCore.QModelIndex() )
   #for idx in OutlineModelIterator(index):
      #print( unicode(idx.data().toString()) )
   
   index = model.index( 0, 0, QtCore.QModelIndex() )
   regex = re.compile( 'The' )
   for node,fromPos,toPos in FindSubstringIterator( OutlineModelIterator(index,recurse=True), regex ):
      print( '{0:4}-{1:4}:  {2}'.format( fromPos, toPos, unicode(node.data().toString()) ) )
