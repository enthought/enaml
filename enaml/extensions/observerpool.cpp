/*-----------------------------------------------------------------------------
|  Copyright (c) 2013, Enthought, Inc.
|  All rights reserved.
|----------------------------------------------------------------------------*/
#include "pythonhelpers.h"
#include <iostream>
#include <vector>


using namespace PythonHelpers;


class ObserverPool
{

    class Topic
    {

    public:

        Topic( PyObjectPtr& topic ) : m_topic( topic ) {}

        ~Topic() {}

        bool match( PyObjectPtr topic )
        {
            return topic == m_topic;
        }

        void add_observer( PyObjectPtr& observer )
        {
            if( !observer )
                return;
            std::vector<PyObjectPtr>::iterator it;
            std::vector<PyObjectPtr>::iterator end = m_observers.end();
            for( it = m_observers.begin(); it != end; ++it )
            {
                if( *it == observer || it->richcompare( observer, Py_EQ ) )
                    return;
            }
            m_observers.push_back( observer );
        }

        void remove_observer( PyObjectPtr& observer )
        {
            if( !observer )
                return;
            std::vector<PyObjectPtr>::iterator it;
            std::vector<PyObjectPtr>::iterator end = m_observers.end();
            for( it = m_observers.begin(); it != end; ++it )
            {
                if( *it == observer || it->richcompare( observer, Py_EQ ) )
                {
                    m_observers.erase( it );
                    return;
                }
            }
        }

        int notify_observers( PyObjectPtr& argument )
        {
            if( !argument )
                return 0;
            std::vector<PyObjectPtr>::iterator it;
            std::vector<PyObjectPtr>::iterator end = m_observers.end();
            for( it = m_observers.begin(); it != end; ++it )
            {
                if( !it->operator()( argument ) )
                    return -1;
            }
            return 0;
        }

        int py_traverse( visitproc visit, void* arg )
        {
            int vret = visit( m_topic.get(), arg );
            if( vret )
                return vret;
            std::vector<PyObjectPtr>::iterator it;
            std::vector<PyObjectPtr>::iterator end = m_observers.end();
            for( it = m_observers.begin(); it != end; ++it )
            {
                vret = visit( it->get(), arg );
                if( vret )
                    return vret;
            }
            return 0;
        }

    private:

        PyObjectPtr m_topic;
        std::vector<PyObjectPtr> m_observers;
    };

public:

    ObserverPool() {}

    ~ObserverPool() {}

    void add_observer( PyObjectPtr& topic, PyObjectPtr& observer )
    {
        if( !topic )
            return;
        std::vector<Topic>::iterator it;
        std::vector<Topic>::iterator end = m_topics.end();
        for( it = m_topics.begin(); it != end; ++it )
        {
            if( it->match( topic ) )
            {
                it->add_observer( observer );
                return;
            }
        }
        m_topics.push_back( Topic( topic ) );
        m_topics.back().add_observer( observer );
    }

    void remove_observer( PyObjectPtr& topic, PyObjectPtr& observer )
    {
        if( !topic )
            return;
        std::vector<Topic>::iterator it;
        std::vector<Topic>::iterator end = m_topics.end();
        for( it = m_topics.begin(); it != end; ++it )
        {
            if( it->match( topic ) )
            {
                it->remove_observer( observer );
                return;
            }
        }
    }

    int notify_observers( PyObjectPtr& topic, PyObjectPtr& argument )
    {
        if( !topic )
            return 0;
        std::vector<Topic>::iterator it;
        std::vector<Topic>::iterator end = m_topics.end();
        for( it = m_topics.begin(); it != end; ++it )
        {
            if( it->match( topic ) )
                return it->notify_observers( argument );
        }
        return 0;
    }

    int py_traverse( visitproc visit, void* arg )
    {
        int vret;
        std::vector<Topic>::iterator it;
        std::vector<Topic>::iterator end = m_topics.end();
        for( it = m_topics.begin(); it != end; ++it )
        {
            vret = it->py_traverse( visit, arg );
            if( vret )
                return vret;
        }
        return 0;
    }

    void py_clear()
    {
        m_topics.clear();
    }


private:

    std::vector<Topic> m_topics;
    ObserverPool(const ObserverPool& other);
    ObserverPool& operator=(const ObserverPool&);

};


