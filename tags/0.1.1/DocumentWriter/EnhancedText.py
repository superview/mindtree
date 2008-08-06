from TkTools import KBController, bind
import Tkinter

class LineNotVisibleException( Exception ):
   pass


class EnhancedTextController( KBController ):
   def __init__( self ):
      KBController.__init__( self )
      self._insert_x_pos      = None
   
   def onTypedCharacterKey( self, event ):
      try:
         event.widget.sel_delete( )
      except:
         pass
      
      event.widget.insert( 'insert', event.char )
      event.widget.sel_clear( )
      event.widget.see( 'insert' )
      
      self._insert_x_pos = None
   
   def onTypedSpecialKey( self, event ):
      widget = event.widget
      
      if event.keysym in ( 'Return','Enter','KP_Enter','Tab','BackSpace','Delete','Insert', 'Escape' ):
         self.typeSpecial( event )
      
      elif event.keysym in ( 'Up', 'Down', 'Left', 'Right', 'Home', 'End', 'Prior', 'Next',
                             'KP_Up', 'KP_Down', 'KP_Left', 'KP_Right', 'KP_Home', 'KP_End', 'KP_Prior', 'KP_Next' ):
         self.moveCarrot( event )
      
      elif self._control:
         self.typeControlCombo( event )

   def moveCarrot( self, event ):
      widget = event.widget
      widget.see( 'insert' )
      if self._shift:
         if not widget.sel_isAnchorSet():
            widget.mark_set( 'anchor', 'insert' )
      else:
         widget.sel_clear( )
      
      if not self._shift:
         if event.keysym in ('Up','Down'):
            if self._insert_x_pos is None:
               self._insert_x_pos = event.widget.bbox( 'insert' )[0]
         else:
            self._insert_x_pos = None
      
      if event.keysym in ( 'Home', 'KP_Home' ):
         if self._control:
            # Move to beginning of text
            widget.mark_set( 'insert', '1.0' )
         else:
            # Move to front of line
            insert = widget.index( 'insert' )
            dline_start = widget.dline_start( insert )
            dline_end   = widget.dline_end( insert )
            dline_first = widget.search( "[^[:space:]]", dline_start, dline_end, regexp=True )
            
            if dline_first == '':
               widget.mark_set( 'insert', dline_start )
            elif widget.compare( 'insert', '!=', dline_first ):
               widget.mark_set( 'insert', dline_first )
            else:
               widget.mark_set( 'insert', dline_start )
      elif event.keysym in ( 'End', 'KP_End' ):
         if self._control:
            # Move to end of text
            widget.mark_set( 'insert', 'end' )
         else:
            # Move to end of line
            widget.mark_set( 'insert', widget.dline_end('insert') )
      elif event.keysym == 'Right':
         if self._control:
            # Move by word
            currentPos = widget.index( 'insert' )
            maxPos     = widget.index( 'end wordstart' )
            
            if currentPos == maxPos:
               return
            
            offset = 1
            while widget.compare( currentPos, '==', widget.index('insert') ):
               widget.mark_set( 'insert', 'insert wordend +%dc wordstart' % offset )
               offset += 1
         else:
            # Move by character
            widget.mark_set( 'insert', 'insert +1 chars' )
      elif event.keysym == 'Left':
         if self._control:
            # Move by word
            currentPos = widget.index( 'insert' )
            minPos     = widget.index( '1.0 wordstart' )
            
            if currentPos == minPos:
               return
            
            offset = 2
            widget.mark_set( 'insert', 'insert wordstart' )
            while widget.compare( currentPos, '==', widget.index('insert') ):
               widget.mark_set( 'insert', 'insert -%dc wordstart' % offset )
               offset += 1
         else:
            # Move by character
            widget.mark_set( 'insert', 'insert -1 chars' )
      elif event.keysym == 'Down':
         if self._control:
            # Move by Paragraph
            widget.mark_set( 'insert', 'insert +1 lines' )
         else:
            # Move by line
            widget.mark_set( 'insert', widget.dline_next( 'insert', useThisX=self._insert_x_pos ) )
      elif event.keysym == 'Up':
         if self._control:
            # Move by Paragraph
            widget.mark_set( 'insert', 'insert -1 lines' )
            pass
         else:
            # Move by line
            widget.mark_set( 'insert', widget.dline_prev( 'insert', useThisX=self._insert_x_pos ) )
      elif event.keysym == 'Prior':
         if self._control:
            pass
         else:
            # Move by page
            if widget.bbox( '1.0' ):
               widget.mark_set( 'insert', '1.0' )
            else:
               pos = widget.bbox( 'insert' )
               event.widget.yview_scroll( -1, 'pages' )
               widget.mark_set( 'insert', '@%d,%d' % pos[:2] )
      elif event.keysym == 'Next':
         if self._control:
            pass
         else:
            # Move by page
            if widget.bbox( 'end -1 chars' ):
               widget.mark_set( 'insert', 'end -1 chars' )
            else:
               pos = widget.bbox( 'insert' )
               event.widget.yview_scroll( 1, 'pages' )
               widget.mark_set( 'insert', '@%d,%d' % pos[:2] )
      
      widget.see( 'insert' )

   def typeSpecial( self, event ):
      widget = event.widget
      
      if event.keysym in ( 'Return', 'Enter', 'KP_Enter' ):
         try:
            widget.sel_delete( )
         finally:
            widget.insert( 'insert', '\n' )
            widget.see( 'insert' )
      elif event.keysym == 'Tab':
         widget.insert( 'insert', '\t' )
         # We need to steal back focus since the widget manager will try to take it
         widget.after( 1, widget.focus_set )
      elif event.keysym == 'BackSpace':
         try:
            widget.delete( 'sel.first', 'sel.last' )
         except:
            widget.delete( 'insert -1 chars', 'insert' )
      elif event.keysym in ( 'Delete', 'KP_Delete' ):
         try:
            widget.delete( 'sel.first', 'sel.last' )
         except:
            widget.delete( 'insert', 'insert +1 chars' )
      elif event.keysym == 'Escape':
         # Clear the current selection
         pass
      
      widget.sel_clear()
      self._insert_x_pos = None

   def typeControlCombo( self, event ):
      import pickle
      widget = event.widget
      
      if event.keysym == 'a':
         # select all
         widget.mark_set( 'anchor', '1.0' )
         widget.mark_set( 'insert', 'end' )
         widget.sel_update( )
      elif event.keysym == 'c':
         # copy
         try:
            content = widget.dump( 'sel.first', 'sel.last' )
            result = pickle.dumps( content )
            widget.clipboard_append( result )
         except:
            pass
      elif event.keysym == 'r':
         # Redo
         try:
            widget.edit_redo( )
         except:
            pass
         widget.sel_clear( )
      elif event.keysym == 'v':
         # paste
         try:
            widget.sel_delete( )
         except:
            pass
         
         try:
            widget.mark_set( 'insert', 'sel.first' )
            widget.delete( 'sel.first', 'sel.last' )
         except:
            pass
         
         result = pickle.loads( widget.clipboard_get( ) )
         widget.insert( 'insert', result )
         widget.sel_clear( )
      elif event.keysym == 'x':
         # cut
         try:
            widget.sel_delete( )
         except:
            pass
         
         try:
            content = widget.dump( 'sel.first', 'sel.last' )
            result = pickle.dumps( content )
            widget.clipboard_append( result )
            widget.delete( 'sel.first', 'sel.last' )
            widget.ins_updateTags( )
         except:
            pass
         widget.sel_clear( )
      elif event.keysym == 'z':
         # Undo
         try:
            widget.edit_undo( )
         except:
            pass
         widget.sel_clear( )
      
      self._insert_x_pos = None

   @bind( '<ButtonPress-1>' )
   def click( self, event ):
      event.widget.focus_set( )
      
      if not self._shift and not self._control:
         event.widget.sel_clear( )
         event.widget.mark_set( 'anchor', 'current' )
      
      self._insert_x_pos = None

   @bind( '<B1-Motion>', '<Shift-Button1-Motion>' )
   def dragSelection( self, event ):
      widget = event.widget
      
      if event.y < 0:
         widget.yview_scroll( -1, 'units' )
      elif event.y >= widget.winfo_height():
         widget.yview_scroll( 1, 'units' )
      
      if not widget.sel_isAnchorSet( ):
         widget.mark_set( 'anchor', '@%d,%d' % (event.x+2, event.y) )
      
      widget.mark_set( 'insert', '@%d,%d' % (event.x+2, event.y) )
      self._insert_x_pos = None

   @bind( '<ButtonRelease-1>' )
   def moveCarrot_deselect( self, event ):
      widget = event.widget
      
      widget.focus_set( )
      widget.grab_release( )
      widget.mark_set( 'insert', 'current' )
      self._insert_x_pos = None

   @bind( '<Double-ButtonPress-1>' )
   def selectWord( self, event ):
      event.widget.mark_set( 'anchor', 'insert wordstart' )
      event.widget.mark_set( 'insert', 'insert wordend' )
      self._insert_x_pos = None

   @bind( '<Triple-ButtonPress-1>' )
   def selectLine( self, event ):
      event.widget.mark_set( 'anchor', 'insert linestart' )
      event.widget.mark_set( 'insert', 'insert lineend' )
      self._insert_x_pos = None

   @bind( '<Button1-Leave>' )
   def scrollView( self, event ):
      widget = event.widget
      
      if event.y < 0:
         widget.yview_scroll( -1, 'units' )
      elif event.y >= widget.winfo_height():
         widget.yview_scroll( 1, 'units' )
      
      widget.grab_set( )
   
   @bind( '<MouseWheel>' )
   def wheelScroll( self, event ):
      widget = event.widget
      
      if event.delta < 0:
         widget.yview_scroll( 1, 'units' )
      else:
         widget.yview_scroll( -1, 'units' )
   

