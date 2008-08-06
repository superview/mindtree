import Tix
import Tkinter
import tkFont
import time
import os
import os.path


def fixTkinter( ):
   # - Tix.py is missing the bbox() method of class HList.  This method is
   #   needed for TreeEditor to implement Drag-n-drop.  Here's the implementation:
   #      def info_bbox(self,entry):
   #	  return [ int(pos) for pos in self.tk.call(self._w, 'info', 'bbox', entry).split( ) ]
   #   This fix is now incorporated into MindTree.  File TreeEditor.py, class TreeEditor in
   #   method _drawWidget()
   def info_bbox( self, path ):
      coordList = self.tk.call(self._w, 'info', 'bbox', path).split( ' ' )
      return [ int(val) for val in coordList ]
   
   Tix.HList.info_bbox = info_bbox


from copy import copy

class Path( object ):
   def __init__( self, value=None ):
      self._disk      = None
      self._path      = None
      self._name      = None
      self._extension = None
      
      if isinstance( value, Path ):
         self._disk, self._path, self._name, self._extenaion = value._disk, value._path, value._name, value._extenaion
      elif isinstance( value, str ):
         self._disk, self._path, self._name, self._extenaion = Path.split( value )
   
   @staticmethod
   def splitFilePath( path ):
      if path is None or (path == ''):
         return '','','',''
      
      fixedPath = os.path.normpath( os.path.normcase( path ) )
      disk, pathRest = os.path.splitdrive( fixedPath )
      path, pathRest = os.path.split( pathRest )
      filename, extension = os.path.splitext( pathRest )
      return disk, path, filename, extension


def exceptionPopup( ):
   import tkMessageBox
   import traceback
   
   tkMessageBox.showerror( 'Exception', traceback.format_exc( ) )


# Utility Functions
def dirPath( *parts ):
   if isinstance( parts, str ):
      return parts
   
   return os.path.join( *parts ) + os.sep


def filePath( *parts ):
   if isinstance( parts, str ):
      return parts
   
   return os.path.join( *parts )


def splitFilePath( path ):
   if path is None or (path == ''):
      return '','','',''
   
   fixedPath = os.path.normpath( os.path.normcase( path ) )
   disk, pathRest = os.path.splitdrive( fixedPath )
   path, pathRest = os.path.split( pathRest )
   filename, extension = os.path.splitext( pathRest )
   return disk, path, filename, extension
   

# GUI Callback Helpers
def CALLBACK( callback, *args, **kwargs ):
   """Use this for Tk callbacks.  Pass it arguments that you wish to be passed
   to the callback when it's invoked.  The first argument to the callback will
   be the event.
   """
   def do_call():
      return callback( *args, **kwargs )
   
   return do_call

def EVTCALLBACK( callback, *args, **kwargs ):
   """Use this for Tk callbacks.  Pass it arguments that you wish to be passed
   to the callback when it's invoked.  The first argument to the callback will
   be the event.
   """
   def do_call( evt ):
      return callback( *args, **kwargs )
   
   return do_call

def EVTCALLBACK2( callback, *args, **kwargs ):
   """Use this for Tk callbacks.  Pass it arguments that you wish to be passed
   to the callback when it's invoked.  The first argument to the callback will
   be the event.
   """
   def do_call( evt ):
      return callback( evt, *args, **kwargs )
   
   return do_call

#def picklable( object ):
   #import inspect
   #import tkCommonDialog
   #if isinstance( object, (Tkinter.Wm,Tkinter.Misc,Tkinter.Variable,Tkinter.Image,Tkinter.Event,tkFont.Font,tkCommonDialog.Dialog) ):
      #return False
   #else:
      #for name,value in inspect.getmembers( object ):
         #if not picklable( value ):
            #return False
      #return True

