import ast


def attributes(expr):
    """ Returns the tuple of tuples of possible trackable dotted attribute 
    strings. An example of a non-trackable attribute is that which follows 
    anything other than a name. For example,
        
        foo.bar.baz(a + b, c).spam.eggs + [i for i in range(ham)]

    The attributes set will include:
        
        (('foo', 'bar.baz'),)

    The attribute spam.eggs will not be included since it would be 
    an untrackable dependency.

    The inner tuples of the returned tuple have two elements, the first 
    is the name of the object and the second is the extended attribute 
    being accessed on the object.
    
    """
    msg = 'Expression must be an ast.Expression node.'
    assert isinstance(expr, ast.Expression), msg
    
    attributes = set()
    seen_attrs = set()

    for node in ast.walk(expr):
        if isinstance(node, ast.Attribute):
            if node not in seen_attrs:
                attrs = [node.attr]
                while isinstance(node, ast.Attribute):
                    seen_attrs.add(node)
                    node = node.value
                    if isinstance(node, ast.Attribute):
                        attrs.append(node.attr)
                    elif isinstance(node, ast.Name):
                        attr = (node.id, '.'.join(attrs))
                        attributes.add(attr)
    
    return tuple(attributes)


def is_extended_attribute(expr):
    """ Asserts that the given expression is a single extended
    attribute expression that terminates in a Name. For example:

        a.b
        a.b.c
        a.b.c.d
    
    will pass validation, while:

        a().b
        a.b().c
        a.b.c()
        a + b + c

    will not. This function will return True on success, and False
    otherwise.

    """
    node = expr.body
    flat = [node]
    while isinstance(node, ast.Attribute):
        node = node.value
        flat.append(node)
    attrs = flat[:-1]
    name = flat[-1]
    res = all([isinstance(attr, ast.Attribute) for attr in attrs])
    return res and isinstance(name, ast.Name)


