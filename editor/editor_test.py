from PySide.QtGui import QApplication
from PySide.QtWebKit import QWebView, QWebSettings
from ace_text_editor import AceTextEditor

app = QApplication([])

class AceWidget(QWebView):
    def __init__(self, text="", mode="text", theme="textmate"):
        """ Initialize the editor window

        """
        super(AceWidget, self).__init__()
        self.ace_editor = AceTextEditor(text=text, mode=mode, theme=theme)
        
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

        self.main_frame = self.page().mainFrame()
        self.main_frame.addToJavaScriptWindowObject('py_ace_editor', self.ace_editor)
            
        self.ace_editor.generate_ace_event('set_text', 'getSession()',
            'ace_editor.getSession().getDocument().getValue()', 'change')
        
        self.ace_editor.generate_binding('theme_changed', 'ace_editor',
             'setTheme')
        self.ace_editor.generate_binding('mode_changed',
             'ace_editor.getSession()', 'setMode')
        
        self.setHtml(self.ace_editor.generate_html())
            
    def editor(self):
        """ Return the ace editor

        """
        return self.ace_editor


widget = AceWidget(mode="python")
widget.show()

def after_load():
    widget.editor().set_theme('twilight')
    
widget.loadFinished.connect(after_load)

app.exec_()

print widget.editor().text()

