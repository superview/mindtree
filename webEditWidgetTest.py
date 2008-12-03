from PyQt4 import QtCore, QtGui
import sys


class WebEdit( object ):
   def __init__( self, parent ):
      self._editor = QtGui.QTextEdit( parent )
   
   def show( self ):
      self._editor.show( )
   
   def setMinimumWidth( self, sz ):
      self._editor.setMinimumWidth( sz )
   
   def setMinimumHeight( self, sz ):
      self._editor.setMinimumHeight( sz )


app = QtGui.QApplication( sys.argv )

win = QtGui.QMainWindow( )
edit = WebEdit( win )
edit.setMinimumWidth( 300 )
edit.setMinimumHeight( 100 )

win.show( )

app.exec_( )
