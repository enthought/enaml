/*-----------------------------------------------------------------------------
|  Copyright (c) 2012, Enthought, Inc.
|  All rights reserved.
|----------------------------------------------------------------------------*/
#include "pythonhelpers.h"


using namespace PythonHelpers;


#define ATOM_BIT        ( static_cast<size_t>( 0 ) )
#define INDEX_OFFSET    ( static_cast<size_t>( 1 ) )
#define SIZE_T_BITS     ( static_cast<size_t>( sizeof( size_t ) * 8 ) )


extern "C" {


// pre-allocated PyString objects
static PyObject* _atom_members;
static PyObject* _undefined;
static PyObject* _notify;
static PyObject* _default;
static PyObject* _validate;


/*
The data array for a CAtom is malloced large enough to hold `count`
number of object pointers PLUS enough extra pointers to use as a bit
field for storing whether notifications are enabled for the member.
For example, and atom with 10 members will have a `data` block of
44 bytes on a 32bit system: 40 bytes for the data, and 4 bytes for
the bit field. If the number of members increases to 32, the data
block will have 136 bytes: 128 for the data, and 8 bytes for the bit
field. The number of bits needed for the bitfield is always 1 greater
than the `count`, to account for the bit needed for the atom object
as a whole.
*/
typedef struct {
    PyObject_HEAD
    Py_ssize_t count;
    PyObject** data;
} CAtom;


typedef struct {
    PyObject_HEAD
    size_t flags;
    Py_ssize_t index;
    PyObject* name;
} CMember;


enum CMemberFlag
{
    MemberHasDefault = 0x1,
    MemberHasValidate = 0x2
};


static int
CMember_Check( PyObject* member );


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
    PyDictPtr members_ptr(
        PyObject_GetAttr( reinterpret_cast<PyObject*>( type ), _atom_members )
    );
    if( !members_ptr )
        return 0;
    if( !members_ptr.check_exact() )
        return py_expected_type_fail( members_ptr.get(), "dict" );
    PyObjectPtr self_ptr( PyType_GenericNew( type, args, kwargs ) );
    if( !self_ptr )
        return 0;
    Py_ssize_t count = members_ptr.size();
    if( count > 0 )
    {
        // count + 1 accounts for the atom bit.
        size_t blocks = ( count + 1 ) / SIZE_T_BITS;
        size_t extra = ( count + 1 ) % SIZE_T_BITS;
        if( extra > 0 )
            ++blocks;
        void* data = PyMem_MALLOC( sizeof( PyObject* ) * ( count + blocks ) );
        if( !data )
            return PyErr_NoMemory();
        memset( data, 0, sizeof( PyObject* ) * ( count + blocks ) );
        CAtom* atom = reinterpret_cast<CAtom*>( self_ptr.get() );
        atom->data = reinterpret_cast<PyObject**>( data );
        atom->count = count;
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
lookup_member( CAtom* self, PyObject* name )
{
    PyObjectPtr member(
        PyObject_GetAttr( reinterpret_cast<PyObject*>( self->ob_type ), name )
    );
    if( !member )
        return 0;
    if( !CMember_Check( member.get() ) )
        return py_expected_type_fail( member.get(), "CMember" );
    return member.release();
}


static PyObject*
CAtom_lookup_member( CAtom* self, PyObject* name )
{
    if( !PyString_Check( name ) )
        return py_expected_type_fail( name, "str" );
    return lookup_member( self, name );
}


static PyObject*
CAtom_notifications_enabled( CAtom* self, PyObject* args )
{
    PyObject* name = 0;
    if( !PyArg_ParseTuple( args, "|S", &name ) )
        return 0;
    if( self->count == 0 )
        Py_RETURN_FALSE;
    size_t notifybit = ATOM_BIT;
    if( name )
    {
        PyObjectPtr member( lookup_member( self, name ) );
        if( !member )
            return 0;
        CMember* cmember = reinterpret_cast<CMember*>( member.get() );
        notifybit = cmember->index + INDEX_OFFSET;
    }
    if( get_notify_bit( self, notifybit ) )
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


static PyObject*
toggle_notifications( CAtom* self, PyObject* args, bool enable )
{
    PyObject* name = 0;
    if( !PyArg_ParseTuple( args, "|S", &name ) )
        return 0;
    if( self->count == 0 )
        Py_RETURN_FALSE;
    size_t notifybit = ATOM_BIT;
    if( name )
    {
        PyObjectPtr member( lookup_member( self, name ) );
        if( !member )
            return 0;
        CMember* cmember = reinterpret_cast<CMember*>( member.get() );
        notifybit = cmember->index + INDEX_OFFSET;
    }
    set_notify_bit( self, notifybit, enable );
    Py_RETURN_TRUE;
}


static PyObject*
CAtom_enable_notifications( CAtom* self, PyObject* args )
{
    return toggle_notifications( self, args, true );
}


static PyObject*
CAtom_disable_notifications( CAtom* self, PyObject* args )
{
    return toggle_notifications( self, args, false );
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
    // count + 1 accounts for the atom bit
    size_t blocks = ( self->count + 1 ) / SIZE_T_BITS;
    size_t extra = ( self->count + 1 ) % SIZE_T_BITS;
    if( extra > 0 )
        ++blocks;
    Py_ssize_t size = self->ob_type->tp_basicsize;
    size += sizeof( PyObject* ) * ( self->count + blocks );
    return PyInt_FromSsize_t( size );
}


static PyMethodDef
CAtom_methods[] = {
    { "lookup_member",
      ( PyCFunction )CAtom_lookup_member, METH_O,
      "Lookup a member on the atom." },
    { "notifications_enabled",
      ( PyCFunction )CAtom_notifications_enabled, METH_VARARGS,
      "Get whether notification is enabled for the atom." },
    { "enable_notifications",
      ( PyCFunction )CAtom_enable_notifications, METH_VARARGS,
      "Enabled notifications for the atom." },
    { "disable_notifications",
      ( PyCFunction )CAtom_disable_notifications, METH_VARARGS,
      "Disable notifications for the atom." },
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
    member->name = _undefined;
    Py_INCREF( member->name );
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
    PyObjectPtr selfptr( self, true );
    if( !owner )
        return selfptr.release();
    if( !PyObject_TypeCheck( owner, &CAtom_Type ) )
        return py_expected_type_fail( owner, "CAtom" );
    CAtom* atom = reinterpret_cast<CAtom*>( owner );
    CMember* member = reinterpret_cast<CMember*>( self );
    if( member->index >= atom->count )
        return py_no_attr_fail( owner, PyString_AsString( member->name ) );
    PyObjectPtr value( atom->data[ member->index ], true );
    if( value )
        return value.release();
    if( member->flags & MemberHasDefault )
    {
        value = PyObject_CallMethodObjArgs( self, _default, owner, member->name, 0 );
        if( !value )
            return 0;
    }
    else
        value.set( Py_None, true );
    atom->data[ member->index ] = value.newref();
    return value.release();
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
    PyObjectPtr newptr( value, true );
    if( newptr && member->flags & MemberHasValidate )
    {
        newptr = PyObject_CallMethodObjArgs(
            self, _validate, owner, member->name, value, 0
        );
        if( !newptr )
            return -1;
    }
    // Update internal structure before notification, since notification
    // may cause side effects. The reference to the old value reference
    // is stolen so that it's freed when the ptr is destroyed.
    PyObjectPtr oldptr( atom->data[ member->index ] );
    atom->data[ member->index ] = newptr.newref();
    size_t member_bit = member->index + INDEX_OFFSET;
    if( get_notify_bit( atom, ATOM_BIT ) && get_notify_bit( atom, member_bit ) )
    {
        if( !oldptr )
            oldptr.set( Py_None, true );
        if( !newptr )
            newptr.set( Py_None, true );
        if( oldptr != newptr && !oldptr.richcompare( newptr, Py_EQ, true ) )
        {
            PyObjectPtr result( PyObject_CallMethodObjArgs(
                owner, _notify, member->name, oldptr.get(), newptr.get(), 0 )
            );
            if( !result )
                return -1;
        }
    }
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
    if( !value )
        value = _undefined;
    else if( !PyString_Check( value ) )
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


static int
toggle_member_flag( CMember* self, PyObject* value, CMemberFlag flag )
{
    if( !value )
        value = Py_False;
    else if( !PyBool_Check( value ) )
    {
        py_expected_type_fail( value, "bool" );
        return -1;
    }
    if( value == Py_True )
        self->flags |= flag;
    else
        self->flags &= ~flag;
    return 0;
}


static PyObject*
CMember_get_has_default( CMember* self, void* context )
{
    if( self->flags & MemberHasDefault )
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


static int
CMember_set_has_default( CMember* self, PyObject* value, void* context )
{
    return toggle_member_flag( self, value, MemberHasDefault );
}


static PyObject*
CMember_get_has_validate( CMember* self, void* context )
{
    if( self->flags & MemberHasValidate )
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


static int
CMember_set_has_validate( CMember* self, PyObject* value, void* context )
{
    return toggle_member_flag( self, value, MemberHasValidate );
}


static PyGetSetDef
CMember_getset[] = {
    { "_name",
      ( getter )CMember_get_name, ( setter )CMember_set_name,
      "Get and set the name to which the member is bound. Use with extreme caution!" },
    { "_index",
      ( getter )CMember_get_index, ( setter )CMember_set_index,
      "Get and set the index to which the member is bound. Use with extreme caution!" },
    { "has_default",
      ( getter )CMember_get_has_default, ( setter )CMember_set_has_default,
      "Get and set whether the member has a default function or method." },
    { "has_validate",
      ( getter )CMember_get_has_validate, ( setter )CMember_set_has_validate,
      "Get and set whether the member has a validate function or method." },
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
    (struct PyMethodDef*)0,                 /* tp_methods */
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


static int
CMember_Check( PyObject* member )
{
    return PyObject_TypeCheck( member, &CMember_Type );
}


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
    _undefined = PyString_FromString( "<undefined>" );
    if( !_undefined )
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

