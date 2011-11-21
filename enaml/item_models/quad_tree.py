#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" This is the Python reference implementation of the QuadTree structure
used by the standard model objects. Users should build the Cython version
in enaml/speedups in order to have a reasonably fast implementation.

"""
import operator


class Rect(object):
    """ An internal rect class that can hit test a point and calculate
    if it can fully contain another Rect. 

    """
    __slots__ = ('x1', 'y1', 'x2', 'y2')

    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    
    def hit_test(self, x, y):
        """ Returns True if this Rect contains the point or if the point
        lies on the edge of the Rect, False otherwise.

        """
        return (self.x1 <= x <= self.x2) and (self.y1 <= y <= self.y2)

    def rect_test(self, rect):
        """ Returns True if this rect fully bounds the other rect with no
        overlap, False otherwise. Edge alignment is not considered overlap.

        """
        contains = (
            self.x1 <= rect.x1 and
            self.y1 <= rect.y1 and
            self.x2 >= rect.x2 and
            self.y2 >= rect.y2
        )
        return contains


class QuadObject(Rect):
    """ A public Rect subclass for storing user objects in the tree
    with a given priority.

    """
    __slots__ = ('priority', 'obj')

    def __init__(self, x1=0, y1=0, x2=0, y2=0, obj=None, priority=0):
        """ Initialize a QuadObject.

        Parameters
        ----------
        x1 : int >= 0
            The x-coord of the upper left of the rect
        y1 : int >= 0
            The y-coord of the upper left of the rect
        x2 : int >= 0
            The x-coord of the lower right of the rect
        y2 : int >= 0
            The y-coord of the lower right of the rect
        obj : object, optional
            A Python object to associate with the rect
        priority : int >= 0, optional
            An integer priority to use in relation to other nodes in the
            tree. This is used by the QuadTree class to return the highest
            priority hit when there are multiple hits for a given point.
            Defaults to zero.

        """
        super(QuadObject, self).__init__(x1, y1, x2, y2)
        if priority < 0:
            raise ValueError('Priority must be >= 0')
        self.obj = obj
        self.priority = priority


class TreeNode(Rect):
    """ An internal class representing a node in a QuadTree.

    """
    __slots__ = ('children', 'quad_objs', 'leaf_size')
    
    def __init__(self, x1, y1, x2, y2, leaf_size):
        super(TreeNode, self).__init__(x1, y1, x2, y2)
        self.leaf_size = leaf_size
        self.children = None
        self.quad_objs = None

    def hits(self, x, y, res):
        """ Recursively append 'hits' to the provided list. 
        
        A 'hit' is found when this node contains the given point *and* 
        this node contains a QuadObject which *also* contains the point.
        If this node contains the point, then all of the children are
        recursively tested for hits as well.

        """
        if self.hit_test(x, y):
            if self.quad_objs is not None:
                for quad_obj in self.quad_objs:
                    if quad_obj.hit_test(x, y):
                        res.append(quad_obj)

            if self.children is not None:
                for child in self.children:
                    child.hits(x, y, res)

    def insert(self, quad_obj, depth, max_depth):
        """ Inserts the QuadObject into the tree. 
        
        Depth indicates our current depth in the tree and max_depth is 
        the maximum depth allowed in the tree (these are arguments so 
        that we save the memory costs of storing two pointers on each
        node). If this node does not have any children, they are created, 
        provided that we don't exceed the maximum depth. The QuadObject is 
        then attached to the smallest node that will fully bound its rect.

        """
        # If this method is called, then we know that we fully bound
        # the given rect. So if we're not yet at capacity, we can
        # just store the object and bail early.
        if self.quad_objs is None:
            self.quad_objs = []

        if (len(self.quad_objs) < self.leaf_size) or (depth >= max_depth):
            if quad_obj not in self.quad_objs:
                self.quad_objs.append(quad_obj)
                return
        
        # If we get here, we may need to subdivide and rearrange
        if self.children is None:
            self.subdivide()
            self.redistribute_quads(depth, max_depth)
           
        # Now we test our children to see if one can fully contain
        # the QuadObject. If it can, we defer to it. Otherwise, it
        # overlaps and we hold onto it ourselves
        for child in self.children:
            if child.rect_test(quad_obj):
                child.insert(quad_obj, depth + 1, max_depth)
                return
        
        if quad_obj not in self.quad_objs:
            self.quad_objs.append(quad_obj)
    
    def remove(self, quad_obj):
        """ Remove a QuadObject from the tree.
        
        """
        del_idx = -1
        if self.quad_objs is not None:
            for i, test_obj in enumerate(self.quad_objs):
                if quad_obj is test_obj:
                    del_idx = i
                    break

        if del_idx >= 0:
            del self.quad_objs[del_idx]
        else:
            if self.children is not None:
                for child in self.children:
                    if child.rect_test(quad_obj):
                        child.remove(quad_obj)
                        return

    def contents(self, res):
        """ Append all of the quad objects to the results list 
        recursively.

        """
        if self.quad_objs is not None:
            res.extend(self.quad_objs)
        if self.children is not None:
            for child in self.children:
                child.contents(res)

    def redistribute_quads(self, depth, max_depth):
        """ After subdivsion, call this method to redistribute the quad
        objects appropriately within the new children.

        """
        unmoved = []
        for quad_obj in self.quad_objs:
            for child in self.children:
                if child.rect_test(quad_obj):
                    child.insert(quad_obj, depth + 1, max_depth)
                    break
            else:
                unmoved.append(quad_obj)
        self.quad_objs = unmoved

    def subdivide(self):
        """ Call this method to subdivide this node into 4 children.

        """
        leaf_size = self.leaf_size

        x1 = self.x1
        x4 = self.x2
        x2 = (x4 - x1) / 2 + x1
        x3 = x2 + 1

        y1 = self.y1
        y4 = self.y2
        y2 = (y4 - y1) / 2 + y1
        y3 = y2 + 1

        child1 = TreeNode(x1, y1, x2, y2, leaf_size)
        child2 = TreeNode(x3, y1, x4, y2, leaf_size)
        child3 = TreeNode(x1, y3, x2, y4, leaf_size)
        child4 = TreeNode(x3, y3, x4, y4, leaf_size)

        self.children = (child1, child2, child3, child4)


class QuadTree(object):
    """ A simple quad tree data structure that is optimized for insertion
    and hit testing. It doesn't provide any functionality beyond that.

    """
    __slots__ = ('max_depth', 'root')

    def __init__(self, x1, y1, x2, y2, max_depth=8, leaf_size=4):
        """ Construct a quad tree.

        Parameters
        ----------
        x1 : int >= 0
            The x-coord of the upper left of the tree
        y1 : int >= 0
            The y-coord of the upper left of the tree
        x2 : int >= 0
            The x-coord of the lower right of the tree
        y2 : int >= 0
            The y-coord of the lower right of the tree
        max_depth : int >= 0, optional
            The maximum depth of the tree. Defaults to 8.
        leaf_size : int >= 1, optional
            The number of objects to hold in a leaf before subdividing
            if max_depth is not yet reached. Defaults to 4.

        """
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
            msg = 'The corners of a QuadTree must all be >= 0'
            raise ValueError(msg)
        if max_depth < 1:
            raise ValueError('max_depth must be >= 1')
        if x1 > x2 or y1 > y2:
            msg = 'Invalid corner ordering (%s, %s, %s, %s)'
            raise ValueError(msg % (x1, y1, x2, y2))
        if leaf_size < 1:
            raise ValueError('Leaf size must be >= 1')
        self.root = TreeNode(x1, y1, x2, y2, leaf_size)
        self.max_depth = max_depth

    def insert(self, quad_obj):
        """ Insert a QuadObject into the tree.
        
        The bounds of the QuadObject must be fully contained within the
        quad tree or a ValueError will be raised.
        
        Parameters
        ----------
        quad_obj : QuadObject
            The quad object to insert into the tree
        
        """
        root = self.root
        if root.rect_test(quad_obj):
            root.insert(quad_obj, 0, self.max_depth)
        else:
            raise ValueError('QuadObject does not fit in the tree')  
    
    def remove(self, quad_obj):
        """ Remove a QuadObject from the tree.

        If the QuadObject does not exist in the tree. This is a no-op.

        """
        root = self.root
        if root.rect_test(quad_obj):
            root.remove(quad_obj)

    def hits(self, x, y):
        """ Returns the list of objects from the occupy rectangles which
        contain the given coordinate.

        Parameters
        ----------
        x : int
            The x-coord of the hit point
        y : int 
            The y-coord of the hit point

        Returns
        -------
        hits : list of QuadObjects
            The list of all objects with occupy rectangles which intersect
            with the given point. The ordering of the objects is arbitrary.

        """
        res = []
        self.root.hits(x, y, res)
        return res

    def priority_hit(self, x, y):
        """ Returns the highest priority hit from the possible hits
        in the tree.

        Parameters
        ----------
        x : int
            The x-coord of the hit point
        y : int 
            The y-coord of the hit point

        Returns
        -------
        hit : QuadObject or None
            The QuadObject with the highest priority or None if there was 
            no hit.

        """
        # We expect the amount of overlap in the tree to be small so 
        # populating a list of hits should not be expensive, this is
        # easier than traversing the tree according to a criteria.
        hits = []
        self.root.hits(x, y, hits)
        if len(hits) > 0:
            return max(hits, key=operator.attrgetter('priority'))

    def contents(self):
        """ Return a list of all the items in the tree in no particular
        order.

        """
        res = []
        self.root.contents(res)
        return res


try:
    from ..speedups.quad_tree import QuadTree, QuadObject
except ImportError:
    pass


