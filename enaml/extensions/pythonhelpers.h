/*-----------------------------------------------------------------------------
|  Copyright (c) 2012, Enthought, Inc.
|  All rights reserved.
|----------------------------------------------------------------------------*/
#pragma once
#include <Python.h>
#include <structmember.h>


namespace PythonHelpers 
{

/*-----------------------------------------------------------------------------
| Exception Handling
|----------------------------------------------------------------------------*/
PyObject*
py_type_fail( const char* message )
{
    PyErr_SetString( PyExc_TypeError, message );
    return 0;
}


PyObject* 
py_expected_type_fail( PyObject* pyobj, const char* expected_type )
{
    PyErr_Format(
        PyExc_TypeError,
        "Expected object of type `%s`. Got object of type `%s` instead.",
        expected_type, pyobj->ob_type->tp_name
    );
    return 0;
}


/*-----------------------------------------------------------------------------
| Object Ptr
|----------------------------------------------------------------------------*/
class PyObjectPtr {

public:

    PyObjectPtr() : m_pyobj( 0 ) { }

    PyObjectPtr( const PyObjectPtr& objptr ) : m_pyobj( objptr.m_pyobj )
    {
        incref();
    }

    PyObjectPtr( PyObject* pyobj, bool takeref=false ) : m_pyobj( pyobj )
    {
        if( takeref )
            incref();
    }

    ~PyObjectPtr()
    {
        release( true );
    }

    PyObject* get() const
    {
        return m_pyobj;
    }

    PyObject* release( bool giveref=false )
    {
        PyObject* pyobj = m_pyobj;
        m_pyobj = 0;
        if( giveref )
            Py_XDECREF( pyobj );
        return pyobj;
    }

    void incref() const
    {
        Py_XINCREF( m_pyobj );
    }

    void decref() const
    {
        Py_XDECREF( m_pyobj );
    }

    size_t refcount() const
    {
        if( m_pyobj )
            return m_pyobj->ob_refcnt;
        return 0;
    }

    bool is_None()
    {
        return m_pyobj == Py_None;
    }

    bool is_True()
    {
        return m_pyobj == Py_True;
    }

    bool is_False()
    {
        return m_pyobj == Py_False;
    }

    operator void*() const
    {
        return static_cast<void*>( m_pyobj );
    }

    PyObjectPtr& operator=( const PyObjectPtr& rhs )
    {
        PyObject* old = m_pyobj;
        m_pyobj = rhs.m_pyobj;
        Py_XINCREF( m_pyobj );
        Py_XDECREF( old );
        return *this;
    }

protected:

    PyObject* m_pyobj;

};


/*-----------------------------------------------------------------------------
| Tuple Ptr
|----------------------------------------------------------------------------*/
class PyTuplePtr : public PyObjectPtr {

public:

    PyTuplePtr() : PyObjectPtr() { }

    PyTuplePtr( const PyObjectPtr& objptr ) : PyObjectPtr( objptr ) { }

    PyTuplePtr( PyObject* pytuple, bool takeref=false ) : 
        PyObjectPtr( pytuple, takeref ) { }

    Py_ssize_t size() const
    {
        return PyTuple_GET_SIZE( m_pyobj );
    }

    PyObjectPtr get_item( Py_ssize_t index ) const
    {
        return PyObjectPtr( PyTuple_GET_ITEM( m_pyobj, index ), true );
    }

};


/*-----------------------------------------------------------------------------
| List Ptr
|----------------------------------------------------------------------------*/
class PyListPtr : public PyObjectPtr {

public:

    PyListPtr() : PyObjectPtr() { }

    PyListPtr( const PyObjectPtr& objptr ) : PyObjectPtr( objptr ) { }

    PyListPtr( PyObject* pylist, bool takeref=false ) : 
        PyObjectPtr( pylist, takeref ) { }

    Py_ssize_t size() const
    {
        return PyList_GET_SIZE( m_pyobj );
    }

    PyObjectPtr get_item( Py_ssize_t index ) const
    {
        return PyObjectPtr( PyList_GET_ITEM( m_pyobj, index ), true );
    }