class tkMath( object ):
   PIXELS_PER_INCH    = 0
   PIXELS_PER_CM      = 0
   PIXELS_PER_MM      = 0
   PIXELS_PER_POINT   = 0
   
   @staticmethod
   def setup( root ):
      tkMath.PIXELS_PER_INCH  = root.winfo_fpixels( '1i' )
      tkMath.PIXELS_PER_CM    = root.winfo_fpixels( '1c' )
      tkMath.PIXELS_PER_MM    = root.winfo_fpixels( '1m' )
      tkMath.PIXELS_PER_POINT = root.winfo_fpixels( '1p' )
   
   @staticmethod
   def pixelsToInches( pixels ):
      return pixels / tkMath.PIXELS_PER_INCH
   
   @staticmethod
   def pixelsToCM( pixels ):
      return pixels / tkMath.PIXELS_PER_CM
   
   @staticmethod
   def pixelsToMM( pixels ):
      return pixels / tkMath.PIXELS_PER_MM
   
   @staticmethod
   def pixelsToPoints( pixels ):
      return pixels / tkMath.PIXELS_PER_POINT
   
   @staticmethod
   def inchesToPixels( inches ):
      return inches * tkMath.PIXELS_PER_INCH
   
   @staticmethod
   def cmToPixels( cm ):
      return cm * tkMath.PIXELS_PER_CM

   @staticmethod
   def mmToPixels( mm ):
      return mm * tkMath.PIXELS_PER_MM

   @staticmethod
   def pointsToPixels( points ):
      return points * tkMath.PIXELS_PER_POINT

   @staticmethod
   def coordToPixels( tkCoord ):
      if isinstance( tkCoord, str ):
         if tkCoord[-1] == 'i':
            return tkMath.inchesToPixels( float(tkCoord[:-1]) )
         elif tkCoord[-1] == 'c':
            return tkMath.cmToPixels( float(tkCoord[:-1]) )
         elif tkCoord[-1] == 'm':
            return tkMath.mmToPixels( float(tkCoord[:-1]) )
         elif tkCoord[-1] == 'p':
            return tkMath.pointsToPixels( float(tkCoord[:-1]) )
         else:
            return tkCoord
      else:
         return tkCoord

   @staticmethod
   def compare( coord1, coord2 ):
      return tkMath.coordToPixels(coord1) - tkMath.coordToPixels(coord2)

   @staticmethod
   def add( coord1, coord2 ):
      return tkMath.coordToPixels(coord1) + tkMath.coordToPixels(coord2)
   
   @staticmethod
   def sub( coord1, coord2 ):
      return tkMath.coordToPixels(coord1) - tkMath.coordToPixels(coord2)
   
   @staticmethod
   def tkPolar( x1, y1, x2, y2 ):
      import math
      deltaX = math.fabs( x1 - x2 )
      deltaY = math.fabs( y1 - y2 )
      
      direction = math.atan( deltaY, deltaX )
      distance  = math.sqrt( deltaX**2 + deltaY**2 )
      
      return direction, distance

   @staticmethod
   def tkCartesian( x1, y1, direction, distance ):
      import math
      deltaX = distance * math.cos( direction )
      deltaY = distance * math.sin( direction )
      
      return x1 + deltaX, x2 + deltaY


# Quick Widgets
def menuItem( menu, label, cmd=None, accel=None, **opts ):
   altKeyPos = label.find( '&' )
   if altKeyPos == -1:
      opts[ 'label' ] = label
   else:
      opts[ 'label' ] = ''.join( label.split( '&' ) )
      opts[ 'underline' ] = altKeyPos
   
   if accel is not None:
      opts[ 'accelerator' ] = accel
   
   if cmd is not None:
      opts[ 'command' ] = cmd
   
   menu.add_command( **opts )


class Toolbar( Tkinter.Frame ):
   TOOLSET_PACK_OPTIONS  = { 'side':'left', 'fill':'y', 'padx':4, 'pady':2 }
   TOOLBAR_FRAME_OPTIONS = { 'relief':'raised', 'borderwidth':2 }
   
   def __init__( self, parent ):
      Tkinter.Frame.__init__( self, parent, **Toolbar.TOOLBAR_FRAME_OPTIONS )
      self._toolsets = { }

   def add( self, name, toolset ):
      toolset.pack( **Toolbar.TOOLSET_PACK_OPTIONS )
      self._toolsets[ name ] = toolset
   
   def get( self, toolsetName, toolName=None ):
      toolset = self._toolsets[ toolsetName ]
      if toolName:
         return toolset.get( toolName )
      else:
         return toolset

   def setState( self, newState ):
      for toolset in self._toolsets.values( ):
         toolset.setState( newState )

