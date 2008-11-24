from ApplicationFramework import RES, PluggableTool
from PyQt4 import QtCore, QtGui

class Spelling( PluggableTool, QtGui.QWidget ):
   NAME             = 'Spelling'
   VERSION          = ( 1, 0 )
   BUILD_DATE       = ( 2008, 11, 24 )
   
   DEFAULT_SETTINGS = {
                      }

   def __init__( self, parent, app ):
      PluggableTool.__init__( self )
      QtGui.QWidget.__init__( self, parent )
      
      self._gridLayout = QtGui.QGridLayout( self )
      self._gridLayout.setObjectName( 'SpellingGridLayout' )
   
pluginClass = Spelling
