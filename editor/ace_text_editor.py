from PySide.QtCore import QObject, Signal, Slot
from string import Template
import os

HTML_TEMPLATE = Template("""
<html>
<head>
  <script src="${resource_path}/ace.js" type="text/javascript"></script>
  <style type="text/css" media="screen">
    body {
        overflow: hidden;
    }
    
    #editor { 
        margin: 0;
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
    }
  </style>
</head>
<body>

<div id="editor">${text}</div>
    
<script>
    var ace_editor = ace.edit("editor");
    ace_editor.getSession().setMode('${mode}');
    ace_editor.setTheme('${theme}')
    ${events}
    ${bindings}
</script>

</body>
</html>
""")


EVENT_TEMPLATE = Template("""
    py_${func} = function() {
        py_ace_editor.${func}(${args});
    }
    ace_editor.${target}.on("${event_name}", py_${func});
""")

BINDING_TEMPLATE = Template("""
    py_ace_editor.${signal}.connect(${target}, "${func}")
""")

class AceTextEditor(QObject):

    text_changed = Signal(unicode)
    mode_changed = Signal(unicode)
    theme_changed = Signal(unicode)
    document_changed = Signal(unicode, unicode)
    
    def __init__(self, text="", mode="text", theme="textmate"):
        """ Initialize the editor

        """
        super(AceTextEditor, self).__init__()
        self.set_text(text)
        self.set_mode(mode)
        self.set_theme(theme)
        self._events = []
        self._bindings = []

    @Slot(unicode)
    def set_text(self, text):
        """ Set the text of the editor

        """
        self._text = text

    def text(self):
        """ Return the text of the editor

        """
        return self._text

    def set_mode(self, mode):
        """ Set the mode of the editor

        """
        if mode.startswith('ace/mode'):
            self._mode = mode
        else:
            self._mode = 'ace/mode/'+mode
        self.mode_changed.emit(self._mode)

    def mode(self):
        """ Return the mode of the editor

        """
        return self._mode

    def set_theme(self, theme):
        """ Set the theme of the editor

        """
        if theme.startswith('ace/theme'):
            self._theme = theme
        else:
            self._theme = "ace/theme/"+theme
        self.theme_changed.emit(self._theme)

    def theme(self):
        """ Return the theme of the editor

        """
        return self._theme

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
        event = EVENT_TEMPLATE.substitute(func=_func, args=_args, target=_target,
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

    def generate_html(self):
        """ Generate the html code for the ace editor

        """
        _text = self.text()
        _mode = self.mode()
        _theme = self.theme()
        _r_path = "file://" + os.path.abspath('ace/')
        _events = '\n'.join(self._events)
        _bindings = '\n'.join(self._bindings)
        return HTML_TEMPLATE.substitute(text=_text, mode=_mode, theme=_theme,
                                        resource_path=_r_path, events=_events,
                                        bindings=_bindings)
