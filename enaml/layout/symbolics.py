from collections import defaultdict
import operator

import csw


class LinearSymbolic(object):

    @staticmethod
    def almost_equal(a, b, eps=1e-8):
        return abs(a - b) < eps

    @staticmethod
    def nonlinear(msg):
        raise TypeError('Non-linear expression: %s' % msg)
    
    @staticmethod
    def nonlinear_op(op):
        raise TypeError('Non-linear operator: `%s`' % op)

    def convert_to_csw(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __add__(self, other):
        raise NotImplementedError
    
    def __mul__(self, other):
        raise NotImplementedError
    
    def __div__(self, other):
        raise NotImplementedError

    def __str__(self):
        return self.__repr__()

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self + -1 * other
    
    def __rsub__(self, other):
        return other + -1 * self

    def __rmul__(self, other):
        return self * other

    def __rdiv__(self, other):
        if isinstance(other, (float, int, LinearSymbolic)):
            self.nonlinear('[ %s ] / [ %s ]' % (other, self))
        else:
            msg = 'Invalid type for linear symbolic operation %s' % type(other)
            raise TypeError(msg)

    def __floordiv__(self, other):
        self.nonlinear_op('//')
    
    __rfloordiv__ = __floordiv__

    def __mod__(self, other):
        self.nonlinear_op('%')
    
    __rmod__ = __mod__

    def __divmod__(self, other):
        self.nonlinear_op('divmod')
    
    __rdivmod__ = __divmod__

    def __pow__(self, other):
        self.nonlinear_op('**')
    
    __rpow__ = __pow__

    def __lshift__(self, other):
        self.nonlinear_op('<<')

    __rlshift__ = __lshift__

    def __rshift__(self, other):
        self.nonlinear_op('>>')
    
    __rrshift__ = __rshift__

    def __and__(self, other):
        self.nonlinear_op('&')
    
    __rand__ = __and__

    def __or__(self, other):
        self.nonlinear_op('|')

    __ror__ = __or__
    
    def __xor__(self, other):
        self.nonlinear_op('^')
    
    __rxor__ = __xor__

    def __lt__(self, other):
        raise ValueError('Invalid constraint operation.')

    def __gt__(self, other):
        raise ValueError('Invalid constraint operation.')
    
    def __ne__(self, other):
        raise ValueError('Invalid constraint operation')

    def __le__(self, other):
        if isinstance(other, (float, int)):
            rhs = LinearExpression([], float(other))
        elif isinstance(other, LinearSymbolic):
            rhs = other
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return LEConstraint(self, rhs)
    
    def __ge__(self, other):
        if isinstance(other, (float, int)):
            rhs = LinearExpression([], float(other))
        elif isinstance(other, LinearSymbolic):
            rhs = other
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return GEConstraint(self, rhs)

    def __eq__(self, other):
        if isinstance(other, (float, int)):
            rhs = LinearExpression([], float(other))
        elif isinstance(other, LinearSymbolic):
            rhs = other
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return EQConstraint(self, rhs)


class Term(LinearSymbolic):

    def __init__(self, var, coeff=1.0):
        self.var = var
        self.coeff = coeff
    
    def __repr__(self):
        return '%s * %s' % (self.coeff, self.var)

    def __add__(self, other):
        if isinstance(other, (float, int)):
            terms = [self]
            const = float(other)
            expr = LinearExpression(terms, const)
        elif isinstance(other, Term):
            terms = [self, other]
            expr = LinearExpression(terms)
        elif isinstance(other, ConstraintVariable):
            terms = [self, Term(other)]
            expr = LinearExpression(terms)
        elif isinstance(other, LinearExpression):
            expr = other + self
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return expr
    
    def __mul__(self, other):
        if isinstance(other, (float, int)):
            res = Term(self.var, float(other) * self.coeff)
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] * [ %s ]' % (self, other))
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return res
    
    def __div__(self, other):
        if isinstance(other, (float, int)):
            res = (1.0 / float(other)) * self
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] / [ %s ]' % (self, other))
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return res

    def convert_to_csw(self):
        return self.coeff * self.var.convert_to_csw()


