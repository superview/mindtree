import tkSimpleDialog
import Tix
from StyledText import StyledText, Style, Font
from TkTools import Toolbar, Toolset
import tkFont
from ObjectText import *


DIALOG_FONT       = 'Times 8'

class StylingControl( object ):
   def __init__( self ):
      self._state             = 'normal'
      
      self._currentStyleName  = Tix.StringVar( value='' )
      
      self._fontFamily        = Tix.StringVar( )
      self._fontSize          = Tix.StringVar( )
      self._bold              = Tix.BooleanVar( )
      self._italic            = Tix.BooleanVar( )
      self._underline         = Tix.BooleanVar( )
      self._overstrike        = Tix.BooleanVar( )
      self._foreground        = Tix.StringVar( value='black' )
      self._background        = Tix.StringVar( )
      self._offset            = Tix.StringVar( )
      self._fgstipple         = Tix.StringVar( )
      self._bgstipple         = Tix.StringVar( )
      self._borderwidth       = Tix.StringVar( )
      self._relief            = Tix.StringVar( )
      self._justify           = Tix.StringVar( )
      self._wrap              = Tix.StringVar( )
      self._lmargin1          = Tix.StringVar( )
      self._lmargin2          = Tix.StringVar( )
      self._rmargin           = Tix.StringVar( )
      self._spacing1          = Tix.StringVar( )
      self._spacing2          = Tix.StringVar( )
      self._spacing3          = Tix.StringVar( )
      self._tabs              = Tix.StringVar( )
      
      self._fgColorButton         = None
      self._bgColorButton         = None
      self._styleNameListWidget   = None

   def updateVariables( self, styleOrDict, currentStyleName=None ):
      self.setControlState( 'disabled' )
      
      self._fontFamily.set(  styleOrDict['family']           )
      self._fontSize.set(    str(styleOrDict['size'])        )
      self._bold.set(        bool(styleOrDict['bold'])       )
      self._italic.set(      bool(styleOrDict['italic'])     )
      self._underline.set(   bool(styleOrDict['underline'])  )
      self._overstrike.set(  bool(styleOrDict['overstrike']) )
      self._offset.set(      styleOrDict['offset']           )
      self._fgstipple.set(   styleOrDict['fgstipple']        )
      self._bgstipple.set(   styleOrDict['bgstipple']        )
      self._borderwidth.set( styleOrDict['borderwidth']      )
      self._relief.set(      styleOrDict['relief']           )
      self._justify.set(     styleOrDict['justify']          )
      self._wrap.set(        styleOrDict['wrap']             )
      self._lmargin1.set(    styleOrDict['lmargin1']         )
      self._lmargin2.set(    styleOrDict['lmargin2']         )
      self._rmargin.set(     styleOrDict['rmargin']          )
      self._spacing1.set(    styleOrDict['spacing1']         )
      self._spacing2.set(    styleOrDict['spacing2']         )
      self._spacing3.set(    styleOrDict['spacing3']         )
      self._tabs.set(        styleOrDict['tabs']             )
      
      if self._fgColorButton:
         self._fgColorButton.config( foreground=styleOrDict[ 'foreground' ] )
         #self._bgColorButton.config( background=styleOrDict[ 'background' ] )
      
      if currentStyleName:
         self._currentStyleName.set( currentStyleName )
      
      self.setControlState( 'normal' )

   def updateStyleList( self, styleNameList, exclusionList ):
      if self._state == 'disabled':
         return
      
      self._styleNameListWidget.delete( 0, 'end' )
      styleNameList.sort( )
      
      for name in styleNameList:
         if name not in exclusionList:
            self._styleNameListWidget.insert( 'end', name )

   def setControlState( self, newState ):
      self._state = newState

   def chooseColor( self, variable ):
      def _chooseColor( event=None ):
         import tkColorChooser
         
         newColor = tkColorChooser.askcolor( parent=self )[1]
         if newColor:
            variable.set( newColor )
            self.newColorChosen( variable )
      return _chooseColor

   def newColorChosen( self, variable ):
      pass
   
