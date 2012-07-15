from ..qt.QtWebKit import QWebView, QWebSettings
from qt_ace_editor import QtAceEditor

class QtAceEditorView(QWebView):
    def __init__(self, parent=None):
        """ Initialize the editor window

        """
        super(QtAceEditorView, self).__init__(parent)
        self.ace_editor = QtAceEditor()

        # XXX this is used for debugging, it should be taken out eventually
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

        self.main_frame = self.page().mainFrame()
        self.main_frame.addToJavaScriptWindowObject('py_ace_editor', self.ace_editor)
            
        self.ace_editor.generate_ace_event('set_text_from_js', 'getSession()',
            'ace_editor.getSession().getDocument().getValue()', 'change')
        
        self.ace_editor.generate_binding('theme_changed', 'ace_editor',
             'setTheme')
        self.ace_editor.generate_binding('mode_changed',
             'ace_editor.getSession()', 'setMode')
        self.ace_editor.generate_binding('text_changed',
             'ace_editor.getSession().doc', 'setValue')
        self.ace_editor.generate_binding('auto_pair_changed', 'ace_editor',
                                         'setBehavioursEnabled')
        self.ace_editor.generate_binding('font_size_changed', 'ace_editor',
                                         'setFontSize')
        self.ace_editor.generate_binding('margin_line_changed', 'ace_editor',
                                         'setShowPrintMargin')
        self.ace_editor.generate_binding('margin_line_column_changed',
                                         'ace_editor', 'setPrintMarginColumn')
                
        html = self.ace_editor.generate_html()
        self.setHtml(html)
            
    def editor(self):
        """ Return the ace editor

        """
        return self.ace_editor

