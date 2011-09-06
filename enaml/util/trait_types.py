from traits.api import TraitType, Interface


class SubClass(TraitType):

    def __init__(self, cls):
        super(SubClass, self).__init__()
        if issubclass(cls, Interface):
            self.info = (cls, True)
        else:
            self.info = (cls, False)

    def validate(self, obj, name, value):
        cls, interface = self.info
        if interface:
            if issubclass(value.__implements__, cls):
                return value
        else:
            if issubclass(value, cls):
                return value
        if interface:
            msg = 'Class must be and implementor of %s.' % cls
            raise TypeError(msg)
        else:
            msg = 'Class must be a subclass of %s.' % cls
            raise TypeError(msg)