class StyleEditor( tkSimpleDialog.Dialog, StylingControl ):
   SAMPLE_TEXT = '''This is some sample text for the style widget.  The style of this text is what is configured for the style named at the top of this widget.  The quick brown fox jumped over the lazy dog.
This is a second paragraph.  The next paragraph will demonstrate tabs.
1\t2\t3\t4\t5\t6\t7\t8\t9\t0
'''
   SAMPLE_TAG = 'sampleTag'
   DEFAULT_TEXT_FONT = None

   def __init__( self, styler ):
      StylingControl.__init__( self )
      
      # Fields
      self._state             = 'normal'
      self._stext             = styler
      self._currentStyleName.set( 'default' )
      
      # Widgets
      self._stylesCombo       = None
      self._sample            = None
      self._styles            = self._stext.styles()
      
      tkSimpleDialog.Dialog.__init__( self, styler.winfo_toplevel(), 'Style Editor' )

   def body( self, parent ):
      parent.winfo_toplevel().wm_resizable( False, True )
      parent.option_add( '*font', DIALOG_FONT )
      
      self._setGUIState( 'disabled' )
      
      styleFrame = Tix.Frame( parent )
      self._stylesCombo = Tix.ComboBox( styleFrame, label='Style', editable=True,
                    dropdown=True, fancy=False, variable=self._currentStyleName,
                    history=False, command=self.onSelectedStyle, selectmode=Tix.IMMEDIATE )
      self._stylesCombo.pack( side=Tix.LEFT, padx=5, pady=5 )
      Tix.Button( styleFrame, text='Commit', command=self.commit        ).pack( side=Tix.LEFT, padx=5, pady=5 )
      Tix.Button( styleFrame, text='Revert', command=self.onRevertStyle ).pack( side=Tix.LEFT, padx=5, pady=5 )
      Tix.Button( styleFrame, text='Delete', command=self.onDeleteStyle ).pack( side=Tix.LEFT, padx=5, pady=5 )
      Tix.Button( styleFrame, text='Save',   command=self.onSaveStyles  ).pack( side=Tix.LEFT, padx=5, pady=5 )
      Tix.Button( styleFrame, text='Load',   command=self.onLoadStyles  ).pack( side=Tix.LEFT, padx=5, pady=5 )
      styleFrame.grid( row=0, column=0, columnspan=2 )
      
      self._styleNameListWidget = self._stylesCombo.subwidget( 'listbox' )
      
      # Text Styling
      textFrame = self.buildTextStylingFrame( parent )
      textFrame.grid( row=1, column=0, padx=2, pady=2, sticky='nsew' )
      
      # Paragraph Styling
      paragraphFrame = self.buildParagraphStylingFrame( parent )
      paragraphFrame.grid( row=1,column=1, padx=2, pady=2, sticky='nsew' )
      
      # Sample Text
      defaultStyle = self._styles[ 'default' ]
      articleFont = defaultStyle[ 'font' ]
      wrap        = defaultStyle[ 'wrap' ]
      spacing1    = defaultStyle[ 'spacing1' ]
      spacing2    = defaultStyle[ 'spacing2' ]
      spacing3    = defaultStyle[ 'spacing3' ]
      self._sample = StyledText( parent, styleLibrary=self._styles, font=articleFont.tkFont(), wrap=wrap, spacing1=spacing1, spacing2=spacing2, spacing3=spacing3, height=8 )
      self._sample.grid( row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew' )
      
      # Initialize the widgets
      
      #   Pack style names into the combo box
      styleNameList = self._stext.styles().keys()
      styleNameList.sort( )
      for name in styleNameList:
         self._stylesCombo.insert( Tix.END, name )
      
      #   Setup the sample text
      self._sample.insert( '1.0', StyleEditor.SAMPLE_TEXT )
      self._sample.config( state=Tix.DISABLED )
      
      self.updateStyleList( )
      self.updateGUIControls( )
      self.updateSample( )
      
      self._setGUIState( 'normal' )

   def buildTextStylingFrame( self, parent ):
      textFrame = Tix.LabelFrame( parent, label='Text Styling', background='SystemButtonFace', labelside=Tix.ACROSSTOP, padx=5, pady=5 )
      
      row = 0
      
      # Font Selection
      Tix.Label( textFrame.frame, text='Font:', anchor=Tix.W ).grid( row=row, column=0, padx=5, pady=5, sticky=Tix.W )
      fontCombo = Tix.ComboBox( textFrame.frame, editable=False,
                    dropdown=True, fancy=False, variable=self._fontFamily,
                    history=False, command=self.onApplyEdits, selectmode=Tix.IMMEDIATE )
      fontCombo.entry.config( )
      fontCombo.grid( row=row, column=1, columnspan=2, padx=5, pady=5, sticky=Tix.W )
      sizeCombo = Tix.ComboBox( textFrame.frame, editable=True,
                    dropdown=True, fancy=False, variable=self._fontSize,
                    history=False, command=self.onApplyEdits, selectmode=Tix.IMMEDIATE )
      sizeCombo.entry.config( width=5 )
      sizeCombo.grid( row=row, column=3, padx=5, pady=5, sticky=Tix.W )
      
      row += 1
      
      # Style Selection
      Tix.Label( textFrame.frame, text='Styles:', anchor=Tix.W ).grid( row=row, column=0, padx=5, pady=5, sticky=Tix.W )
      Tix.Checkbutton( textFrame.frame, text='Bold', font=DIALOG_FONT + ' bold', variable=self._bold,
                      command=self.onApplyEdits ).grid( row=row, column=1, padx=5, pady=5, sticky=Tix.W )
      Tix.Checkbutton( textFrame.frame, text='Italic', font=DIALOG_FONT + ' italic', variable=self._italic,
                      command=self.onApplyEdits ).grid( row=row, column=2, padx=5, pady=5, sticky=Tix.W )
      Tix.Checkbutton( textFrame.frame, text='Under', font=DIALOG_FONT + ' underline', variable=self._underline,
                      command=self.onApplyEdits ).grid( row=row, column=3, padx=5, pady=5, sticky=Tix.W )
      Tix.Checkbutton( textFrame.frame, text='Over', font=DIALOG_FONT + ' overstrike', variable=self._overstrike,
                      command=self.onApplyEdits ).grid( row=row, column=4, padx=5, pady=5, sticky=Tix.W )
      
      row += 1
      
      # Offset
      Tix.Label( textFrame.frame, text='Offset:', anchor=Tix.W ).grid( row=row, column=0, padx=5, pady=5, sticky=Tix.W )
      Tix.Radiobutton( textFrame.frame, text='Normal', variable=self._offset, value='normal', command=self.onApplyEdits ).grid( row=row, column=1, padx=5, pady=5, sticky=Tix.W )
      Tix.Radiobutton( textFrame.frame, text='Superscript', variable=self._offset, value='superscript', command=self.onApplyEdits ).grid( row=row, column=2, padx=5, pady=5, sticky=Tix.W )
      Tix.Radiobutton( textFrame.frame, text='Subscript', variable=self._offset, value='subscript', command=self.onApplyEdits ).grid( row=row, column=3, padx=5, pady=5, sticky=Tix.W )
      
      row += 1
      
      # Pen
      Tix.Label( textFrame.frame, text='Pen:', anchor=Tix.W ).grid( row=row, column=0, padx=5, pady=5, sticky=Tix.W )
      colorFrame = Tix.Frame( textFrame.frame )
      Tix.Label( colorFrame, text='Foreground' ).grid( row=0, column=1, padx=5, pady=5 )
      Tix.Label( colorFrame, text='Background' ).grid( row=0, column=2, padx=5, pady=5 )
      
      Tix.Label( colorFrame, text='Color', anchor=Tix.W ).grid( row=1, column=0, padx=5, pady=5, sticky=Tix.W )
      self._fgColorButton = Tix.Button( colorFrame, text=' '*20,
                                  background=self._foreground.get(),
                                  command=self.chooseColor(self._foreground) )
      self._fgColorButton.grid( row=1, column=1, padx=5, pady=5 )
      #self._bgColorButton = Tix.Button( colorFrame,text=' '*20,
                                  #background=self._background.get(),
                                  #command=self.chooseColor(self._background) )
      #self._bgColorButton.grid( row=1, column=2, padx=5, pady=5 )
      
      Tix.Label( colorFrame, text='Stipple', anchor=Tix.W ).grid( row=2, column=0, padx=5, pady=5, sticky=Tix.W )
      fgStippleCombo = Tix.ComboBox( colorFrame, editable=True,
                    dropdown=True, fancy=False, variable=self._fgstipple,
                    history=False, command=self.onApplyEdits, selectmode=Tix.IMMEDIATE )
      fgStippleCombo.entry.config( width=10 )
      fgStippleCombo.grid( row=2, column=1, padx=5, pady=5 )
      bgStippleCombo = Tix.ComboBox( colorFrame, editable=True,
                    dropdown=True, fancy=False, variable=self._bgstipple,
                    history=False, command=self.onApplyEdits, selectmode=Tix.IMMEDIATE )
      bgStippleCombo.entry.config( width=10 )
      bgStippleCombo.grid( row=2, column=2, padx=5, pady=5 )
      colorFrame.grid( row=row, column=1, columnspan=4, padx=5, pady=5, sticky=Tix.W )
      
      row += 1
      
      # Border Options
      Tix.Label( textFrame.frame, text='Border:', anchor=Tix.W ).grid( row=row, column=0, padx=5, pady=5, sticky=Tix.W )
      bdwidthCombo = Tix.ComboBox( textFrame.frame, label='Width', editable=True,
                    dropdown=True, fancy=False, variable=self._borderwidth,
                    history=False, command=self.onApplyEdits, selectmode=Tix.IMMEDIATE )
      bdwidthCombo.entry.config( width=5 )
      bdwidthCombo.grid( row=row, column=1, columnspan=2, padx=5, pady=5, sticky=Tix.W )
      reliefCombo = Tix.ComboBox( textFrame.frame, label='Relief', editable=False,
                    dropdown=True, fancy=False, variable=self._relief,
                    history=False, command=self.onApplyEdits, selectmode=Tix.IMMEDIATE )
      reliefCombo.entry.config( width=10 )
      reliefCombo.grid(row=row, column=3, columnspan=2, padx=5, pady=5, sticky=Tix.W )
      
      #   Populate the font family combo box
      familyList = list(tkFont.families( ))
      familyList.sort()
      for family in familyList:
         if family[0] == '@':
            continue
         fontCombo.insert( Tix.END, family )
      
      #   Populate the font size combo box
      for size in xrange( 6,35 ):
         sizeCombo.insert( Tix.END, '%d' % size )
      
      #   Pack Stiple boxes
      for value in [ '', 'gray12', 'gray25', 'gray50', 'gray75' ]:
         fgStippleCombo.insert( Tix.END, value )
         bgStippleCombo.insert( Tix.END, value )
      
      #   Pack Borderwidth box
      for width in range( 0, 10 ):
         bdwidthCombo.insert( Tix.END, '%d' % width )
      
      #   Pack Border relief box
      for relief in [ 'flat', 'raised', 'sunken', 'groove', 'ridge', 'solid' ]:
         reliefCombo.insert( Tix.END, relief )
      
      return textFrame
   
   def buildParagraphStylingFrame( self, parent ):
      paragraphFrame = Tix.LabelFrame( parent, label='Paragraph Styling', background='SystemButtonFace', labelside=Tix.ACROSSTOP, padx=5, pady=5 )
      
      row = 0
      
      # Justification
      Tix.Label( paragraphFrame.frame, text='Justify:', anchor=Tix.W ).grid( row=row, column=0, padx=5, pady=5, sticky=Tix.W )
      Tix.Radiobutton( paragraphFrame.frame, text='Left',   variable=self._justify, value=Tix.LEFT,   command=self.onApplyEdits ).grid( row=row, column=1, padx=5, pady=5, sticky=Tix.W )
      Tix.Radiobutton( paragraphFrame.frame, text='Center', variable=self._justify, value=Tix.CENTER, command=self.onApplyEdits ).grid( row=row, column=2, padx=5, pady=5, sticky=Tix.W )
      Tix.Radiobutton( paragraphFrame.frame, text='Right',  variable=self._justify, value=Tix.RIGHT,  command=self.onApplyEdits ).grid( row=row, column=3, padx=5, pady=5, sticky=Tix.W )
      
      row += 1
      
      # Wrapping
      Tix.Label( paragraphFrame.frame, text='Wrap:', anchor=Tix.W ).grid( row=row, column=0, padx=5, pady=5, sticky=Tix.W )
      Tix.Radiobutton( paragraphFrame.frame, text='None', variable=self._wrap, value=Tix.NONE, command=self.onApplyEdits ).grid( row=row, column=1, padx=5, pady=5, sticky=Tix.W )
      Tix.Radiobutton( paragraphFrame.frame, text='Char', variable=self._wrap, value=Tix.CHAR, command=self.onApplyEdits ).grid( row=row, column=2, padx=5, pady=5, sticky=Tix.W )
      Tix.Radiobutton( paragraphFrame.frame, text='Word', variable=self._wrap, value=Tix.WORD, command=self.onApplyEdits ).grid( row=row, column=3, padx=5, pady=5, sticky=Tix.W )
      
      row += 1
      
      # Margins
      Tix.Label( paragraphFrame.frame, text='Margins:', anchor=Tix.W ).grid( row=row, column=0, padx=5, pady=5, sticky=Tix.W )
      le = Tix.LabelEntry( paragraphFrame.frame, label='L-Margin1' )
      le.label.configure( anchor=Tix.W )
      le.entry.configure( textvariable=self._lmargin1, width=4 )
      le.entry.bind( '<FocusOut>', self.onApplyEdits )
      le.grid( row=row, column=1, columnspan=2, padx=5, pady=5, sticky=Tix.W )
      le = Tix.LabelEntry( paragraphFrame.frame, label='R-Margin'  )
      le.label.configure( anchor=Tix.W )
      le.entry.configure( textvariable=self._rmargin,  width=4  )
      le.entry.bind( '<FocusOut>', self.onApplyEdits )
      le.grid( row=row, column=3, columnspan=2, padx=5, pady=5, sticky=Tix.W )
      
      row += 1
      
      le = Tix.LabelEntry( paragraphFrame.frame, label='L-Margin2' )
      le.label.configure( anchor=Tix.W )
      le.entry.configure( textvariable=self._lmargin2, width=4 )
      le.entry.bind( '<FocusOut>', self.onApplyEdits )
      le.grid( row=row, column=1, columnspan=2, padx=5, pady=5, sticky=Tix.W )
      
      row += 1
      
      # Line Spacing
      Tix.Label( paragraphFrame.frame, text='Spacing:', anchor=Tix.W ).grid( row=row, column=0, padx=5, pady=5, sticky=Tix.W )
      Tix.Label( paragraphFrame.frame, text=u'Before \u00B6', anchor=Tix.W ).grid( row=row, column=1, padx=5, pady=5, sticky=Tix.W )
      spacing1Combo = Tix.ComboBox( paragraphFrame.frame, editable=True,
                    dropdown=True, fancy=False, variable=self._spacing1,
                    history=False, command=self.onApplyEdits, selectmode=Tix.IMMEDIATE )
      spacing1Combo.entry.config( width=10 )
      spacing1Combo.grid( row=row, column=2, padx=5, pady=5, sticky=Tix.W )
      Tix.Label( paragraphFrame.frame, text=u'After \u00B6', anchor=Tix.W ).grid( row=row, column=3, padx=5, pady=5, sticky=Tix.W )
      spacing3Combo = Tix.ComboBox( paragraphFrame.frame, editable=True,
                    dropdown=True, fancy=False, variable=self._spacing3,
                    history=False, command=self.onApplyEdits, selectmode=Tix.IMMEDIATE )
      spacing3Combo.entry.config( width=10 )
      spacing3Combo.grid( row=row, column=4, padx=5, pady=5, sticky=Tix.W )
      
      row += 1
      
      Tix.Label( paragraphFrame.frame, text='Lines', anchor=Tix.W ).grid( row=row, column=1, padx=5, pady=5, sticky=Tix.W )
      spacing2Combo = Tix.ComboBox( paragraphFrame.frame, editable=True,
                    dropdown=True, fancy=False, variable=self._spacing2,
                    history=False, command=self.onApplyEdits, selectmode=Tix.IMMEDIATE )
      spacing2Combo.entry.config( width=10 )
      spacing2Combo.grid( row=row, column=2, padx=5, pady=5, sticky=Tix.W )
      
      row += 1
      
      # Tabs
      le = Tix.Label( paragraphFrame.frame, text='Tabs', anchor=Tix.W ).grid( row=row, column=1, padx=5, pady=5, sticky=Tix.W )
      le = Tix.Entry( paragraphFrame.frame, width=20, textvariable=self._tabs )
      le.bind( '<FocusOut>', self.onApplyEdits )
      le.grid( row=row, column=2, columnspan=2, padx=5, pady=5, sticky=Tix.W )
      
      # Initialization
      for value in [ 'None', 'Half Line', 'One Line', 'Two Lines' ]:
         spacing1Combo.insert( Tix.END, value )
         spacing2Combo.insert( Tix.END, value )
         spacing3Combo.insert( Tix.END, value )
      
      return paragraphFrame
   
   # Transdfer Data
   def update( self, makeThisStyleCurrent=None ):
      self.updateStyleList( )
      self.updateGUIControls( makeThisStyleCurrent )
      self.updateSample( )
   
   def commit( self ):
      newStyleName = self._currentStyleName.get()
      if newStyleName and (newStyleName != ''):
         self._styles[ newStyleName ] = self.makeStyleObj()
         self._sample.setStyle( '1.0', 'end', newStyleName )
      
      self.updateStyleList( makeThisStyleCurrent=newStyleName )

   def updateStyleList( self, makeThisStyleCurrent=None ):
      self._stylesCombo.configure( state='disabled' )
      
      StylingControl.updateStyleList( self, self._styles.keys(), [ StyleEditor.SAMPLE_TAG ] )
      
      if makeThisStyleCurrent:
         if self._styleNameListWidget.size() > 0:
            for idx,name in enumerate(self._styleNameListWidget.get( 0, 'end' )):
               if name == makeThisStyleCurrent:
                  self._stylesCombo.pick( idx )
                  break
            else:
               self._stylesCombo.pick( 0 )
      
      self._stylesCombo.configure( state='normal' )
   
   def updateGUIControls( self, aStyle=None ):
      if aStyle:
         theStyle = aStyle
      else:
         theStyle = self._styles[ self._currentStyleName.get() ]
      
      self.updateVariables( theStyle.opts() )

   def updateSample( self ):
      if self._sample:
         self._styles[StyleEditor.SAMPLE_TAG] = self.makeStyleObj()
         self._sample.setStyle( '1.0', 'end', StyleEditor.SAMPLE_TAG )

   def makeStyleObj( self ):
      try:
         return Style( family      = self._fontFamily.get( ),
                       size        = int(self._fontSize.get( )),
                       bold        = bool(self._bold.get( )),
                       italic      = bool(self._italic.get( )),
                       offset      = self._offset.get( ),
                       underline   = bool(self._underline.get( )),
                       overstrike  = bool(self._overstrike.get( )),
                       foreground  = self._foreground.get( ),
                       background  = self._background.get( ),
                       fgstipple   = self._fgstipple.get( ),
                       bgstipple   = self._bgstipple.get( ),
                       borderwidth = self._borderwidth.get( ),
                       relief      = self._relief.get( ),
                       justify     = self._justify.get( ),
                       wrap        = self._wrap.get( ),
                       lmargin1    = self._lmargin1.get( ),
                       lmargin2    = self._lmargin2.get( ),
                       rmargin     = self._rmargin.get( ),
                       spacing1    = self._spacing1.get( ),
                       spacing2    = self._spacing2.get( ),
                       spacing3    = self._spacing3.get( ),
                       tabs        = self._tabs.get( )
                     )
      except:
         return DEFAULT_STYLE

   def _setGUIState( self, newState ):
      self._state = newState
   
   # Handle GUI events
   def onSelectedStyle( self, styleName ):
      if self._state == 'disabled':
         return
      
      if self._currentStyleName.get() not in self._sample.styles():
         return
      
      self.updateGUIControls( )
      self.updateSample( )
   
   def onRevertStyle( self ):
      self.update( )
   
   def onDeleteStyle( self ):
      styleName = self._currentStyleName.get()
      if styleName == 'default':
         return
      
      del self._styles[ styleName ]
      self._sample.tag_delete( styleName )
      
      self._currentStyleName.set( self._styleNameListWidget.get( 0 ) )
      
      if len(self._sample.styles()) == 0:
         self._currentStyleName.set('')
         self.update( self.defaultStyle )
      else:
         self.update( )
      
      self._stylesCombo.pick( 0 )
   
   def newColorChosen( self, variable ):
      self.updateGUIControls( )
      self.updateSample( )
   
   def onApplyEdits( self, event=None ):
      if self._state == 'disabled':
         return
      
      self.updateSample( )

   def onSaveStyles( self ):
      import tkFileDialog
      import pickle
      filename = tkFileDialog.asksaveasfilename( parent=self, defaultextension='sty' )
      if not filename or (filename == ''):
         return
      
      if StyleEditor.SAMPLE_TAG in self._sample.styles():
         del self._sample.styles()[ StyleEditor.SAMPLE_TAG ]
      
      theFile = file( filename, 'w' )
      pickle.dump( self._sample.styles(), theFile )
   
   def onLoadStyles( self ):
      import tkFileDialog
      import pickle
      filename = tkFileDialog.askopenfilename( parent=self, defaultextension='sty' )
      if not filename or (filename == ''):
         return
      
      theFile = file( filename, 'r' )
      styleDefinitions = pickle.load( theFile )
      if StyleEditor.SAMPLE_TAG in styleDefinitions:
         del styleDefinitions[ StyleEditor.SAMPLE_TAG ]
      
      styles = self._sample.styles()
      for styleName,styleDef in styleDefinitions.iteritems():
         styles[ styleName ] = styleDef
      
      styleList = styles.keys()
      styleList.sort()
      
      self.updateStyleList( makeThisStyleCurrent=styleList[0] )

   # Override
   def apply( self ):
      if StyleEditor.SAMPLE_TAG in self._styles:
         del self._styles[ StyleEditor.SAMPLE_TAG ]

   def cancel( self, evt=None ):
      if StyleEditor.SAMPLE_TAG in self._styles:
         del self._styles[ StyleEditor.SAMPLE_TAG ]
      
      tkSimpleDialog.Dialog.cancel( self, evt )


class DocumentWriter( Tix.Frame, StylingControl ):
   def __init__( self, parent, **options ):
      Tix.Frame.__init__( self, parent )
      StylingControl.__init__( self )
      
      self._styleCombo        = None
      
      # The View
      textFrame = Tix.Frame( self )
      textFrame.columnconfigure( 0, weight=1 )
      textFrame.rowconfigure(    0, weight=1 )
      self.stext         = StyledText( textFrame, **options )
      xscroll            = Tix.Scrollbar( textFrame, orient='horizontal',command=self.stext.xview )
      yscroll            = Tix.Scrollbar( textFrame, orient='vertical',  command=self.stext.yview )
      self.stext.grid( row=0, column=0, sticky='nsew' )
      xscroll.grid(    row=1, column=0, sticky='ew' )
      yscroll.grid(    row=0, column=1, sticky='ns' )
      
      self.stext[ 'xscrollcommand' ] = xscroll.set
      self.stext[ 'yscrollcommand' ] = yscroll.set
      
      # Toolbar 1
      self._tb1 = Toolbar( self )
      self._tb1.pack( side='top', fill='x', padx=2, pady=2 )
      
      paragraphFrame = self.paragraphAttributeToolbar( self._tb1 )
      self._tb1.add( 'paragraph', paragraphFrame )
      
      # Toolbar 2
      self._tb2 = Toolbar( self )
      self._tb2.pack( side='top', fill='x', padx=2, pady=2 )
      
      self._tb2.add( 'style',  self.styleToolbar( self._tb2 ) )
      self._tb2.add( 'font',   self.fontAttributeToolbar( self._tb2 ) )
      self._tb2.add( 'object', self.objectToolbar( self._tb2 ) )
      self._styleNameListWidget = self._styleCombo.subwidget( 'listbox' )
      
      self._updateStyleToolbar( )
      
      # The Styled Text Widget
      textFrame.pack( side='top', fill='both', padx=3, expand=1 )
      
      # Bind to all events that move the insertion carrot
      self.stext.bind( '<KeyPress-BackSpace>', self._updateToolbarValues, '+' )
      self.stext.bind( '<KeyPress-Up>',        self._updateToolbarValues, '+' )
      self.stext.bind( '<KeyPress-Down>',      self._updateToolbarValues, '+' )
      self.stext.bind( '<KeyPress-Left>',      self._updateToolbarValues, '+' )
      self.stext.bind( '<KeyPress-Right>',     self._updateToolbarValues, '+' )
      self.stext.bind( '<KeyPress-Home>',      self._updateToolbarValues, '+' )
      self.stext.bind( '<KeyPress-End>',       self._updateToolbarValues, '+' )
      self.stext.bind( '<KeyPress-Prior>',     self._updateToolbarValues, '+' )
      self.stext.bind( '<KeyPress-Next>',      self._updateToolbarValues, '+' )
      self.stext.bind( '<ButtonPress-1>',      self._updateToolbarValues, '+' )
      self.stext.bind( '<ButtonRelease-1>',    self._updateToolbarValues, '+' )
      
      self.stext.bind( '<<Reinitialized>>', self._updateStyleToolbar  )
      
      if 'font' in options:
         StyleEditor.DEFAULT_TEXT_FONT = options[ 'font' ]
      else:
         StyleEditor.DEFAULT_TEXT_FONT = self.stext[ 'font' ]

   # GUI Elements
   def fontAttributeToolbar( self, parent ):
      lst = list(tkFont.families( ))
      lst.sort()
      
      familyList    = [ name for name in lst if name[0] != '@' ]
      szList        = [ str(x) for x in range(6,31) ]
      stippleValues = [ '', 'gray12', 'gray25', 'gray50', 'gray75' ]
      reliefValues  = [ 'flat','sunken','raised','groove','ridge','solid']
      
      fontFrame = Toolset( parent )
      familyCombo = fontFrame.addCombo(  'families',   self._fontFamily, familyList, Font.DEFAULT_FONT['family'], width=15, command=self.onChooseAttribute('family', self._fontFamily))
      familyCombo.subwidget('listbox').config( width=30, height=20 )
      fontFrame.addCombo(  'sizes',      self._fontSize, szList,     Font.DEFAULT_FONT['size'],   width=3,  command=self.onChooseAttribute('size',   self._fontSize))
      fontFrame.addPushButton( 'bold',       self._bold,     text='B', font=Toolset.FONT + ' bold', command=self.onToggleAttribute('bold') )
      fontFrame.addPushButton( 'italic',     self._italic,      text='I', font=Toolset.FONT + ' italic', command=self.onToggleAttribute('italic') )
      fontFrame.addPushButton( 'underline',  self._underline,  text='U', font=Toolset.FONT + ' underline', command=self.onToggleAttribute('underline') )
      fontFrame.addPushButton( 'overstrike', self._overstrike, text='O', font=Toolset.FONT + ' overstrike', command=self.onToggleAttribute('overstrike') )
      fontFrame.addCombo(  'offset',     self._offset, ['normal','superscript','subscript'], 'normal', width=9, command=self.onChooseAttribute('offset',self._offset))
      self._fgColorButton = fontFrame.addButton( 'fgColor',    text='A', font=Toolset.FONT + ' bold', command=self.onChangeColor('foreground') )
      #self._bgColorButton = fontFrame.addButton( 'bgColor',    text='A', font=Toolset.FONT + ' bold', command=self.onChangeColor('background') )
      #fontFrame.addCombo(  'bgColor',    text='A', font=Toolset.FONT + ' bold', command=self.onChangeBG )
      #fontFrame.addCombo(  'fgStipple',  self._fgstipple, stippleValues, '', width=5, command=self.onChooseAttribute('fgstipple', self._fgstipple))
      #fontFrame.addCombo(  'bgStipple',  self._bgstipple, stippleValues, '', width=5, command=self.onChooseAttribute('bgstipple', self._bgstipple))
      fontFrame.addLabel(  'border',     text='border' )
      le = fontFrame.addEntry(  'bdwidth',    self._borderwidth, width=4 )
      le.bind( '<FocusOut>', self.onChooseAttribute('borderwidth',self._borderwidth) )
      fontFrame.addCombo(  'relief',     self._relief, reliefValues, 'flat', width=5, command=self.onChooseAttribute('relief',self._relief))
      
      return fontFrame
   
   def paragraphAttributeToolbar( self, parent ):
      paragraphFrame = Toolset( parent )
      paragraphFrame.addCombo( 'justify',  self._justify, ['left','right','center'], 'left', width=5, command=self.onChooseAttribute('justify',self._justify) )
      paragraphFrame.addCombo( 'wrap',     self._wrap,    ['none','char','word'],    'none', width=5, command=self.onChooseAttribute('wrap',self._wrap ))
      paragraphFrame.addEntry( 'lmargin1', self._lmargin1, 'L-Margin1', width=4, command=self.onChooseAttribute('lmargin1',self._lmargin1))
      paragraphFrame.addEntry( 'lmargin2', self._lmargin2, 'L-Margin2', width=4, command=self.onChooseAttribute('lmargin2',self._lmargin2))
      paragraphFrame.addEntry( 'rmargin',  self._rmargin,  'R-Margin',  width=4, command=self.onChooseAttribute('rmargin', self._rmargin))
      
      paragraphFrame.addEntry( 'spacing1', self._spacing1, 'Spacing1', width=4, command=self.onChooseAttribute('spacing1',self._spacing1))
      paragraphFrame.addEntry( 'spacing2', self._spacing2, 'Spacing2', width=4, command=self.onChooseAttribute('spacing2',self._spacing2))
      paragraphFrame.addEntry( 'spacing3', self._spacing3, 'Spacing3', width=4, command=self.onChooseAttribute('spacing3',self._spacing3))
      paragraphFrame.addEntry( 'tabs',     self._tabs,     'Tabs',     width=4, command=self.onChooseAttribute('tabs',    self._tabs))
      return paragraphFrame
   
   def styleToolbar( self, parent ):
      styleFrame = Toolset( parent )
      self._styleCombo = styleFrame.addCombo( 'style', self._currentStyleName, command=self.onStyleChosen )
      styleFrame.addButton( 'edit', text='Edit', command=self.editStyles )
      return styleFrame
   
   def objectToolbar( self, parent ):
      objectFrame = Toolset( parent )
      objectFrame.addButton( 'image', text='image', command=self.onInsertImage )
      objectFrame.addButton( 'bookmark', text='bookmark', command=lambda:None  )
      objectFrame.addButton( 'link',     text='link',     command=self.onLink  )
      objectFrame.addButton( 'list',     text='list',     command=lambda:None  )
      objectFrame.addButton( 'table',    text='table',    command=lambda:None  )
      return objectFrame
   
   def _updateStyleToolbar( self, event=None ):
      styleNameList = self.stext.styles( ).keys( )
      
      # Remove any deleted styles from the text widget
      tagList       = self.stext.tag_names( )
      for name in set(tagList) - set(styleNameList):
         self.stext.tag_delete( name )
      
      # Repopulate the style combo box and text widgets
      self._styleCombo.subwidget( 'listbox' ).delete( '0', Tix.END )
      styleNameList.sort( )
      for name in styleNameList:
         self._styleCombo.insert( Tix.END, name )
         self.stext.tag_config( name, **self.stext.styles()[name].tagOptions( ) )
   
   def _updateToolbarValues( self, event=None ):
      opts = self.stext.effectiveInsertStyling( )
      self.updateVariables( *opts )
   
   def setControlState( self, newState ):
      StylingControl.setControlState( self, newState )
      self._tb1.setState( newState )
      self._tb2.setState( newState )

   # GUI Handlers
   def onLink( self, event=None ):
      self.stext.insertObject( Link_STObject( ) )

   def onToggleAttribute( self, attributeName ):
      def _onToggleAttribute( ):
         if self.stext.sel_isSelection( ):
            opts = self.stext.effectiveStyling( 'sel.first' )[0]
            newValue = not opts[ attributeName ]
            self.stext.setAttribute( 'sel.first', 'sel.last', attributeName, newValue )
         else:
            opts = self.stext.effectiveInsertStyling( )[0]
            newValue = not opts[ attributeName ]
            self.stext.setInsertAttribute( attributeName, newValue )
         
         self._updateToolbarValues( )
         self.stext.focus_set( )
      return _onToggleAttribute

   def onChooseAttribute( self, attributeName, tkVariable ):
      def _onChooseAttribute( value ):
         value = tkVariable.get( )
         if value and (value != ''):
            if attributeName == 'size':
               value = int(value)
            
            if self.stext.sel_isSelection( ):
               self.stext.setAttribute( Tix.SEL_FIRST, Tix.SEL_LAST, attributeName, value )
            else:
               style = Style
               self.stext.setInsertAttribute( attributeName, value )
         
         self._updateToolbarValues( )
         self.stext.focus_set( )
      return _onChooseAttribute

   def onApplyParagraph( self ):
      if self.stext.sel_isSelection( ):
         self.stext.setAttribute( Tix.SEL_FIRST, Tix.SEL_LAST, 'lmargin1', self._lmargin1.get() )
         self.stext.setAttribute( Tix.SEL_FIRST, Tix.SEL_LAST, 'lmargin2', self._lmargin2.get() )
         self.stext.setAttribute( Tix.SEL_FIRST, Tix.SEL_LAST, 'rmargin',  self._rmargin.get()  )
         self.stext.setAttribute( Tix.SEL_FIRST, Tix.SEL_LAST, 'spacing1', self._spacing1.get() )
         self.stext.setAttribute( Tix.SEL_FIRST, Tix.SEL_LAST, 'spacing2', self._spacing2.get() )
         self.stext.setAttribute( Tix.SEL_FIRST, Tix.SEL_LAST, 'spacing3', self._spacing3.get() )
         self.stext.setAttribute( Tix.SEL_FIRST, Tix.SEL_LAST, 'tabs',     self._tabs.get()     )
      else:
         self.stext.setInsertAttribute( 'lmargin1', self._lmargin1.get() )
         self.stext.setInsertAttribute( 'lmargin2', self._lmargin2.get() )
         self.stext.setInsertAttribute( 'rmargin',  self._rmargin.get()  )
         self.stext.setInsertAttribute( 'spacing1', self._spacing1.get() )
         self.stext.setInsertAttribute( 'spacing2', self._spacing2.get() )
         self.stext.setInsertAttribute( 'spacing3', self._spacing3.get() )
         self.stext.setInsertAttribute( 'tabs',     self._tabs.get()     )
      
      self._updateToolbarValues( )
      self.stext.focus_set( )
   
   def onChangeColor( self, option ):
      def _changeColor( event=None ):
         import tkColorChooser
         newColor = tkColorChooser.askcolor( parent=self )[1]
         if newColor:
            if self.stext.sel_isSelection( ):
               self.stext.setAttribute( Tix.SEL_FIRST, Tix.SEL_LAST, option, newColor )
            else:
               self.stext.setInsertAttribute( option, newColor )
         
         self._updateToolbarValues( )
         self.stext.focus_set( )
      return _changeColor
   
   def onInsertImage( self, filename=None ):
      if filename is None:
         import tkFileDialog
         filename = tkFileDialog.askopenfilename( parent=self, filetypes=[ ( 'GIF Image', '*.gif' ) ] )
         if not filename or (filename == ''):
            return
      
      self.stext.insert( 'insert', filename, 'image' )
      self.stext.focus_set( )

   def onStyleChosen( self, styleName ):
      if styleName and (styleName != ''):
         if self.stext.sel_isSelection( ):
            self.stext.setStyle( Tix.SEL_FIRST, Tix.SEL_LAST, styleName )
         else:
            self.stext.setInsertStyle( styleName )
      
      self.stext.focus_set( )
   
   def editStyles( self ):
      StyleEditor( self.stext )
      self._updateStyleToolbar( )
      self.stext.focus_set( )


if __name__=='__main__':
   class PyWrite( Tix.Tk ):
      def __init__( self ):
         Tix.Tk.__init__( self )
         
         self._toolBar    = Tix.Frame( self )
         self._openBtn    = Tix.Button( self._toolBar, text='open', command=self.onOpen )
         self._openBtn.pack( side='left' )
         self._saveBtn    = Tix.Button( self._toolBar, text='save', command=self.onSave )
         self._saveBtn.pack( side='left' )
         
         self._text       = DocumentWriter( self, font="{Lucida Sans Unicode} 12" )
         
         self._toolBar.pack( side='top', fill='x' )
         self._text.pack( side='top', fill='x' )
      
      def onOpen( self ):
         import tkFileDialog
         import pickle
         filename = tkFileDialog.askopenfilename( parent=self )
         if not filename or (filename == ''):
            return
         
         self._filename = filename
         theFile = file( filename, 'r' )
         docData = pickle.load( theFile )
         
         if isinstance( docData, (str,unicode) ):
            self._text.stext.insert( docData )
         else:
            self._text.stext.insert( 'end', docData[0], docData[1], 'model' )
      
      def onSave( self ):
         import tkFileDialog
         import pickle
         filename = tkFileDialog.asksaveasfilename( parent=self )
         if not filename or (filename == ''):
            return
         
         theFile = file( filename, 'w' )
         docData = self._text.getModel( )
         pickle.dump( docData, theFile )
   

   wp = PyWrite( )
   wp.mainloop( )

