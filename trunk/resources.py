import Tix
import tkFont
from TkTools import *


class MindtreeResources( Resources ):
   def __init__( self ):
      Resources.__init__( self )
   
   def loadValues( self, imageDir='', cursorDir='' ):
      # Directories
      Resources.loadValues( self, imageDir, cursorDir )
      #self.IMAGE_DIR                 = imageDir
      #self.CURSOR_DIR                = cursorDir
      self.PLUGIN_DIR                = dirPath( self.APP_DIR, 'Plugins' )
      self.WORKSPACE_DIR             = dirPath( self.APP_DIR, 'workspace' )
      
      
      # Application Information
      self.APP_NAME                  = 'MindTree'
      self.APP_VERSION               = '1.0b1'
      self.APP_INIT_FILENAME         = 'MindTree.ini'
      self.APP_RECENT                = 'recent.ini'
      
      
      # Data File Information
      self.OUTLINE_FILE_TYPES        = [ ( 'MindTree Data File', '*.mt' ), ( 'All Files', '*.*' ) ]
      self.OUTLINE_FILE_EXTENSION    = 'mt'
      
      
      # Icons
      self.BITMAP_ICON               = 'questhead'
      
      # Images
      self.SPLASH_SCREEN_IMAGE       = self.image( 'splash.gif'        )
      self.TBIMG_FILE_NEW            = self.image( 'file_new.gif'      )
      self.TBIMG_FILE_OPEN           = self.image( 'file_open.gif'     )
      self.TBIMG_FILE_SAVE           = self.image( 'file_save.gif'     )
      self.TBIMG_EDIT_CUT            = self.image( 'edit_cut.gif'      )
      self.TBIMG_EDIT_COPY           = self.image( 'edit_copy.gif'     )
      self.TBIMG_EDIT_PASTE          = self.image( 'edit_paste.gif'    )
      self.TBIMG_EDIT_UNDO           = self.image( 'edit_undo.gif'     )
      self.TBIMG_EDIT_REDO           = self.image( 'edit_redo.gif'     )
      self.TBIMG_TREE_EXPAND         = self.image( 'tree_expand.gif'   )
      self.TBIMG_TREE_COLLAPSE       = self.image( 'tree_collapse.gif' )
      self.TBIMG_SEARCH_FIND         = self.image( 'find.gif'          )
      self.FILE_IMG                  = self.image( 'file.gif'          )
      self.TEXTFILE_IMG              = self.image( 'textfile.gif'      )
      self.IMAGE_NOT_FOUND           = self.image( 'unknown.gif'       )
      self.BOOKMARK                  = self.image( 'bookmark.gif'      )
      
      
      # Strings
      self.APPLICATION_NAME_STR      = 'MindTree'
      self.APPLICATION_DATAFILE_NAME = 'MindTree Data File'
      self.FILE_MENU_STR             = '&File'
      self.FILE_NEW_MENU_STR         = '&New'
      self.FILE_OPEN_MENU_STR        = '&Open...'
      self.FILE_SAVE_MENU_STR        = '&Save'
      self.FILE_SAVEAS_MENU_STR      = 'Save &As...'
      self.FILE_CLOSE_MENU_STR       = '&Close'
      self.FILE_EXIT_MENU_STR        = 'E&xit'
      self.HIDE_SHOW_MENU_STR        = 'Hide/Show'
      self.IMPORT_MENU_STR           = 'Import...'
      self.EXPORT_MENU_STR           = 'Export...'
      self.TOOLS_MENU_STR            = 'Tools'
      self.HELP_MENU_STR             = 'Help'
      self.HELP_ABOUT_MENU_STR       = 'About...'
      self.HELP_APP_HELP_MENU_STR    = 'MindTree Help...'
      self.TBHELP_FILE_NEW           = 'New File'
      self.TBHELP_FILE_OPEN          = 'Open File'
      self.TBHELP_FILE_CLOSE         = 'Close File'
      self.TBHELP_FILE_SAVE          = 'Save File'
      self.TBHELP_ARTICLE_CUT        = 'Article Cut'
      self.TBHELP_ARTICLE_COPY       = 'Article Copy'
      self.TBHELP_ARTICLE_PASTE      = 'Article Paste'
      self.TBHELP_EDIT_UNDO          = 'Undo Edit'
      self.TBHELP_EDIT_REDO          = 'Redo Edit'
      self.TBHELP_TREE_EXPAND        = 'Expand Tree'
      self.TBHELP_TREE_COLLAPSE      = 'Collapse Tree'
      self.TBHELP_FIND               = 'Find'
      self.FIND_STYLE_REGEX          = 'regex'
      self.FILE_NEW_ACCEL_STR        = 'Ctrl-N'
      self.FILE_OPEN_ACCEL_STR       = 'Ctrl-O'
      self.FILE_CLOSE_ACCEL_STR      = 'Ctrl-W'
      self.FILE_SAVE_ACCEL_STR       = 'Ctrl-S'
      
      
      # Keyboard Accelerators
      self.NEW_FILE_ACCEL            = '<Control-KeyPress-N>'
      self.OPEN_FILE_ACCEL           = '<Control-KeyPress-O>'
      self.CLOSE_FILE_ACCEL          = '<Control-KeyPress-W>'
      self.SAVE_FILE_ACCEL           = '<Control-KeyPress-S>'
      self.UNDO_CHANG_ACCEL          = '<Control-KeyPress-Z>'
      self.REDO_CHANGE_ACCEL         = '<Control-KeyPress-Y>'
      self.FIND_ACCEL                = '<Control-KeyPress-F>'
      self.REPLACE_ACCEL             = '<Control-KeyPress-H>'
      self.QUICKFIND_ACCEL           = '<F3>'
      
      
      # CURSORS
      self.DnD_INSERT_BEFORE_CURSOR  = self.cursor( 'arrow_insertBefore' )
      self.DnD_INSERT_AFTER_CURSOR   = self.cursor( 'arrow_insertAfter' )
      self.DnD_INSERT_CHILD_CURSOR   = self.cursor( 'arrow_insertChild' )


RES = MindtreeResources( )

