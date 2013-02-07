/*-----------------------------------------------------------------------------
|  Copyright (c) 2012, Enthought, Inc.
|  All rights reserved.
|----------------------------------------------------------------------------*/
#include <iostream>
#include "pythonhelpers.h"


using namespace PythonHelpers;


extern "C" {


static PyObject* _atom_member_count;
static PyObject* _undefined_name;
static PyObject* _notify;


typedef struct {
    PyObject_HEAD
    Py_ssize_t count;
    PyObject** data;
} CAtom;


typedef struct {
    PyObject_HEAD
    int flags;
    Py_ssize_t index;
    PyObject* name;
} CMember;


enum CMemberFlag
{
    MemberHasDefault = 0x1,
    MemberHasValidate = 0x2,
    MemberIsListenable = 0x4,
};


static PyObject*
CAtom_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    Py_ssize_t count = 0;
    PyObjectPtr py_count_ptr( PyObject_GetAttr(
        reinterpret_cast<PyObject*>( type ), _atom_member_count
    ) );
    if( !py_count_ptr )
        return 0;
    count = PyInt_AsSsize_t( py_count_ptr.get() );
    if( count < 0 )
    {
        if( PyErr_Occurred() )
            return 0;
        count = 0;
    }
    PyObjectPtr self_ptr( PyType_GenericNew( type, args, kwargs ) );
    if( !self_ptr )
        return 0;
    CAtom* atom = reinterpret_cast<CAtom*>( self_ptr.get() );
    atom->data = reinterpret_cast<PyObject**>( PyMem_MALLOC( sizeof( PyObject* ) * count ) );
    if( !atom->data )
        return PyErr_NoMemory();
    memset( atom->data, 0, sizeof( PyObject* ) * count );
    atom->count = count;
    return self_ptr.release();
}


static void
CAtom_clear( CAtom* self )
{
    Py_ssize_t count = self->count;
    for( Py_ssize_t i = 0; i < count; ++i )
    {
        Py_CLEAR( self->data[ i ] );
    }
}


static int
CAtom_traverse( CAtom* self, visitproc visit, void* arg )
{
    Py_ssize_t count = self->count;
    for( Py_ssize_t i = 0; i < count; ++i )
    {
        Py_VISIT( self->data[ i ] );
    }
    return 0;
}


static void
CAtom_dealloc( CAtom* self )
{
    PyObject_GC_UnTrack( self );
    CAtom_clear( self );
    PyMem_FREE( self->data );
    self->ob_type->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
CAtom_notify( CAtom* self, PyObject* args )
{
    // Implement in a subclass to do any necessary work.
    Py_RETURN_NONE;
}


static PyMethodDef
CAtom_methods[] = {
    { "notify", ( PyCFunction )CAtom_notify, METH_VARARGS,
      "Notify any listeners that a member value has changed" },
    { 0 } // sentinel
};


PyTypeObject CAtom_Type = {
    PyObject_HEAD_INIT( &PyType_Type )
    0,                                      /* ob_size */
    "catom.CAtom",                          /* tp_name */
    sizeof( CAtom ),                        /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)CAtom_dealloc,              /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)0,                            /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)0,                         /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_HAVE_GC, /* tp_flags */
    0,                                      /* Documentation string */
    (traverseproc)CAtom_traverse,           /* tp_traverse */
    (inquiry)CAtom_clear,                   /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)CAtom_methods,     /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)CAtom_new,                     /* tp_new */
    (freefunc)PyObject_GC_Del,              /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static PyObject*
CMember_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObjectPtr self_ptr( PyType_GenericNew( type, args, kwargs ) );
    if( !self_ptr )
        return 0;
    Py_INCREF( _undefined_name );
    reinterpret_cast<CMember*>( self_ptr.get() )->name = _undefined_name;
    return self_ptr.release();
}


