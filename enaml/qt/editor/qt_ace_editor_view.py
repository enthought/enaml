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
        self.main_frame.addToJavaScriptWindowObject('py_ace_editor',
                                                    self.ace_editor)

    def set_columns(self, columns):
        html = self.ace_editor.generate_html(columns)
        self.setHtml(html)

    def editor(self):
        """ Return the ace editor

        """
        return self.ace_editor
