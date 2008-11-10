# Read and Convert a MindTree v1.0 Project file

from OutlineModel import OutlineModel, TreeNode
from MindTree1ModelLib import readMT1Model
from PyQt4 import QtCore

def convertProject( aProject ):
   newModelOutline = _convertProject( aProject.data._tree )
   newModelOutline._title = QtCore.QVariant( unicode(aProject._title) )
   return newModelOutline

def _convertProject( oldModelTreeNode, newModelParentNode=None ):
   title   = unicode(oldModelTreeNode.title)
   article = ''
   
   if isinstance( oldModelTreeNode.article, list ):
      for key,val,index in oldModelTreeNode.article:
         if key == 'text':
            article += val

   newModelTreeNode = TreeNode( title, newModelParentNode, article )
   for oldChildNode in oldModelTreeNode.children( ):
      newModelTreeNode.appendChild( _convertProject(oldChildNode, newModelTreeNode) )
   return newModelTreeNode

def importMT1Project( filename, projectName ):
   mt1Model = readMT1Model( filename, projectName )
   theConvertedProject = convertProject( mt1Model )
   return OutlineModel( theConvertedProject )