    bool append( PyObjectPtr& pyobj ) const
    {
        if( PyList_Append( m_pyobj, pyobj.get() ) == 0 )
            return true;
        return false;
    }

};


/*-----------------------------------------------------------------------------
| Dict Ptr
|----------------------------------------------------------------------------*/
class PyDictPtr : public PyObjectPtr {

public:

    PyDictPtr() : PyObjectPtr() { }

    PyDictPtr( const PyObjectPtr& objptr ) : PyObjectPtr( objptr ) { }

    PyDictPtr( PyObject* pydict, bool takeref=false ) : 
        PyObjectPtr( pydict, takeref ) { }

    Py_ssize_t size() const
    {
        return PyDict_Size( m_pyobj );
    }

    PyObjectPtr get_item( PyObjectPtr& key ) const
    {
        return PyObjectPtr( PyDict_GetItem( m_pyobj, key.get() ), true );
    }

    PyObjectPtr get_item( const char* key ) const
    {
        return PyObjectPtr( PyDict_GetItemString( m_pyobj, key ), true );
    }

    PyObjectPtr get_item( std::string& key ) const
    {
        return get_item( key.c_str() );
    }

    bool set_item( PyObjectPtr& key, PyObjectPtr& value ) const
    {
        if( PyDict_SetItem( m_pyobj, key.get(), value.get() ) == 0 )
            return true;
        return false;
    }

    bool set_item( const char* key, PyObjectPtr& value ) const
    {
        if( PyDict_SetItemString( m_pyobj, key, value.get() ) == 0 )
            return true;
        return false;
    }

    bool set_item( std::string& key, PyObjectPtr& value ) const
    {
        return set_item( key.c_str(), value );
    }

    bool del_item( PyObjectPtr& key ) const
    {
        if( PyDict_DelItem( m_pyobj, key.get() ) == 0 )
            return true;
        return false;
    }

    bool del_item( const char* key ) const
    {
        if( PyDict_DelItemString( m_pyobj, key ) == 0 )
            return true;
        return false;
    }

    bool del_item( std::string& key ) const
    {
        return del_item( key.c_str() );
    }

    template<typename _FACTORY_T>
    PyObjectPtr setdefault( PyObjectPtr& key ) const
    {
        PyObjectPtr value( get_item( key ) );
        if( !value )
        {
            value = _FACTORY_T()();
            if( !set_item( key, value ) )
                value = 0;
        }
        return value;
    }

};


/*-----------------------------------------------------------------------------
| Method Ptr
|----------------------------------------------------------------------------*/
class PyMethodPtr : public PyObjectPtr {

public:

    PyMethodPtr() : PyObjectPtr() { }

    PyMethodPtr( const PyObjectPtr& objptr ) : PyObjectPtr( objptr ) { }

    PyMethodPtr( PyObject* pymethod, bool takeref=false ) : 
        PyObjectPtr( pymethod, takeref ) { }

    PyObjectPtr get_self() const
    {
        return PyObjectPtr( PyMethod_GET_SELF( m_pyobj ), true );
    }

    PyObjectPtr get_function() const
    {
        return PyObjectPtr( PyMethod_GET_FUNCTION( m_pyobj ), true );
    }

    PyObjectPtr get_class() const
    {
        return PyObjectPtr( PyMethod_GET_CLASS( m_pyobj ), true );
    }

    PyObjectPtr operator()( PyTuplePtr& args, PyDictPtr& kwargs ) const
    {
        return PyObjectPtr( PyObject_Call( m_pyobj, args.get(), kwargs.get() ) );
    }

};


/*-----------------------------------------------------------------------------
| Weakref Ptr
|----------------------------------------------------------------------------*/
class PyWeakrefPtr : public PyObjectPtr {

public:

    PyWeakrefPtr() : PyObjectPtr() { }

    PyWeakrefPtr( const PyObjectPtr& objptr ) : PyObjectPtr( objptr ) { }

    PyWeakrefPtr( PyObject* pyweakref, bool takeref=true ) : 
        PyObjectPtr( pyweakref, takeref ) { }

    PyObjectPtr operator()() const
    {
        return PyObjectPtr( PyWeakref_GET_OBJECT( m_pyobj ), true );
    }

};

} // namespace PythonHelpers

