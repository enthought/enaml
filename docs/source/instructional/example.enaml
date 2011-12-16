#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import math
import random
import datetime
Window:

    title << model.window_title

    Panel:
        HGroup:

            style.cls = "stretch"

            Group my_group:
                direction = 'top_to_bottom'
                PushButton:
                    style.cls = "expanding"
                    text << "clickme!" if not self.down else "I'm down!"
                    clicked >> model.update_style()

                PushButton pb2:
                    style.cls = "expanding"
                    text = "shuffle"
                    clicked >> setattr(rb1, 'checked', True)

                PushButton static:
                    style.cls = "expanding error_colors"
                    text = "static"
                    clicked >> model.print_msg(msg)

                CheckBox cb1:
                    text = "A simple text box"
                    toggled >> setattr(self, 'text', model.randomize(self.text))


            Html:
                source << ("<center><h1>Hello Enaml!</h1></center><br>" * cmbx.value
                           if not static.down else
                           "<center><h1>Static Down!</h1></center>")

            VGroup:
                style.cls = "fixed"
                Panel:
                    HGroup:
                        direction = 'right_to_left'
                        RadioButton rb1:
                            style.cls = "stretch"
                            text = 'rb1'
                            toggled >> print('rb1:', self.checked)
                        RadioButton:
                            style.cls = "stretch"
                            text = 'rb2'
                            toggled >> print('rb2:', self.checked)
                        RadioButton:
                            style.cls = "stretch"
                            text = 'rb3'
                            toggled >> print('rb3:', self.checked)
                        RadioButton:
                            style.cls = "stretch"
                            text = 'rb4'
                            toggled >> print('rb4:', self.checked)
                Panel:
                    HGroup:
                        RadioButton:
                            style.cls = "stretch"
                            text = 'rb1'
                        RadioButton:
                            style.cls = "stretch"
                            text = 'rb2'
                        RadioButton:
                            style.cls = "stretch"
                            text = 'rb3'
                        RadioButton:
                            style.cls = "stretch"
                            text = 'rb4'

                Calendar:
                    minimum_date = datetime.date(1970, 1, 1)
                    activated >> print('activated', msg.new)
                    selected >> print('selected', msg.new)
                    date >> print('new date', msg.new)

                HGroup:
                    ComboBox cmbx:
                        items = range(100)
                        value = 1
                        selected >> print('selected', msg.new)

                HGroup:
                    style.border_left_width = 20
                    style.border_top_width = 20
                    style.border_bottom_width = 20
                    Label:
                        text = 'min:'
                    Label:
                        text << str(sb.low)
                    Label:
                        text = 'max:'
                    Label:
                        text << str(sb.high)
                    Label:
                        text = 'val:'
                    Label:
                        text << str(sb.value)

                HGroup:
                    CheckBox wrap_box:
                        style.cls << "error_colors" if mf.error else "normal_colors"
                        text = 'Allow wrap:'
                        toggled >> setattr(cmbx, 'value', 42)
                    SpinBox sb:
                        prefix << 'Foo ' if wrap_box.checked else 'Bar '
                        suffix << ' lb' if wrap_box.checked else ' kg'
                        wrap := wrap_box.checked
                        special_value_text = "Auto"
                        step = 2
                        low << -20 if not self.wrap else 0
                        high = 20

                HGroup:
                    Label:
                        text = "A Slider!"
                        style.cls = "no_stretch"
                    Slider:
                        value = 10
                        value >> print(self.value)
                        to_slider = lambda val: math.log10(val)
                        from_slider = lambda val: 10 ** val
                        tick_interval = 0.5
                        orientation << ('vertical'
                                        if wrap_box.checked else
                                        'horizontal')

                Field mf:
                    to_string = str
                    from_string = lambda val: int(val) if val else 0
                    value = 0
                    style.background_color << "error" if self.error else "nocolor"
