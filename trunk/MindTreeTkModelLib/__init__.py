from Project import Project
from Outline import *

def readMT1Model( filename, projectName ):
   try:
      import pickle
      data = pickle.load( open( filename, 'rb' ) )
      return Project( filename, data, projectName )
   except:
      import tkMessageBox
      tkMessageBox.showerror( 'Error', 'An unknown error occured while trying to load file.' )
      return None


