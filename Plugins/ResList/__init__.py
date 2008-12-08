from PyQt4 import QtCore, QtGui, Qt
from OutlineView import ArticleViewWidget
from MindTreeApplicationFramework import *


class ResDialog( QtGui.QDialog ):
   def __init__( self, parent, app, outlineView ):
      QtGui.QDialog.__init__( self, parent )
      
      self._app         = app
      self._outlineView = outlineView
      
      self.nameText     = None
      self.typeText     = None
      self.valueText    = None
      
      layout = QtGui.QGridLayout( self )
      layout.setObjectName( 'gridLayout' )
      
      self.setWindowTitle( RES.get('ArticleResource','dialogName',translate=True) )
      
      row = 0
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('ArticleResource','nameLabel',translate=True) )
      layout.addWidget( label, row, 0, 1, 1 )
      
      self._nameEdit    = QtGui.QLineEdit( self )
      layout.addWidget( self._nameEdit, row, 1, 1, 1 )
      
      row += 1
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('ArticleResource','typeLabel',translate=True) )
      layout.addWidget( label, row, 0, 1, 1 )
      
      self._typeEdit = QtGui.QComboBox( self )
      self._typeEdit.addItems( RES.getMultipartResource('ArticleResource','resourceTypes',translate=True) )
      layout.addWidget( self._typeEdit, row, 1, 1, 1 )
      
      row += 1
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('ArticleResource','valueLabel',translate=True) )
      layout.addWidget( label, row, 0, 1, 1 )
      
      self._valueEdit = QtGui.QLineEdit( self )
      layout.addWidget( self._valueEdit, row, 1, 1, 1 )
      
      locateButton = QtGui.QPushButton( self )
      locateButton.setText( RES.get('ArticleResource','locateLabel',translate=True) )
      layout.addWidget( locateButton, row, 2, 1, 1 )
      QtCore.QObject.connect( locateButton, QtCore.SIGNAL('clicked()'), self.locateValue )
      
      row += 1
      
      button = QtGui.QPushButton( self )
      button.setText( RES.get('ArticleResource','okLabel',translate=True ) )
      QtCore.QObject.connect( button, QtCore.SIGNAL('clicked()'), self.ok )
      layout.addWidget( button, row, 0, 1, 2 )
      
      button = QtGui.QPushButton( self )
      button.setText( RES.get('ArticleResource','cancelLabel',translate=True) )
      layout.addWidget( button, row, 2, 1, 2 )
      QtCore.QObject.connect( button, QtCore.SIGNAL('clicked()'), self.cancel )
   
   def ok( self ):
      self.nameText   = unicode(self._nameEdit.text( ))
      self.typeText   = unicode(self._typeEdit.currentText( )).upper()
      self.valueText  = unicode(self._valueEdit.text( ))
      
      self.done( QtGui.QDialog.Accepted )
   
   def cancel( self ):
      self.done( QtGui.QDialog.Rejected )

   def locateValue( self ):
      index = self._typeEdit.currentIndex( )
      types = RES.getMultipartResource('ArticleResource','resourceTypes')
      selectedType = types[index].upper()
      
      if selectedType == 'STRING':
         text = self._valueEdit.text( )
      elif selectedType == 'IMAGE':
         text = self.locateImageResource( )
      elif selectedType == 'BOOKMARK':
         title = RES.get('ArticleResource','locateBookmarkTitle')
         text  = RES.get('ArticleResource','locateBookmarkText')
         dlg = QtGui.QMessageBox( QtGui.QMessageBox.Question, title, text, QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel )
         result = dlg.exec_( )
         if result == QtGui.QMessageBox.Yes:
            current = self._outlineView.outlineWidget().currentIndex()
            text = current.internalPointer().id()
         else:
            return
         
      elif selectedType == 'LINK':
         return
      else:
         return
      
      self._valueEdit.setText( text )

   def locateImageResource( self ):
      IMAGE_DIR = RES.get('ArticleResource','imageDir')
      
      dlg = QtGui.QFileDialog( self, 'Insert image...', '', ArticleViewWidget.ImageFormats )
      dlg.setFileMode( QtGui.QFileDialog.ExistingFile )
      dlg.setModal(True)
      if not dlg.exec_():
         return   # The operation was canceled
      
      filenames = dlg.selectedFiles( )
      
      if len(filenames) != 1:
         return   # The operation was canceled
      
      filename = unicode(filenames[0])
      disk,path,name,ext = splitFilePath( filename )
      
      # Copy the image to the resource folder if needed
      imagePath = os.path.join( IMAGE_DIR, name + ext )
      if not os.path.exists( imagePath ):
         if not os.path.exists( IMAGE_DIR ):
            os.mkdir( IMAGE_DIR )
         import shutil
         shutil.copy( filename, imagePath )
      
      self.nameText  = unicode(self._nameEdit.text())
      self.typeText  = unicode(self._typeEdit.currentText()).upper()
      self.valueText = '{0}/{1}{2}'.format( IMAGE_DIR, name, ext )
      
      if self.nameText == '':
         self.nameText = '{0}{1}'.format( name, ext )
      
      return self.valueText


