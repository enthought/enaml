from ..qt.QtWebKit import QWebView, QWebSettings
from ..qt.QtCore import QUrl
from qt_ace_editor import QtAceEditor


class QtAceEditorView(QWebView):
    def __init__(self, parent=None):
        """ Initialize the editor window

        """
        super(QtAceEditorView, self).__init__(parent)
        self.ace_editor = QtAceEditor(self)

        # XXX this is used for debugging, it should be taken out eventually
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

    def set_columns(self, columns):
        """ Set the number of columns for the editor

        """
        html = self.ace_editor.generate_html(columns)
        self.setHtml(html, QUrl.fromLocalFile(__file__))
        self.page().mainFrame().addToJavaScriptWindowObject('py_ace_editor',
                                                             self.ace_editor)

    def editor(self):
        """ Return the ace editor

        """
        return self.ace_editor
