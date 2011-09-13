from traits.api import HasStrictTraits, Instance, on_trait_change

from ..style_node import StyleNode


NULL = object()

NO_OP = lambda *args, **kwargs: None


class WXStyleHandler(HasStrictTraits):

    style_node = Instance(StyleNode)

    style_dict = Instance(dict, ())

    @on_trait_change('style_node:tag_updated')
    def _tag_updated(self, tag):
        self._update_tag(tag)

    def _update_tag(self, tag, no_op=NO_OP):
        style_dict = self.style_dict
        if tag in style_dict:
            old = self.style_dict[tag]
        else:
            old = NULL
        new = self.style_node.get_tag(tag)
        if old != new:
            style_dict[tag] = new
            name = 'style_%s' % tag
            getattr(self, name, no_op)(new)