class Toolset( Tkinter.Frame ):
   FONT                  = 'Times 8'
   TOOLSET_FRAME_OPTIONS = { 'borderwidth':2, 'relief':'groove' }
   TOOL_PACK_OPTIONS     = { 'side':'left' }
   
   def __init__( self, parent ):
      Tkinter.Frame.__init__( self, parent, **Toolset.TOOLSET_FRAME_OPTIONS )
      self._widgets   = { }
      self._callbacks = { }
   
   def add( self, name, aWidget ):
      self._widgets[ name ] = aWidget
      
      try:
         self._callbacks[ name ] = aWidget['command']
      except:
         self._callbacks[ name ] = None
      
      aWidget.pack( fill='y', **Toolset.TOOL_PACK_OPTIONS )
      return aWidget
   
   def get( self, name ):
      return self._widgets[ name ]

   def addButton( self, name, **options ):
      opts = { 'relief':'groove' }
      opts.update( options )
      
      if 'font' not in options:
         options[ 'font' ] = Toolset.FONT
      
      theButton = Tkinter.Button( self, **opts )
      return self.add( name, theButton )

   def addPushButton( self, name, variable, **options ):
      opts = { 'indicatoron':False, 'offrelief':'flat', 'font':Toolset.FONT,
               'overrelief':'raised', 'variable':variable }
      opts.update( options )
      
      theButton = Tkinter.Checkbutton( self, **opts )
      return self.add( name, theButton )

   def addCombo( self, name, variable, values=[], default=None, **options ):
      if 'editable' not in options:
         options[ 'editable' ] = False
      if 'width' in options:
         width = options[ 'width' ]
         del options[ 'width' ]
      else:
         width = None
      if 'font' in options:
         font = options[ 'font' ]
         del options[ 'font' ]
      else:
         font = Toolset.FONT
      
      if 'command' in options:
         theCommand = options[ 'command' ]
         del options[ 'command' ]
      
      theCombo = Tix.ComboBox( self, dropdown=True, fancy=False,
                               variable=variable, history=False,
                               selectmode=Tk.BROWSE, **options )
      
      background = options.get( 'background', 'white' )
      foreground = options.get( 'foreground', 'black' )
      if width:
         theCombo.subwidget('listbox').config( font=font, width=width, borderwidth=0, background=background, disabledforeground=foreground )
         theCombo.subwidget('entry').  config( font=font, width=width, borderwidth=0, disabledbackground=background, disabledforeground=foreground )
      else:
         theCombo.subwidget('listbox').config( font=font, borderwidth=0, background=background, disabledforeground=foreground )
         theCombo.subwidget('entry').  config( font=font, borderwidth=0, disabledbackground=background, disabledforeground=foreground )
      theCombo.arrow.config( relief='flat', overrelief='raised' )
      
      for value in values:
         theCombo.insert( Tk.END, value )
      
      if default:
         variable.set( default )
      
      theCombo[ 'command' ] = theCommand
      
      return self.add( name, theCombo )

   def addLabel( self, name, **options ):
      if 'font' not in options:
         options[ 'font' ] = Toolset.FONT
      
      theLabel = Tkinter.Label( self, **options )
      return self.add( name, theLabel )

   def addEntry( self, name, variable, label=None, **options ):
      if 'font' not in options:
         options[ 'font' ] = Toolset.FONT
      
      le = Tix.LabelEntry( self, label=label )
      le.label.configure( font=options['font'] )
      if 'width' in options:
         le.entry.configure( width=options['width'], textvariable=variable )
      else:
         le.entry.configure( textvariable=variable )
      if 'command' in options:
         le.entry.bind( '<FocusOut>', options['command'] )
      le.pack( side=Tkinter.LEFT, padx=5, pady=5 )
      
      return le
   
   def setState( self, newState ):
      for name,widget in self._widgets.iteritems( ):
         widget.config( state=newState )
         
         if newState == 'disabled':
            # Remove the callback
            try:
               self._callbacks[ name ] = widget[ 'command' ]
               widget.config( command='none' )
            except:
               self._callbacks[ name ] = None
         
         elif newState == 'normal':
            # Reinstall the callback
            widget.config( command=self._callbacks[ name ] )

