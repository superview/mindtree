from Plugins import MindTree1Importer
from OutlineModel import OutlineModel, TextIterator, OutlineModelIterator, ArticleIterator
from PyQt4 import QtCore, QtGui
import re
import sys

class FindIterator( TextIterator ):
   def __init__( self, reObj ):
      TextIterator.__init__( self )
      self._regexObj = reObj
      self._pos      = 0
   
   def restart( self, text ):
      TextIterator.restart( self, text )
      self._pos      = 0
   
   def next( self ):
      TextIterator.next( self )
      
      match = self._regexObj.search( self._text, self._pos )
      try:
         start, stop = match.span( )
      except:
         raise StopIteration
      
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
   
   index = model.index( 0, 0, QtCore.QModelIndex() )
   regex = re.compile( 'the', re.IGNORECASE )
   itr   = ArticleIterator( OutlineModelIterator(index), FindIterator(regex) )
   while True:
      node,span = itr.next()
      print( '{0:4}-{1:4}:  {2}'.format( span[0], span[1], unicode(node.data().toString()) ) )
