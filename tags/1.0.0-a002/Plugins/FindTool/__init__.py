from tkApplicationFramework import PluggableTool
import Tix
from TreeEditor import ForewardFinder


class FindTool( PluggableTool ):
   NAME             = 'Find'
   GUI_LABEL        = 'Find/Replace'
   DEFAULT_SETTINGS = { }
   TAG_NAME         = '$find'
   
   def __init__( self, aView ):
      PluggableTool.__init__( self, aView )
      self._textWidget  = self._view._articleView.stext
      self._textWidget.tag_config( FindTool.TAG_NAME, background='yellow' )
      self._searchOpts = None
      self._chk        = None
      self._exprType   = None
      self._caseOpt    = None
      self._word       = None
      self._wordOpts   = None
      
      self._regEx      = Tix.StringVar( )
      self._soughtExpr = ''
      self._finder     = None
   
   def buildGUI( self, parent ):
      PluggableTool.buildGUI( self, parent )
      
      frame = Tix.Frame( parent )
      
      entry     = Tix.Entry( frame, textvariable=self._regEx )
      entry.grid( row=1, column=1, columnspan=2 )
      
      self._searchOpts = Tix.StringVar( )
      searchOpts = Tix.OptionMenu( frame, variable=self._searchOpts, options='label.width 15 label.anchor e menubutton.width 15' )
      searchOpts.add_command( 'entry',   label='Selected Entry'   )
      searchOpts.add_command( 'subtree', label='Selected Subtree' )
      searchOpts.add_command( 'all',     label='Entire Tree'      )
      if not self.CONFIG.has_option( 'Find-Tool', 'object' ):
         self.CONFIG.set( 'Find-Tool', 'object', 'all' )
      self._searchOpts.set( self.CONFIG.get( 'Find-Tool', 'object' ) )
      searchOpts.grid( row=1, column=3 )
      
      self._exprType = Tix.IntVar( )
      self._exprType.set( self.CONFIG.get( 'Find-Tool', 'useRegEx' ) == 'yes' )
      self._chk = Tix.Checkbutton( frame, justify=Tix.LEFT, text='Regular Expr', variable=self._exprType, command=self.useRegEx )
      self._chk.grid( row=2, column=1, columnspan=3 )
      
      self._caseOpt = Tix.IntVar( )
      self._caseOpt.set( self.CONFIG.get( 'Find-Tool', 'ignoreCase' ) == 'yes' )
      self._case = Tix.Checkbutton( frame, justify=Tix.LEFT, text='Ignore Case', variable=self._caseOpt )
      self._case.grid( row=3, column=1, columnspan=3 )
      
      self._word = Tix.StringVar( )
      self._wordOpts = Tix.OptionMenu( frame, label='Word Options', variable=self._wordOpts, options='label.width 15 label.anchor e menubutton.width 15' )
      self._wordOpts.add_command( 'any',           label='any'             )
      self._wordOpts.add_command( 'wholeWords',    label='Whole Words'     )
      self._wordOpts.add_command( 'beginnings',    label='Word Beginnings' )
      self._wordOpts.add_command( 'endings',       label='Word Endings'    )
      if not self.CONFIG.has_option( 'Find-Tool', 'constraint' ):
         self.CONFIG.set( 'Find-Tool', 'constraint', 'any' )
      self._word.set( self.CONFIG.get( 'Find-Tool', 'constraint' ) )
      self._wordOpts.grid( row=4, column=1, columnspan=3 )
      
      Tix.Button( frame, text='Next', command=self.onFind ).grid( row=5, column=1 )
      
      if self.CONFIG.get( 'Find-Tool', 'useRegEx' ) == 'yes':
         self._case.config( state=Tix.DISABLED )
         self._wordOpts.config( state=Tix.DISABLED )
      
      return frame

   def onFind( self ):
      self._textWidget.tag_remove( FindTool.TAG_NAME, '1.0', 'end' )
      newSoughtExpr = self._regEx.get( )
      
      if newSoughtExpr != self._soughtExpr:
         self._soughtExpr = newSoughtExpr
         import re
         findStyle = self.CONFIG.get( 'Find-Tool', 'quickStyle' )
         if findStyle == 'extended':
            if self._soughtExpr.islower( ):
               soughtRegExpr = re.compile( self._soughtExpr, re.IGNORECASE )
            else:
               soughtRegExpr = re.compile( self._soughtExpr )
         elif findStyle == 'regex':
            soughtRegExpr = re.compile( self._soughtExpr )
         else:
            soughtRegExpr = re.compile( self._soughtExpr )
         
         self._finder = ForewardFinder( self._view._view.getModel()[0], soughtRegExpr )
      
      try:
         path,subject,lineNo,begin,end = self._finder.next( )
         self._textWidget.tag_add( FindTool.TAG_NAME, '%d.%d' % (lineNo,begin), '%d.%d' % (lineNo,end) )
         self._textWidget.see( '%d.%d' % (lineNo,begin) )
         print '[ %03d : %03d : %03d ] - %s' % ( lineNo, begin, end, path )
      except:
         print 'Expression not found.'


   def useRegEx( self ):
      if self._exprType.get() == 1:
         self.CONFIG.set( 'Find-Tool', 'useRegEx', 'yes' )
         self._case.config( state=Tix.DISABLED )
         self._wordOpts.config( state=Tix.DISABLED )
      else:
         self.CONFIG.set( 'Find-Tool', 'useRegEx', 'no' )
         self._case.config( state=Tix.NORMAL )
         self._wordOpts.config( state=Tix.NORMAL )

pluginClass = FindTool

