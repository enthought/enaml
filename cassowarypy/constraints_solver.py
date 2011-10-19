
from itertools import izip, chain

from traits.api import HasStrictTraits, Float, Str, ReadOnly

#------------------------------------------------------------------------------
# My Stuff
#------------------------------------------------------------------------------
class Symbolic(object):

    def _validate(self, other):
        if isinstance(other, Symbolic):
            res = other
        else:
            try:
                res = Constant(float(other))
            except TypeError:
                raise TypeError('Invalid expression value %s' % other)
        return res

    def __add__(self, other):
        other = self._validate(other)
        return LinearExpression(self, LinearExpression.ADD, other)

    def __radd__(self, other):
        other = self._validate(other)
        return LinearExpression(other, LinearExpression.ADD, self)
    
    def __sub__(self, other):
        other = self._validate(other)
        return LinearExpression(self, LinearExpression.SUB, other)

    def __rsub__(self, other):
        other = self._validate(other)
        return LinearExpression(other, LinearExpression.SUB, self)

    def __mul__(self, other):
        other = self._validate(other)
        return LinearExpression(self, LinearExpression.MUL, other)

    def __rmul__(self, other):
        other = self._validate(other)
        return LinearExpression(other, LinearExpression.MUL, self)
    
    def __div__(self, other):
        other = self._validate(other)
        return LinearExpression(self, LinearExpression.DIV, other)

    def __rdiv__(self, other):
        other = self._validate(other)
        return LinearExpression(other, LinearExpression.DIV, self)

    def __lt__(self, other):
        other = self._validate(other)
        return LinearInequality(self, LinearInequality.LT, other)
    
    def __le__(self, other):
        other = self._validate(other)
        return LinearInequality(self, LinearInequality.LE, other)
    
    def __gt__(self, other):
        other = self._validate(other)
        return LinearInequality(self, LinearInequality.GT, other)
    
    def __ge__(self, other):
        other = self._validate(other)
        return LinearInequality(self, LinearInequality.GE, other)
    
    def __eq__(self, other):
        other = self._validate(other)
        return LinearInequality(self, LinearInequality.EQ, other)


class LinearExpression(Symbolic):

    ADD = 0
    
    SUB = 1
    
    MUL = 2
    
    DIV = 3

    op_map = {ADD: '+', SUB: '-', MUL: '*', DIV: '/'}

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def __repr__(self):
        return '(%s %s %s)' % (self.lhs, self.op_map[self.op], self.rhs)

    def __str__(self):
        return self.__repr__()

    def variables(self):
        lvars = self.lhs.variables()
        rvars = self.rhs.variables()
        return set(v for v in chain(lvars, rvars))


class LinearInequality(object):

    LT = 0

    LE = 1

    GT = 2

    GE = 3

    EQ = 4

    op_map = {LT: '<', LE: '<=', GT: '>', GE: '>=', EQ: '=='}

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def __repr__(self):
        return '%s %s %s' % (self.lhs, self.op_map[self.op], self.rhs)

    def __str__(self):
        return self.__repr__()


class Constant(HasStrictTraits, Symbolic):

    value = ReadOnly

    def __init__(self, value):
        super(Constant, self).__init__()
        try:
            self.value = float(value)
        except TypeError:
            raise TypeError('Invalid constant value %s' % value)
    
    def __repr__(self):
        return '%s' % self.value
    
    def __str__(self):
        return self.__repr__()

    def __abs__(self):
        return abs(self.value)

    def variables(self):
        return ()


class Variable(HasStrictTraits, Symbolic):

    name = Str

    value = Float

    def __init__(self, name='', value=0.0):
        super(Variable, self).__init__(name=name, value=value)

    def __repr__(self):
        return '%s{%s}' % (self.name, self.value)
    
    def __str__(self):
        return self.__repr__()
        
    def __abs__(self):
        return abs(self.value)

    def variables(self):
        yield self


class ObjectiveVariable(object):

    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name


