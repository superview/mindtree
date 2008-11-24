from PyQt4 import QtCore, QtGui, Qt
from ApplicationFramework import PluggableTool, RES


class Resources( QtGui.QTabWidget, PluggableTool ):
   theApp = None

   NAME             = 'Resources'
   VERSION          = ( 1, 0 )
   BUILD_DATE       = ( 2008, 11, 24 )

   DEFAULT_SETTINGS = {
                         'font' : 'Lucida Sans Unicode:12',
                      }
   
   def __init__( self, parent, app ):
      Resources.theApp = app
      
      QtGui.QTabWidget.__init__( self, parent )
      PluggableTool.__init__( self )

 
pluginClass = Resources