class ResourcesEditorModel( QtCore.QAbstractItemModel ):
   def __init__( self, proj=None, parent=None ):
      QtCore.QAbstractItemModel.__init__(self, parent)
      
      self._project     = proj
      self._resNameList = [ ]
      
      if self._project:
         self._resNameList = list(self._project.res_names())
         self._resNameList.sort( )
   
   def columnCount( self, parent ):
      return 3    # [ name, type, value ]
   
   def data( self, index, role ):
      if not index.isValid( ):
         return QtCore.QVariant( )
      
      if role != QtCore.Qt.DisplayRole:
         return QtCore.QVariant( )
      
      row = index.row()
      resName = self._resNameList[ row ]
      
      if index.column() == 0:
         val = resName
      else:
         val = self._project.res_info(resName)[ index.column() - 1 ]
      
      return QtCore.QVariant(val)
   
   def flags( self, index ):
      if not index.isValid( ):
         return QtCore.Qt.ItemIsEnabled
      
      return QtCore.Qt.ItemIsEditable | QtCore.QAbstractItemModel.flags( self, index )
   
   def headerData(self, section, orientation, role):
      header = [ 'Name', 'Type', 'Value', 'Uses' ]
      
      if (orientation == QtCore.Qt.Horizontal) and (role == QtCore.Qt.DisplayRole):
         return QtCore.QVariant( header[section] )
      
      return QtCore.QVariant()

   def index(self, row, column, parentIndex):
      if row < 0 or column < 0 or row >= self.rowCount(parentIndex) or column >= self.columnCount(parentIndex):
         return QtCore.QModelIndex()
      
      return self.createIndex(row, column, None)

   def parent( self, index ):
      return self.createIndex(0, 0, None)
   
   def rowCount(self, parent):
      return len(self._resNameList)

   
