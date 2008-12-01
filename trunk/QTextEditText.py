from PyQt4 import QtCore, QtGui
import sys


app = QtGui.QApplication( sys.argv )
win = QtGui.QMainWindow( )
edit = QtGui.QTextEdit( win )
edit.setMinimumHeight( 400 )
edit.setMinimumWidth( 800 )
win.show( )

# Styles
print( '\nStyles' )
print( unicode(edit.document().defaultStyleSheet()) )

# Formats
print( '\nFormats' )
formatList = edit.document().allFormats()
print( len(formatList) )

# Inserting
edit.insertHtml( '<H1>Hello</H1>Here is some normal text and some <b>bold</b>.' )

# Formats
print( '\nFormats' )
formatList = edit.document().allFormats()
print( len(formatList) )

# Fragments
print( '\nFragments' )
txtBlock = edit.document().begin()
while txtBlock != edit.document().end():
   print( 'Text Block' )
   fragIter = txtBlock.begin()
   while not fragIter.atEnd():
      frag = fragIter.fragment()
      print( '- frag ({0:3}):  {0}'.format( frag.charFormatIndex(), unicode(frag.text()) ) )
      fragIter += 1
   
   txtBlock = txtBlock.next()

# Contents
print( '\nContents' )
print( unicode(edit.toHtml()) )

app.exec_( )
