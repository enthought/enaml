from PySide.QtCore import QObject, Signal, Slot
from string import Template
import os

HTML_TEMPLATE = Template("""
    <html>
    <head>
        <script src="${resource_path}/ace/ace.js" type="text/javascript"></script>
        <script src="${resource_path}/jquery-1.7.2.min.js"
            type="text/javascript"></script>
        <script src="${resource_path}/jquery-ui-1.8.21.custom.min.js"
            type="text/javascript"></script>
        <link href="${resource_path}/editor.css" rel="stylesheet" />
    </head>
    <body>
    ${editors}
    </body>
    </html>
""")

EVENT_TEMPLATE = Template("""
    py_${func} = function() {
        py_ace_editor.${func}(${args});
    }
    editor.${target}.on("${event_name}", py_${func});
""")

BINDING_TEMPLATE = Template("""
    py_ace_editor.${signal}.connect(${target}, "${func}")
""")


class QtAceEditor(QObject):
    columns_changed = Signal(unicode)
    title_changed = Signal(unicode)
    text_changed = Signal(unicode)
    mode_changed = Signal(unicode)
    theme_changed = Signal(unicode)
    auto_pair_changed = Signal(bool)
    font_size_changed = Signal(int)
    margin_line_changed = Signal(bool)
    margin_line_column_changed = Signal(int)

    def __init__(self, parent=None):
        """ Initialize the editor

        """
        super(QtAceEditor, self).__init__(parent)
        self._events = []
        self._bindings = []

    def set_columns(self, columns):
        """ Set the number of columns in the editor

        """
        self.columns = columns

    def set_title(self, title):
        """ Set the title of the current tab in the editor

        """
        self._title = title
        self.title_changed.emit(title)

    def set_text(self, text):
        """ Set the text of the editor

        """
        self._text = text
        self.text_changed.emit(text)

    @Slot(unicode)
    def set_text_from_js(self, text):
        """ Set the text from the javascript editor. This method is required
        because set_text emits the signal to update the text again.

        """
        self._text = text

    def text(self):
        """ Return the text of the editor

        """
        return self._text

    def set_mode(self, mode):
        """ Set the mode of the editor

        """
        if mode.startswith('ace/mode/'):
            self._mode = mode
        else:
            self._mode = 'ace/mode/' + mode
        self.mode_changed.emit(self._mode)

    def mode(self):
        """ Return the mode of the editor

        """
        return self._mode

    def set_theme(self, theme):
        """ Set the theme of the editor

        """
        if theme.startswith('ace/theme/'):
            self._theme = theme
        else:
            self._theme = "ace/theme/" + theme
        self.theme_changed.emit(self._theme)

    def theme(self):
        """ Return the theme of the editor

        """
        return self._theme

    def set_auto_pair(self, auto_pair):
        """ Set the auto_pair behavior of the editor

        """
        self._auto_pair = auto_pair
        self.auto_pair_changed.emit(auto_pair)

    def set_font_size(self, font_size):
        """ Set the font size of the editor

        """
        self._font_size = font_size
        self.font_size_changed.emit(font_size)

    def show_margin_line(self, margin_line):
        """ Set the margin line of the editor

        """
        self._margin_line = margin_line
        self.margin_line_changed.emit(margin_line)

    def set_margin_line_column(self, margin_line_col):
        """ Set the margin line column of the editor

        """
        self._margin_line_column = margin_line_col
        self.margin_line_column_changed.emit(margin_line_col)

    def generate_ace_event(self, _func, _target, _args, _event_name):
        """ Generate a Javascript ace editor event handler.

        Parameters
        -----------
        _func : string
            The python method to be called on the python AceEditor object

        _args : string
            The javascript expression to pass to the method

        _target : string
            The Ace Editor target to tie the event to

        _event_name : string
            The name of the AceEditor event

        """
        event = EVENT_TEMPLATE.substitute(func=_func, args=_args,
                                          target=_target,
                                          event_name=_event_name)
        self._events.append(event)

    def generate_binding(self, _signal, _target, _func):
        """ Generate a connection between a Qt signal and a javascript function.
        Any parameters given to the signal will be passed to the javascript
        function.

        Parameters
        ----------
        _signal : string
             The name of the Qt signal

        _target : string
            The name of the target Javascript object

        _func : string
            The name of the function to call on the target object

        """
        binding = BINDING_TEMPLATE.substitute(signal=_signal, target=_target,
                                              func=_func)
        self._bindings.append(binding)

    def generate_html(self, columns=1):
        """ Generate the html code for the ace editor

        """
        # XXX better way to access files here?
        p = os.path
        template_path = p.join(p.dirname(p.abspath(__file__)), 'editor.html')
        editor_template = Template(open(template_path, 'r').read())

        _editors = []
        for _column in range(columns):
            self.generate_ace_event('set_text_from_js', 'getSession()',
                 'editor.getSession().getDocument().getValue()', 'change')

            self.generate_binding('title_changed', 'this', 'setTitle')
            self.generate_binding('theme_changed', 'editor',
                 'setTheme')
            self.generate_binding('mode_changed',
                 'editor.getSession()', 'setMode')
            self.generate_binding('text_changed',
                 'editor.getSession().doc', 'setValue')
            self.generate_binding('auto_pair_changed', 'editor',
                 'setBehavioursEnabled')
            self.generate_binding('font_size_changed', 'editor',
                 'setFontSize')
            self.generate_binding('margin_line_changed', 'editor',
                 'setShowPrintMargin')
            self.generate_binding('margin_line_column_changed',
                 'editor', 'setPrintMarginColumn')

            _editors.append(editor_template.substitute(column=_column,
                events='\n'.join(self._events),
                bindings='\n'.join(self._bindings)))
            self._bindings = []
            self._events = []

        _r_path = "file://" + p.join(p.dirname(p.abspath(__file__)))
        return HTML_TEMPLATE.substitute(resource_path=_r_path,
                                        editors='\n'.join(_editors))
