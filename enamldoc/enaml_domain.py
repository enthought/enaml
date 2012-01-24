# -*- coding: utf-8 -*-
"""
    sphinx.domains.enaml
    ~~~~~~~~~~~~~~~~~~~~~

    The Enaml domain.
    (Subclassed extensively from the Python domain)

    :copyright: Copyright 2012 by Enthought, Inc
"""

from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType, Index
from sphinx.util.nodes import make_refnode

# Subclass objects defined in the Python domain
from sphinx.domains.python import PythonDomain, PyModulelevel, PyClasslike, PyClassmember
from sphinx.domains.python import PyModule,  PyXRefRole

## class EnamlDefn(PyClasslike):
##     """
##     Enaml defn formatting particulars
##     """

##     def get_signature_prefix(self, sig):
##         return 'Enaml defn '

##     def get_index_text(self, modname, name_cls):
##         return _('%s (Enaml defn)') % name_cls[0]

class EnamlDeclaration(PyClasslike):
    """
    Enaml Declaration formatting particulars.
    """

    def get_signature_prefix(self, sig):
        ## import pdb; pdb.set_trace()
        return 'Enaml declared component '

    def get_index_text(self, modname, name_cls):
        """return a signature to appear in the index listing"""

        if modname is not None:
            # if the declaration was in a module, report it 
            return _('%s (Enaml declaration in %s)') % (name_cls[0], modname)
        else:
            # give a simple description if the directive is self-contained
            return _('%s (Enaml declaration)') % (name_cls[0])

class EnamlDomain(PythonDomain):
    """Enaml language domain."""
    name = 'enaml'
    label = 'Enaml'
    object_types = {
        'enaml_module':    ObjType(l_('enaml module'),    'mod', 'obj'),
        ## 'enaml_defn':      ObjType(l_('enaml built-in'),  'enaml_comp', 'obj'),
        'enaml_decl':      ObjType(l_('enaml derived'),   'enaml_comp', 'obj'),
        }

    directives = {
        ## 'enaml_defn':      EnamlDefn,
        'enaml_decl':      EnamlDeclaration,
        'enaml_module':    PyModule,
        }
    roles = {
        'mod':   PyXRefRole(),
        'enaml_comp': PyXRefRole(),
        }