class Resources( QtGui.QTabWidget, MindTreePluggableTool ):
   theApp = None

   NAME             = 'Resources'
   VERSION          = ( 1, 1 )
   BUILD_DATE       = ( 2008, 12, 4 )

   DEFAULT_SETTINGS = {
                      # Resources
                      'filterLabel':            'Filter',
                      'filterList':             'all:images:bookmarks:links',
                      'addBtnLabel':            'Add',
                      'removeBtnLabel':         'Remove',
                      'modifyBtnLabel':         'Modify',
                      'insertBtnLabel':         'Insert',
                      # Configuration
                      'font':                   'Lucida Sans Unicode:12'
                      }
   
   def __init__( self, parent, app, outlineView ):
      Resources.theApp = app
      self._outlineView = outlineView
      self._project     = outlineView.getProject( )
      self._resModel    = ResourcesEditorModel( self._project )
      
      QtCore.QObject.connect( outlineView, QtCore.SIGNAL('newProject()'), self.newProject )
      
      QtGui.QTabWidget.__init__( self, parent )
      MindTreePluggableTool.__init__( self, parent, app, outlineView )
      
      gridLayout = QtGui.QGridLayout( self )
      gridLayout.setObjectName( 'ResGridLayout' )
      
      row = 0
      
      boxLayout = QtGui.QBoxLayout( QtGui.QBoxLayout.LeftToRight )
      gridLayout.addLayout( boxLayout, row, 0, 1, 2 )
      
      label = QtGui.QLabel( self )
      label.setText( RES.get('Resources','filterLabel',translate=True) )
      boxLayout.addWidget( label, QtCore.Qt.AlignHCenter )
      
      self._filter = QtGui.QComboBox( self )
      self._filter.addItems( RES.getMultipartResource('Resources','filterList',translate=True) )
      boxLayout.addWidget( self._filter, QtCore.Qt.AlignHCenter )
      
      row += 1
      
      self._resList = QtGui.QTreeView( self )
      gridLayout.addWidget( self._resList, row, 0, 4, 2 )
      self._resList.setColumnWidth( 1, 5 )
      self._resList.setSortingEnabled( False )
      self._resList.setModel( self._resModel )
      
      self._addBtn = QtGui.QPushButton( self )
      self._addBtn.setText( RES.get('Resources','addBtnLabel',translate=True) )
      QtCore.QObject.connect( self._addBtn, QtCore.SIGNAL('clicked()'), self.addResource )
      gridLayout.addWidget( self._addBtn, row, 2, 1, 1 )
      
      row += 1
      
      self._removeBtn = QtGui.QPushButton( self )
      self._removeBtn.setText( RES.get('Resources','removeBtnLabel',translate=True) )
      QtCore.QObject.connect( self._addBtn, QtCore.SIGNAL('clicked()'), self.delResource )
      gridLayout.addWidget( self._removeBtn, row, 2, 1, 1 )
      
      row += 1
      
      self._insertBtn = QtGui.QPushButton( self )
      self._insertBtn.setText( RES.get('Resources','insertBtnLabel',translate=True) )
      QtCore.QObject.connect( self._addBtn, QtCore.SIGNAL('clicked()'), self.insertResource )
      gridLayout.addWidget( self._insertBtn, row, 2, 1, 1 )

   def addResource( self ):
      dlg = ResDialog( self, Resources.theApp, self._outlineView )
      if dlg.exec_( ) == QtGui.QDialog.Rejected:
         return
      
      resName    = dlg.nameText
      resTypeStr = dlg.typeText
      resValue   = dlg.valueText
      
      if resTypeStr == 'IMAGE':
         resType  = MindTreeProject.IMAGE_RES
         
         resObj = QtCore.QVariant(QtGui.QImage(resValue))
         self._outlineView.articleWidget().document().addResource( QtGui.QTextDocument.ImageResource, QtCore.QUrl(resValue), resObj )
      
      elif resTypeStr == 'STRING':
         resType = MindTreeProject.STRING_RES
      
      elif resTypeStr == 'BOOKMARK':
         resType = MindTreeProject.BOOKMARK_RES
      
      elif resType == 'LINK':
         resType = MindTreeProject.LINK_RES
      
      else:
         raise Exception
      
      self._project.res_add( resName, resType, resValue )
      
      self.refresh( )

   def delResource( self ):
      pass
   
   def insertResource( self ):
      textCursor = self._outlineView.articleWidget().textCursor()
      textCursor.insertHtml( '<img src="{0}"/>'.format(resURL) )

   def newProject( self ):
      self._project = self._outlineView.getProject( )
      QtCore.QObject.connect( self._project, QtCore.SIGNAL('resourceChange()'), self.refresh )
      self.refresh( )
   
   def refresh( self ):
      self._project     = self._outlineView.getProject( )
      self._resModel    = ResourcesEditorModel( self._project )
      self._resList.setModel( self._resModel )
      self._resList.resizeColumnToContents( 1 )

 
pluginClass = Resources
