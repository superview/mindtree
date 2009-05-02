from __future__ import print_function, unicode_literals
from PyQt4 import QtCore, QtGui

from OutlineModel import OutlineModel, TreeNode
from MindTreeApplicationFramework import *


class TreeView_Delegate( QtGui.QItemDelegate ):
   def __init__( self, parent ):
      QtGui.QItemDelegate.__init__( self, parent )
   
   def createEditor( self, parent, option, index ):
      editor = QtGui.QItemDelegate.createEditor( self, parent, option, index )
      editor.installEventFilter( self.parent() )
      return editor
   
   def setEditorData( self, editor, index ):
      text = unicode( index.data().toString() )
      editor.setText( text )
   
   def setModelData( self, editor, model, index ):
      model.setData( index, editor.text(), QtCore.Qt.DisplayRole )
   

class TreeView( QtGui.QTreeView ):
   '''Emits: entryRightClicked(QPoint,QModelIndex),
             dragBegun(QModelIndex)
   '''
   def __init__( self, parent ):
      QtGui.QTreeView.__init__( self, parent )
      
      alternatingRowColors = RES.getboolean('OutlineEdit','alternatingRowColors')
      
      # Drag and Drop
      self.setDragEnabled(True)
      self.setAcceptDrops(True)
      self.setDropIndicatorShown(True)
      self.setDragDropMode( QtGui.QAbstractItemView.InternalMove )
      
      # Entry Editing
      self.setItemDelegate( TreeView_Delegate(self) )
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
      self.setAllColumnsShowFocus(True)
      
      # Drag and Drop Cursors
      self.insertBefore_cursor  = RES.getDragCursor('OutlineEdit','DnD_insertBeforeCursor')
      self.insertAfter_cursor   = RES.getDragCursor('OutlineEdit','DnD_insertAfterCursor')
      self.insertChild_cursor   = RES.getDragCursor('OutlineEdit','DnD_insertChildCursor')

   def invalidate( self, index ):
      region = QtGui.QRegion( self.visualRect( index ) )
      self.setDirtyRegion( region )

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
      
      self.emit( QtCore.SIGNAL('dragBegun(QModelIndex)'),dragStartIndex )
      
      # Execute the drag (this is blocking)
      savedDragIndex = QtCore.QPersistentModelIndex( dragStartIndex )  # Save the drag start index
      dropAction = self.drag.exec_( QtCore.Qt.MoveAction )             # Perform the drag
      dragStartIndex = QtCore.QModelIndex(savedDragIndex)              # Retrieve the drag start index
      
      # If the drag was successful, remove the node
      if dropAction == QtCore.Qt.MoveAction:
         self.model().removeNode( dragStartIndex )

   def dragMoveEvent( self, event ):
      index,relation = self._dnd_insertionPos( event )
      self.setCurrentIndex( index )
      self.setSelection( QtCore.QRect( event.pos(), event.pos() ), QtGui.QItemSelectionModel.ClearAndSelect )
      self._selectCursor( relation )

   def dragEnterEvent( self, event ):
      if event.mimeData().hasFormat( RES.get('Mime','mindTreeOutline') ):
         event.acceptProposedAction( )

   def dragLeaveEvent( self, event ):
      self.setState( QtGui.QAbstractItemView.NoState )

   def dropEvent( self, event ):
      if event.source() is self:
         if event.possibleActions() & QtCore.Qt.MoveAction:
            event.acceptProposedAction()
            
            # Determine the drop location
            point = event.pos()
            index = self.indexAt( point )
            
            newParent = index.parent()
            if newParent is None:
               newParent = QtCore.QModelIndex()
            
            newRow = index.row()
            
            # Extract the node
            mimeData = event.mimeData()
            if not mimeData.hasFormat( RES.get('Mime','mindTreeOutline') ):
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
         if mousePos.x() >= rectOfEntryUnderMouse.x() + RES.getint('OutlineEdit','DnD_siblingChildBound'):
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
      self.drag.setDragCursor( cursor[0], QtCore.Qt.MoveAction )
      self.drag.setHotSpot( cursor[1] )
      #self.setCursor( cursor )
      #QtGui.QApplication.setOverrideCursor( cursor )


