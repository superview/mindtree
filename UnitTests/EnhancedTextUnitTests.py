from Tkinter import *
import tkFont
from DocumentWriter.EnhancedText import EnhancedText
import unittest

SampleText = '''To create a new project, use the New Project item in the Project menu.  This will prompt you to save any changes to your currently open project and will create a new untitled project.  If Wing is started without any command line arguments, the most recent project is opened, or if no project exists then the Default Project is opened.  
  When you create a new project, you will often want to alter some of the Project Properties to point Wing at the version of Python you want to use, set PYTHONPATH so Wing's source analyzer and debugger can find your files, and set any other necessary runtime environment for your code.  
To add files to your project, use the following items in the Project menu: 
   Add Directory allows you to specify a directory to include in the project.  In many cases, this is the only operation needed to set up a new project.  You will be able to specify a filter of which files to include, whether to include hidden & temporary files, and whether to include subdirectories.  The list of files in the project will be updated as files matching the criteria are added and removed from the disk.  
   Add Current File will add the frontmost current editor file to the project if it is not already there.  
Add New File is used to create a new file and simultaneously add it to your project.  
Add File will prompt you to select a single file to add to the project view.  Note that this also may result in adding a new directory to the project manager window, if that file is the first to be added for a directory.  
        A subset of these options can be accessed from the context menu that appears when right-clicking your mouse on the surface of the project manager window.
'''

class TestEnhancedText( unittest.TestCase ):
   def setUp( self ):
      self.root = Tk()
      self.font = tkFont.Font( font='Courier 8' )
      self.text = EnhancedText( self.root, height=20, width=80, font=self.font )
      self.text.grid( row=0, column=0, sticky='nsew' )
      
      xscroll            = Scrollbar( self.root, orient='horizontal',command=self.text.xview )
      yscroll            = Scrollbar( self.root, orient='vertical',  command=self.text.yview )
      xscroll.grid(    row=1, column=0, sticky='ew' )
      yscroll.grid(    row=0, column=1, sticky='ns' )
      self.text[ 'xscrollcommand' ] = xscroll.set
      self.text[ 'yscrollcommand' ] = yscroll.set
      
      self.root.update( )

   #def try_dline_start_end( self, index, startIndex, endIndex ):
      #idx = self.text.dline_start( index )
      #self.assertEqual( idx, startIndex )
      
      #idx = self.text.dline_end( index )
      #self.assertEqual( idx, endIndex )

   #def testEmptyText( self ):
      #self.try_dline_start_end( '1.0', '1.0', '1.0' )
      #idx = self.text.dline_next( self.text.index('1.0') )
      #self.assertEqual( idx, '1.0' )
      
      #idx = self.text.dline_prev( self.text.index('1.0') )
      #self.assertEqual( idx, '1.0' )

   def testPopulatedText( self ):
      self.text.insert( '1.0', SampleText )
      self.text.update( )
      
      self.try_dline_start_end( '@100,100', '2.107', '2.204' )
      self.try_dline_start_end( '@100,110', '2.107', '2.204' )
      self.try_dline_start_end( '@100,120', '2.205', '2.288' )
      self.try_dline_start_end( '@100,130', '3.0',   '3.75'  )
      self.try_dline_start_end( '@100,140', '3.0',   '3.75'  )

if __name__=='__main__':
   root = Tk()
   text = EnhancedText( root )
   text.pack( )
   root.mainloop( )

   