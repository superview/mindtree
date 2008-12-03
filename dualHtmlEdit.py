from PyQt4 import QtCore, QtGui, QtWebKit
import sys

class DualHtmlEditor( QtGui.QSplitter ):
   def __init__( self, parent ):
      QtGui.QSplitter.__init__( self, parent )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 10 )
      sizePolicy.setHorizontalStretch( 10 )
      self.setSizePolicy(sizePolicy)
      self.setMinimumSize(QtCore.QSize(700, 700))
      self.setOrientation(QtCore.Qt.Horizontal)
      self.setChildrenCollapsible(False)
      
      self._buildGui( )
   
   def _buildGui( self ):
      self._buildWidgets( )
      
      self._defineActions( )
      
      self._buildMenus( )
      self._buildToolbars( )
   
   def _buildWidgets( self ):
      # Source View
      self._sourceView = QtGui.QTextEdit( self )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 5 )
      sizePolicy.setHorizontalStretch( 1 )
      self._sourceView.setSizePolicy( sizePolicy )
      self._sourceView.setMinimumHeight( 100 )
      self._sourceView.setMinimumWidth( 200 )
      
      # Html View
      self._htmlView   = QtGui.QTextEdit( self )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 5 )
      sizePolicy.setHorizontalStretch( 1 )
      self._htmlView.setSizePolicy( sizePolicy )
      self._htmlView.setMinimumHeight( 100 )
      self._htmlView.setMinimumWidth( 200 )

   def _defineActions( self ):
      pass
   
   def _buildMenus( self ):
      pass
   
   def _buildToolbars( self ):
      pass


if __name__ == '__main__':
   app = QtGui.QApplication( sys.argv )
   
   win = QtGui.QMainWindow( )
   edit = QtWebKit.QWebView( win )
   edit.setHtml( 'one two three' )
   sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
   sizePolicy.setVerticalStretch( 5 )
   sizePolicy.setHorizontalStretch( 1 )
   edit.setSizePolicy( sizePolicy )
   #edit = DualHtmlEditor( win )
   
   win.resize( 903, 719 )
   sizePolicy = QtGui.QSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
   sizePolicy.setHorizontalStretch( 1 )
   sizePolicy.setVerticalStretch( 1 )
   win.setSizePolicy( sizePolicy )
   
   win.show()
   
   app.exec_()
