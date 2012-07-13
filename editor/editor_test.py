from PySide.QtGui import QApplication, QMainWindow
from PySide.QtWebKit import QWebView, QWebSettings
from ace_text_editor import AceTextEditor

app = QApplication([])

class AceMainWindow(QMainWindow):
    def __init__(self, text="", mode="text", theme="textmate"):
        """ Initialize the editor window

        """
        super(AceMainWindow, self).__init__()
        self.ace_editor = AceTextEditor(text=text, mode=mode, theme=theme)
        
        self.web_view = QWebView()
        self.web_view.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

        self.main_frame = self.web_view.page().mainFrame()
        self.main_frame.addToJavaScriptWindowObject('py_ace_editor', self.ace_editor)
            
        self.ace_editor.generate_ace_event('set_text', 'getSession()',
            'ace_editor.getSession().getDocument().getValue()', 'change')
        self.ace_editor.generate_binding('theme_changed', 'ace_editor',
             'setTheme')
        self.ace_editor.generate_binding('mode_changed',
             'ace_editor.getSession()', 'setMode')
        
        html = self.ace_editor.generate_html()
        self.web_view.setHtml(html)
        
        self.setCentralWidget(self.web_view)
            
    def editor(self):
        """ Return the ace editor

        """
        return self.ace_editor


window = AceMainWindow(mode="python")
window.show()

def after_load():
    window.editor().set_theme('twilight')
    
window.web_view.loadFinished.connect(after_load)

app.exec_()

print window.editor().text()

