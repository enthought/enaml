from enaml.core.api import Atom, Observable, Member, Int, Float, List, Tuple


class Bar(Atom):

    baz = Member()

    ham = Float(43.4)


class Foo(Observable):

    a = Int(2)

    b = Member(factory=dict)

    c = List()

    d = Tuple()

    def notify(self, change):
        print 'notify:\t\t', change
        super(Foo, self).notify(change)


class Listener(object):

    def target(self, change):
        print 'listener:\t', change


def printer(change):
    print 'printer:\t', change


listener = Listener()

f = Foo()
f.observe('a', printer)
f.observe('c|d', printer, regex=True)
f.observe('.*', listener.target, regex=True)

b = Bar()
print 'Bar defaults:', b.baz, b.ham
print

print '-----'
print 'start'
print '-----'
print

f.a = 12
f.b = 'foostring'
f.c = range(2)
f.d = (1, 2, 3)

print
print 'suppress `c`'
with f.suppress_notifications('c'):
    f.c = [0, 0, 0]
    f.a = 42
print 'end suppress `c`'

print
print 'suppress all'
with f.suppress_notifications():
    f.a = 19
    f.b = object()
    f.c = range(4)
    f.d = (5, 4, 3)
print 'end suppress all'

print
print 'deleting listener'
del listener

del f.a
del f.b

print
print 'unobserving'
f.unobserve('.*', printer, regex=True)
print

del f.c
del f.d
print f.a, f.b, f.c, f.d
print
print '---'
print 'end'
print '---'

