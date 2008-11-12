from __future__ import print_function, unicode_literals
from TkTools import splitFilePath
import os
import os.path

class Project( object ):
   NAME_COUNTER = 0
   CONFIG       = None
   
   def __init__( self, filename=None, data=None, title=None ):
      self._title           = title
      self._projectDir      = None
      self._filename        = filename
      self.data             = data      # The actual data in the project
      
      if filename is None:
         filename = self.genUntitledFilename( )
      
      self.setFilename( filename )

   def projectDir( self, fullName=False ):
      return self._projectDir
   
   def filename( self, fullName=False ):
      if fullName:
         return os.path.join( self._projectDir, self._filename )
      else:
         return self._filename

   def setFilename( self, filename ):
      disk,path,name,extension = splitFilePath( filename )
      self._projectDir = os.path.join( disk, path )
      self._filename   = name + extension

   def activateProjectDir( self ):
      os.chdir( self._projectDir )
   
   def isNew( self ):
      if self._projectDir is None:
         return True
      else:
         return False

   def genUntitledFilename( self ):
      Project.NAME_COUNTER += 1
      return 'Untitled%d' % Project.NAME_COUNTER

   def validateModel( self ):
      self.data.validateModel( )

   def updateModel( self ):
      self.data.updateModel( )
   
