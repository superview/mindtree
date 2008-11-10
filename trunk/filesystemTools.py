import os.path


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
   
