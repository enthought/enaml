

class Message(object):

    __slots__ = ('obj', 'name', 'old', 'new')

    def __init__(self, obj, name, old, new):
        self.obj = obj
        self.name = name
        self.old = old
        self.new = new

