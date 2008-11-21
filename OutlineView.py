from PyQt4 import QtCore, QtGui
from OutlineModel import OutlineModel, TreeNode
from ApplicationFramework import RES

from utilities import *


class OutlineView_Delegate( QtGui.QItemDelegate ):
   def __init__( self, parent ):
      QtGui.QItemDelegate.__init__( self, parent )
   
   def createEditor( self, parent, option, index ):
      editor = QtGui.QItemDelegate.createEditor( self, parent, option, index )
      editor.installEventFilter( self.parent() )
      return editor
   
   def setEditorData( self, editor, index ):
      editor.setText( index.internalPointer().data(0) )
   
   def setModelData( self, editor, model, index ):
      model.setData( index, editor.text(), QtCore.Qt.DisplayRole )
   

class OutlineViewWidget( QtGui.QTreeView ):
   '''Emits: entryRightClicked(QPoint,QModelIndex)'''
   def __init__( self, parent ):
      QtGui.QTreeView.__init__( self, parent )
      
      alternatingRowColors = RES.getboolean('OutlineView','alternatingRowColors')
      
      # Drag and Drop
      self.setDragEnabled( True )
      self.setAcceptDrops( True )
      #self.setDropIndicatorShown( True )
      self.setDragDropMode( QtGui.QAbstractItemView.InternalMove )
      
      # Entry Editing
      self.setItemDelegate( OutlineView_Delegate(self) )
      self.setEditTriggers( QtGui.QAbstractItemView.SelectedClicked |
                            QtGui.QAbstractItemView.CurrentChanged )
      
      # Appearance
      self.setAlternatingRowColors( alternatingRowColors )
      self.setUniformRowHeights(True)
      
      # Behavior Settings
      self.setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
      self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
      self.setSortingEnabled(False)
      self.setTabKeyNavigation(False)
      
      # Drag and Drop Cursors
      self.insertBefore_cursor  = RES.getDragCursor('OutlineView','DnD_insertBeforeCursor')
      self.insertAfter_cursor   = RES.getDragCursor('OutlineView','DnD_insertAfterCursor')
      self.insertChild_cursor   = RES.getDragCursor('OutlineView','DnD_insertChildCursor')

   def eventFilter( self, obj, event ):
      if isinstance(obj,QtGui.QLineEdit) and (event.type() == QtCore.QEvent.KeyPress):
         keyEvent = event
         if keyEvent.key() == QtCore.Qt.Key_Tab:
            if keyEvent.modifiers() == QtCore.Qt.ShiftModifier:
               self.parent().dedentNode()
            else:
               self.parent().indentNode()
            
            return True  # disallow target from handling the event.
         
         elif keyEvent.key() == QtCore.Qt.Key_Left:
            if keyEvent.modifiers() == QtCore.Qt.ControlModifier:
               self.parent().dedentNode()
               return True
      
         elif keyEvent.key() == QtCore.Qt.Key_Right:
            if keyEvent.modifiers() == QtCore.Qt.ControlModifier:
               self.parent().indentNode()
               return True
      
         elif keyEvent.key() == QtCore.Qt.Key_Up:
            if keyEvent.modifiers() == QtCore.Qt.ControlModifier:
               self.parent().moveNodeUp()
               return True
      
         elif keyEvent.key() == QtCore.Qt.Key_Down:
            if keyEvent.modifiers() == QtCore.Qt.ControlModifier:
               self.parent().moveNodeDown()
               return True
      
      return False
   
   def keyboardPressEvent( self, keyEvent ):
      if keyEvent.key() == QtCore.Qt.Key_Tab:
         if keyEvent.modifiers() == QtCore.Qt.ShiftModifier:
            self.parent().dedentNode()
         else:
            self.parent().indentNode()

   def _buildGui( self ):
      pass
   
   def _buildWidgets( self ):
      pass

   def _defineActions( self ):
      pass
   
   def _buildMenus( self ):
      pass
   
   def _buildToolbars( self ):
      pass
   
   def onModelChanged( self, index1=None, index2=None ):
      self.emit( QtCore.SIGNAL('modelChanged()') )

   # Drag and Drop
   def mousePressEvent( self, event ):
      if event.button() == QtCore.Qt.RightButton:
         point = event.pos()
         index = self.indexAt( point )
         self.emit( QtCore.SIGNAL('entryRightClicked(QPoint,QModelIndex)'), event.globalPos(), index )
      else:
         import copy
         if event.button() == QtCore.Qt.LeftButton:
            self._dragStartPosition = copy.copy( event.pos() )
            print( 'Clicked {0}'.format(self._dragStartPosition) )
         
         QtGui.QTreeView.mousePressEvent( self, event )

   def mouseMoveEvent( self, event ):
      # Are we doing a drag?
      if not (event.buttons() & QtCore.Qt.LeftButton):
         return
      
      if (event.pos() - self._dragStartPosition).manhattanLength() < QtGui.QApplication.startDragDistance():
         return
      
      # Encode the node and stuff it into a drag object
      dragStartIndex = self.indexAt( self._dragStartPosition )
      mimeData = self.model().mimifyNode( dragStartIndex )
      self.drag = QtGui.QDrag( self )
      self.drag.setMimeData( mimeData )
      
      # Execute the drag (this is blocking)
      dropAction = self.drag.exec_( QtCore.Qt.MoveAction )
      
      # If the drag was successful, remove the node
      if dropAction == QtCore.Qt.MoveAction:
         self.model().removeNode( dragStartIndex )

   def dragMoveEvent( self, event ):
      index,relation = self._dnd_insertionPos( event )
      self.setSelection( QtCore.QRect( event.pos(), event.pos() ), QtGui.QItemSelectionModel.ClearAndSelect )
      self._selectCursor( relation )

   def dragEnterEvent( self, event ):
      print( 'Entered' )
      if event.mimeData().hasFormat( RES.get('OutlineView','nodeMimeType') ):
         event.acceptProposedAction( )

   def dragLeaveEvent( self, event ):
      QtGui.QTreeView.dragLeaveEvent( self, event )

   def dropEvent( self, event ):
      if event.source() is self:
         if event.possibleActions() & QtCore.Qt.MoveAction:
            event.acceptProposedAction()
            
            print( 'Dropping' )
            # Determine the drop location
            point = event.pos()
            index = self.indexAt( point )
            
            newParent = index.parent()
            if newParent is None:
               newParent = QtCore.QModelIndex()
            
            newRow = index.row()
            
            # Extract the node
            mimeData = event.mimeData()
            if not mimeData.hasFormat( RES.get('OutlineView','nodeMimeType') ):
               return
            
            node = self.model().demimifyNode(mimeData)
            
            # Insert the node
            self.model().insertNode( newParent, newRow, node )

   def _dnd_insertionPos( self, evt ):
      # Find the closest entry to the mouse
      mousePos               = evt.pos()
      indexOfentryUnderMouse = self.indexAt( mousePos )
      
      # Is the cursur above or below the midpoint of this entry
      rectOfEntryUnderMouse  = self.visualRect( indexOfentryUnderMouse )
      min_y = rectOfEntryUnderMouse.y()
      max_y = min_y + rectOfEntryUnderMouse.height()
      mid_y = (min_y + max_y) / 2
      if mousePos.y() <= mid_y:
         # Before
         return ( indexOfentryUnderMouse, 'before' )
      else:
         # After (may be sibling or child)
         if mousePos.x() >= rectOfEntryUnderMouse.x() + RES.getint('OutlineView','DnD_siblingChildBound'):
            return ( indexOfentryUnderMouse, 'child' )
         else:
            return ( indexOfentryUnderMouse, 'after' )

   def _selectCursor( self, rel ):
      if rel == 'before':
         cursor = self.insertBefore_cursor
         statusTip = 'Drop before'
      elif rel == 'after':
         cursor = self.insertAfter_cursor
         statusTip = 'Drop after'
      else:
         cursor = self.insertChild_cursor
         statusTip = 'Drop as child'
      
      self.setStatusTip( statusTip )
      self.drag.setDragCursor( cursor[0], QtCore.Qt.CopyAction + QtCore.Qt.MoveAction )
      self.drag.setHotSpot( cursor[1] )
      print( 'Updatable: {0}'.format(self.updatesEnabled()) )
      self.repaint()
      self.update()
      self.window().repaint()
      self.window().update()