#------------------------------------------------------------------------------
# Solver
#------------------------------------------------------------------------------
class Tableau(object):

    @classmethod
    def approx(cls, a, b):
        epsilon = 1e-8
        if a == 0.0:
            res = abs(b) < epsilon
        elif b == 0.0:
            res = abs(a) < epsilon
        else:
            res = abs(a - b) < (abs(a) * epsilon)
        return res

    def __init__(self):
        self.columns = {}
        self.rows = {}
        self.external_rows = set()
        self.external_parameteric_vars = set()
        self.infeasible_rows = set()

    def note_removed_variable(self, var, subject):
        self.columns[var].discard(subject)

    def note_added_variable(self, var, subject):
        if subject:
            self.insert_col_var(var, subject)
    
    def insert_col_var(self, param_var, row_var):
        rowset = self.columns.get(param_var)
        if rowset is None:
            rowset = self.columns[param_var] = set()
        rowset.add(row_var)

    def add_row(self, var, expr):
        self.rows[var] = expr

        for clv in expr.variables():
            self.insert_col_var(clv, var)
            if clv.is_external:
                self._external_parametric_vars.add(clv)
        
        if var.is_external:
            self._external_rows.add(var)
    
    def remove_column(self, var):
        rows = self.columns.pop(var, ())

        for clv in rows:
            expr = self.rows[clv]
            expr.terms().discard(var) # XXX what does this do?
        
        if var.is_external:
            self.external_rows.discard(var)
            self.external_parametric_vars.discard(var)
    
    def remove_row(self, var, empty=set()):
        expr = self.rows.pop(var, ())
        
        for clv, coeff in expr.terms():
            varset = self.columns.get(clv)
            if varset:
                varset.discard(var)
        
        self.infeasible_rows.discard(var)

        if var.is_external:
            self.external_rows.discar(var)
        
        return expr

    def substitute_out(self, old_var, expr):
        varset = self.columns.pop(old_var)
        
        for v in varset:
            row = self.rows[v]
            row.substitute_out(old_var, expr, v, self)
            if v.is_restricted and row.constant() < 0.0:
                self._infeasible_rows.add(v)
        
        if old_var.is_external:
            self._external_rows.add(old_var)
            self._external_parametric_vars.discard(old_var)
         
    def columns_has_key(self, subject):
        return subject in self.columns
    
    def row_expression(self, var):
        return self.rows[var]

           
class SimplexSolver(Tableau):

    def __init__(self):
        super(SimplexSolver, self).__init__()
        self.stay_minus_error_vars = []
        self.stay_plus_error_vars = []

        self.error_vars = {}
        self.marker_vars = {}

        self.resolve_pair = [0.0, 0.0]

        self.objective = ObjectiveVariable('Z')

        self.edit_var_map = {}

        self.slack_counter = 0
        self.artificial_counter = 0
        self.dummy_counter = 0
        self.epsilon = 1e-8

        self.optimize_automatically = True
        self.needs_solving = False
        
        v = Constant(0)
        e = v + v
        self.rows[self.objective] = e

        self.stack_cedcns = [0]

    def add_constraint(self, constraint):
        eplu
