from __future__ import print_function, unicode_literals
from PyQt4 import QtCore, QtGui, QtWebKit
import sys

class DualHtmlEditor( QtGui.QSplitter ):
   def __init__( self, parent ):
      self._sourceView = None
      self._htmlView   = None
      
      QtGui.QSplitter.__init__( self, parent )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 1 )
      self.setSizePolicy(sizePolicy)
      self.setMinimumSize(QtCore.QSize(700, 700))
      self.setOrientation(QtCore.Qt.Horizontal)
      self.setChildrenCollapsible(False)
      
      self._buildGui( )
      self.onTextChanged( )
   
   def setText( self, text ):
      self._sourceView.setText( text )

   def getText( self ):
      return self._sourceView.toPlainText( )

   # Slots
   def onTextChanged( self ):
      text = unicode(self._sourceView.toPlainText( ))
      html = self._getHTML( text )
      self._htmlView.setHtml( html )
   
   def _getHTML( self, text ):
      return text

   # Widget Construction
   def _buildGui( self ):
      self._buildWidgets( )
      
      self._defineActions( )
      
      self._buildMenus( )
      self._buildToolbars( )
   
   def _buildWidgets( self ):
      # Source View
      self._sourceView = QtGui.QTextEdit( self )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 1 )
      self._sourceView.setSizePolicy( sizePolicy )
      self._sourceView.setMinimumHeight( 100 )
      self._sourceView.setMinimumWidth( 200 )
      QtCore.QObject.connect( self._sourceView, QtCore.SIGNAL('textChanged()'), self.onTextChanged )
      
      self._sourceView.setFontFamily( 'Fixedsys' )
      self._sourceView.setFontPointSize( 14 )
      
      # Html View
      self._htmlView   = QtWebKit.QWebView( self )
      #self._htmlView   = QtGui.QTextEdit( self )
      self._htmlView.setEnabled( False )
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 1 )
      self._htmlView.setSizePolicy( sizePolicy )
      self._htmlView.setMinimumHeight( 100 )
      self._htmlView.setMinimumWidth( 200 )
      
      #self._htmlView.setFontFamily( 'Lucida Sans Unicode' )
      #self._htmlView.setFontPointSize( 12 )

   def _defineActions( self ):
      pass
   
   def _buildMenus( self ):
      pass
   
   def _buildToolbars( self ):
      pass


from docutils import examples

class RestructuredDualEditor( DualHtmlEditor ):
   def __init__( self, parent ):
      DualHtmlEditor.__init__( self, parent )

   def _getHTML( self, text ):
      return examples.html_body( text )


if __name__ == '__main__':
   app = QtGui.QApplication( sys.argv )
   
   win = QtGui.QMainWindow( )
   edit = DualHtmlEditor( win )
   sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
   sizePolicy.setVerticalStretch( 5 )
   sizePolicy.setHorizontalStretch( 1 )
   edit.setSizePolicy( sizePolicy )
   
   win.resize( 903, 719 )
   sizePolicy = QtGui.QSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
   sizePolicy.setHorizontalStretch( 1 )
   sizePolicy.setVerticalStretch( 1 )
   win.setSizePolicy( sizePolicy )
   
   win.show()
   
   app.exec_()
