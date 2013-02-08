/*-----------------------------------------------------------------------------
|  Copyright (c) 2012, Enthought, Inc.
|  All rights reserved.
|----------------------------------------------------------------------------*/
#include <iostream>
#include "pythonhelpers.h"


using namespace PythonHelpers;


extern "C" {


static PyObject* _atom_members;
static PyObject* _undefined_name;
static PyObject* _notify;
static PyObject* _default;
static PyObject* _validate;


typedef struct {
    PyObject_HEAD
    size_t notifybits;
    Py_ssize_t count;
    PyObject** data;
} CAtom;


typedef struct {
    PyObject_HEAD
    size_t flags;
    Py_ssize_t index;
    PyObject* name;
} CMember;


#define ATOM_BIT 0
#define MEMBER_BITS_OFFSET 1


static const size_t SIZE_T_BITS = sizeof( size_t ) * 8;


enum CMemberFlag
{
    MemberHasDefault = 0x1,
    MemberHasValidate = 0x2
};


inline bool
get_notify_bit( CAtom* atom, size_t bit )
{
    size_t block = bit / SIZE_T_BITS;
    size_t offset = bit % SIZE_T_BITS;
    size_t bits = reinterpret_cast<size_t>( atom->data[ atom->count + block ] );
    return bits & ( 1 << offset );
}


inline void
set_notify_bit( CAtom* atom, size_t bit, bool set )
{
    size_t block = bit / SIZE_T_BITS;
    size_t offset = bit % SIZE_T_BITS;
    size_t bits = reinterpret_cast<size_t>( atom->data[ atom->count + block ] );
    if( set )
        bits |= ( 1 << offset );
    else
        bits &= ~( 1 << offset );
    atom->data[ atom->count + block ] = reinterpret_cast<PyObject*>( bits );
}


static PyObject*
CAtom_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    Py_ssize_t count = 0;
    PyDictPtr members_ptr( PyObject_GetAttr(
        reinterpret_cast<PyObject*>( type ), _atom_members
    ) );
    if( !members_ptr )
        return 0;
    if( !members_ptr.check_exact() )
        return py_expected_type_fail( members_ptr.get(), "dict" );
    count = members_ptr.size();
    PyObjectPtr self_ptr( PyType_GenericNew( type, args, kwargs ) );
    if( !self_ptr )
        return 0;
    CAtom* atom = reinterpret_cast<CAtom*>( self_ptr.get() );
    atom->count = count;
    if( count > 0 )
    {
        size_t blocks = count / SIZE_T_BITS;
        size_t extra = count % SIZE_T_BITS;
        if( extra > 0 )
            ++blocks;
        void* data = PyMem_MALLOC( sizeof( PyObject* ) * ( count + blocks )  );
        if( !data )
            return PyErr_NoMemory();
        memset( data, 0, sizeof( PyObject* ) * ( count + blocks ) );
        atom->data = reinterpret_cast<PyObject**>( data );
    }
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
    if( self->data )
        PyMem_FREE( self->data );
    self->ob_type->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
CAtom_is_notification_enabled( CAtom* self, PyObject* args )
{
    if( get_notify_bit( self, ATOM_BIT ) )
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


static PyObject*
CAtom_set_notification_enabled( CAtom* self, PyObject* value )
{
    if( value == Py_True )
    {
        set_notify_bit( self, ATOM_BIT, true );
        Py_RETURN_NONE;
    }
    if( value == Py_False )
    {
        set_notify_bit( self, ATOM_BIT, false );
        Py_RETURN_NONE;
    }
    return py_expected_type_fail( value, "bool" );
}



static PyObject*
CAtom_notify( CAtom* self, PyObject* args )
{
    // Reimplement in a subclass as needed.
    Py_RETURN_NONE;
}


static PyObject*
CAtom_sizeof( CAtom* self, PyObject* args )
{
    Py_ssize_t size = self->ob_type->tp_basicsize;
    size += sizeof( PyObject* ) * self->count;
    return PyInt_FromSsize_t( size );
}


static PyMethodDef
CAtom_methods[] = {
    { "is_notification_enabled",
      ( PyCFunction )CAtom_is_notification_enabled, METH_NOARGS,
      "Get whether notification is enabled for the atom." },
    { "set_notification_enabled",
      ( PyCFunction )CAtom_set_notification_enabled, METH_O,
      "Set whether notification is enabled for the atom." },
    { "notify", ( PyCFunction )CAtom_notify, METH_VARARGS,
      "Called when a notifying member is changed. Reimplement as needed." },
    { "__sizeof__", ( PyCFunction )CAtom_sizeof, METH_NOARGS,
      "__sizeof__() -> size of object in memory, in bytes" },
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
    CMember* member = reinterpret_cast<CMember*>( self_ptr.get() );
    Py_INCREF( _undefined_name );
    member->name = _undefined_name;
    // Check for `default` and `validate` methods. Don't do the check
    // on the type, because a subclass which defines a slot but never
    // fills it will still return True.
    if( PyObject_HasAttr( self_ptr.get(), _default ) )
        member->flags |= MemberHasDefault;
    if( PyObject_HasAttr( self_ptr.get(), _validate ) )
        member->flags |= MemberHasValidate;
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
    if( member->flags & MemberHasDefault )
    {
        value = PyObject_CallMethodObjArgs( self, _default, owner, member->name, 0 );
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
    if( value && ( member->flags & MemberHasValidate ) )
    {
        value = PyObject_CallMethodObjArgs( self, _validate, owner, member->name, value, 0 );
        if( !value )
            return -1;
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
    if( get_notify_bit( atom, ATOM_BIT ) && get_notify_bit( atom, member->index + MEMBER_BITS_OFFSET ) )
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
CMember_is_notification_enabled( CMember* self, PyObject* atom )
{
    if( !PyObject_TypeCheck( atom, &CAtom_Type ) )
        return py_expected_type_fail( atom, "CAtom" );
    if( get_notify_bit( reinterpret_cast<CAtom*>( atom ), self->index + MEMBER_BITS_OFFSET ) )
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


static PyObject*
CMember_set_notification_enabled( CMember* self, PyObject* args )
{
    PyObject* atom;
    PyObject* setbit;
    if( !PyArg_ParseTuple( args, "OO", &atom, &setbit ) )
        return 0;
    if( !PyObject_TypeCheck( atom, &CAtom_Type ) )
        return py_expected_type_fail( atom, "CAtom" );
    if( setbit == Py_True )
        set_notify_bit( reinterpret_cast<CAtom*>( atom ), self->index + MEMBER_BITS_OFFSET, true );
    else if( setbit == Py_False )
        set_notify_bit( reinterpret_cast<CAtom*>( atom ), self->index + MEMBER_BITS_OFFSET, false );
    else
        return py_expected_type_fail( setbit, "bool" );
    Py_RETURN_NONE;
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


static PyMethodDef
CMember_methods[] = {
    { "is_notification_enabled",
      ( PyCFunction )CMember_is_notification_enabled, METH_O,
      "Get whether notification is enabled for the member." },
    { "set_notification_enabled",
      ( PyCFunction )CMember_set_notification_enabled, METH_VARARGS,
      "Set whether notification is enabled for the atom." },
    { 0 } // sentinel
};


static PyGetSetDef
CMember_getset[] = {
    { "_name",
      ( getter )CMember_get_name, ( setter )CMember_set_name,
      "Get and set the name to which the member is bound. Use with extreme caution!" },
    { "_index",
      ( getter )CMember_get_index, ( setter )CMember_set_index,
      "Get and set the index to which the member is bound. Use with extreme caution!" },
    { 0 } // sentinel
};


PyTypeObject CMember_Type = {
    PyObject_HEAD_INIT( &PyType_Type )
    0,                                      /* ob_size */
    "catom.CMember",                        /* tp_name */
    sizeof( CMember ),                      /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)CMember_dealloc,            /* tp_dealloc */
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
    (struct PyMethodDef*)CMember_methods,   /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    CMember_getset,                         /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)CMember__get__,           /* tp_descr_get */
    (descrsetfunc)CMember__set__,           /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)CMember_new,                   /* tp_new */
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
    _atom_members = PyString_FromString( "_atom_members" );
    if( !_atom_members )
        return;
    _undefined_name = PyString_FromString( "<undefined>" );
    if( !_undefined_name )
        return;
    _notify = PyString_FromString( "notify" );
    if( !_notify )
        return;
    _default = PyString_FromString( "default" );
    if( !_default )
        return;
    _validate = PyString_FromString( "validate" );
    if( !_validate )
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