# Splash Screens
class SplashScreen( object ):
   '''This class is used in conjunction with the 'with' statement to
   display a splash screen centered on the screen.
   
   It will typically be used as follows:

   ######################
   root = Tkinter.Tk( )

   with SplashScreen( root, mySplashScreenImage ):
      initializeMyAppAndGUI( )

   root.mainloop()
   ######################

   mySpashScreenImage can be a .gif filename or a PhotoImage instance.
   '''
   def __init__( self, root, image, minSplashTime=0.0, displayAppAfterSplash=True ):
      self._root              = root
      self._image             = None
      self._splash            = None
      self._minSplashTime     = time.time() + minSplashTime
      self._dpyAppAfterSplash = displayAppAfterSplash
      
      if isinstance( image, Tix.PhotoImage ):
         self._image = image
      elif isinstance( image, str ):
         self._image = Tix.PhotoImage( file=image )
   
   def __enter__( self ):
      self._root.withdraw( )
      
      scrnWt = self._root.winfo_screenwidth( )
      scrnHt = self._root.winfo_screenheight( )
      
      sImgWt = self._image.width()
      sImgHt = self._image.height()
      
      sImgYPos = (scrnHt / 2) - (sImgHt / 2)
      sImgXPos = (scrnWt / 2) - (sImgWt / 2)
      
      self._splash = Tix.Toplevel()
      self._splash.overrideredirect(1)
      self._splash.geometry( '+%d+%d' % (sImgXPos, sImgYPos) )
      Tix.Label( self._splash, image=self._image, cursor='watch' ).pack( )
      
      self._splash.update( )
   
   def __exit__( self, exc_type, exc_value, traceback ):
      timeNow = time.time()
      if timeNow < self._minSplashTime:
         time.sleep( self._minSplashTime - timeNow )
      
      self._splash.destroy( )
      
      if self._dpyAppAfterSplash:
         self._root.deiconify( )



# Resources
class Resources( object ):
   def __init__( self ):
      import sys
      self.APP_DIR    = sys.path[0] if sys.path[0] != '' else os.getcwd( )
      self.IMAGE_DIR  = ''
      self.CURSOR_DIR = ''

   def loadValues( self, imageDir='', cursorDir='' ):
      self.IMAGE_DIR  = imageDir
      self.CURSOR_DIR = cursorDir

   def image( self, filename, location=None ):
      if location is None:
         location = self.IMAGE_DIR
      
      return Tix.PhotoImage( file=filePath( location, filename ) )
   
   def cursor( self, filename=None, location=None, name=None ):
      if name is not None:
         return name
      elif location is None:
         location = self.CURSOR_DIR
      
      location = location.replace( os.sep, '/' )
      
      return '@' + filePath( location, filename ) + os.extsep + 'cur'
   
   def font( self, *args, **kwargs ):
      return tkFont.Font( *args, **kwargs )


class CustomWidgetMixin( object ):
   def __init__( self, master, **options ):
      theOptions = copy.copy( self.DEFAULT_OPTIONS )
      theOptions.update( options )
      
      Tix.Frame.__init__( master, **self._frameOptions() )
      self._buildGUI( )

   def getOptionList( self ):
      raise NotImplementedError

   def buildGUI( self ):
      raise NotImplementedError

   def _extractOptions( self, BaseWidgetClass, options ):
      '''Given a dictionary of configuration settings (options),
      remove those options listed in wantedOptions from options and
      return a dictionary of wantedOptions to values.
      '''
      baseWidgetOpts = set(BaseWidgetClass.keys( self ))
      
      
      baseWidgetOpts = { }
      for key in baseWidgetOptList:
         baseWidgetOpts[ key ] = BaseWidgetClass.cget( self, key )
      
      wanted    = { }
      frameOpts = { 'background':None, 'relief':None, 'borderwidth':None}
      
      for key,value in options.iteritems( ):
         if key in wantedOptions:
            wanted[ key ] = value
            del options[ key ]
      
      return wanted
   


