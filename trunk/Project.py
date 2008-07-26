import TkTools
import os
import os.path
import shutil


class Project( object ):
   NAME_COUNTER = 0
   CONFIG       = None
   
   def __init__( self, filename=None, data=None ):
      self._projectDir      = None
      self._backupDir       = Project.CONFIG.get( 'Project', 'BackupDir' )
      
      self._filename        = filename
      
      self.modified         = False
      
      self.data             = data      # The actual data in the project
      
      if filename is None:
         filename = self.genUntitledFilename( )
      
      self.setFilename( filename )

   def projectDir( self, fullName=False ):
      return self._projectDir
   
   def backupDir( self, fullName=False ):
      if fullName:
         return os.path.join( self._projectDir, self._backupDir )
      else:
         return self._backupDir
   
   def filename( self, fullName=False ):
      if fullName:
         return os.path.join( self._projectDir, self._filename )
      else:
         return self._filename

   def setFilename( self, filename ):
      disk,path,name,extension = TkTools.splitFilePath( filename )
      self._projectDir = os.path.join( disk, path )
      self._backupDir  = os.path.join( self._projectDir, Project.CONFIG.get( 'Project', 'backupDir' ) )
      self._filename   = name + extension

   def activateProjectDir( self ):
      os.chdir( self._projectDir )
   
   def isNew( self ):
      if self._projectDir is None:
         return True
      else:
         return False

   def backup( self ):
      shutil.copytree( self._projectDir, self._backupDir )
   
   def genUntitledFilename( self ):
      Project.NAME_COUNTER += 1
      return 'Untitled%d' % Project.NAME_COUNTER

   def validateModel( self ):
      self.data.validateModel( )

   def updateModel( self ):
      self.data.updateModel( )
   
