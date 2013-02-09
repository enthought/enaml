/*-----------------------------------------------------------------------------
|  Copyright (c) 2013, Enthought, Inc.
|  All rights reserved.
|----------------------------------------------------------------------------*/
#include "pythonhelpers.h"
#include <iostream>

using namespace PythonHelpers;


extern "C" {


typedef struct {
    PyObject_HEAD
    PyObject* observers;
} ObserverPool;


static PyObject*
ObserverPool_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObjectPtr mgrptr( PyType_GenericNew( type, args, kwargs ) );
    if( !mgrptr )
        return 0;
    ObserverPool* mgr = reinterpret_cast<ObserverPool*>( mgrptr.get() );
    mgr->observers = PyList_New( 0 );
    if( !mgr->observers )
        return 0;
    return mgrptr.release();
}


static void
ObserverPool_clear( ObserverPool* self )
{
    Py_CLEAR( self->observers );
}


static int
ObserverPool_traverse( ObserverPool* self, visitproc visit, void* arg )
{
    Py_VISIT( self->observers );
    return 0;
}


static void
ObserverPool_dealloc( ObserverPool* self )
{
    PyObject_GC_UnTrack( self );
    ObserverPool_clear( self );
    self->ob_type->tp_free( reinterpret_cast<PyObject*>( self ) );
}


// returns a *borrowed* reference to the pool list, or null. `name`
// *must* be an exact string (no subclasses).
static PyObject*
find_pool( ObserverPool* self, PyObject* name, bool force_create=false )
{
    if( !PyString_CHECK_INTERNED( name ) )
        PyString_InternInPlace( &name );
    Py_ssize_t count = PyList_GET_SIZE( self->observers );
    for( Py_ssize_t i = 0; i < count; i += 2 )
    {
        if( PyList_GET_ITEM( self->observers, i ) == name )
            return PyList_GET_ITEM( self->observers, i + 1 );
    }
    if( force_create )
    {
        PyObject* pool = PyList_New( 0 );
        if( !pool )
            return 0;
        if( PyList_Append( self->observers, name ) < 0 )
            return 0;
        if( PyList_Append( self->observers, pool ) < 0 )
            return 0;
        Py_DECREF( pool );
        return pool;
    }
    return 0;
}


static PyObject*
ObserverPool_add( ObserverPool* self, PyObject* args )
{
    PyObject* name;
    PyObject* callback;
    if( !PyArg_ParseTuple( args, "OO", &name, &callback ) )
        return 0;
    if( !PyString_CheckExact( name ) )
        return py_expected_type_fail( name, "str" );
    PyObject* pool = find_pool( self, name, true );
    if( !pool )
        return 0;
    int contains = PySequence_Contains( pool, callback );
    if( contains == -1 )
        return 0;
    if( contains == 1)
        Py_RETURN_NONE;
    if( PyList_Append( pool, callback ) < 0 )
        return 0;
    Py_RETURN_NONE;
}


static PyObject*
ObserverPool_remove( ObserverPool* self, PyObject* args )
{
    PyObject* name;
    PyObject* callback;
    if( !PyArg_ParseTuple( args, "OO", &name, &callback ) )
        return 0;
    if( !PyString_CheckExact( name ) )
        return py_expected_type_fail( name, "str" );
    PyObject* pool = find_pool( self, name );
    if( pool )
    {
        Py_ssize_t index = PySequence_Index( pool, callback );
        if( index == -1 )
            PyErr_Clear();
        else if( PySequence_DelItem( pool, index ) < 0 )
            return 0;
    }
    Py_RETURN_NONE;
}


/*
This method will remove an observer during a dispatch cycle if it
evaluates to boolean false. When a pool associated with a given name
is empty, it is allowed to linger in case new observers are added at
a later time. In the worst case scenario, there will be an empty list
for every observable value on a object. This is unlikely to happen,
and the downside of doing the cleanup can be worse. There are cases
where observers may be rapidly added and removed from an object. If
the observer is singular, performing the cleanup would cause rapid
thrashing of the list and reduce performance. This can be revisted
if situations arise where the current choice does not scale.
*/
static PyObject*
ObserverPool_notify( ObserverPool* self, PyObject* args )
{
    PyObject* name;
    PyObject* arg;
    if( !PyArg_ParseTuple( args, "OO", &name, &arg ) )
        return 0;
    if( !PyString_CheckExact( name ) )
        return py_expected_type_fail( name, "str" );
    PyObject* pool = find_pool( self, name );
    if( pool )
    {
        PyObject* callback;
        PyObjectPtr result;
        Py_ssize_t i = 0;
        // Testing the size on each iteration guards against the slim
        // chance that a notifier causes the method to be re-entered,
        // which has the potential to delete an item ahead of the
        // current code path.
        while( i < PyList_GET_SIZE( pool ) )
        {
            callback = PyList_GET_ITEM( pool, i );
            switch( PyObject_IsTrue( callback ) )
            {
                case 1:
                    result = PyObject_CallFunctionObjArgs( callback, arg, 0 );
                    if( !result )
                        return 0;
                    ++i;
                    break;
                case 0:
                    if( PySequence_DelItem( pool, i ) < 0 )
                        return 0;
                    break;
                case -1:
                default:
                    return 0;
            }
        }
    }
    Py_RETURN_NONE;
}


static PyObject*
ObserverPool_observers( ObserverPool* self )
{
    Py_INCREF( self->observers );
    return self->observers;
}


static PyMethodDef
ObserverPool_methods[] = {
    { "add",
      ( PyCFunction )ObserverPool_add, METH_VARARGS,
      "Add a callback to the pool for the given name." },
    { "remove",
      ( PyCFunction )ObserverPool_remove, METH_VARARGS,
      "Remove a callback from the pool for the given name." },
    { "notify",
      ( PyCFunction )ObserverPool_notify, METH_VARARGS,
      "Notify the callbacks for the given name." },
    { "_observers",
      ( PyCFunction )ObserverPool_observers, METH_NOARGS, "" },
    { 0 } // sentinel
};


PyTypeObject ObserverPool_Type = {
    PyObject_HEAD_INIT( 0 )
    0,                                      /* ob_size */
    "observerpool.ObserverPool",            /* tp_name */
    sizeof( ObserverPool ),                 /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)ObserverPool_dealloc,       /* tp_dealloc */
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
    (traverseproc)ObserverPool_traverse,    /* tp_traverse */
    (inquiry)ObserverPool_clear,            /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)ObserverPool_methods, /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)ObserverPool_new,              /* tp_new */
    (freefunc)PyObject_GC_Del,              /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static PyMethodDef
observerpool_methods[] = {
    { 0 } // Sentinel
};


PyMODINIT_FUNC
initobserverpool( void )
{
    PyObject* mod = Py_InitModule( "observerpool", observerpool_methods );
    if( !mod )
        return;
    if( PyType_Ready( &ObserverPool_Type ) )
        return;
    Py_INCREF( &ObserverPool_Type );
    PyModule_AddObject( mod, "ObserverPool", reinterpret_cast<PyObject*>( &ObserverPool_Type ) );
}


} // extern "C"

