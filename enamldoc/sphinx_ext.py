# -*- coding: utf-8 -*-
"""
    enamldoc
    ~~~~~~~~

    Automatically insert docstrings for enaml built-in and derived widgets and
    components, mirroring and borrowing heavily from the autodoc
    extension. Enaml widgets and components are Python objects that are
    imported in the enaml.imports() context

"""

import re
import inspect
from types import FunctionType, BuiltinFunctionType

from sphinx.application import ExtensionError
from sphinx.util.inspect import getargspec
from sphinx.ext.autodoc import Documenter
from sphinx.ext.autodoc import ModuleLevelDocumenter
from sphinx.ext.autodoc import DocstringSignatureMixin
from sphinx.ext.autodoc import ModuleDocumenter

from enaml_domain import EnamlDomain

from enthought.debug.api import called_from

from enaml.core.import_hooks import EnamlImporter
EnamlImporter.install()

from enaml.core.factory import EnamlDeclaration

class EnamlComponentDocumenter(ModuleLevelDocumenter):
    """ Enaml component documenter class

    The main purpose of this class is to be distinct from Python components and
    change the domain in the Documenter instance to 'enaml'

    """

    def __init__(self, directive, name, indent=u''):
        """ Need to override the parent __init__ so that we can set
        self.domain, which is an instance variable.

        """

        super(EnamlComponentDocumenter, self).__init__(directive, name, indent)
        self.domain = 'enaml'

    def check_module(self):
        """ For Enaml objects, the module name returned by
        self.object.__module__ points to the enaml parsing compiler, rather
        than the logical module name stored in self.modname. Therefore, this
        check will verify that the module points to
        enaml.parsing.enaml_compiler.

        Note - after a fix to correct the .__module__ and .__file__ attributes,
        this method will not be necessary and will need to be deleted.

        """

        #import pdb; pdb.set_trace()
        return self.get_attr(self.object, '__module__', None) == \
            'enaml.parsing.enaml_compiler'

    def format_signature(self):
        """ Thin method for debugging signature formatting.

        """

        super(EnamlComponentDocumenter, self).format_signature()


class EnamlDocstringSignatureMixin(DocstringSignatureMixin):
    """ Mixin for FunctionDocumenter and MethodDocumenter to provide the
    feature of reading the signature from the docstring.

    identical to the autodoc.DocstringSignatureMixin it subclasses and included
    here as an indicator of a possible future avenue for working with docstring
    signatures in enaml -- possibly to replace refactordoc.

    """

    pass


class EnamlDeclarationDocumenter(EnamlDocstringSignatureMixin,
                                 EnamlComponentDocumenter):
    """ Specialized Documenter subclass for Enaml declarations.

    """

    objtype = 'enaml_decl'
    member_order = 35

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, EnamlDeclaration)

    def format_args(self):
        """ Derivation is shown where normally arguments are shown in a
        function prototype.

        """

        ## import pdb; pdb.set_trace()
        return ' (derives from {0})'.format(self.object.__base__)

    def document_members(self, all_members=False):
        pass


## class EnamlDefnDocumenter(EnamlDocstringSignatureMixin,
##                           EnamlComponentDocumenter):
##     """ Specialized Documenter subclass for Enaml defns.

##     """

##     objtype = 'enaml_defn'
##     member_order = 32

##     @classmethod
##     def can_document_member(cls, member, membername, isattr, parent):
##         return isinstance(member, EnamlDefn)

##     def format_args(self):
##         ## if inspect.isbuiltin(self.object) or \
##         ##        inspect.ismethoddescriptor(self.object):
##         ##     # cannot introspect arguments of a C function or method
##         ##     return None
##         try:
##             argspec = getargspec(self.object.__func__)
##         except TypeError:
##             # if a class should be documented as function (yay duck
##             # typing) we try to use the constructor signature as function
##             # signature without the first argument.
##             try:
##                 argspec = getargspec(self.object.__new__)
##             except TypeError:
##                 argspec = getargspec(self.object.__init__)
##                 if argspec[0]:
##                     del argspec[0][0]
##         args = inspect.formatargspec(*argspec)
##         # escape backslashes for reST
##         args = args.replace('\\', '\\\\')
##         return args

##     def document_members(self, all_members=False):
##         """ We may want to use this in the future to include submembers of a
##         defn.

##         """
##         pass


class EnamlModuleDocumenter(ModuleDocumenter):
    """ Subclass of the module documenter for enaml autodocumenting.

    The main purpose of the subclass is to set the domain so that member
    directives are formed properly.

    """

    objtype = 'enaml_module'

    def __init__(self, directive, name, indent=u''):
        """ Need to override the parent __init__ so that we can set
        self.domain, which is an instance variable.

        """
        super(EnamlModuleDocumenter, self).__init__(directive, name, indent)
        self.domain = 'enaml'

    def get_object_members(self, want_all):
        """ Shim method for debugging """
        ## print "EnamlModuleDocumenter: self.options.members:\n {0}".format(
        ##     self.options.members)
        ## import pdb; pdb.set_trace()
        return super(EnamlModuleDocumenter, self).get_object_members(want_all)


def add_documenter(cls):
    """ Register a new Documenter.

    This autodoc function is overridden here solely for the sake of the proper
    error message.

    """
    if not issubclass(cls, Documenter):
        raise ExtensionError('enamldoc documenter %r must be a subclass '
                             'of autodoc.Documenter' % cls)
    AutoDirective._registry[cls.objtype] = cls


def setup(app):
    """ enamldoc extension setup function.

    The setup function is called by Sphinx when loading extensions.  app is the
    instance of the calling app, Sphinx in this case.

    enamldoc borrows heavily from autodoc, so additions to setup and
    configuration are minimal.

    """

    app.add_autodocumenter(EnamlModuleDocumenter)
    app.add_autodocumenter(EnamlDeclarationDocumenter)
    ## app.add_autodocumenter(EnamlDefnDocumenter)

    # import the Enaml domain into the sphinx app
    app.domains['enaml'] = EnamlDomain


    ## app.add_event('enamldoc-import-component')
    ## app.add_event('enamldoc-process-component')


class testcls:
    """ test doc string """

    def __getattr__(self, x):
        return x

    def __setattr__(self, x, y):
        """Attr setter."""
