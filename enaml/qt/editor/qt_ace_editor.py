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

EVENT_TEMPLATE = Template("""
    py_${func} = function() {
        py_ace_editor.${func}(${args});
    }
    this.editor.${target}.on("${event_name}", py_${func});
""")

BINDING_TEMPLATE = Template("""
    router.r_${signal} = function(index, value) {
        try {
            _this['editor_'+index].${func}(value);
        }
        catch(e) {}
    }
    py_ace_editor.${signal}.connect(router, "r_${signal}");
""")

GLOBAL_BINDING_TEMPLATE = Template("""
    py_ace_editor.${signal}.connect(${target}, "${func}");
""")


class QtAceEditor(QObject):
    columns_changed = Signal(int, unicode)
    title_changed = Signal(int, unicode)
    text_changed = Signal(int, unicode)
    mode_changed = Signal(int, unicode)
    theme_changed = Signal(unicode)
    auto_pair_changed = Signal(int, bool)
    font_size_changed = Signal(int, int)
    margin_line_changed = Signal(int, bool)
    margin_line_column_changed = Signal(int, int)

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

    def set_title(self, index, title):
        """ Set the title of the current tab in the editor

        """
        self._title = title
        self.title_changed.emit(index, title)

    def set_text(self, index, text):
        """ Set the text of the editor

        """
        self._text = text
        self.text_changed.emit(index, text)

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

    def set_mode(self, index, mode):
        """ Set the mode of the editor

        """
        if mode.startswith('ace/mode/'):
            self._mode = mode
        else:
            self._mode = 'ace/mode/' + mode
        self.mode_changed.emit(index, self._mode)

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

    def set_auto_pair(self, index, auto_pair):
        """ Set the auto_pair behavior of the editor

        """
        self._auto_pair = auto_pair
        self.auto_pair_changed.emit(index, auto_pair)

    def set_font_size(self, index, font_size):
        """ Set the font size of the editor

        """
        self._font_size = font_size
        self.font_size_changed.emit(index, font_size)

    def set_margin_line(self, index, margin_line):
        """ Set whether or not to display the margin line in the editor

        """
        if type(margin_line) == bool:
            self._margin_line = margin_line
            self.margin_line_changed.emit(index, margin_line)
        else:
            self._margin_line_column = margin_line
            self.margin_line_column_changed.emit(index, margin_line)
            self._margin_line = True
            self.margin_line_changed.emit(index, True)

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
            self.generate_ace_event('set_text_from_js', 'getSession()',
                 '_this.editor.getSession().getDocument().getValue()', 'change')

            self.generate_global_binding('theme_changed', 'this.editor',
                'setTheme')

            _editors.append(editor_template.substitute(column=_column,
                events='\n'.join(self._events), width=_width,
                global_bindings='\n'.join(self._global_bindings)))

            self._global_bindings = []
            self._events = []

        self.generate_binding('title_changed', 'setTitle')
        self.generate_binding('theme_changed', 'editor.setTheme')
        self.generate_binding('mode_changed', 'editor.getSession().setMode')
        self.generate_binding('text_changed',
            'editor.getSession().doc.setValue')
        self.generate_binding('auto_pair_changed',
            'editor.setBehavioursEnabled')
        self.generate_binding('font_size_changed', 'editor.setFontSize')
        self.generate_binding('margin_line_changed',
            'editor.setShowPrintMargin')
        self.generate_binding('margin_line_column_changed',
            'editor.setPrintMarginColumn')

        return HTML_TEMPLATE.substitute(editors='\n'.join(_editors),
                                        bindings='\n'.join(self._bindings))
