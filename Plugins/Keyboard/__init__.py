from tkApplicationFramework import PluggableTool
import Tix
import TkTools

class Keyboard( PluggableTool ):
   NAME             = 'Keyboard'
   GUI_LABEL        = 'Keyboard'
   DEFAULT_SETTINGS = {
                      'row1':   '',
                      'row2':   '',
                      'row3':   '',
                      'row4':   ''
                      }

   def __init__( self, aView ):
      PluggableTool.__init__( self, aView )
      self._buttons = [ ]
      self._values  = [ ]
      
      self._configSectionName = ''
   
   def setName( self, aName ):
      self._configSectionName = 'Keyboard-%s' % aName
   
   def setOption( self, key, value ):
      self.CONFIG.set( self._configSectionName, key, value )

   def getOption( self, key ):
      try:
         return self.CONFIG.get( self._configSectionName, key )
      except:
         return self.CONFIG.get( 'Keyboards', key )

   def buildGUI( self, parent ):
      PluggableTool.buildGUI( self, parent )
      
      btnNumber = 0
      font = self.getOption( 'font' )
      for row in xrange( 0, 5 ):
         try:
            rowValues = self.getOption( 'row%d' % (row + 1) ).strip()
         except:
            continue
         
         if rowValues == '':
            continue
         
         rowValues = [ unichr(int(valStr.strip(),0)) for valStr in rowValues.split( ',' ) ]
         
         for col,btnValue in enumerate( rowValues ):
            button = Tix.Button( parent, text=btnValue, width=2, relief='flat', overrelief='raised', command=TkTools.CALLBACK(self._insertCharacter, btnNumber), font=font )
            button.grid( row=row, column=col, padx=3, pady=3 )
            button.bind( '<ButtonPress-3>', TkTools.CALLBACK(self._editButton,btnNumber) )
            
            self._buttons.append( button )
            self._values.append( btnValue )
            
            btnNumber += 1

   def _insertCharacter( self, buttonNumber, *args, **kwargs ):
      character = self._values[ buttonNumber ]
      
      widget = self._view.focus_get( )
      
      try:
         widget.insert( Tix.INSERT, character )
      except:
         pass
   
   def _editButton( self, which ):
      pass

pluginClass = Keyboard
