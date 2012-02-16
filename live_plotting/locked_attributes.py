import threading


class LockedAttributes(object):
    def __init__(self):
        def setattr(self, attr, value):
            with self.attr_lock:
                self.__dict__[attr] = value
        self.attr_lock = threading.Lock()
        self.__attr__ = setattr
