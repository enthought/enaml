#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Str, Range, on_trait_change

import enaml
from enaml.stdlib.sessions import simple_app
from enaml.qt.qt_local_server import QtLocalServer


class Person(HasTraits):
    """ A simple class representing a person object.

    """
    last_name = Str

    first_name = Str

    age = Range(low=0)

    @on_trait_change('age')
    def debug_print(self):
        """ Prints out a debug message whenever the person's age changes.

        """
        templ = "{first} {last} is {age} years old."
        s = templ.format(
            first=self.first_name, last=self.last_name, age=self.age,
        )
        print s


if __name__ == '__main__':
    with enaml.imports():
        from person_view import PersonView
    
    john = Person(first_name='John', last_name='Doe', age=42)
    app = simple_app(
        'john', 'A view of the Person john', PersonView, person=john
    ) 

    server = QtLocalServer(app)
    client = server.local_client()
    client.start_session('john')
    server.start()