import Tkinter as Tk

PREFIX = "tkController"

class Controller(object):
   def __init__(self, master=None):
      if master is None:
         master = Tk._default_root
      assert master is not None
      self.tag = PREFIX + str(id(self))
      def bind(event, handler):
         master.bind_class(self.tag, event, handler)
      self.create(bind)

   def install(self, widget):
      widgetclass = widget.winfo_class()
      # remove widget class bindings and other controllers
      tags = [self.tag]
      for tag in widget.bindtags():
         if tag != widgetclass and tag[:len(PREFIX)] != PREFIX:
            tags.append(tag)
      widget.bindtags(tuple(tags))

   def create(self, handle):
      # override if necessary
      # the default implementation looks for decorated methods
      for key in dir(self):
         method = getattr(self, key)
         if hasattr(method, "tkevent") and callable(method):
            for eventSequence in method.tkevent:
               handle(eventSequence, method)

def bind(*events):
   def decorator(func):
      func.tkevent = events
      return func
   return decorator

class KBController( Controller ):
   def __init__( self ):
      Controller.__init__( self )
      self._alt     = False
      self._control = False
      self._lock    = False
      self._meta    = False
      self._shift   = False
   
   @bind("<KeyPress>")      # type 2
   def KeyPress(self, event):
      if event.keysym in ('Alt_L', 'Alt_R'):
         self._alt = True
      elif event.keysym in ('Control_L', 'Control_R'):
         self._control = True
      elif event.keysym == 'Caps_Lock':
         self._lock = True
      elif event.keysym in ('Meta_L', 'Meta_R'):
         self._meta = True
      elif event.keysym in ( 'Shift_L', 'Shift_R'):
         self._shift = True
      elif (len(event.char) > 0) and (32 <= ord(event.char) <= 127):
         self.onTypedCharacterKey( event )
      else:
         self.onTypedSpecialKey( event )

   @bind("<KeyRelease>")    # type 3
   def KeyRelease( self, event ):
      if event.keysym in ('Alt_L', 'Alt_R'):
         self._alt = False
      elif event.keysym in ('Control_L', 'Control_R'):
         self._control = False
      elif event.keysym == 'Caps_Lock':
         self._lock = False
      elif event.keysym in ('Meta_L', 'Meta_R'):
         self._meta = False
      elif event.keysym in ('Shift_L', 'Shift_R'):
         self._shift = False
   
   def onTypedCharacterKey( self, event ):
      '''Override to handle typing of any printable keyboard character,
      Typed character is in event.char (which accounts for shift).'''
      pass
   
   def onTypedSpecialKey( self, event ):
      '''Override to handle typing of any special characters (tab, \n, backspace,
      delete, home, prior, insert, etc.  Any any key combinations involving
      Alt or Control.'''
      pass


# ==============================

if __name__=='__main__':
   import Tkinter

   class myController(Controller):
      @bind("<Button-1>")
      def click(self, event):
         self.anchor = event.x, event.y
         self.item = None
      
      @bind("<B1-Motion>")
      def drag(self, event):
         bbox = self.anchor + (event.x, event.y)
         if self.item is None:
            self.item = event.widget.create_rectangle(bbox, fill="red")
         else:
            event.widget.coords(self.item, *bbox)

   # create widgets
   canvas1 = Tkinter.Canvas(bg="white")
   canvas1.pack(side="left")

   canvas2 = Tkinter.Canvas(bg="black")
   canvas2.pack(side="left")

   canvas_controller = myController()

   canvas_controller.install(canvas1)
   canvas_controller.install(canvas2)

   Tkinter.mainloop()


