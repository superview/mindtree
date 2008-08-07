from __future__ import with_statement
import Tix
from Tree import *
from Outline import Outline
from TkTools import menuItem, SplashScreen
from TreeEditor import TreeEditor

from tkApplicationFramework import *
from resources import RES

# Features to Implement:
# - Get Find Working
# - Allow adjusting the options for PhotoImage
# - Add lists to StyledText
# - Implement links between parts of the outline
# - Add tables to StyledText
# - MVC, multiple views, multiple outlines and DnD across views.
# 
# Considerations:
# - Consider adding PIL and support for additional image types
# - Consider designing my own Tree Widget
#
# Standard Library Modifications
# - Dialog boxes flash before appearing on the screen.  To prevent this
#   edit tkSimpleDialog.py.  After the first line for the constructor
#   of the Dialog class insert self.overrideredirect( True ).  At the end
#   of the constructor appears the line self.initial_focus.focus_set()
#   Just before this line insert self.overrideredirect( False ).
# Projects
# - Logic Outline
# - Tkinter/Tix Outlines
# - User's Manual Outline

class MindTree( Application ):
   # Management
   def __init__( self ):
      Application.__init__( self )
      
      self._mainFrame        = None
      self._toolMenu         = None
      self._statusbar        = None
      
      self._soughtExpr       = ''                   # Find & Replace

   # Extension
   def buildGUI( self ):
      # Construct the Widgets
      self._mainFrame = self.makeWorkArea( )
      self.makeMenus( )
      self._toolbar = self.makeToolBar( )
      self._statusbar = self.makeStatusBar( )

      # Assemble the widgets
      self._toolbar.pack( side=Tix.TOP, fill=Tix.X )
      self._mainFrame.pack( side=Tix.TOP, expand=1, fill=Tix.BOTH )
      self._statusbar.pack( side=Tix.BOTTOM, fill=Tix.X )

   def makeWorkArea( self ):
      mainFrame   = Tix.PanedWindow( self, orientation=Tix.VERTICAL )
      editorPane  = mainFrame.add( 'editor', expand=1.0, min=100  )
      toolsFrame  = mainFrame.add( 'tools',  expand=0.0, size=230 )

      self._view  = self._ViewClass( editorPane, self )
      self._view.bind( '<<Modified>>', self.onModified, '+' )
      self._view.pack( expand=1, fill=Tix.BOTH )

      toolsWin    = self.makeToolsArea( toolsFrame )
      toolsWin.pack( expand=1, fill=Tix.BOTH )

      return mainFrame

   def makeMenus( self ):
      menu = Tix.Menu( self )
      self.winfo_toplevel().config( menu=menu )

      # File menu
      fileMenu = Tix.Menu( menu, tearoff=0, activebackground='blue', activeforeground='white' )
      menuItem( fileMenu,    RES.FILE_NEW_MENU_STR,           self.new,                   'Ctrl-N'                )
      menuItem( fileMenu,    RES.FILE_OPEN_MENU_STR,          self.open,                  'Ctrl-O'                )
      menuItem( fileMenu,    RES.FILE_CLOSE_MENU_STR,         self.close,                 'Ctrl-W'                )
      menuItem( fileMenu,    RES.FILE_SAVE_MENU_STR,          self.save,                  'Ctrl-S'                )
      menuItem( fileMenu,    RES.FILE_SAVEAS_MENU_STR,        self.saveAs                                         )
      fileMenu.add_separator( )
      importMenu = Tix.Menu( fileMenu, tearoff=0, activebackground='blue', activeforeground='white' )
      for pluginName,pluginClass in self._plugins.iterPlugins():
         if ImporterPlugin in pluginClass.__bases__:
            menuItem( importMenu,  pluginName,                TkTools.CALLBACK( self.open, pluginClass( self._view ) )          )
      fileMenu.add_cascade( label=RES.IMPORT_MENU_STR,    underline=0, menu=importMenu )

      exportMenu = Tix.Menu( fileMenu, tearoff=0, activebackground='blue', activeforeground='white' )
      for pluginName,pluginClass in self._plugins.iterPlugins():
         if ExporterPlugin in pluginClass.__bases__:
            menuItem( exportMenu,  pluginName,                TkTools.CALLBACK( self.saveAs, anArchiver=pluginClass( self._view ) )          )
      fileMenu.add_cascade( label=RES.EXPORT_MENU_STR, underline=0, menu=exportMenu )
      fileMenu.add_separator( )
      menuItem( fileMenu,    RES.FILE_EXIT_MENU_STR,          self.exit                                           )
      menu.add_cascade( label='File', underline=0, menu=fileMenu )

      # View-Specific Menus
      for subMenuName, subMenu in self._view.menus( menu ):
         subMenu.configure( tearoff=0, activebackground='blue', activeforeground='white' )
         menu.add_cascade( label=subMenuName, underline=0, menu=subMenu )

      # Tool Menu
      toolMenu = Tix.Menu( menu, tearoff=0, activebackground='blue', activeforeground='white' )

      for pluginName,plugin in self._plugins.iterPlugins():
         if isinstance( plugin, PluggableTool ):
            menuItem( toolMenu, plugin.GUI_LABEL )
      menu.add_cascade( label='Tools', underline=0, menu=toolMenu )

      menu.add_separator( )

      # Help Menu
      helpMenu = Tix.Menu( menu, tearoff=0, activebackground='blue', activeforeground='white' )
      menuItem( helpMenu,    RES.HELP_MENU_STR,                 None,                       'F1'                    )
      menuItem( helpMenu,    RES.HELP_ABOUT_MENU_STR                                                                )
      menu.add_cascade( label='Help', underline=0, menu=helpMenu )

      # Accelerator Key Bindings
      self.winfo_toplevel().bind_all( RES.NEW_FILE_ACCEL,    self.new                                            )
      self.winfo_toplevel().bind_all( RES.OPEN_FILE_ACCEL,   self.open                                           )
      self.winfo_toplevel().bind_all( RES.CLOSE_FILE_ACCEL,  self.close                                          )
      self.winfo_toplevel().bind_all( RES.SAVE_FILE_ACCEL,   self.save                                           )
      self.winfo_toplevel().bind_all( RES.UNDO_CHANG_ACCEL,  self._view.undo                                     )
      self.winfo_toplevel().bind_all( RES.REDO_CHANGE_ACCEL, self._view.redo                                     )
      self.winfo_toplevel().bind_all( RES.FIND_ACCEL,        self.find                                           )
      self.winfo_toplevel().bind_all( RES.REPLACE_ACCEL,     self._view.replace                                  )
      self.winfo_toplevel().bind_all( RES.QUICKFIND_ACCEL,   TkTools.CALLBACK( self.onQuickFind )                )

   def makeToolBar( self ):
      def toolbarItem( toolbar, img, cmd=None, **opts ):
         if 'balloonmessage' in opts:
            balloonmessage = opts[ 'balloonmessage' ]
            del opts[ 'balloonmessage' ]
         else:
            balloonmessage = None

         if cmd is not None:
            opts[ 'command' ] = cmd

         opts[ 'image' ] = img
         opts[ 'relief' ] = Tix.FLAT

         btn = Tix.Button( toolbar, **opts )
         btn.pack( side=Tix.LEFT )

         if balloonmessage:
            Tix.Balloon( toolbar.winfo_toplevel( ) ).bind_widget( btn, msg=balloonmessage )

      toolbar = Tix.Frame( self, relief=Tix.RAISED )

      file_tb = Tix.Frame( toolbar, relief=Tix.GROOVE, borderwidth=2 )
      toolbarItem( file_tb, RES.TBIMG_FILE_NEW,   self.new,  balloonmessage=RES.TBHELP_FILE_NEW  )
      toolbarItem( file_tb, RES.TBIMG_FILE_OPEN,  self.open, balloonmessage=RES.TBHELP_FILE_OPEN )
      toolbarItem( file_tb, RES.TBIMG_FILE_SAVE,  self.save, balloonmessage=RES.TBHELP_FILE_SAVE )
      file_tb.pack( side=Tix.LEFT, padx=2, pady=2 )

      edit_tb = Tix.Frame( toolbar, relief=Tix.GROOVE, borderwidth=2 )
      toolbarItem( edit_tb, RES.TBIMG_EDIT_CUT,   self._view.cut,   balloonmessage=RES.TBHELP_ARTICLE_CUT   )
      toolbarItem( edit_tb, RES.TBIMG_EDIT_COPY,  self._view.copy,  balloonmessage=RES.TBHELP_ARTICLE_COPY  )
      toolbarItem( edit_tb, RES.TBIMG_EDIT_PASTE, self._view.paste, balloonmessage=RES.TBHELP_ARTICLE_PASTE )
      edit_tb.pack( side=Tix.LEFT, padx=2, pady=2 )

      edit_tb2 = Tix.Frame( toolbar, relief=Tix.GROOVE, borderwidth=2 )
      toolbarItem( edit_tb2, RES.TBIMG_EDIT_UNDO,  self._view.undo, balloonmessage=RES.TBHELP_EDIT_UNDO  )
      toolbarItem( edit_tb2, RES.TBIMG_EDIT_REDO,  self._view.redo, balloonmessage=RES.TBHELP_EDIT_REDO  )
      edit_tb2.pack( side=Tix.LEFT, padx=2, pady=2 )

      tree_tb = Tix.Frame( toolbar, relief=Tix.GROOVE, borderwidth=2 )
      toolbarItem( tree_tb, RES.TBIMG_TREE_EXPAND,   TkTools.CALLBACK( self._view.expand ),   balloonmessage=RES.TBHELP_TREE_EXPAND   )
      toolbarItem( tree_tb, RES.TBIMG_TREE_COLLAPSE, TkTools.CALLBACK( self._view.collapse ), balloonmessage=RES.TBHELP_TREE_COLLAPSE )
      tree_tb.pack( side=Tix.LEFT, padx=2, pady=2 )

      find_tb = Tix.Frame( toolbar, relief=Tix.GROOVE, borderwidth=2 )
      self._quickFindEntry = Tix.Entry( find_tb, width=25 )
      self._quickFindEntry.pack( side=Tix.LEFT )
      self._quickFindEntry.bind( '<Return>', TkTools.CALLBACK( self.onQuickFind ) )
      toolbarItem( find_tb, RES.TBIMG_SEARCH_FIND, TkTools.CALLBACK( self.onQuickFind ) )
      find_tb.pack( side=Tix.LEFT, padx=2, pady=2 )

      return toolbar

   def makeStatusBar( self ):
      statusbar = Tix.Frame( self, borderwidth=3, relief=Tix.FLAT )

      Tix.Label( statusbar, text='Field 1', anchor=Tix.W, relief=Tix.SUNKEN, borderwidth=2 ).pack( side=Tix.LEFT, fill=Tix.X, expand=1 )
      Tix.Label( statusbar, text='Field 2', width=20, anchor=Tix.W, relief=Tix.SUNKEN, borderwidth=2 ).pack( side=Tix.LEFT )
      Tix.Label( statusbar, text='Field 3', width=10, anchor=Tix.W, relief=Tix.SUNKEN, borderwidth=2 ).pack( side=Tix.LEFT )
      Tix.Label( statusbar, text='Field 4', width=10, anchor=Tix.W, relief=Tix.SUNKEN, borderwidth=2 ).pack( side=Tix.LEFT )

      return statusbar

   def makeToolsArea( self, parent ):
      def addTools( parentNB, fullToolList, toolOrder=None ):
         if toolOrder is None:
            for toolName in fullToolList:
               try:
                  fullToolList.remove( toolName )
                  toolPane = parentNB.add( toolName.lower(), label=toolName )
                  plugin = self._plugins.makePlugin( toolName, self._view )
                  toolWidget = plugin.buildGUI( toolPane )
                  toolWidget.pack( )
               except:
                  pass
         else:
            for toolName in toolOrder:
               try:
                  fullToolList.remove( toolName )
                  toolPane = parentNB.add( toolName.lower(), label=toolName )
                  plugin = self._plugins.makePlugin( toolName, self._view )
                  toolWidget = plugin.buildGUI( toolPane )
                  toolWidget.pack( )
               except:
                  if toolName in fullToolList:
                     fullToolList.remove( toolName )

      toolsWin = None

      tools = [ ]
      for pluginName,pluginClass in self._plugins.iterPlugins( ):
         if PluggableTool in pluginClass.__bases__:
            tools.append( pluginName )

      toolsWin  = Tix.PanedWindow( parent, orientation=Tix.HORIZONTAL )

      toolsLeft   = toolsWin.add( 'tools',  expand=1.0 )
      toolsRight  = toolsWin.add( 'keyboards', expand=1.0 )

      # Build the Tools Notebook
      toolsLeftNB = Tix.NoteBook( toolsLeft )

      toolOrder = self.CONFIG.get( 'Tools', 'toolOrder' ).split(',')
      addTools( toolsLeftNB, tools, toolOrder )

      # Build the Keyboards Notebook
      keyboardNB = Tix.NoteBook( toolsRight )
      keyboardNB.pack( expand=True, fill=Tix.BOTH )
      keyboards = self.CONFIG.get( 'Keyboards', 'keyboardOrder' ).split(',')

      for keyboardName in keyboards:
         keyboardLabel = keyboardName
         keyboardName = keyboardName.replace( ' ', '_' ).lower()
         toolPane = keyboardNB.add( keyboardName, label=keyboardLabel )
         plugin = self._plugins.makePlugin( 'Keyboard', self._view )
         plugin.setName( keyboardLabel )
         plugin.buildGUI( toolPane )

      toolsLeftNB.pack( expand=True, fill=Tix.BOTH )

      return toolsWin

   def onQuickFind( self ):
      newSoughtExpr = self._quickFindEntry.get( )

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

         self._view.setupFind( soughtRegExpr )

      try:
         path,subject,lineNo,begin,end = self._view.findNext( )
         print '[ %03d : %03d : %03d ] - %s' % ( lineNo, begin, end, path )
      except:
         print 'Expression not found.'

   def find( self ):
      pass



if __name__== '__main__' :
   print 'Starting MindTree'
   mt = MindTree( )

   with SplashScreen( mt, 'resources\\images\\splash.gif' ):
      TkTools.fixTkinter( )
      
      rootDir = RES.APP_DIR
      imagesDir = TkTools.dirPath( rootDir, 'Resources', 'images'  )
      cursorDir = TkTools.dirPath( rootDir, 'Resources', 'cursors' )
      RES.loadValues( imagesDir, cursorDir )
      
      archiver = Archiver( RES.OUTLINE_FILE_TYPES, RES.OUTLINE_FILE_EXTENSION )
      mt.iconbitmap( RES.BITMAP_ICON )
      mt.setupMVC( Outline, TreeEditor, archiver )
      mt.setupConfig( RES.APP_INIT_FILENAME, RES.APP_RECENT )
      mt.initializePlugins( RES.PLUGIN_DIR )
      mt.buildGUI( )
      workingDir = Application.CONFIG.get( 'Workspace', 'directory' )
      archiver.setup( workingDir )
      mt.winfo_toplevel().wm_geometry( Application.CONFIG.get( 'Window', 'Geometry' ) )
      
      mt.new( )

   mt.mainloop()
