from TkTools import *
import unittest


class DirPathTests( unittest.TestCase ):
   def testEmptyPath( self ):
      path1Parts  = [ ]
      path1Answer = '\\'
      self.assertRaises( TypeError, dirPath, *path1Parts )

   def testAbsolutePath( self ):
      path1Parts  = ( 'c:', )
      path1Answer = 'c:\\'
      self.assertEqual( dirPath( *path1Parts ), path1Answer )

   def testLongAbsolutePath( self ):
      path1Parts  = ( 'c:', 'one', 'two', 'three' )
      path1Answer = 'c:one\\two\\three\\'
      self.assertEqual( dirPath( *path1Parts ), path1Answer )
   
class FilePathTests( unittest.TestCase ):
   def testEmptyPath( self ):
      path1Parts  = [ ]
      path1Answer = ''
      self.assertRaises( TypeError, filePath, *path1Parts )

   def testAbsolutePath( self ):
      path1Parts  = ( 'c:', )
      path1Answer = 'c:'
      self.assertEqual( filePath( *path1Parts ), path1Answer )

   def testLongAbsolutePath( self ):
      path1Parts  = ( 'c:', 'one', 'two', 'three' )
      path1Answer = 'c:one\\two\\three'
      self.assertEqual( filePath( *path1Parts ), path1Answer )
   
class SplitPathTest( unittest.TestCase ):
   def testEmptyPath( self ):
      disk,path,file,extension = splitFilePath( '' )
      self.assertEqual( disk,      ''   )
      self.assertEqual( path,      ''   )
      self.assertEqual( file,      ''   )
      self.assertEqual( extension, ''   )
   
   def testRootPath( self ):
      disk,path,file,extension = splitFilePath( 'c:' )
      self.assertEqual( disk,      'c:' )
      self.assertEqual( path,      ''   )
      self.assertEqual( file,      ''   )
      self.assertEqual( extension, ''   )
      
      disk,path,file,extension = splitFilePath( 'c:\\' )
      self.assertEqual( disk,      'c:' )
      self.assertEqual( path,      '\\' )
      self.assertEqual( file,      ''   )
      self.assertEqual( extension, ''   )
      
      disk,path,file,extension = splitFilePath( '\\' )
      self.assertEqual( disk,      ''   )
      self.assertEqual( path,      '\\' )
      self.assertEqual( file,      ''   )
      self.assertEqual( extension, ''   )
   
   def testBasicFilename( self ):
      disk,path,file,extension = splitFilePath( 'filename' )
      self.assertEqual( disk,      ''         )
      self.assertEqual( path,      ''         )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, ''         )
      
      disk,path,file,extension = splitFilePath( 'filename.txt' )
      self.assertEqual( disk,      ''         )
      self.assertEqual( path,      ''         )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, '.txt'     )

   def testDirFilename( self ):
      disk,path,file,extension = splitFilePath( 'dir\\filename' )
      self.assertEqual( disk,      ''         )
      self.assertEqual( path,      'dir'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, ''         )
      
      disk,path,file,extension = splitFilePath( 'dir\\filename.txt' )
      self.assertEqual( disk,      ''         )
      self.assertEqual( path,      'dir'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, '.txt'     )

   def testLongDirFilename( self ):
      disk,path,file,extension = splitFilePath( 'dir1\\dir2\dir3\\filename' )
      self.assertEqual( disk,      ''         )
      self.assertEqual( path,      'dir1\\dir2\\dir3'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, ''         )
      
      disk,path,file,extension = splitFilePath( 'dir1\\dir2\\dir3\\filename.txt' )
      self.assertEqual( disk,      ''         )
      self.assertEqual( path,      'dir1\\dir2\\dir3'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, '.txt'     )

   def testDiskDirFilename( self ):
      disk,path,file,extension = splitFilePath( 'c:\\dir\\filename' )
      self.assertEqual( disk,      'c:'       )
      self.assertEqual( path,      '\\dir'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, ''         )
      
      disk,path,file,extension = splitFilePath( 'c:dir\\filename' )
      self.assertEqual( disk,      'c:'       )
      self.assertEqual( path,      'dir'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, ''         )
      
      disk,path,file,extension = splitFilePath( 'c:\\dir\\filename.txt' )
      self.assertEqual( disk,      'c:'       )
      self.assertEqual( path,      '\\dir'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, '.txt'     )
      
      disk,path,file,extension = splitFilePath( 'c:dir\\filename.txt' )
      self.assertEqual( disk,      'c:'       )
      self.assertEqual( path,      'dir'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, '.txt'     )

   def testDiskLongDirFilename( self ):
      disk,path,file,extension = splitFilePath( 'c:\\dir1\\dir2\dir3\\filename' )
      self.assertEqual( disk,      'c:'       )
      self.assertEqual( path,      '\\dir1\\dir2\\dir3'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, ''         )
      
      disk,path,file,extension = splitFilePath( 'c:dir1\\dir2\dir3\\filename' )
      self.assertEqual( disk,      'c:'       )
      self.assertEqual( path,      'dir1\\dir2\\dir3'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, ''         )
      
      disk,path,file,extension = splitFilePath( 'c:\\dir1\\dir2\\dir3\\filename.txt' )
      self.assertEqual( disk,      'c:'       )
      self.assertEqual( path,      '\\dir1\\dir2\\dir3'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, '.txt'     )
      
      disk,path,file,extension = splitFilePath( 'c:dir1\\dir2\\dir3\\filename.txt' )
      self.assertEqual( disk,      'c:'       )
      self.assertEqual( path,      'dir1\\dir2\\dir3'      )
      self.assertEqual( file,      'filename' )
      self.assertEqual( extension, '.txt'     )

class TestTkMath( unittest.TestCase ):
   def setUp( self ):
      import Tkinter
      self.root = Tkinter.Tk( )
      tkMath.setup( self.root )
   
   def tearDown( self ):
      del self.root
      self.root = None