class ArticleViewWidget( QtGui.QTextEdit ):
   ImageFormats = 'Windows bitmap (*.bmp);;Graphic Interchange Format (*.gif);;Joint Photographic Experts Group (*.jpg);;Portable Network Graphics (*.png);;Tagged Image File Format (*.tif *.tiff);;All Files (*.*)'
   
   def __init__( self, parent ):
      QtGui.QTextEdit.__init__( self, parent )
      self._resources = { }
      
      self._buildGui( )
      self._updateToolbars( )

   def addImageResource( self, resURL, filename ):
      resType = QtGui.QTextDocument.ImageResource
      self._resources[ resURL ] = ( resType, filename )
      res = QtCore.QVariant(QtGui.QImage(filename))
      self.document().addResource( resType, QtCore.QUrl(resURL), res )

   def setResources( self, resDict ):
      self._resources = resDict
   
   def clear( self, keepResources=True ):
      QtGui.QTextEdit.clear( self )
      
      # Reload the resources
      if keepResources:
         for resUrl, resInfo in self._resources.iteritems():
            resType, resDetail = resInfo
            
            if resType == QtGui.QTextDocument.ImageResource:
               res = QtCore.QVariant(QtGui.QImage(resDetail))
               self.document().addResource( resType, QtCore.QUrl(resUrl), res )
   
   def getResources( self ):
      return self._resources
   
   def getFixedMenus( self ):
      return [ self.menuArticle ]
   
   def getToolbars( self ):
      return [ self._articletoolbar, self._styleToolbar, self._objectToolbar ]
   
   def articlePrint( self ):
      printer = QtGui.QPrinter( )
      dlg = QtGui.QPrintDialog( printer, self )
      if dlg.exec_() == QtGui.QDialog.Accepted:
         printer = dlg.printer()
         self.print_( printer )
   
   def editUndo( self ):
      self.undo()
   
   def editRedo( self ):
      self.redo()

   def articleCut( self ):
      self.cut()
   
   def articleCopy( self ):
      self.copy()
   
   def articlePaste( self ):
      self.paste()
   
   def articleSelectAll( self ):
      pass

   def textFontFamily( self, font ):
      if isinstance( font, QtGui.QFont ):
         family = font.family()
      QtGui.QTextEdit.setFontFamily( self, family )
      self.setFocus()
      self._updateToolbars()

   def textFontSize( self, size ):
      if isinstance( size, QtCore.QString ):
         size = int(str(size))
      elif isinstance( size, (str,unicode) ):
         size = int( size )
      QtGui.QTextEdit.setFontPointSize( self, size )
      self.setFocus()
      self._updateToolbars()

   def textStyleBold( self ):
      isBold = self.fontWeight()
      if isBold == QtGui.QFont.Bold:
         self.setFontWeight( QtGui.QFont.Normal )
      else:
         self.setFontWeight( QtGui.QFont.Bold )
      self._updateToolbars()
   
   def textStyleItalic( self ):
      isItalic = self.fontItalic()
      self.setFontItalic( not isItalic )
      self._updateToolbars()
   
   def textStyleUnderline( self ):
      isUnderlined = self.fontUnderline()
      self.setFontUnderline( not isUnderlined )
      self._updateToolbars()
   
   def textStyleOverstrike( self ):
      pass
   
   def textAlignLeft( self ):
      self.setAlignment( QtCore.Qt.AlignLeft )
      self._updateToolbars()
   
   def textAlignRight( self ):
      self.setAlignment( QtCore.Qt.AlignRight )
      self._updateToolbars()
   
   def textAlignCenter( self ):
      self.setAlignment( QtCore.Qt.AlignHCenter )
      self._updateToolbars()
   
   def textAlignFull( self ):
      self.setAlignment( QtCore.Qt.AlignJustify )
      self._updateToolbars()

   def textInsertImage( self ):
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
      resDir = RES.get('Project','imageDir')
      imagePath = os.path.join( resDir, name + ext )
      if not os.path.exists( imagePath ):
         if not os.path.exists( resDir ):
            os.mkdir( resDir )
         import shutil
         shutil.copy( filename, imagePath )
      
      resURL = 'res://img/{0}{1}'.format( name, ext )
      
      self.addImageResource( resURL, imagePath )
      self.textCursor().insertHtml( '<img src="{0}"/>'.format(resURL) )

   def _updateToolbars( self ):
      # Font Combo
      fontFamily = unicode(self.currentFont().family())
      self._fontFamilyCombo.setEditText( fontFamily )
      
      # Font Size
      fontSize = unicode(self.fontPointSize())
      self._fontSizeCombo.setEditText( fontSize )
      
      # Styles
      isBold = True if self.fontWeight() == QtGui.QFont.Bold else False
      self.textBoldAction.setChecked( isBold )
      self.textItalicAction.setChecked( self.fontItalic() )
      self.textUnderlineAction.setChecked( self.fontUnderline() )
      
      # Alignment
      alignment = self.alignment()
      if alignment == QtCore.Qt.AlignLeft:
         self.textAlignLeftAction.setChecked( True )
      elif alignment == QtCore.Qt.AlignRight:
         self.textAlignRightAction.setChecked( True )
      elif alignment == QtCore.Qt.AlignHCenter:
         self.textAlignCenterAction.setChecked( True )
      elif alignment == QtCore.Qt.AlignJustify:
         self.textAlignFullAction.setChecked( True )
   
   # Construct the widget
   def _buildGui( self ):
      self._buildWidgets( )
      self._defineActions( )
      self._buildMenus( )
      self._buildToolbars( )
   
   def _buildWidgets( self ):
      articleFont = RES.getFont( 'ArticleView', 'Font' )
      self.setFont( articleFont )
      
      QtCore.QObject.connect( self, QtCore.SIGNAL('cursorPositionChanged()'), self._cursorPositionChanged )
      
      self._fontFamilyCombo = QtGui.QFontComboBox( self )
      QtCore.QObject.connect( self._fontFamilyCombo, QtCore.SIGNAL('currentFontChanged(QFont)'), self.textFontFamily )
      
      self._fontSizeCombo = QtGui.QComboBox( self )
      
      self._fontSizeCombo.addItems( [ str(x) for x in (8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72) ] )
      QtCore.QObject.connect( self._fontSizeCombo, QtCore.SIGNAL('activated(QString)'), self.textFontSize )

   def _defineActions( self ):
      self.printAction               = RES.installAction( 'articlePrint',       self )
      
      self.editUndoAction            = RES.installAction( 'editUndo',           self )
      self.editRedoAction            = RES.installAction( 'editRedo',           self )
      
      self.articleCutAction          = RES.installAction( 'articleCut',         self )
      self.articleCopyAction         = RES.installAction( 'articleCopy',        self )
      self.articlePasteAction        = RES.installAction( 'articlePaste',       self )
      
      self.articleSelectAllAction    = RES.installAction( 'articleSelectAll',   self )
      
      self.textBoldAction            = RES.installAction( 'textStyleBold',      self )
      self.textItalicAction          = RES.installAction( 'textStyleItalic',    self )
      self.textUnderlineAction       = RES.installAction( 'textStyleUnderline', self )
      self.textOverstrikeAction      = RES.installAction( 'textStyleOverstrike',self )
      
      self.textAlignLeftAction       = RES.installAction( 'textAlignLeft',      self )
      self.textAlignRightAction      = RES.installAction( 'textAlignRight',     self )
      self.textAlignCenterAction     = RES.installAction( 'textAlignCenter',    self )
      self.textAlignFullAction       = RES.installAction( 'textAlignFull',      self )
      self.textAlignGroup            = QtGui.QActionGroup( self )
      self.textAlignGroup.addAction( self.textAlignLeftAction )
      self.textAlignGroup.addAction( self.textAlignRightAction )
      self.textAlignGroup.addAction( self.textAlignCenterAction )
      self.textAlignGroup.addAction( self.textAlignFullAction )
      align = RES.get( 'ArticleView', 'align' )
      if align.upper() == 'RIGHT':
         self.textAlignRightAction.setChecked( True )
      elif align.upper() == 'CENTER':
         self.textAlignCenterAction.setChecked( True )
      elif align.upper() == 'FULL':
         self.textAlignFullAction.setChecked( True )
      else:
         self.textAlignLeftAction.setChecked( True )
      
      self.textInsertImageAction   = RES.installAction( 'textInsertImage', self )

   
   def _buildMenus( self ):
      self.menuArticle = QtGui.QMenu(self)
      self.menuArticle.setObjectName("menuArticle")
      self.menuArticle.setTitle(QtGui.QApplication.translate("MainWindow", "Article", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuArticle.addAction( self.articleCutAction )
      self.menuArticle.addAction( self.articleCopyAction )
      self.menuArticle.addAction( self.articlePasteAction )
      self.menuArticle.addSeparator()
      self.menuArticle.addAction( self.articleSelectAllAction )
      self.menuArticle.addSeparator()
      self.menuArticle.addAction( self.textInsertImageAction )
   
   def _buildToolbars( self ):
      self._articletoolbar = QtGui.QToolBar( 'articleEditingToolbar', self )
      self._articletoolbar.addAction( self.printAction )
      self._articletoolbar.addSeparator( )
      self._articletoolbar.addAction( self.articleCutAction )
      self._articletoolbar.addAction( self.articleCopyAction )
      self._articletoolbar.addAction( self.articlePasteAction )
      self._articletoolbar.addSeparator( )
      self._articletoolbar.addAction( self.editUndoAction )
      self._articletoolbar.addAction( self.editRedoAction )
      
      self._styleToolbar = QtGui.QToolBar( 'textStyleToolbar', self )
      self._styleToolbar.addWidget( self._fontFamilyCombo )
      self._styleToolbar.addWidget( self._fontSizeCombo )
      self._styleToolbar.addSeparator( )
      self._styleToolbar.addAction( self.textBoldAction )
      self._styleToolbar.addAction( self.textItalicAction )
      self._styleToolbar.addAction( self.textUnderlineAction )
      self._styleToolbar.addAction( self.textOverstrikeAction )
      
      # Alignment
      self._styleToolbar.addSeparator( )
      self._styleToolbar.addAction( self.textAlignLeftAction )
      self._styleToolbar.addAction( self.textAlignRightAction )
      self._styleToolbar.addAction( self.textAlignCenterAction )
      self._styleToolbar.addAction( self.textAlignFullAction )
      
      # Superscript/Subscript
      
      # Line Spacing
      
      # Objects
      self._objectToolbar = QtGui.QToolBar( 'objectToolbar', self )
      self._objectToolbar.addSeparator( )
      self._objectToolbar.addAction( self.textInsertImageAction )

   def _cursorPositionChanged( self ):
      self._updateToolbars( )

class OutlineView(QtGui.QSplitter):
   '''Emits: QtCore.SIGNAL("modelChanged()")'''
   def __init__( self, parent ):
      QtGui.QSplitter.__init__( self, parent )
      
      self._outlineView            = None      # The TreeView widget
      self._articleView            = None      # The TextEdit widget
      self._model                  = None      # The model for the data
      self._resources              = { }
      self._currentArticleModified = False     # Has the article currently being edited been modified?
      
      self._buildGui( )

   def getFixedMenus( self ):
      menus = [ self.menuTree ]
      menus.extend( self._articleView.getFixedMenus() )
      return menus

   def getToolbars( self ):
      toolbars = [ self._treetoolbar ]
      toolbars.extend( self._articleView.getToolbars() )
      return toolbars
   
   # Basic Operations
   def setModel( self, modelData ):
      modelData[0].validate( )
      
      
      try:
         self._model, self._resources = modelData
         self.swappingArticle = False
         
         self._articleView.clear( )
         
         self._outlineView.setModel( self._model )
         self._articleView.setResources( self._resources )
         
         QtCore.QObject.connect( self._outlineView.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged )
         QtCore.QObject.connect( self._model, QtCore.SIGNAL( 'dataChanged(QModelIndex,QModelIndex)' ), self.onModelChanged )
         QtCore.QObject.connect( self._articleView, QtCore.SIGNAL( 'textChanged()' ), self.onArticleChanged )
      
      except:
         exceptionPopup( )
      
      indexOfFirst = self._model.index( 0, 0, QtCore.QModelIndex() )
      self.selectionChanged( indexOfFirst )

   def getModel( self ):
      return self._model, self._resources

   def commitChanges( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex( )
      
      if self._currentArticleModified:
         theDocument = self._articleView.document()
         
         if theDocument.isEmpty():
            article     = ''
         else:
            article     = unicode( theDocument.toHtml() )
         
         index.internalPointer().setArticle( article )

   def insertNode( self, newParentIndex, newRow, newNode=None ):
      try:
         self._model.insertNode( newParentIndex, newRow, newNode )
         self._outlineView.setCurrentIndex( self._model.index(newRow, 0, newParentIndex) )
         self.onModelChanged()
      except:
         exceptionPopup( )
   
   def deleteNode( self, index=None ):
      if index is None:
         index = self.currentIndex()
      
      try:
         self.model().removeNode( index )
         self.onModelChanged()
      except:
         exceptionPopup()

   def moveNode( self, index, newParentIndex, newRow ):
      try:
         self._model.moveNode( index, newParentIndex, newRow )
         self._outlineView.setCurrentIndex( self._model.index(newRow, 0, newParentIndex) )
         self.onModelChanged()
      except:
         exceptionPopup()

   def expandAll( self ):
      try:
         self._outlineView.expandAll( )
      except:
         exceptionPopup()

   def expandNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self._outlineView.expand( self._outlineView.currentIndex() )
      except:
         exceptionPopup()

   def collapseAll( self ):
      try:
         self._outlineView.collapseAll( )
      except:
         exceptionPopup()

   def collapseNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self._outlineView.collapse( self._outlineView.currentIndex() )
      except:
         exceptionPopup()

   # Advanced Operations (built on top of Basic Operations)
   def selectionChanged( self, newSelection, oldSelection=None ):
      # Save the currently active article
      self.swappingArticle = True
      
      if oldSelection:
         if isinstance( oldSelection, QtCore.QModelIndex ):
            index = oldSelection
         else:
            indexes = oldSelection.indexes()
            if indexes and (len(indexes) > 0):
               index = indexes[0]
            else:
               index = None
         
         if index:
            self.commitChanges( index )
      
      # Reinitialize the article widget
      self._articleView.clear( )
      
      # Display the newly selected article
      if newSelection:
         self._currentArticleModified = False
         if isinstance( newSelection, QtCore.QModelIndex ):
            index = newSelection
         else:
            indexes = newSelection.indexes()
            if indexes and (len(indexes) > 0):
               index = indexes[0]
            else:
               index = None
         
         if index:
            outlineNode = index.internalPointer( )
            
            if outlineNode is not None:
               self._articleView.setHtml( outlineNode.article() )
               self._articleView.setDocumentTitle( outlineNode.data(0) )
      
      self.swappingArticle = False

   def insertNodeBefore( self, index=None, node=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self.insertNode( index.parent(), index.row(), node )
      except:
         exceptionPopup()

   def insertNodeAfter( self, index=None, node=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self.insertNode( index.parent(), index.row() + 1, node )
      except:
         exceptionPopup()

   def insertNodeAsChild( self, index=None, node=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         self.insertNode( index, 0, node )
      except:
         exceptionPopup()

   def indentNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         theNodeRow = index.row()
         if theNodeRow == 0:
            return
         
         theNewParent = index.sibling( index.row() - 1, 0 )
         if len(theNewParent.internalPointer()._childNodes) == 0:
            self.moveNode( index, theNewParent, 0 )
      except:
         exceptionPopup()

   def dedentNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         if len(index.parent().internalPointer()._childNodes) != 1:
            return
         
         newParent = index.parent().parent()
         newRow    = index.parent().row() + 1
         self.moveNode( index, newParent, newRow )
      except:
         exceptionPopup()

   def moveNodeUp( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         theRow = index.row()
         if theRow == 0:
            return
         
         self.moveNode( index, index.parent(), theRow - 1 )
      except:
         exceptionPopup()

   def moveNodeDown( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         theRow = index.row()
         if theRow == (len(index.internalPointer()._parentNode._childNodes)-1):
            return
         
         self.moveNode( index, index.parent(), theRow + 1 )
      except:
         exceptionPopup()

   def cutNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         mimeObject = self._model.mimifyNode( index )
         
         try:
            QtGui.QApplication.clipboard().setMimeData( mimeObject )
         except:
            return
         
         self.deleteNode( index )
      except:
         exceptionPopup()

   def copyNode( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         mimeObject = self._model.mimifyNode( index )
         
         QtGui.QApplication.clipboard().setMimeData( mimeObject )
      
      except:
         exceptionPopup()
   
   def pasteNodeBefore( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         mimeObject = QtGui.QApplication.clipboard().mimeData()
         if not mimeObject.hasFormat( RES.get('OutlineView','nodeMimeType') ):
            return
         
         node = self._model.demimifyNode( mimeObject )
         self.insertNodeBefore( index, node )
      except:
         exceptionPopup( )

   def pasteNodeAfter( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         mimeObject = QtGui.QApplication.clipboard().mimeData()
         if not mimeObject.hasFormat( RES.get('OutlineView','nodeMimeType') ):
            return
         
         node = self._model.demimifyNode( mimeObject )
         self.insertNodeAfter( index, node )
      except:
         exceptionPopup( )
   
   def pasteNodeAsChild( self, index=None ):
      if index is None:
         index = self._outlineView.currentIndex()
      
      try:
         mimeObject = QtGui.QApplication.clipboard().mimeData()
         if not mimeObject.hasFormat( RES.get('OutlineView','nodeMimeType') ):
            return
         
         node = self._model.demimifyNode( mimeObject )
         self.insertNodeAsChild( index, node )
      except:
         exceptionPopup( )
   
   # Slots
   def onArticleChanged( self ):
      if not self.swappingArticle:
         self._currentArticleModified = True
         self.onModelChanged( )

   def onModelChanged( self, index1=None, index2=None ):
      self.emit( QtCore.SIGNAL('modelChanged()') )

   def entryRightClicked( self, point, index ):
      self._outlineView.setCurrentIndex( index )
      self.menuTree.popup(point)

   # GUI Construction
   def _buildGui( self ):
      self._buildWidgets( )
      
      self._defineActions( )
      
      self._buildMenus( )
      self._buildToolbars( )

   def _buildWidgets( self ):
      outlineFont = RES.getFont( 'OutlineView', 'Font' )
      
      self._outlineView = OutlineViewWidget(self)
      self._outlineView.setObjectName("outlineView")
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 0 )
      self._outlineView.setSizePolicy(sizePolicy)
      self._outlineView.setMinimumSize(QtCore.QSize(100, 100))
      self._outlineView.setSizeIncrement(QtCore.QSize(1, 1))
      self._outlineView.setFont( outlineFont )
      
      self._articleView = ArticleViewWidget(self)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 1 )
      self._articleView.setSizePolicy(sizePolicy)
      self._articleView.setMinimumSize(QtCore.QSize(100, 100))
      self._articleView.setObjectName("articleView")
      
      QtCore.QObject.connect( self._outlineView, QtCore.SIGNAL('entryRightClicked(QPoint,QModelIndex)'), self.entryRightClicked )

   def _defineActions( self ):
      self.cutNodeAction             = RES.installAction( 'cutNode',           self )
      self.copyNodeAction            = RES.installAction( 'copyNode',          self )
      self.pasteNodeBeforeAction     = RES.installAction( 'pasteNodeBefore',   self )
      self.pasteNodeAfterAction      = RES.installAction( 'pasteNodeAfter',    self )
      self.pasteNodeAsChildAction    = RES.installAction( 'pasteNodeAsChild',  self )
      self.expandAllAction           = RES.installAction( 'expandAll',         self )
      self.collapseAllAction         = RES.installAction( 'collapseAll',       self )
      self.expandNodeAction          = RES.installAction( 'expandNode',        self )
      self.collapseNodeAction        = RES.installAction( 'collapseNode',      self )
      self.moveNodeUpAction          = RES.installAction( 'moveNodeUp',        self )
      self.moveNodeDownAction        = RES.installAction( 'moveNodeDown',      self )
      self.indentNodeAction          = RES.installAction( 'indentNode',        self )
      self.dedentNodeAction          = RES.installAction( 'dedentNode',        self )
      self.insertNewNodeBeforeAction = RES.installAction( 'insertNodeBefore',  self )
      self.insertNewNodeAfterAction  = RES.installAction( 'insertNodeAfter',   self )
      self.insertNewChildAction      = RES.installAction( 'insertNodeAsChild', self )
      self.deleteNodeAction          = RES.installAction( 'deleteNode',        self )

   def _buildMenus( self ):
      self.menuTree = QtGui.QMenu(self)
      self.menuTree.setObjectName("menuTree")
      self.menuTree.setTitle(QtGui.QApplication.translate("MainWindow", "Tree", None, QtGui.QApplication.UnicodeUTF8))
      
      self.menuTree.addAction( self.cutNodeAction )
      self.menuTree.addAction( self.copyNodeAction )
      self.menuTree.addAction( self.pasteNodeBeforeAction )
      self.menuTree.addAction( self.pasteNodeAfterAction )
      self.menuTree.addAction( self.pasteNodeAsChildAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self.expandAllAction )
      self.menuTree.addAction( self.collapseAllAction )
      self.menuTree.addAction( self.expandNodeAction )
      self.menuTree.addAction( self.collapseNodeAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self.insertNewNodeBeforeAction )
      self.menuTree.addAction( self.insertNewNodeAfterAction )
      self.menuTree.addAction( self.insertNewChildAction )
      self.menuTree.addAction( self.deleteNodeAction )
      self.menuTree.addSeparator()
      self.menuTree.addAction( self.indentNodeAction )
      self.menuTree.addAction( self.dedentNodeAction )
      self.menuTree.addAction( self.moveNodeUpAction )
      self.menuTree.addAction( self.moveNodeDownAction )

   def _buildToolbars( self ):
      self._treetoolbar = QtGui.QToolBar( 'treeToolbar', self )
      self._treetoolbar.addAction( self.expandAllAction )
      self._treetoolbar.addAction( self.collapseAllAction )
