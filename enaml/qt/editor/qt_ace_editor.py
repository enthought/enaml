from ..qt.QtCore import QObject, Signal, Slot
from string import Template
import os

HTML_TEMPLATE = Template("""
    <html>
    <head>
        <script src="ace/ace.js" type="text/javascript"></script>
        <script src="jquery-1.7.2.min.js"
            type="text/javascript"></script>
        <script src="jquery-ui-1.8.21.custom.min.js"
            type="text/javascript"></script>
        <link href="editor.css" rel="stylesheet" />
    </head>
    <body>
        ${editors}
        <script type='text/javascript'>
            var router = {};
            var _this = this;
            ${bindings}
        </script>
    </body>
    </html>
""")

BINDING_TEMPLATE = Template("""
    router.r_${signal} = function(col_index, tab_index, value) {
        try {
            _this['editor_'+col_index].${func}(tab_index, value);
        }
        catch(e) {
            return;
        }
    }
    py_ace_editor.${signal}.connect(router, "r_${signal}");
""")

GLOBAL_BINDING_TEMPLATE = Template("""
    py_ace_editor.${signal}.connect(${target}, "${func}");
""")


class QtAceEditor(QObject):
    columns_changed = Signal(int, int, unicode)
    title_changed = Signal(int, int, unicode)
    text_changed = Signal(int, int, unicode)
    mode_changed = Signal(int, int, unicode)
    theme_changed = Signal(unicode)
    auto_pair_changed = Signal(bool)
    font_size_changed = Signal(int)
    margin_line_changed = Signal(bool)
    margin_line_column_changed = Signal(int)
    text_changed_from_js = Signal(int, int, unicode)
    tab_added = Signal(int, int)

    def __init__(self, parent=None):
        """ Initialize the editor

        """
        super(QtAceEditor, self).__init__(parent)
        self._events = []
        self._bindings = []
        self._global_bindings = []

    def set_columns(self, columns):
        """ Set the number of columns in the editor

        """
        self.columns = columns

    def set_title(self, col_index, tab_index, title):
        """ Set the title of the current tab in the editor

        """
        self.title_changed.emit(col_index, tab_index, title)

    def set_text(self, col_index, tab_index, text):
        """ Set the text of the editor

        """
        self.text_changed.emit(col_index, tab_index, text)

    @Slot(int, int, unicode)
    def set_text_from_js(self, col_index, tab_index, text):
        """ Set the text of the editor

        """
        self.text_changed_from_js.emit(col_index, tab_index, text)

    def set_mode(self, col_index, tab_index, mode):
        """ Set the mode of the editor

        """
        if not mode.startswith('ace/mode/'):
            mode = 'ace/mode/' + mode
        self.mode_changed.emit(col_index, tab_index, mode)

    def set_theme(self, theme):
        """ Set the theme of the editor

        """
        if not theme.startswith('ace/theme/'):
            theme = "ace/theme/" + theme
        self.theme_changed.emit(theme)

    def set_auto_pair(self, auto_pair):
        """ Set the auto_pair behavior of the editor

        """
        self.auto_pair_changed.emit(auto_pair)

    def set_font_size(self, font_size):
        """ Set the font size of the editor

        """
        self.font_size_changed.emit(font_size)

    def set_margin_line(self, margin_line):
        """ Set whether or not to display the margin line in the editor

        """
        if (margin_line == -1):
            self.margin_line_changed.emit(False)
        else:
            self.margin_line_changed.emit(True)
            self.margin_line_column_changed.emit(margin_line)

    def generate_binding(self, _signal, _func):
        """ Generate a connection between a Qt signal and a javascript function.
        Any parameters given to the signal will be passed to the javascript
        function.

        Parameters
        ----------
        _signal : string
             The name of the Qt signal

        _func : string
            The name of the function to call on the target object

        """
        binding = BINDING_TEMPLATE.substitute(signal=_signal, func=_func)
        self._bindings.append(binding)

    def generate_global_binding(self, _signal, _target, _func):
        """ Generate a connection between a Qt signal and a javascript function.
        Any parameters given to the signal will be passed to the javascript
        function. A global binding differs from a regular binding in that
        the binding applies to all editors.

        Parameters
        ----------
        _signal : string
             The name of the Qt signal

        _target : string
            The name of the target Javascript object

        _func : string
            The name of the function to call on the target object

        """
        binding = GLOBAL_BINDING_TEMPLATE.substitute(signal=_signal,
                                                     target=_target, func=_func)
        self._global_bindings.append(binding)

    def generate_html(self, columns=1):
        """ Generate the html code for the ace editor

        """
        # XXX better way to access template here?
        p = os.path
        template_path = p.join(p.dirname(p.abspath(__file__)), 'editor.html')
        editor_template = Template(open(template_path, 'r').read())

        _width = 100 / columns - 1

        _editors = []
        for _column in range(columns):
            self.generate_global_binding('theme_changed', 'this.editor',
                'setTheme')
            self.generate_global_binding('auto_pair_changed', 'this.editor',
                 'setBehavioursEnabled')
            self.generate_global_binding('font_size_changed', 'this.editor',
                 'setFontSize')
            self.generate_global_binding('margin_line_changed', 'this.editor',
                 'setShowPrintMargin')
            self.generate_global_binding('margin_line_column_changed',
                 'this.editor', 'setPrintMarginColumn')

            _editors.append(editor_template.substitute(column=_column,
                width=_width, global_bindings='\n'.join(self._global_bindings)))

            self._global_bindings = []
            self._events = []

        self.generate_binding('title_changed', 'setTitle')
        self.generate_binding('mode_changed', 'setMode')
        self.generate_binding('text_changed', 'setText')

        return HTML_TEMPLATE.substitute(editors='\n'.join(_editors),
                                        bindings='\n'.join(self._bindings))