class EnhancedText( Tkinter.Text ):
   '''This Text widget replacement, corrects the movement by
   Up and Down arrows and the Home and End keys such that
   they work on display-lines rather than on paragraphs.'''
   def __init__( self, parent, **options ):
      options[ 'takefocus' ] = True
      Tkinter.Text.__init__( self, parent, **options )
      
      controller = EnhancedTextController( )
      controller.install( self )

   # Selection Operations
   def sel_clear( self ):
      try:
         self.tag_remove( 'sel', '1.0', 'end' )
         self.mark_unset( 'anchor' )
      except:
         pass
   
   def sel_isAnchorSet( self ):
      try:
         self.index( 'anchor' )
         return True
      except:
         return False

   def sel_isSelection( self ):
      try:
         self.index( 'sel.first' )
         return True
      except:
         return False

   def sel_update( self ):
      self.tag_remove( 'sel', '1.0', 'end' )
      
      if self.compare( 'anchor', '<', 'insert' ):
         self.tag_add( 'sel', 'anchor', 'insert' )
      elif self.compare( 'anchor', '>', 'insert' ):
         self.tag_add( 'sel', 'insert', 'anchor' )
   
   def sel_delete( self ):
      try:
         Tkinter.Text.delete( self, 'sel.first', 'sel.last' )
      except:
         pass
      self.sel_clear( )
   
   # Display Lines
   def dline_start( self, index ):
      '''
      Returns the index of the first character on the display line which
      contains index.
      '''
      try:
         x,y,width,height = self.bbox( index )
         return self.index( '@%d,%d' % (0, y) )
      except:
         raise LineNotVisibleException
   
   def dline_end( self, index ):
      '''
      Returns the index of the last character on the display line which
      contains index.
      '''
      try:
         x,y,width,height = self.bbox( index )
         return self.index( '@%d,%d' % ( self.winfo_width(), y ) )
      except:
         raise LineNotVisibleException

   def dline_prev( self, index, useThisX=None ):
      '''
      Returns the index of the display-line immediately above the index
      provided.  If useThisX is provided, the returned index is as close to x
      as possible, otherwise, the x from bbox(index) is used.
      '''
      delta = 10
      spacing = self.bbox( self.index( '@1,1' ) )[1]
      minY = delta + spacing
      
      x,y,width,height = self.bbox( index )
      
      if useThisX:
         x = useThisX
      
      insertIndex = self.index( index )
      newIndex = self.index( '@%d,%d' % ( x, y ) )
      while self.compare( newIndex, '==', insertIndex) and self.compare(insertIndex, '>', '1.0'):
         if y < minY:
            self.yview_scroll( -1, 'units' )
            x,y,width,height = self.bbox( insertIndex )
         y -= delta
         newIndex = self.index( '@%d,%d' % ( x, y ) )
         
         if self.index('@1,1') == '1.0':
            lastIndexOnTopDisplayLine = self.dline_end( '1.0' )
            if self.compare( newIndex, '<=', lastIndexOnTopDisplayLine ):
               break
      
      return newIndex
   
   def dline_next( self, index, useThisX=None ):
      '''
      Returns the index of the display-line immediately below the index
      provided.  If useThisX is provided, the returned index is as close to x
      as possible, otherwise, the x from bbox(index) is used.
      '''
      index = self.index( index )
      self.see( index )
      x,y,width,height,baseline = self.dlineinfo( index )
      maxY = self.winfo_height() - 1
      
      if useThisX:
         x = useThisX
      
      newY = y + height + 1
      while newY >= maxY:
         self.yview_scroll( 1, 'units' )
         self.see( index )
         x,y,width,height,baseline = self.dlineinfo( index )
         
         if useThisX:
            x = useThisX
         
         newY = y + height + 1
      
      newIndex = self.index( '@%d,%d' % (x, newY) )
      while self.compare( newIndex, '==', index ) and self.compare( newIndex, '<', 'end -1 chars' ):
         newY += 5
         while newY >= maxY:
            self.yview_scroll( 1, 'units' )
            self.see( index )
            x,y,width,height,baseline = self.dlineinfo( index )
            
            if useThisX:
               x = useThisX
            
            newY = y + height + 1
         
         newIndex = self.index( '@%d,%d' % (x,newY) )
      
      return newIndex
   
   # Overloads
   def dump( self, index1='1.0', index2='end', command=None, omittedTags=None, omittedMarks=None, **options ):
      '''Get the contents of the widget from index1 (inclusive) through index2
      (not inclusive).  If dump is False, a text string is returned; otherwise
      a tuple (dump,activeTags) is returned where activeTags is a list of tags
      that are active (open) at index1 - information lacking from the dump
      itself.
      
      omittedMarks is a sequence of tags to omit from the final report.
         default:  [ ]
      
      omittedTags is a sequence of marks to omit from the final report.
         default:  [ ]
      '''
      index1 = self.index( index1 )
      index2 = self.index( index2 )
      
      theDump = Tkinter.Text.dump( self, index1, index2, **options )
      
      if not omittedMarks:
         omittedMarks = [ ]
      
      if not omittedTags:
         omittedTags  = [ ]
      
      finalReport = [ ]
      for key,val,index in theDump:
         if (key == 'mark') and (val in omittedMarks):
            continue
         elif (key in ['tagon','tagoff']) and (val in omittedTags):
            continue
         
         finalReport.append( ( key, val, index ) )
      
      if (finalReport[-1][0] == 'text') and (len(finalReport[-1][1].strip()) == 0):
         del finalReport[-1]
      
      if index1 != '1.0':
         activeTags = self.tag_names( index1 )
         for tagName in activeTags:
            if tagName in omittedTags:
               continue
            
            finalReport.insert( 0, ( 'tagon', tagName, index1 ) )
      
      #self.validateDump( finalReport )
      
      return finalReport

   def mark_set( self, name, index ):
      Tkinter.Text.mark_set( self, name, index )
      
      if name == 'insert':
         try:
            self.sel_update( )
         except:
            pass

   # Styling Operations
   def iterRegion( self, index1, index2 ):
      '''This method iterates over the styled subregions of a given region.
      For this method, a "subregion" is defined as any contiguous segment of
      indecies with exactly the same tags (and thus styling).  Upon each
      iteration, the method returns a "subregion style description" of the
      form:
         ( beginIndex, endIndex, [ activeStyleNames ] )
      The list is guaranteed complete.  beginIndex of the first subregion
      description will always equal index1, and endIndex of the last subregion
      will always equal index2.  Further, for any two adjacent subregion
      descriptions endIndex of the first will always equal beginIndex of the
      second.  Thus no gaps occur in the mapping.
      '''
      # Temporarily remove the selection
      #try:
         #selRegion = self.tag_ranges( 'sel' )
         #self.tag_remove( 'sel', '1.0', 'end' )
      #except:
         #selRegion = None
      
      # Begin the main loop
      theDump = Tkinter.Text.dump( self, index1, index2, tag=True )
      
      subregionBegin = idx = index1
      for key,val,idx in theDump:
         if (key in ['tagon','tagoff']) and key.startswith('$'):
            continue
         if idx != subregionBegin:
            yield subregionBegin,idx,self.tag_names( subregionBegin )
            subregionBegin = idx
      
      if idx != index2:
         yield idx,index2,self.tag_names( subregionBegin )
      
      # Restore the selection
      #if selRegion:
         #self.tag_add( 'sel', *selRegion )

   def tag_configuration( self, tagName ):
      config = { }
      
      for name,value in self.tag_config( tagName ):
         if len(value) == 5:
            config[ name ] = value[4]
      
      return config

   @staticmethod
   def validateDump( aDump ):
      assert isinstance( aDump, list )
      
      for key,val,index in aDump:
         if key not in ( 'tagon','tagoff','mark','text','image','window' ):
            raise Exception( "Invalid key in dump: %s" % key )
         
         if not isinstance( val, (str,unicode) ):
            raise Exception( "Invalid value in dump: %s" % val )
         
         if not isinstance( index, (str,unicode) ):
            raise Exception( "Invalid index in dump: %s" % index )
         
         try:
            line,sep,col = index.partition( '.' )
            if sep != '.':
               raise Exception( "Invalid index format in dump: %s" % index )
            
            try:
               int(line)
            except:
               raise Exception( "Invalid index format in dump: %s" % index )
            
            try:
               int(col)
            except:
               raise Exception( "Invalid index format in dump: %s" % index )
         except:
            raise Exception( "Invalid index format in dump: %s" % index )



