[Application]
REQUIRED_PYTHON_VERSION = 2.6
NAME                    = MindTree
VERSION                 = 1.2
BUILD                   = 2008.11.12.24.42

fileTypes               = MindTree Outline File (*.mto);;All Files (*.*)
fileExtension           = mto

pluginDir               = plugins

[OutlineView]
emptyArticleIcon        = resources/images/file.gif
fullArticleIcon         = resources/images/textfile.gif

[action.newFile]
text                    = New
icon                    = resources/icons/file_new.ico
statustip               = Begin a new project.

[action.openFile]
text                    = Open...
icon                    = resources/icons/file_open.ico
statustip               = Open an existing project.

[action.close]
text                    = Close

[action.saveFile]
text                    = Save
icon                    = resources/icons/file_save.ico
statustip               = Save the current project.

[action.saveFileAs]
text                    = Save as...

[action.importFile]
text                    = Import...

[action.exportFile]
text                    = Export...

[action.exit]
text                    = Exit

[action.help]
text                    = Help

[action.helpAbout]
text                    = About...

[action.editUndo]
text                    = Undo
icon                    = resources/icon/undo.ico
statustip               = Undo the most recent change.

[action.editRedo]
text                    = Redo
icon                    = resources/icons/edit_redo.ico
statustip               = Redo the most recent undo.

[action.articleCut]
text                    = Cut Text
icon                    = resources/icons/edit_cut.ico
statustip               = Cut the selected text to the clipboard.
      
[action.articleCopy]
text                    = Copy Text
icon                    = resources/icons/edit_copy.ico
statustip               = Copy the selected text to the clipboard.

[action.articlePaste]
text                    = Paste Text
icon                    = resources/icons/edit_paste.ico
statustip               = Paste the contents of the clipboard.

[action.articleSelectAll]
text                    = Select All Text

[action.cutNode]
text                    = Cut Node

[action.copyNode]
text                    = Copy Node

[action.pasteNodeBefore]
text                    = Paste Node Before

[action.pasteNodeAfter]
text                    = Paste Node After
      
[action.pasteNodeChild]
text                    = Paste Node Child

[action.expandAll]
text                    = Expand All
icon                    = resources/icons/expand.ico
statustip               = Expand all nodes of the outline.

[action.expandNode]
text                    = Expand Node

[action.collapseAll]
text                    = Collapse All
icon                    = resources/icons/collapse.ico
statustip               = Collapse all nodes of the outline.

[action.collapseNode]
text                    = Collapse Node

[action.moveNodeUp]
text                    = Move Node Up
shortcut                = Ctrl+Up

[action.moveNodeDown]
text                    = Move Node Down
shortcut                = Ctrl+Down

[action.indentNode]
text                    = Indent Node
shortcut                = Ctrl+Right
shortcut                = Tab

[action.dedentNode]
text                    = Dedent Node
shortcut                = Ctrl+Left
shortcut                = Shift+Tab

[action.insertNewNodeBefore]
text                    = New Node Before

[action.insertNewNodeAfter]
text                    = New Node After
shortcut                = Return
shortcut                = Enter

[action.insertNewChildAction]
text                    = New Child

[action.deleteNode]
text                    = Delete Node
