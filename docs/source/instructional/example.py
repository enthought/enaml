#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
#!/usr/bin/env python

import random

from traits.api import HasTraits, Str

from enaml.factory import EnamlFactory
from enaml.color import Color
from enaml.style_sheet import style

colors = Color.color_map.keys()

class Model(HasTraits):
    """ Traits model to interact with the enaml widget

    """

    message = Str('Foo Model Message!')
    window_title = Str('Window Title!')

    def print_msg(self, args):
        """ Print a message to standard output.

        """
        print self.message, args

    def randomize(self, string):
        """ Suffle the letters in the string.

        """
        l = list(string)
        random.shuffle(l)
        return ''.join(l)

    def update_style(self):
        """ Update the style of the widget

        """
        # create a new style name .error_colors
        # with random foreground/background colors
        sty = style('.error_colors',
            color = random.choice(colors),
            background_color=random.choice(colors),
        )
        # update the vew style sheet with the new style
        view.style_sheet.update(sty)


fact = EnamlFactory('./example.enaml')

view = fact(model=Model())

view.show()

