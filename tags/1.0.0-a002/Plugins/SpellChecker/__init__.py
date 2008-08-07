from tkApplicationFramework import PluggableTool

import Tkinter
import Tix

import enchant.checker
from enchant.tokenize import EmailFilter, URLFilter

class SpellChecker( PluggableTool ):
   NAME             = 'Spelling'
   DEFAULT_SETTINGS = {
                         'language':         'en_US',
                         'personalwordlist': '',
                      }
   TAG_NAME         = '_spellchecker_'

   def __init__( self, aView ):
      PluggableTool.__init__( self, aView )
      self._textWidget  = self._view._articleView.stext
      self._textWidget.tag_config( SpellChecker.TAG_NAME, foreground='red', borderwidth=1, relief='solid' )
      
      self._language    = Tkinter.StringVar( )
      
      language = self.getOption( 'language' )
      self._chkr = enchant.checker.SpellChecker(language, filters=[EmailFilter,URLFilter])
      
      self._currentLine  = 0
      self._maxLine      = 0
      
      self._errWord      = Tkinter.StringVar( )
      self._errIndex     = '1.0'
      self._textLines    = [ ]
      self._scanLineNum  = 0
      
      self._suggestions = None
      self._entry       = None
      self._globalReplace = { }
   
   def buildGUI( self, parent ):
      restartBtn    = Tkinter.Button( parent, text='Recheck', command=self.restart )
      restartBtn.grid( row=0, column=0, padx=3, sticky='ew' )
      
      clearBtn = Tkinter.Button( parent, text='Stop', command=self.clear )
      clearBtn.grid( row=1, column=0, padx=3, sticky='ew' )
      
      self._suggestions = Tix.ScrolledListBox( parent, browsecmd=self.selectSuggestion )
      self._suggestions.subwidget( 'listbox' ).config( height=8 )
      self._suggestions.grid( row=0, column=1, rowspan=5, padx=3 )
      
      self._entry = Tkinter.Entry( parent, textvariable=self._errWord )
      self._entry.grid( row=0, column=2, columnspan=2, sticky='ew', padx=3 )
      
      replaceBtn    = Tkinter.Button( parent, text='Replace', command=self.replace )
      replaceBtn.grid( row=1, column=2, padx=3, sticky='ew' )
      
      replaceAllBtn = Tkinter.Button( parent, text='Replace All', command=self.replaceAll )
      replaceAllBtn.grid( row=1, column=3, padx=3, sticky='ew' )
      
      ignoreBtn     = Tkinter.Button( parent, text='Ignore', command=self.ignore )
      ignoreBtn.grid( row=2, column=2, padx=3, sticky='ew' )
      
      ignoreAllBtn  = Tkinter.Button( parent, text='Ignore All', command=self.ignoreAll )
      ignoreAllBtn.grid( row=2, column=3, padx=3, sticky='ew' )
      
      addToPWLBtn   = Tkinter.Button( parent, text='Add', command=self.addToPWL )
      addToPWLBtn.grid( row=3, column=2, padx=3, sticky='ew' )
   
   def restart( self ):
      self._scanLineNum = 0
      self._textLines = self._textWidget.get( '1.0', 'end' ).splitlines( )
      self._chkr.set_text( self._textLines[ self._scanLineNum ] )
      self._scanLineNum += 1
      self.next( )
   
   def clear( self ):
      self._errWord.set( '' )
      self._suggestions.subwidget( 'listbox' ).delete( 0, 'end' )
      self._textWidget.tag_remove( SpellChecker.TAG_NAME, '1.0', 'end' )
   
   def selectSuggestion( self ):
      listbox = self._suggestions.subwidget( 'listbox' )
      idx = listbox.curselection( )
      if isinstance( idx, tuple ):
         self._errWord.set( listbox.get( idx[0] ) )
      else:
         raise Exception

   def replace( self ):
      newWord = self._errWord.get( )
      if newWord == self._chkr.word:
         return
      
      pos = self._chkr.wordpos
      
      # replace it in the checker
      self._chkr.replace( newWord )
      
      # replace it in the text
      startIndex = '%d.%d' % (self._scanLineNum, pos)
      endIndex   = '%d.%d' % (self._scanLineNum,pos+len(self._chkr.word))
      self._textWidget.delete( startIndex, endIndex )
      self._textWidget.insert( startIndex, newWord )
      
      self.next( )
   
   def replaceAll( self ):
      self._globalReplace[ self._chkr.word ] = self._errWord.get( )
      self.replace( )
   
   def ignore( self ):
      self.next( )
   
   def ignoreAll( self ):
      self._chkr.ignore_always( )
      self.next( )
   
   def addToPWL( self ):
      self._chkr.add_to_personal( self._errWord.get( ) )
      self.next( )
   
   def next( self ):
      self._errWord.set( '' )
      self._suggestions.subwidget( 'listbox' ).delete( 0, 'end' )
      self._textWidget.tag_remove( SpellChecker.TAG_NAME, '1.0', 'end' )
      
      try:
         self._next( )
      except StopIteration:
         return
      
      while self._chkr.word in self._globalReplace:
         self._errWord.set( self._globalReplace[ self._chkr.word ] )
         self.replace( )
         self._next
      
      self._errWord.set( self._chkr.word )
      for word in self._chkr.suggest( ):
         self._suggestions.subwidget( 'listbox' ).insert( 'end', word )
      self._suggestions.subwidget( 'listbox' ).selection_set( 0 )
      self.selectSuggestion( )
      
      self._errIndex = '%d.%d' % ( self._scanLineNum, self._chkr.wordpos )
      self._textWidget.see( self._errIndex )
      self._textWidget.tag_add( SpellChecker.TAG_NAME, self._errIndex, '%d.%d' % (self._scanLineNum, self._chkr.wordpos+len(self._chkr.word)) )
      self._textWidget.tag_config( SpellChecker.TAG_NAME, foreground='red', borderwidth=1, relief='solid' )

   def _next( self ):
      try:
         self._chkr.next( )
      except StopIteration:
         if self._scanLineNum == len(self._textLines):
            raise StopIteration
         else:
            self._chkr.set_text( self._textLines[ self._scanLineNum ] )
            self._scanLineNum += 1
         
         self._next()

pluginClass = SpellChecker