extern "C" {


typedef struct {
    PyObject_HEAD
    ObserverPool* pool;
} PyObserverPool;


static void
PyObserverPool_clear( PyObserverPool* self )
{
    if( self->pool )
        self->pool->py_clear();
}


static int
PyObserverPool_traverse( PyObserverPool* self, visitproc visit, void* arg )
{
    if( self->pool )
        return self->pool->py_traverse( visit, arg );
    return 0;
}


static void
PyObserverPool_dealloc( PyObserverPool* self )
{
    PyObject_GC_UnTrack( self );
    PyObserverPool_clear( self );
    delete self->pool;
    self->ob_type->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
PyObserverPool_add_observer( PyObserverPool* self, PyObject* args )
{
    PyObject* topic;
    PyObject* observer;
    if( !PyArg_ParseTuple( args, "OO", &topic, &observer ) )
        return 0;
    if( !PyString_CheckExact( topic ) )
        return py_expected_type_fail( topic, "str" );
    if( !PyString_CHECK_INTERNED( topic ) )
        PyString_InternInPlace( &topic );
    PyObjectPtr topicptr( topic, true );
    PyObjectPtr observerptr( observer, true );
    if( !self->pool )
        self->pool = new ObserverPool();
    self->pool->add_observer( topicptr, observerptr );
    Py_RETURN_NONE;
}


static PyObject*
PyObserverPool_remove_observer( PyObserverPool* self, PyObject* args )
{
    PyObject* topic;
    PyObject* observer;
    if( !PyArg_ParseTuple( args, "OO", &topic, &observer ) )
        return 0;
    if( !PyString_CheckExact( topic ) )
        return py_expected_type_fail( topic, "str" );
    if( !self->pool )
        Py_RETURN_NONE;
    if( !PyString_CHECK_INTERNED( topic ) )
        PyString_InternInPlace( &topic );
    PyObjectPtr topicptr( topic, true );
    PyObjectPtr observerptr( observer, true );
    self->pool->remove_observer( topicptr, observerptr );
    Py_RETURN_NONE;
}


static PyObject*
PyObserverPool_notify_observers( PyObserverPool* self, PyObject* args )
{
    PyObject* topic;
    PyObject* argument;
    if( !PyArg_ParseTuple( args, "OO", &topic, &argument ) )
        return 0;
    if( !PyString_CheckExact( topic ) )
        return py_expected_type_fail( topic, "str" );
    if( !PyString_CHECK_INTERNED( topic ) )
        PyString_InternInPlace( &topic );
    if( self->pool )
    {
        PyObjectPtr topicptr( topic, true );
        PyTuplePtr argsptr( PyTuple_New( 1 ) );
        argsptr.set_item( 0, argument, true );
        if( self->pool->notify_observers( topicptr, argsptr ) < 0 )
            return 0;
    }
    Py_RETURN_NONE;
}


static PyMethodDef
PyObserverPool_methods[] = {
    { "add_observer",
      ( PyCFunction )PyObserverPool_add_observer, METH_VARARGS,
      "Add an observer to the pool for a given topic." },
    { "remove_observer",
      ( PyCFunction )PyObserverPool_remove_observer, METH_VARARGS,
      "Remove an observer from the pool for a given topic." },
    { "notify_observers",
      ( PyCFunction )PyObserverPool_notify_observers, METH_VARARGS,
      "Notify the observers for a given topic." },
    { 0 } // sentinel
};


PyTypeObject PyObserverPool_Type = {
    PyObject_HEAD_INIT( 0 )
    0,                                      /* ob_size */
    "observerpool.ObserverPool",            /* tp_name */
    sizeof( PyObserverPool ),               /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)PyObserverPool_dealloc,     /* tp_dealloc */
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
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_GC,  /* tp_flags */
    0,                                      /* Documentation string */
    (traverseproc)PyObserverPool_traverse,  /* tp_traverse */
    (inquiry)PyObserverPool_clear,          /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)PyObserverPool_methods, /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)PyType_GenericNew,             /* tp_new */
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
    if( PyType_Ready( &PyObserverPool_Type ) )
        return;
    PyObject* pytype = reinterpret_cast<PyObject*>( &PyObserverPool_Type );
    Py_INCREF( pytype );
    PyModule_AddObject( mod, "ObserverPool", pytype );
}


} // extern "C"

