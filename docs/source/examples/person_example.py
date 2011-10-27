from traits.api import HasTraits, Str, Int
import enaml

with enaml.imports():
    from person_example import PersonWindow

class Person(HasTraits):
    name = Str
    age = Int
    address = Str

p = Person(name='Bob', age=18)
view = PersonWindow(p)
view.show()