class ArticleView( QtGui.QTextEdit ):
   ImageFormats   = 'Windows bitmap (*.bmp);;Graphic Interchange Format (*.gif);;Joint Photographic Experts Group (*.jpg);;Portable Network Graphics (*.png);;Tagged Image File Format (*.tif *.tiff);;All Files (*.*)'
   FONT_SIZE_STRS = [ str(x) for x in (8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72) ]
   
   def __init__( self, parent ):
      QtGui.QTextEdit.__init__( self, parent )
      self._project     = None
      self._outlineNode = None
      self._specialSelections = { }
      
      self._buildGui( )
      self._updateToolbars( )

   def setModified( self, modified ):
      self.document().setModified( modified )
   
   def isModified( self ):
      return self.document().isModified()

   # Slots
   def addImageResourceToArticleWidget( self, resName ):
      IMAGE_DIR = RES.get('Project','imageDir')
      url = '{0}/{1}'.format( IMAGE_DIR, resName )
      
      resType = QtGui.QTextDocument.ImageResource
      resObj = QtCore.QVariant(QtGui.QImage(url))
      self.document().addResource( resType, QtCore.QUrl(url), resObj )
      
      return url

   def setProject( self, aProject ):
      self._project = aProject

   def setOutlineNode( self, anOutlineNode ):
      self._outlineNode = anOutlineNode
      
      # Install the image resources
      for name in anOutlineNode.imageList():
         self.addImageResourceToArticleWidget( name )
      
      # Install the article text
      self.setHtml( anOutlineNode.article() )
      self.setDocumentTitle( anOutlineNode.data(0) )
   
   def getFixedMenus( self ):
      return [ self.menuArticle ]
   
   def getToolbars( self ):
      return { 'Article Edit':self._articletoolbar,
               'Text Align':self._alignToolbar,
               'Article Text Style':self._styleToolbar,
               'Insert Object':self._objectToolbar }
   
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
   
   def textStyleSuperscript( self ):
      cursor = self.textCursor( )
      selectedText = cursor.selectedText( )
      
      if selectedText == '':
         return
      
      cursor.insertHtml( '<SUP>{0}</SUP>'.format(selectedText) )
   
   def textStyleSubscript( self ):
      cursor = self.textCursor( )
      selectedText = cursor.selectedText( )
      
      if selectedText == '':
         return
      
      cursor.insertHtml( u'<SUB>{0}</SUB>'.format(selectedText) )
   
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

   def textAlignOffset( self ):
      cursor = self.textCursor( )
      cursor.insertList( QtGui.QTextListFormat.ListDisc )
      
      backSpaceEvent = QtGui.QKeyEvent( QtCore.QEvent.KeyPress, QtCore.Qt.Key_Backspace, QtCore.Qt.NoModifier )
      self.keyPressEvent( backSpaceEvent )
   
   def textInsertImage( self ):
      IMAGE_DIR = RES.get( 'Project','imageDir' )
      
      dlg = QtGui.QFileDialog( self, 'Insert image...', '', ArticleView.ImageFormats )
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
      
      resName = name + ext
      
      self._outlineNode.imageList().append( resName )
      url = self.addImageResourceToArticleWidget( resName )
      
      self.textCursor().insertHtml( '<img src="{0}"/>'.format(url) )

   def textInsertLink( self ):
      title  = RES.get('ArticleView','createLinkDlgTitle',translate=True)
      prompt = RES.get('ArticleView','createLinkDlgPrompt',translate=True)
      error   = RES.get('ArticleView','createLink_warnNoSelect',translate=True)
      
      cursor = self.textCursor( )
      selectedText = cursor.selectedText( )
      if selectedText == '':
         QtGui.QMessageBox.information( self, title,error )
         return
      
      result,pressedOK = QtGui.QInputDialog.getText( self, title, prompt )
      if not pressedOK:
         return
      
      url = unicode(result)
      
      cursor.insertHtml( '<A HREF="{0}">{1}</A>'.format(url, selectedText) )
   
   def textEditLink( self ):
      title  = RES.get('ArticleView','editLinkDlgTitle',translate=True)
      prompt = RES.get('ArticleView','createLinkDlgPrompt',translate=True)
      error   = RES.get('ArticleView','createLink_warnNoSelect',translate=True)
      
      cursor = self.textCursor( )
      format = cursor.charFormat( )
      url    = format.anchorHref( )
      
      if url == '':
         return
      
      newUrl,pressedOK = QtGui.QInputDialog.getText( self, title, prompt, QtGui.QLineEdit.Normal, url )
      if not pressedOK:
         return
      
      #newUrl = unicode(newUrl)
      #format.setAnchorHref( newUrl )

   def textInsertList( self ):
      cursor = self.textCursor( )
      cursor.insertList( QtGui.QTextListFormat.ListDisc )

   def textInsertTable( self ):
      cursor = self.textCursor( )
      cursor.insertTable( 2, 2 )

   def _updateToolbars( self ):
      # Font Combo
      fontFamily = unicode(self.currentFont().family())
      font = QtGui.QFont( fontFamily )
      self._fontFamilyCombo.setCurrentFont( font )
      
      # Font Size
      size = int(self.fontPointSize())
      if size != 0:
         index = ArticleView.FONT_SIZE_STRS.index( unicode(size) )
         self._fontSizeCombo.setCurrentIndex( index )
      
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
   
   def listChangeBulletStyle( self ):
      cursor = self.textCursor( )
      theList = cursor.currentList( )
      
      if theList:
         theListFormat = theList.format( )
         theCurrentStyle = theListFormat.style( )
         
         styles = { QtGui.QTextListFormat.ListDisc:      'Disc',
                    QtGui.QTextListFormat.ListCircle:    'Circle',
                    QtGui.QTextListFormat.ListSquare:    'Square',
                    QtGui.QTextListFormat.ListDecimal:   'Number',
                    QtGui.QTextListFormat.ListLowerAlpha:'Alpha (lower)',
                    QtGui.QTextListFormat.ListUpperAlpha:'Alpha (upper)' 
                    }
         
         styleNums  = styles.keys()
         styleNames = styles.values()
         
         currentStyleNum = styleNums.index( theCurrentStyle )
         
         selectedStyle, ok = QtGui.QInputDialog.getItem( self, 'Bullet Style', 'Bullet style', styleNames, currentStyleNum, False )
         
         if not ok:
            return
         
         styleIndex = styleNames.index( selectedStyle )
         newStyle = styleNums[ styleIndex ]
         
         theListFormat.setStyle( newStyle )
         theList.setFormat( theListFormat )
   
   def listIndentIncrease( self ):
      cursor = self.textCursor( )
      theList = cursor.currentList( )
      
      if theList:
         theListFormat = theList.format( )
         indent = theListFormat.indent( )
         theListFormat.setIndent( indent + 1 )
         theList.setFormat( theListFormat )
   
   def listIndentDecrease( self ):
      cursor = self.textCursor( )
      theList = cursor.currentList( )
      
      if theList:
         theListFormat = theList.format( )
         indent = theListFormat.indent( )
         if indent == 0:
            return
         
         theListFormat.setIndent( indent - 1 )
         theList.setFormat( theListFormat )
   
   def tableRowInsert( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         tableCell = theTable.cellAt( cursor )
         theTable.insertRows( tableCell.row(), 1 )
   
   def tableRowDelete( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         tableCell = theTable.cellAt( cursor )
         theTable.removeRows( tableCell.row(), 1 )
   
   def tableColumnInsert( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         tableCell = theTable.cellAt( cursor )
         theTable.insertColumns( tableCell.column(), 1 )
   
   def tableColumnDelete( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         tableCell = theTable.cellAt( cursor )
         theTable.removeColumns( tableCell.column(), 1 )

   def _tableCellInfo( self, table, position ):
      theTableCell = table.cellAt( position )
      
      row        = theTableCell.row( )
      rowSpan    = theTableCell.rowSpan( )
      
      column     = theTableCell.column( )
      columnSpan = theTableCell.columnSpan( )
      
      return row, column, rowSpan, columnSpan
   
   def tableCellMergeRight( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         cursorPos = cursor.position()
         row,col,rowSpan,colSpan = self._tableCellInfo( theTable, cursorPos )
         
         theTable.mergeCells( row, col, rowSpan, colSpan + 1 )
   
   def tableCellSplitRight( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         cursorPos = cursor.position()
         row,col,rowSpan,colSpan = self._tableCellInfo( theTable, cursorPos )
         
         if colSpan > 1:
            theTable.splitCell( row, col, rowSpan, colSpan - 1 )
   
   def tableCellMergeDown( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         cursorPos = cursor.position()
         row,col,rowSpan,colSpan = self._tableCellInfo( theTable, cursorPos )
         
         theTable.mergeCells( row, col, rowSpan + 1, colSpan )
   
   def tableCellSplitDown( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         cursorPos = cursor.position()
         row,col,rowSpan,colSpan = self._tableCellInfo( theTable, cursorPos )
         
         if rowSpan > 1:
            theTable.splitCell( row, col, rowSpan - 1, colSpan )
   
   def tableHeaderRowAdd( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         theTableFormat = theTable.format()
         numHeaderRows = theTableFormat.headerRowCount( )
         theTableFormat.setHeaderRowCount( numHeaderRows + 1 )
         theTable.setFormat( theTableFormat )
   
   def tableHeaderRowRem( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         theTableFormat = theTable.format()
         numHeaderRows = theTableFormat.headerRowCount( )
         
         if numHeaderRows == 0:
            return
         
         theTableFormat.setHeaderRowCount( numHeaderRows - 1 )
         theTable.setFormat( theTableFormat )
   
   def tableCellAlign( self ):
      cursor = self.textCursor( )
      theTable = cursor.currentTable( )
      
      if theTable:
         cursorPos = cursor.position()
         
         alignList = [ 'Center', 'North', 'North East', 'North West', 'West', 'East', 'South', 'South West', 'South East' ]
         
         selectedStyle, ok = QtGui.QInputDialog.getItem( self, 'Cell Alignment', 'align', alignList, 0, False )
         
         if not ok:
            return
         
         if selectedStyle == 'Center':
            align = QtCore.Qt.AlignHCenter + QtCore.Qt.AlignVCenter
         elif selectedStyle == 'North':
            align = QtCore.Qt.AlignHCenter + QtCore.Qt.AlignTop
         elif selectedStyle == 'North West':
            align = QtCore.Qt.AlignLeft + QtCore.Qt.AlignTop
         elif selectedStyle == 'North East':
            align = QtCore.Qt.AlignRight + QtCore.Qt.AlignTop
         elif selectedStyle == 'West':
            align = QtCore.Qt.AlignLeft + QtCore.Qt.AlignVCenter
         elif selectedStyle == 'East':
            align = QtCore.Qt.AlignRight + QtCore.Qt.AlignVCenter
         elif selectedStyle == 'South':
            align = QtCore.Qt.AlignHCenter + QtCore.Qt.AlignBottom
         elif selectedStyle == 'South West':
            align = QtCore.Qt.AlignLeft + QtCore.Qt.AlignBottom
         elif selectedStyle == 'South East':
            align = QtCore.Qt.AlignRight + QtCore.Qt.AlignBottom
         
         
   
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
      
      self._fontSizeCombo.addItems( ArticleView.FONT_SIZE_STRS )
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
      
      self.textSuperscriptAction     = RES.installAction( 'textStyleSuperscript', self )
      self.textSubscriptAction       = RES.installAction( 'textStyleSubscript',   self )
      
      self.textAlignLeftAction       = RES.installAction( 'textAlignLeft',        self )
      self.textAlignRightAction      = RES.installAction( 'textAlignRight',       self )
      self.textAlignCenterAction     = RES.installAction( 'textAlignCenter',      self )
      self.textAlignFullAction       = RES.installAction( 'textAlignFull',        self )
      self.textAlignOffsetAction     = RES.installAction( 'textAlignOffset',      self )
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
      self.textInsertLinkAction    = RES.installAction( 'textInsertLink',  self )
      self.textEditLinkAction      = RES.installAction( 'textEditLink',    self )
      self.textInsertListAction    = RES.installAction( 'textInsertList',  self )
      self.textInsertTableAction   = RES.installAction( 'textInsertTable', self )
      
      # List Specific Actions
      self.listChangeBulletStyleAction = RES.installAction( 'listChangeBulletStyle', self )
      self.listIndentIncreaseAction= RES.installAction( 'listIndentIncrease', self )
      self.listIndentDecreaseAction= RES.installAction( 'listIndentDecrease', self )
      
      # Table Specific Actions
      self.tableRowInsertAction    = RES.installAction( 'tableRowInsert',    self )
      self.tableRowDeleteAction    = RES.installAction( 'tableRowDelete',    self )
      self.tableColumnInsertAction = RES.installAction( 'tableColumnInsert', self )
      self.tableColumnDeleteAction = RES.installAction( 'tableColumnDelete', self )
      
      self.tableCellMergeLeftAction = RES.installAction( 'tableCellMergeRight',  self )
      self.tableCellSplitLeftAction = RES.installAction( 'tableCellSplitRight',  self )
      self.tableCellMergeDownAction = RES.installAction( 'tableCellMergeDown', self )
      self.tableCellSplitDownAction = RES.installAction( 'tableCellSplitDown', self )
      
      self.tableHeaderRowAddAction  = RES.installAction( 'tableHeaderRowAdd', self )
      self.tableHeaderRowRemAction  = RES.installAction( 'tableHeaderRowRem', self )
      
      self.tableCellAlignAction     = RES.installAction( 'tableCellAlign', self )

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
      self.menuArticle.addAction( self.textInsertListAction )
      self.menuArticle.addAction( self.textInsertTableAction )
   
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
      self._styleToolbar.addSeparator( )
      self._styleToolbar.addAction( self.textSuperscriptAction )
      self._styleToolbar.addAction( self.textSubscriptAction )
      
      # Alignment
      self._alignToolbar = QtGui.QToolBar( 'articleAlignToolbar', self )
      self._alignToolbar.addAction( self.textAlignLeftAction )
      self._alignToolbar.addAction( self.textAlignRightAction )
      self._alignToolbar.addAction( self.textAlignCenterAction )
      self._alignToolbar.addAction( self.textAlignFullAction )
      self._alignToolbar.addAction( self.textAlignOffsetAction )
      
      # Line Spacing
      
      # Objects
      self._objectToolbar = QtGui.QToolBar( 'objectToolbar', self )
      self._objectToolbar.addSeparator( )
      self._objectToolbar.addAction( self.textInsertListAction )
      self._objectToolbar.addAction( self.textInsertTableAction )
      self._objectToolbar.addAction( self.textInsertImageAction )
      self._objectToolbar.addAction( self.textInsertLinkAction  )

   def _cursorPositionChanged( self ):
      self._updateToolbars( )
   
   def contextMenuEvent( self, event ):
      menu = self.createStandardContextMenu( )
      
      menu.addSeparator( )
      menu.addAction( self.textEditLinkAction )
      menu.addSeparator( )
      menu.addAction( self.listChangeBulletStyleAction )
      menu.addAction( self.listIndentIncreaseAction )
      menu.addAction( self.listIndentDecreaseAction )
      menu.addSeparator( )
      menu.addAction( self.tableRowInsertAction )
      menu.addAction( self.tableRowDeleteAction )
      menu.addAction( self.tableColumnInsertAction )
      menu.addAction( self.tableColumnDeleteAction )
      menu.addSeparator( )
      menu.addAction( self.tableCellMergeLeftAction )
      menu.addAction( self.tableCellSplitLeftAction )
      menu.addAction( self.tableCellMergeDownAction )
      menu.addAction( self.tableCellSplitDownAction )
      menu.addSeparator( )
      menu.addAction( self.tableHeaderRowAddAction )
      menu.addAction( self.tableHeaderRowRemAction )
      menu.addSeparator( )
      menu.addAction( self.tableCellAlignAction )
      
      menu.exec_( event.globalPos() )
      
      del menu
   

class OutlineEdit(QtGui.QSplitter):
   '''Emits: QtCore.SIGNAL("modelChanged()")   -- the model has been modified.
             QtCore.SIGNAL("newProject()")     -- a new project is being edited.
   '''
   def __init__( self, parent ):
      QtGui.QSplitter.__init__( self, parent )
      
      self._project     = None
      self._model       = None      # The model for the data
      self._treeView    = None      # The TreeView widget
      self._articleView = None      # The TextEdit widget
      
      self._buildGui( )
      
      self.setProject( MindTreeProject( ) )

   def getFixedMenus( self ):
      menus = [ self.menuTree ]
      menus.extend( self._articleView.getFixedMenus() )
      return menus

   def getToolbars( self ):
      toolbars = { 'Tree Toolbar':self._treetoolbar }
      toolbars.update( self._articleView.getToolbars() )
      return toolbars

   # Subwidget Access (mainly used by pluggable tools
   def outlineWidget( self ):
      return self._treeView

   def articleWidget( self ):
      return self._articleView

   # Basic Operations
   def invalidate( self, index=None ):
      '''Force the outline tree redraw the entry.'''
      if index is None:
         index = self._treeView.currentIndex()
      
      self._treeView.invalidate( index )
   
   def setProject( self, aProject ):
      self.swappingArticle = True
      
      try:
         self._project = aProject
         self._model   = aProject.outline()
         
         self._articleView.clear( )
         
         self._treeView.setModel( self._model )
         self._treeView.resizeColumnToContents( 0 )
         self._articleView.setProject( aProject )
         
         QtCore.QObject.connect( self._treeView.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged )
         QtCore.QObject.connect( self._model, QtCore.SIGNAL( 'dataChanged(QModelIndex,QModelIndex)' ), self.onModelChanged )
         QtCore.QObject.connect( self._articleView, QtCore.SIGNAL( 'textChanged()' ), self.onArticleChanged )
      
      except:
         exceptionPopup( )
      
      indexOfFirst = self._model.index( 0, 0, QtCore.QModelIndex() )
      self._treeView.setCurrentIndex( indexOfFirst )
      
      self.emit( QtCore.SIGNAL('newProject()') )
      self.swappingArticle = False

   def commitChanges( self, index=None ):
      if index is None:
         index = self._treeView.currentIndex( )
      
      if self._articleView.isModified():
         theDocument = self._articleView.document()
         
         if theDocument.isEmpty():
            article     = ''
         else:
            article     = unicode( theDocument.toHtml() )
         
         index.internalPointer().setArticle( article )

   def insertNode( self, newParentIndex, newRow, newNode=None ):
      try:
         self._model.insertNode( newParentIndex, newRow, newNode )
         self._treeView.setCurrentIndex( self._model.index(newRow, 0, newParentIndex) )
         self.onModelChanged()
      except:
         exceptionPopup( )
   
   def deleteNode( self, index=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
      try:
         if not self._treeView.model().removeNode( index ):
            return
         
         self.onModelChanged()
      except:
         exceptionPopup()

   def moveNode( self, index, newParentIndex, newRow ):
      try:
         self._model.moveNode( index, newParentIndex, newRow )
         self._treeView.setCurrentIndex( self._model.index(newRow, 0, newParentIndex) )
         self.onModelChanged()
      except:
         exceptionPopup()

   def expandAll( self ):
      try:
         self._treeView.expandAll( )
      except:
         exceptionPopup()

   def expandNode( self, index=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
      try:
         self._treeView.expand( self._treeView.currentIndex() )
      except:
         exceptionPopup()

   def collapseAll( self ):
      try:
         self._treeView.collapseAll( )
      except:
         exceptionPopup()

   def collapseNode( self, index=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
      try:
         self._treeView.collapse( self._treeView.currentIndex() )
      except:
         exceptionPopup()

   # Advanced Operations (built on top of Basic Operations)
   def selectionChanged( self, newSelection, oldSelection=None ):
      self.swappingArticle = True
      
      # Commit active article
      if oldSelection:
         # Get the index of the selection
         indexes = oldSelection.indexes()
         if indexes and (len(indexes) > 0):
            index = indexes[0]
         else:
            index = None
         
         if index:
            self.commitChanges( index )
            
            if index.column() == 1:
               node = index.internalPointer()
               bookmarkDict = self._project.bookmarks()
               bookmarkDict[ node.bookmark() ] = node.id()
      
      # Reinitialize the article widget
      self._articleView.clear( )
      
      # Display the newly selected article
      newIndex = self._treeView.currentIndex()
      self._articleView.setModified( False )
      
      if newIndex:
         outlineNode = newIndex.internalPointer( )
         
         if outlineNode is not None:
            self._articleView.setOutlineNode( outlineNode )
      
      self.swappingArticle = False

   def insertNodeBefore( self, index=None, node=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
      try:
         self.insertNode( index.parent(), index.row(), node )
      except:
         exceptionPopup()

   def insertNodeAfter( self, index=None, node=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
      try:
         self.insertNode( index.parent(), index.row() + 1, node )
      except:
         exceptionPopup()

   def insertNodeAsChild( self, index=None, node=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
      try:
         self.insertNode( index, 0, node )
      except:
         exceptionPopup()

   def indentNode( self, index=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
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
         index = self._treeView.currentIndex()
      
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
         index = self._treeView.currentIndex()
      
      try:
         theRow = index.row()
         if theRow == 0:
            return
         
         self.moveNode( index, index.parent(), theRow - 1 )
      except:
         exceptionPopup()

   def moveNodeDown( self, index=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
      try:
         theRow = index.row()
         if theRow == (len(index.internalPointer()._parentNode._childNodes)-1):
            return
         
         self.moveNode( index, index.parent(), theRow + 1 )
      except:
         exceptionPopup()

   def cutNode( self, index=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
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
         index = self._treeView.currentIndex()
      
      try:
         mimeObject = self._model.mimifyNode( index )
         
         QtGui.QApplication.clipboard().setMimeData( mimeObject )
      
      except:
         exceptionPopup()
   
   def pasteNodeBefore( self, index=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
      try:
         mimeObject = QtGui.QApplication.clipboard().mimeData()
         if not mimeObject.hasFormat( RES.get('Mime','mindTreeOutline') ):
            return
         
         node = self._model.demimifyNode( mimeObject )
         self.insertNodeBefore( index, node )
      except:
         exceptionPopup( )

   def pasteNodeAfter( self, index=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
      try:
         mimeObject = QtGui.QApplication.clipboard().mimeData()
         if not mimeObject.hasFormat( RES.get('Mime','mindTreeOutline') ):
            return
         
         node = self._model.demimifyNode( mimeObject )
         self.insertNodeAfter( index, node )
      except:
         exceptionPopup( )
   
   def pasteNodeAsChild( self, index=None ):
      if index is None:
         index = self._treeView.currentIndex()
      
      try:
         mimeObject = QtGui.QApplication.clipboard().mimeData()
         if not mimeObject.hasFormat( RES.get('Mime','mindTreeOutline') ):
            return
         
         node = self._model.demimifyNode( mimeObject )
         self.insertNodeAsChild( index, node )
      except:
         exceptionPopup( )

   #def nodeBookmark( self ):
      ## get bookmark name and node and bookmarkDictionary
      #title = RES.get('OutlineEdit','createBookmarkDlgTitle',translate=True)
      #prompt = RES.get('OutlineEdit','createBookmarkDlgPrompt',translate=True)
      
      #result,pressedOK = QtGui.QInputDialog.getText( self, title, prompt )
      #if not pressedOK:
         #return
      
      #name = unicode(result)
      #node = self._treeView.currentIndex().internalPointer()
      #bookmarkDict = self._project.bookmarks()
      
      ## Verify that the node isn't already bookmarked
      #if (name in bookmarkDict) and (node.id() != bookmarkDict[name]):
         #QtGui.QMessageBox.critical( self, 'Error', 'Bookmark name \'{0}\' is already in use.' )
         #return
      
      ## Register the bookmark
      #node.setBookmarkName( name )
      #bookmarkDict[ name ] = node.id()
      
      ## Update the tree's drawing of the current entry
      #self.invalidate( )
   
   # Slots
   def onArticleChanged( self ):
      if not self.swappingArticle:
         self.onModelChanged( )

   def onModelChanged( self, index1=None, index2=None ):
      self.emit( QtCore.SIGNAL('modelChanged()') )

   def entryRightClicked( self, point, index ):
      self._treeView.setCurrentIndex( index )
      self.menuTree.popup(point)

   # GUI Construction
   def _buildGui( self ):
      self._buildWidgets( )
      
      self._defineActions( )
      
      self._buildMenus( )
      self._buildToolbars( )

   def _buildWidgets( self ):
      outlineFont = RES.getFont( 'OutlineEdit', 'Font' )
      
      self._treeView = TreeView(self)
      self._treeView.setObjectName("outlineView")
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 0 )
      self._treeView.setSizePolicy(sizePolicy)
      self._treeView.setMinimumSize(QtCore.QSize(100, 100))
      self._treeView.setSizeIncrement(QtCore.QSize(1, 1))
      self._treeView.setFont( outlineFont )
      
      self._articleView = ArticleView(self)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      sizePolicy.setVerticalStretch( 1 )
      sizePolicy.setHorizontalStretch( 1 )
      self._articleView.setSizePolicy(sizePolicy)
      self._articleView.setMinimumSize(QtCore.QSize(100, 100))
      self._articleView.setObjectName("articleView")
      
      QtCore.QObject.connect( self._treeView, QtCore.SIGNAL('entryRightClicked(QPoint,QModelIndex)'), self.entryRightClicked )
      QtCore.QObject.connect( self._treeView, QtCore.SIGNAL('dragBegun(QModelIndex)'), self.commitChanges ) 

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
      #self.bookmarkEntryAction       = RES.installAction( 'nodeBookmark',      self )

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
      #self._treetoolbar.addAction( self.bookmarkEntryAction )
