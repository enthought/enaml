import sys


def _show_dialog(caller_frame, msg_type, *args, **kwargs):
    toolkit = caller_frame.f_globals['__toolkit__']
    try:
        dialog = toolkit.utils[msg_type]
    except (KeyError, AttributeError):
        raise
    else:
        dialog(*args, **kwargs)

def error(*args, **kwargs):
    frame = sys._getframe(1)
    _show_dialog(frame, 'error', *args, **kwargs)

def warning(*args, **kwargs):
    frame = sys._getframe(1)
    _show_dialog(frame, 'warning', *args, **kwargs)

def question(*args, **kwargs):
    frame = sys._getframe(1)
    _show_dialog(frame, 'question', *args, **kwargs)

def information(*args, **kwargs):
    frame = sys._getframe(1)
    _show_dialog(frame, 'information', *args, **kwargs)