#------------------------------------------------------------------------------
# My Stuff
#------------------------------------------------------------------------------
class Constant(object):

    __slot__ = ('value',)

    def __init__(self, value):
        try:
            self.value = float(value)
        except TypeError:
            raise TypeError('Invalid value %s' % value)
    
    def __repr__(self):
        return str(self.value)
    
    def __str__(self):
        return self.__repr__()

    def __add__(self, other):
        if isinstance(other, (int, float)):
            res = Constant(self.value + other)
        elif isinstance(other, Constant):
            res = Constant(self.value + other.value)
        elif isinstance(other, Variable):
            res = LinearExpression([other], const=self)
        elif isinstance(other, LinearExpression):
            const = self + other.const
            res = LinearExpression(other.terms, const=const)
        else:
            raise TypeError('Invalid expression component %s' % other)
        return res

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            res = Constant(self.value - other)
        elif isinstance(other, Constant):
            res = Constant(self.value - other.value)
        elif isinstance(other, Variable):
            other = other * -1
            res = LinearExpression([other], const=self)
        elif isinstance(other, LinearExpression):
            const = self - other.const
            terms = [term * -1 for term in other.terms]
            res = LinearExpression(terms, const=const)
        else:
            raise TypeError('Invalid expression component %s' % other)
        return res

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            res = Constant(other - self.value)
        elif isinstance(other, Constant):
            res = Constant(other.value - self.value)
        elif isinstance(other, Variable):
            const = -1 * self
            res = LinearExpression([other], const=const)
        elif isinstance(other, LinearExpression):
            const = other.const - self
            res = LinearExpression(other.terms, const=const)
        else:
            raise TypeError('Invalid expression component %s' % other)
        return res

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            res = Constant(other * self.value)
        elif isinstance(other, Constant):
            res = Constant(other.value * self.value)
        elif isinstance(other, Variable):
            coeff = self.value * other.coeff
            res = Variable(other.name, coeff=coeff)
        elif isinstance(other, LinearExpression):
            terms = [self * term for term in other.terms]
            const = other.const
            res = LinearExpression(terms, const=const)
        else:
            raise TypeError('Invalid expression component %s' % other)
        return res

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __div__(self, other):
        if isinstance(other, (int, float)):
            res = Constant(self.value / float(other))
        elif isinstance(other, Constant):
            res = Constant(self.value / float(other.value))
        elif isinstance(other, (Variable, LinearExpression)):
            raise ValueError('Non-linear expression')
        else:
            raise TypeError('Invalid expression component %s' % other)
        return res

    def __rdiv__(self, other):
        if isinstance(other, (int, float)):
            res = Constant(other / float(self.value))
        elif isinstance(other, Constant):
            res = Constant(other.value / float(self.value))
        elif isinstance(other, Variable):
            coeff = other.coeff / float(self.value)
            ret
        else:
            raise TypeError('Invalid expression component %s' % other)
        return res

    def __lt__(self, other):
        other = self._validate(other)
        return LinearInequality(self, LinearInequality.LT, other)
    
    def __le__(self, other):
        other = self._validate(other)
        return LinearInequality(self, LinearInequality.LE, other)
    
    def __gt__(self, other):
        other = self._validate(other)
        return LinearInequality(self, LinearInequality.GT, other)
    
    def __ge__(self, other):
        other = self._validate(other)
        return LinearInequality(self, LinearInequality.GE, other)
    
    def __eq__(self, other):
        other = self._validate(other)
        return LinearInequality(self, LinearInequality.EQ, other)


class Variable(Symbol):

    __slots__ = ('name', 'value', 'coeff')

    def __init__(self, name, value=0.0, coeff=1.0):
        self.name = name
        self.value = value
        self.coeff = coeff
                
    def __repr__(self):
        return '%s%s' % (self.coeff, self.name)
    
    def __str__(self):
        return self.__repr__()


class LinearExpression(Symbol):

    __slots__ = ('lhs', 'op', 'rhs')

    ADD = 0
    
    SUB = 1
    
    MUL = 2
    
    DIV = 3

    op_map = {ADD: '+', SUB: '-', MUL: '*', DIV: '/'}

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def __repr__(self):
        return '(%s %s %s)' % (self.lhs, self.op_map[self.op], self.rhs)

    def __str__(self):
        return self.__repr__()

    def variables(self, varset=None):
        if varset is None:
            varset = set()

        lhs = self.rhs
        if isinstance(lhs, Variable):
            varset.add(lhs)
        elif isinstance(lhs, LinearExpression):
            lhs.variables(varset)

        rhs = self.rhs
        if isinstance(rhs, Variable):
            varset.add(rhs)
        elif isinstance(rhs, LinearExpression):
            rhs.variables(varset)
        
        return varset


class LinearInequality(object):

    __slots__ = ('lhs', 'op', 'rhs')

    LT = 0

    LE = 1

    GT = 2

    GE = 3

    EQ = 4

    op_map = {LT: '<', LE: '<=', GT: '>', GE: '>=', EQ: '=='}

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def __repr__(self):
        return '%s %s %s' % (self.lhs, self.op_map[self.op], self.rhs)

    def __str__(self):
        return self.__repr__()




class ObjectiveVariable(object):

    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name