class LinearExpression(LinearSymbolic):

    @classmethod
    def reduce_terms(cls, terms):
        mapping = defaultdict(float)
        for term in terms:
            mapping[term.var] += term.coeff
        terms = tuple(Term(var, coeff) for (var, coeff) in mapping.iteritems() 
                      if not cls.almost_equal(coeff, 0.0))
        return terms

    def __init__(self, terms, constant=0.0):
        self.terms = self.reduce_terms(terms)
        self.constant = constant

    def __repr__(self):
        s = sorted(self.terms, key=operator.attrgetter('coeff'))
        terms = ' + '.join(str(term) for term in s)
        return terms + ' + %s' % self.constant

    def __add__(self, other):
        if isinstance(other, (float, int)):
            expr = LinearExpression(self.terms, self.constant + float(other))
        elif isinstance(other, Term):
            terms = list(self.terms) + [other]
            expr = LinearExpression(terms, self.constant)
        elif isinstance(other, ConstraintVariable):
            terms = list(self.terms) + [Term(other)]
            expr = LinearExpression(terms, self.constant)
        elif isinstance(other, LinearExpression):
            terms = list(self.terms) + list(other.terms)
            const = self.constant + other.constant
            expr = LinearExpression(terms, const)
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return expr
    
    def __mul__(self, other):
        if isinstance(other, (float, int)):
            terms = [other * term for term in self.terms]
            const = self.constant * other
            res = LinearExpression(terms, const)
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] * [ %s ]' % (self, other))
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return res
    
    def __div__(self, other):
        if isinstance(other, (float, int)):
            res = (1.0 / float(other)) * self
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] / [ %s ]' % (self, other))
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return res

    def convert_to_csw(self):
        csw_terms = [term.convert_to_csw() for term in self.terms]
        return sum(csw_terms) + self.constant


class ConstraintVariable(LinearSymbolic):

    def __init__(self, name):
        self.name = name
        self.csw_var = csw.Variable(name)

    def __repr__(self):
        return '%s' % self.name

    def __add__(self, other):
        if isinstance(other, (float, int)):
            terms = [Term(self)]
            const = float(other)
            expr = LinearExpression(terms, const)
        elif isinstance(other, Term):
            terms = [Term(self), other]
            expr = LinearExpression(terms)
        elif isinstance(other, ConstraintVariable):
            terms = [Term(self), Term(other)]
            expr = LinearExpression(terms)
        elif isinstance(other, LinearExpression):
            expr = other + self
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return expr
    
    def __mul__(self, other):
        if isinstance(other, (float, int)):
            res = Term(self, float(other))
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] * [ %s ]' % (self, other))
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return res
    
    def __div__(self, other):
        if isinstance(other, (float, int)):
            res = (1.0 / float(other)) * self
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] / [ %s ]' % (self, other))
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return res

    def convert_to_csw(self):
        return self.csw_var


class LinearConstraint(object):

    op = '<abtract>'

    strength_map = {
        'weak': csw.sWeak(),
        'medium': csw.sMedium(),
        'strong': csw.sStrong(),
        'required': csw.sRequired(),
    }

    def __init__(self, lhs, rhs, strength='required'):
        self.lhs = lhs
        self.rhs = rhs
        self.strength = strength

    def __repr__(self):
        return '%s %s %s' % (self.lhs, self.op, self.rhs)
    
    def __str__(self):
        return self.__repr__()

    def __or__(self, other):
        if isinstance(other, basestring):
            mapping = self.strength_map
            if other not in mapping:
                raise ValueError('Invalid strength `%s`' % other)
            self.strength = other
        else:
            msg = 'Strength must be a string. Got %s instead.' % type(other)
            raise TypeError(msg)
        return self
        
    def __ror__(self, other):
        return self.__or__(other)

    def convert_to_csw(self):
        raise NotImplementedError


class LEConstraint(LinearConstraint):

    op = '<='

    def convert_to_csw(self):
        lhs = self.lhs.convert_to_csw()
        rhs = self.rhs.convert_to_csw()
        strength = self.strength_map[self.strength]
        return csw.LinearInequality(lhs, csw.cnLEQ, rhs, strength)


class GEConstraint(LinearConstraint):

    op = '>='

    def convert_to_csw(self):
        lhs = self.lhs.convert_to_csw()
        rhs = self.rhs.convert_to_csw()
        strength = self.strength_map[self.strength]
        return csw.LinearInequality(lhs, csw.cnGEQ, rhs, strength)


class EQConstraint(LinearConstraint):

    op = '=='

    def convert_to_csw(self):
        lhs = self.lhs.convert_to_csw()
        rhs = self.rhs.convert_to_csw()
        strength = self.strength_map[self.strength]
        return csw.LinearEquation(lhs, rhs, strength)