static void
CMember_dealloc( CMember* self )
{
    Py_DECREF( self->name );
    self->ob_type->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
CMember__get__( PyObject* self, PyObject* owner, PyObject* type )
{
    if( !owner )
    {
        Py_INCREF( self );
        return self;
    }
    if( !PyObject_TypeCheck( owner, &CAtom_Type ) )
        return py_expected_type_fail( owner, "CAtom" );
    CAtom* atom = reinterpret_cast<CAtom*>( owner );
    CMember* member = reinterpret_cast<CMember*>( self );
    if( member->index >= atom->count )
        return py_no_attr_fail( owner, PyString_AsString( member->name ) );
    PyObject* value = atom->data[ member->index ];
    if( value )
    {
        Py_INCREF( value );
        return value;
    }
    if( member->default_func )
    {
        value = PyObject_CallFunctionObjArgs( member->default_func, owner, member->name, 0 );
        if( !value )
            return 0;
    }
    else
    {
        value = Py_None;
        Py_INCREF( value );
    }
    atom->data[ member->index ] = value;
    Py_INCREF( value );
    return value;
}


static int
CMember__set__( PyObject* self, PyObject* owner, PyObject* value )
{
    if( !PyObject_TypeCheck( owner, &CAtom_Type ) )
    {
        py_expected_type_fail( owner, "CAtom" );
        return -1;
    }
    CAtom* atom = reinterpret_cast<CAtom*>( owner );
    CMember* member = reinterpret_cast<CMember*>( self );
    if( member->index >= atom->count )
    {
        py_no_attr_fail( owner, PyString_AsString( member->name ) );
        return -1;
    }
    // `value` is currently null or a borrowed reference
    if( value && member->validate_func )
    {
        value = PyObject_CallFunctionObjArgs( member->validate_func, owner, member->name, value, 0 );
        if( !value )
            return 0;
        // `value` is now an owned reference
    }
    else
    {
        // take an owned reference for storing `value` in the struct
        Py_XINCREF( value );
    }
    // swap before decrefing since that can have side effects
    PyObject* old = atom->data[ member->index ];
    atom->data[ member->index ] = value;
    if( member->listenable )
    {
        PyObject* oldval = old == 0 ? Py_None : old;
        PyObject* newval = value == 0 ? Py_None : value;
        if( !PyObject_CallMethodObjArgs( owner, _notify, member->name, oldval, newval, 0 ) )
        {
            Py_XDECREF( old );
            return -1;
        }
    }
    Py_XDECREF( old );
    return 0;
}


static PyObject*
CMember_get_name( CMember* self, void* context )
{
    Py_INCREF( self->name );
    return self->name;
}


static int
CMember_set_name( CMember* self, PyObject* value, void* context )
{
    if( !PyString_Check( value ) )
    {
        py_expected_type_fail( value, "string" );
        return -1;
    }
    PyObject* old = self->name;
    self->name = value;
    Py_INCREF( value );
    Py_DECREF( old );
    return 0;
}


static PyObject*
CMember_get_index( CMember* self, void* context )
{
    return PyInt_FromSsize_t( self->index );
}


static int
CMember_set_index( CMember* self, PyObject* value, void* context )
{
    if( !value )
    {
        self->index = 0;
        return 0;
    }
    if( !PyInt_Check( value ) )
    {
        py_expected_type_fail( value, "int" );
        return -1;
    }
    Py_ssize_t index = PyInt_AsSsize_t( value );
    if( index < 0 && PyErr_Occurred() )
        return -1;
    self->index = index < 0 ? 0 : index;
    return 0;
}


static PyObject*
CMember_get_default_func( CMember* self, void* context )
{
    if( !self->default_func )
        Py_RETURN_NONE;
    Py_INCREF( self->default_func );
    return self->default_func;
}


static int
CMember_set_default_func( CMember* self, PyObject* value, void* context )
{
    value = value == Py_None ? 0 : value;
    if( value && !PyCallable_Check( value ) )
    {
        py_expected_type_fail( value, "callable" );
        return -1;
    }
    PyObject* old = self->default_func;
    self->default_func = value;
    Py_XINCREF( value );
    Py_XDECREF( old );
    return 0;
}


static PyObject*
CMember_get_validate_func( CMember* self, void* context )
{
    if( !self->validate_func )
        Py_RETURN_NONE;
    Py_INCREF( self->validate_func );
    return self->validate_func;
}


static int
CMember_set_validate_func( CMember* self, PyObject* value, void* context )
{
    value = value == Py_None ? 0 : value;
    if( value && !PyCallable_Check( value ) )
    {
        py_expected_type_fail( value, "callable" );
        return -1;
    }
    PyObject* old = self->validate_func;
    self->validate_func = value;
    Py_XINCREF( value );
    Py_XDECREF( old );
    return 0;
}


static PyObject*
CMember_get_listenable( CMember* self, void* context )
{
    if( self->listenable )
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


static int
CMember_set_listenable( CMember* self, PyObject* value, void* context )
{
    if( value == Py_True )
        self->listenable = true;
    else if( value == Py_False )
        self->listenable = false;
    else
    {
        py_expected_type_fail( value, "bool" );
        return -1;
    }
    return 0;
}


static PyGetSetDef
CMember_getset[] = {
    { "_member_name",
      ( getter )CMember_get_name,
      ( setter )CMember_set_name,
      "Get and set the name to which the member is bound. Use with extreme caution!" },
    { "_member_index",
      ( getter )CMember_get_index,
      ( setter )CMember_set_index,
      "Get and set the index to which the member is bound. Use with extreme caution!" },
    { "default_func",
      ( getter )CMember_get_default_func,
      ( setter )CMember_set_default_func,
      "Get and set the default function for the member. Must be callable or None." },
    { "validate_func",
      ( getter )CMember_get_validate_func,
      ( setter )CMember_set_validate_func,
      "Get and set the validate function for the member. Must be callable or None." },
    { "listenable",
      ( getter )CMember_get_listenable,
      ( setter )CMember_set_listenable,
      "Get and set whether the member is listenable. Must be a bool." },
    { 0 } // sentinel
};


PyTypeObject CMember_Type = {
    PyObject_HEAD_INIT( &PyType_Type )
    0,                                      /* ob_size */
    "catom.CMember",                         /* tp_name */
    sizeof( CMember ),                       /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)CMember_dealloc,             /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)0,                            /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)0,                         /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /* tp_flags */
    0,                                      /* Documentation string */
    (traverseproc)0,                        /* tp_traverse */
    (inquiry)0,                             /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)0,                 /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    CMember_getset,                          /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)CMember__get__,            /* tp_descr_get */
    (descrsetfunc)CMember__set__,            /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)CMember_new,                    /* tp_new */
    (freefunc)PyObject_Del,                 /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static PyMethodDef
catom_methods[] = {
    { 0 } // Sentinel
};


PyMODINIT_FUNC
initcatom( void )
{
    PyObject* mod = Py_InitModule( "catom", catom_methods );
    if( !mod )
        return;
    _atom_member_count = PyString_FromString( "_atom_member_count" );
    if( !_atom_member_count )
        return;
    _undefined_name = PyString_FromString( "<undefined>" );
    if( !_undefined_name )
        return;
    _notify = PyString_FromString( "notify" );
    if( !_notify )
        return;
    if( PyType_Ready( &CAtom_Type ) )
        return;
    if( PyType_Ready( &CMember_Type ) )
        return;
    Py_INCREF( &CAtom_Type );
    Py_INCREF( &CMember_Type );
    PyModule_AddObject( mod, "CAtom", reinterpret_cast<PyObject*>( &CAtom_Type ) );
    PyModule_AddObject( mod, "CMember", reinterpret_cast<PyObject*>( &CMember_Type ) );
}


} // extern "C"

