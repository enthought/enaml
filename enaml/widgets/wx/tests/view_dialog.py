#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory


custom = StringIO("""
from enaml.dialogs import information, error, warning, question
from enaml.enums import Buttons

Dialog dialog:
    title = 'My Dialog'
    
    Panel:
        VGroup:
            HGroup:
                ComboBox combo_buttons:
                    items = [Buttons.OK, Buttons.OK_CANCEL, Buttons.YES_NO]
                    value = self.items[0]
                
                ComboBox combo_icon:
                    items = [information, error, warning, question]
                    value = self.items[0]
                    to_string = lambda x: x.func_name.capitalize()
                            
            PushButton:
                text = 'Show custom dialog'
                clicked >> combo_icon.value('A message...', combo_buttons.value)
                #clicked >> error('Message')
""")

if __name__ == '__main__':
    # Manually put __toolkit__ into the namespace.
    fact = EnamlFactory(custom)
    view = fact(__toolkit__=fact._toolkit)
    view.show()
