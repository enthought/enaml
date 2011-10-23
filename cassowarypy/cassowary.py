import sys
from itertools import izip, chain

MAX_VALUE = sys.float_info.max

EPS = 1e-8

def almost_equal(a, b):
    if a == 0.0:
        res = abs(b) < EPS
    elif b == 0.0:
        res = abs(a) < EPS
    else:
        res = abs(a - b) < (abs(a) * EPS)
    return res


_calls = []
def wrap_all(cls):
    import types
    def wrapper(f):
        def caller(*args, **kwargs):
            res = f(*args, **kwargs)
            call = '%s::%s' % (cls.__name__, f.__name__)
            if call not in _calls:
                _calls.append(call)
            return res
        return caller
    
    for key, value in cls.__dict__.items():
        if isinstance(value, types.FunctionType):
            setattr(cls, key, wrapper(value))

    return cls

#------------------------------------------------------------------------------
# Variables
#------------------------------------------------------------------------------
@wrap_all
class AbstractVariable(object):

    iVariableNumber = 0

    def __init__(self, arg1=None, arg2=None):
        self.hash_code = self.iVariableNumber
        self.iVariableNumber += 1
        if arg1 is None or isinstance(arg1, basestring):
            self._name = arg1 if arg1 is not None else 'v%s' % self.hash_code
        else:
            varnumber = arg1
            prefix = arg2
            self._name = '%s%s' % (prefix, varnumber)

    def __repr__(self):
        return self.toString()
    
    def __str__(self):
        return self.toString()

    def hashCode(self):
        return self.hash_code

    def name(self):
        return self._name
    
    def setName(self, name):
        self._name = name

    def isDummy(self):
        return False

    def isExternal(self):
        raise NotImplementedError

    def isPivotable(self):
        raise NotImplementedError
    
    def isRestricted(self):
        raise NotImplementedError

    def toString(self):
        return 'ABSTRACT[%s]' % self._name
         
@wrap_all
class Variable(AbstractVariable):

    _ourVarMap = {}

    @classmethod
    def getVarMap(cls):
        return cls._ourVarMap
    
    @classmethod
    def setVarMap(cls, mapping):
        cls._ourVarMap = mapping

    def __init__(self, name_or_val=None, value=None):
        if isinstance(name_or_val, basestring):
            super(Variable, self).__init__(name_or_val)
            self._value = value if value is not None else 0.0
        elif isinstance(name_or_val, (int, float)):
            super(Variable, self).__init__()
            self._value = float(name_or_val)
        else:
            super(Variable, self).__init__()
            self._value = 0.0
        
        if self._ourVarMap is not None:
            self._ourVarMap[self._name] = self
        
        self._attachedObject = None

    def isDummy(self):
        return False
    
    def isExternal(self):
        return True
    
    def isPivotable(self):
        return False
    
    def isRestricted(self):
        return False
    
    def toString(self):
        return '[%s:%s]' % (self.name(), self._value)

    # change the value held -- should *not* use this if the variable is
    # in a solver -- instead use addEditVar() and suggestValue() interface
    def value(self):
        return self._value
    
    def set_value(self, value):
        self._value = value

    # permit overriding in subclasses in case something needs to be
    # done when the value is changed by the solver
    # may be called when the value hasn't actually changed -- just 
    # means the solver is setting the external variable
    def change_value(self, value):
        self._value = value

    def setAttachedObject(self, obj):
        self._attachedObject = obj
    
    def getAttachedObject(self, obj):
        self._attachedObject = obj

@wrap_all
class DummyVariable(AbstractVariable):

    def isDummy(self):
        return True
    
    def isExternal(self):
        return False

    def isPivotable(self):
        return False
    
    def isRestricted(self):
        return True

    def toString(self):
        return '[%s:dummy]' % self.name()

@wrap_all
class ObjectiveVariable(AbstractVariable):

    def isExternal(self):
        return False
    
    def isPivotable(self):
        return False
    
    def isRestricted(self):
        return False
    
    def toString(self):
        return '%s:obj:%s]' % (self.name(), self.hashCode())

@wrap_all
class SlackVariable(AbstractVariable):

    def isExternal(self):
        return False
    
    def isPivotable(self):
        return True
    
    def isRestricted(self):
        return True

    def toString(self):
        return '[%s:slack]' % self.name()


#------------------------------------------------------------------------------
# Point
#------------------------------------------------------------------------------
@wrap_all
class Point(object):

    def __init__(self, x, y, suffix=None):
        if isinstance(x, Variable):
            self.x = x
        else:
            if suffix is not None:
                self.x = Variable('x%s' % suffix, float(x))
            else:
                self.x = Variable(float(x))

        if isinstance(y, Variable):
            self.y = y
        else:
            if suffix is not None:
                self.y = Variable('y%s' % suffix, float(y))
            else:
                self.y = Variable(float(y))
    
    def SetXY(self, x, y):
        if isinstance(x, Variable):
            self.x = x
        else:
            self.x.set_value(x)
        
        if isinstance(y, Variable):
            self.y = y
        else:
            self.y.set_value(y)
                
    def X(self):
        return self.x
    
    def Y(self):
        return self.y

    def Xvalue(self):
        return self.X().value()
    
    def Yvalue(self):
        return self.Y().value()
    
    def toString(self):
        return '(%s, %s)' % (self._clv_x, self._clv_y)
    

#------------------------------------------------------------------------------
# Weights
#------------------------------------------------------------------------------
@wrap_all
class SymbolicWeight(object):

    def __init__(self, w1, w2, w3):
        w1 = float(w1)
        w2 = float(w2)
        w3 = float(w3)
        self._values = (w1, w2, w3)
    
    def __repr__(self):
        return self.toString()
    
    def __str__(self):
        return self.toString()

    def times(self, n):
        vals = (val * n for val in self._values)
        return SymbolicWeight(*vals)
    
    def divideBy(self, n):
        vals = (val / n for val in self._values)
        return SymbolicWeight(*vals)

    def add(self, other):
        vals = (this + that for this, that in izip(self._values, other._values))
        return SymbolicWeight(*vals)

    def subtract(self, other):
        vals = (this - that for this, that in izip(self._values, other._values))
        return SymbolicWeight(*vals)

    def lessThan(self, other):
        return self._values < other._values

    def lessThanOrEqual(self, other):
        return self._values <= other._values
    
    def equal(self, other):
        self._values == other._values

    def greaterThan(self, other):
        return not self.lessThatOrEqual(other)
    
    def greaterThanOrEqual(self, other):
        return not self.lessThan(other)

    def isNegative(self):
        return self.lessThan(self.clsZero)
    
    def toDouble(self):
        return sum(val * 1000**idx for idx, val in enumerate(reversed(self._values)))

    def toString(self):
        return '[%s]' % ', '.join(str(val) for val in self._values)
    
    def cLevels(self):
        return len(self._values)

SymbolicWeight.clsZero = SymbolicWeight(0.0, 0.0, 0.0)


#------------------------------------------------------------------------------
# Strength
#------------------------------------------------------------------------------
@wrap_all
class Strength(object):

    def __init__(self, name, symbolicWeight, w2=None, w3=None):
        self._name = name
        if isinstance(symbolicWeight, SymbolicWeight):
            self._symbolicWeight = symbolicWeight
        else:
            self._symbolicWeight = SymbolicWeight(symbolicWeight, w2, w3)

    def __repr__(self):
        return self.toString()
    
    def __str__(self):
        return self.toString()

    def isRequired(self):
        return self is self.required

    def toString(self):
        return '%s:%s' % (self.name(), self.symbolicWeight())
    
    def symbolicWeight(self):
        return self._symbolicWeight

    def name(self):
        return self._name
    
    def set_name(self, name):
        self._name = name
    
    def set_symbolicWeight(self, symbolicWeight):
        self._symbolicWeight = symbolicWeight

Strength.required = Strength('<required>', 1000., 1000., 1000.)

Strength.strong = Strength('<strong>', 1.0, 0.0, 0.0)

Strength.medium = Strength('<medium>', 0.0, 1.0, 0.0)

Strength.weak = Strength('<weak>', 0.0, 0.0, 1.0)


#------------------------------------------------------------------------------
# Constraints
#------------------------------------------------------------------------------
@wrap_all
class Constraint(object):

    iConstraintNumber = 0

    def __init__(self, strength=Strength.required, weight=1.0):
        self.hash_code = self.iConstraintNumber
        self.iConstraintNumber += 1
        self._strength = strength
        self._weight = weight
        self._times_added = 0
        self._attachedObject = None

    def __repr__(self):
        return self.toString()
    
    def __str__(self):
        return self.toString()
    
    def hashCode(self):
        return self.hash_code
    
    def isEditConstraint(self):
        return False

    def isInequality(self):
        return False

    def isRequired(self):
        return self._strength.isRequired()
    
    def isStayConstraint(self):
        return False

    def strength(self):
        return self._strength

    def weight(self):
        return self._weight

    def toString(self):
        return '%s{%s}(%s)' % (self._strength, self.weight(), self.expression())

    def setAttachedObject(self, obj):
        self._attachedObject = obj
    
    def getAttachedObject(self, obj):
        return self._attachedObject

    def changeStrength(self, strength):
        if self._times_added == 0:
            self.setStrength(strength)
        else:
            raise ValueError('Too difficult')
    
    def addedTo(self, solver):
        self._times_added += 1
    
    def removedFrom(self, solver):
        self._times_added -= 1

    def setStrength(self, strength):
        self._strength = strength
    
    def setWeight(self, weight):
        self._weight = weight

@wrap_all
class EditOrStayConstraint(Constraint):

    def __init__(self, clv, strength=Strength.required, weight=1.0):
        super(EditOrStayConstraint, self).__init__(strength, weight)
        self._variable = clv
        self._expression = LinearExpression(self._variable, -1.0, self._variable.value())

    def variable(self):
        return self._variable
    
    def expression(self):
        return self._expression
    
    def setVariable(self, var):
        self._variable = var

@wrap_all
class EditConstraint(EditOrStayConstraint):

    def isEditConstraint(self):
        return True
    
    def toString(self):
        return '%s %s' % ('edit', super(EditConstraint, self).toString())
    
@wrap_all
class StayConstraint(EditOrStayConstraint):

    def __init__(self, clv, strength=Strength.weak, weight=1.0):
        super(StayConstraint, self).__init__(clv, strength, weight)

    def isStayConstraint(self):
        return True

    def toString(self):
        return '%s %s' % ('stay', super(StayConstraint, self).toString())

@wrap_all
class LinearConstraint(Constraint):

    def __init__(self, expression, strength=Strength.required, weight=1.0):
        super(LinearConstraint, self).__init__(strength, weight)
        self._expression = expression

    def expression(self):
        return self._expression
    
    def setExpression(self, expr):
        self._expression = expr

@wrap_all
class LinearInequality(LinearConstraint):

    def __init__(self, a1, a2=None, a3=None, a4=Strength.required, a5=1.0):
        if isinstance(a1, LinearExpression) and isinstance(a3, AbstractVariable):
            cle = a1
            op = a2
            clv = a3
            super(LinearInequality, self).__init__(cle.clone(), a4, a5)
            if op == CL.LEQ:
                self._expression.multiplyMe(-1.0)
                self._expression.addVariable(clv)
            elif op == CL.GEQ:
                self._expression.addVariable(clv, -1.0)
            else:
                raise ValueError('Invalid operator in LinearInequality constructor')
        elif isinstance(a1, LinearExpression):
            if a2 is None:
                a2 = Strength.required
            if a3 is None:
                a3 = 1.0
            super(LinearInequality, self).__init__(a1, a2, a3)
        elif a2 == CL.GEQ:
            super(LinearInequality, self).__init__(LinearExpression(a3), a4, a5)
            self._expression.multiplyMe(-1.0)
            self._expression.addVariable(a1)
        elif a2 == CL.LEQ:
            super(LinearInequality, self).__init__(LinearExpression(a3), a4, a5)
            self._expression.addVariable(a1, -1.0)
        else:
            raise ValueError('Invalid operator in LinearInequality constructor')

    def isInequality(self):
        return True
    
    def toString(self):
        return '%s >= 0 )' % super(LinearInequality, self).toString()

@wrap_all
class LinearEquation(LinearConstraint):

    def __init__(self, a1, a2=None, a3=None, a4=None):
        if isinstance(a1, LinearExpression) and not a2 or isinstance(a2, Strength):
            a2 = a2 or Strength.required
            a3 = a3 or 1.0
            super(LinearEquation, self).__init__(a1, a2, a3)
        elif isinstance(a1, AbstractVariable) and isinstance(a2, LinearExpression):
            clv = a1
            cle = a2
            strength = a3 or Strength.required
            weight = a4 or 1.0
            super(LinearEquation, self).__init__(cle, strength, weight)
            self._expression.addVariable(clv, -1.0)
        elif isinstance(a1, AbstractVariable) and isinstance(a2, (int, float)):
            clv = a1
            val = float(a2)
            strength = a3 or Strength.required
            weight = a4 or 1.0
            super(LinearEquation, self).__init__(LinearExpression(val), strength, weight)
            self._expression.addVariable(clv, -1.0)
        elif isinstance(a1, LinearExpression) and isinstance(a2, AbstractVariable):
            cle = a1
            clv = a2
            strength = a3 or Strength.required
            weight = a4 or 1.0
            super(LinearEquation, self).__init__(cle.clone(), strength, weight)
            self._expression.addVariable(clv, -1.0)
        elif ((isinstance(a1, LinearExpression) or isinstance(a1, AbstractVariable) or isinstance(a1, (float, int))) and
              (isinstance(a2, LinearExpression) or isinstance(a2, AbstractVariable) or isinstance(a2, (float, int)))):
            if isinstance(a1, LinearExpression):
                a1 = a1.clone()
            else:
                a1 = LinearExpression(a1)
            if isinstance(a2, LinearExpression):
                a2 = a2.clone()
            else:
                a2 = LinearExpression(a2)
            a3 = a3 or Strength.required
            a4 = a4 or 1.0
            super(LinearEquation, self).__init__(a1, a3, a4)
            self._expression.addExpression(a2, -1.0)
        else:
            raise ValueError('Bad initializer to LinearEquation.')

    def toString(self):
        return '%s = 0 )' % super(LinearEquation, self).toString()
    

#------------------------------------------------------------------------------
# Linear Expression
#------------------------------------------------------------------------------
@wrap_all
class LinearExpression(object):
            
    def __init__(self, clv=None,  value=1.0, constant=0.0):
        self._constant = constant
        self._terms = {}
        if isinstance(clv, AbstractVariable):
            self._terms[clv] = value
        elif isinstance(clv, (float, int)):
            self._constant = float(clv)
        
    def __repr__(self):
        return self.toString()
    
    def __str__(self):
        return self.toString()

    def initializeFromHash(self, constant, terms):
        self._constant = constant
        self._terms = terms.copy()
        return self

    def multiplyMe(self, n):
        self._constant *= n
        for var, coeff in self._terms.iteritems():
            self._terms[var] = coeff * n
        return self

    def clone(self):
        return LinearExpression().initializeFromHash(self._constant, self._terms)
    
    def times(self, expr):
        if isinstance(expr, (float, int)):
            res = self.clone().multiplyMe(expr)
        else:
            if self.isConstant():
                res = expr.times(self._constant)
            elif expr.isConstant():
                res = self.times(expr._constant)
            else:
                raise ValueError('Nonlinear expression')
        return res

    def plus(self, expr):
        if isinstance(expr, LinearExpression):
            res = self.clone().addExpression(expr, 1.0)
        elif isinstance(expr, Variable):
            res = self.clone().addVariable(expr, 1.0)
        else:
            raise ValueError('Something messed up that isnt handled by cassowary')
        return res
    
    def minus(self, expr):
        if isinstance(expr, LinearExpression):
            res = self.clone().addExpression(expr, -1.0)
        elif isinstance(expr, Variable):
            res = self.clone().addVariable(expr, -1.0)
        else:
            raise ValueError('Something messed up that isnt handled by cassowary')
        return res
    
    def divide(self, expr):
        if isinstance(expr, (float, int)):
            expr = float(expr)
            if almost_equal(expr, 0.0):
                raise ValueError('Nonlinear expression (divide by zero)')
            res = self.times(1.0 / expr)
        elif isinstance(expr, LinearExpression):
            if not expr.isConstant():
                raise ValueError('Nonlinear expression')
            res = self.times(1.0 / expr._constant)
        else:
            raise ValueError('Something messed up that isnt handled by cassowary')
        return res

    def divFrom(self, expr):
        if not self.isConstant() or almost_equal(self._constant, 0.0):
            raise ValueError('Nonlinear expresssion')
        return expr.divide(self)
    
    def subtractFrom(self, expr):
        return expr.minus(self)
    
    def addExpression(self, expr, n=0.0, subject=None, solver=None):
        if isinstance(expr, AbstractVariable):
            expr = LinearExpression(expr)
            print 'casted var to expression'
        self.incrementConstant(n * expr.constant())
        n = n or 1.0
        for var, coeff in expr.terms().iteritems():
            self.addVariable(var, coeff * n, subject, solver)
        return self
    
    def addVariable(self, var, c=1.0, subject=None, solver=None):
        coeff = self._terms.get(var)
        if coeff is not None:
            new_coeff = coeff + c
            if almost_equal(new_coeff, 0.0):
                if solver is not None:
                    solver.noteRemovedVariable(var, subject)
                del self._terms[var]
            else:
                self._terms[var] = new_coeff
        else:
            if not almost_equal(c, 0.0):
                self._terms[var] = c
                if solver is not None:
                    solver.noteAddedVariable(var, subject)
        return self

    def setVariable(self, var, c):
        self._terms[var] = c
        return self
    
    def anyPivotVariable(self):
        if self.isConstant():
            raise ValueError('anyPivotableVariable called on a constant')
        for var in self._terms:
            if var.isPivotable():
                return var
    
    def substituteOut(self, outvar, expr, subject, solver):
        multiplier = self._terms.pop(outvar)
        self.incrementConstant(multiplier * expr.constant())
        for var, coeff in expr.terms().iteritems():
            old_coeff = self._terms.get(var)
            if old_coeff is not None:
                newCoeff = old_coeff + multiplier * coeff
                if almost_equal(newCoeff, 0.0):
                    solver.noteRemovedVariable(var, subject)
                    del self._terms[var]
                else:
                    self._terms[var] = newCoeff
            else:
                self._terms[var] = multiplier * coeff
                solver.noteAddedVariable(var, subject)
        
    def changeSubject(self, old_subject, new_subject):
        self._terms[old_subject] = self.newSubject(new_subject)
    
    def newSubject(self, subject):
        reciprocal = 1.0 / self._terms.pop(subject)
        self.multiplyMe(-reciprocal)
        return reciprocal
    
    def coefficientFor(self, var):
        return self._terms.get(var, 0.0)
    
    def constant(self):
        return self._constant
    
    def set_constant(self, c):
        self._constant = c
    
    def terms(self):
        return self._terms
    
    def incrementConstant(self, c):
        self._constant += c
    
    def isConstant(self):
        return len(self._terms) == 0
    
    def toString(self):
        bstr = ''
        needsplus = False
        if not almost_equal(self._constant, 0.0) or self.isConstant():
            bstr += str(self._constant)
            if self.isConstant():
                return bstr
            else:
                needsplus = True
        for var, coeff in self._terms.iteritems():
            if needsplus:
                bstr += ' + '
            bstr += '%s * %s'  % (coeff, var)
            needsplus = True
        return bstr
    
    @staticmethod
    def Plus(e1, e2):
        return e1.plus(e2)
    
    @staticmethod
    def Minus(e1, e2):
        return e1.minus(e2)
    
    @staticmethod
    def Times(e1, e2):
        return e1.times(e2)
    
    @staticmethod
    def Divide(e1, e2):
        return e1.divide(e2)


#------------------------------------------------------------------------------
# CL
#------------------------------------------------------------------------------
@wrap_all
class CL(object):
    
    GEQ = 1
    LEQ = 2

    def debugprint(self, s):
        pass
    
    def traceprint(self, s):
        pass
    
    def fnenterprint(self, s):
        pass
    
    def fnexitprint(self, s):
        pass
    
    def Assert(self, f, description):
        assert f, description
    
    @staticmethod
    def Plus(e1, e2):
        if not isinstance(e1, LinearExpression):
            e1 = LinearExpression(e1)
        if not isinstance(e2, LinearExpression):
            e2 = LinearExpression(e2)
        return e1.plus(e2)
    
    @staticmethod
    def Minus(e1, e2):
        if not isinstance(e1, LinearExpression):
            e1 = LinearExpression(e1)
        if not isinstance(e2, LinearExpression):
            e2 = LinearExpression(e2)
        return e1.minus(e2)
    
    @staticmethod
    def Times(e1, e2):
        if isinstance(e1, LinearExpression) and isinstance(e2, LinearExpression):
            res = e1.times(e2)
        elif isinstance(e1, LinearExpression) and isinstance(e2, Variable):
            res = e1.times(LinearExpression(e2))
        elif isinstance(e1, Variable) and isinstance(e2, LinearExpression):
            res = LinearExpression(e1).times(e2)
        elif isinstance(e1, LinearExpression) and isinstance(e2, (float, int)):
            res = e1.times(LinearExpression(e2))
        elif isinstance(e1, (float, int)) and isinstance(e1, LinearExpression):
            res = LinearExpression(e1).times(e2)
        elif isinstance(e1, (float, int)) and isinstance(e2, Variable):
            res = LinearExpression(e2, e1)
        elif isinstance(e1, Variable) and isinstance(e2, (float, int)):
            res = LinearExpression(e1, e2)
        else:
            raise ValueError('Something broke in cassowary')
        return res

    @staticmethod
    def Divide(e1, e2):
        return e1.divide(e2)


#------------------------------------------------------------------------------
# Tableau
#------------------------------------------------------------------------------
@wrap_all
class Tableau(object):

    def __init__(self):
        self._columns = {}
        self._rows = {}
        self._infeasibleRows = set()
        self._externalRows = set()
        self._externalParametricVars = set()
    
    def __repr__(self):
        return self.toString()

    def __str__(self):
        return self.toString()

    def noteRemovedVariable(self, var, subject):
        if subject is not None:
            self._columns[var].discard(subject)
    
    def noteAddedVariable(self, var, subject):
        if subject is not None:
            self.insertColVar(var, subject)
    
    def getInternalInfo(self):
        strs = [
            "Tableau Information:\n",
            "Rows %s" % len(self._rows),
            " (= %s constraints" % (len(self._rows) - 1),
            "\nColumns: %s" % len(self._columns),
            "\nInfeasible Rows: %s" % len(self._infeasibleRows),
            "\nExternal basic variables: %s" % len(self._externalRows),
            "\nExternal parametric variables: %s\n" % len(self._externalParametricVars),
        ]
        return ''.join(strs)

    def toString(self):
        headings = ['Tableau:', 'Columns:', 'Infeasible rows:', 
                    'External basic variables:', 'External parametric variables:']
        
        templ = '\n\n%s\n'.join(headings)

        row_parts = ['%s <==> %s\n' % item for item in self._rows.iteritems()]
        rows = ''.join(row_parts)
        return 'tableau'
        return templ % (rows, self._columns, self._infeasibleRows,
                        self._externalRows, self._externalParametricVars)
    
    def insertColVar(self, param_var, row_var):
        self._columns.setdefault(param_var, set()).add(row_var)

    def addRow(self, aVar, expr):
        self._rows[aVar] = expr
        for var, coeff in expr.terms().iteritems():
            self.insertColVar(var, aVar)
            if var.isExternal():
                self._externalParametricVars.add(var)
        if aVar.isExternal():
            self._externalRows.add(aVar)

    def removeColumn(self, aVar):
        rows = self._columns.pop(aVar, None)
        if rows is not None:
            for var in rows:
                expr = self._rows[var]
                expr.terms().pop(aVar, None)
        else:
            pass
        if aVar.isExternal():
            self._externalRows.discard(aVar)
            self._externalParametricVars.discard(aVar)
    
    def removeRow(self, aVar):
        expr = self._rows[aVar]
        for var, coeff in expr.terms().iteritems():
            varset = self._columns.get(var)
            if varset is not None:
                varset.discard(aVar)
        self._infeasibleRows.discard(aVar)
        if aVar.isExternal():
            self._externalRows.discard(aVar)
        del self._rows[aVar]
        return expr

    def substituteOut(self, oldVar, expr):
        varset = self._columns[oldVar]
        for var in varset:
            row = self._rows[var]
            row.substituteOut(oldVar, expr, var, self)
            if var.isRestricted() and row.constant() < 0.0:
                self._infeasibleRows.add(var)
        if oldVar.isExternal():
            self._externalRows.add(oldVar)
            self._externalParametricVars.discard(oldVar)
        del self._columns[oldVar]
        
    def columns(self):
        return self._columns
        
    def rows(self):
        return self._rows
    
    def columnsHasKey(self, subject):
        return subject in self._columns
    
    def rowExpression(self, var):
        return self._rows.get(var)

                
#------------------------------------------------------------------------------
# Simplex Solver
#------------------------------------------------------------------------------


@wrap_all
class SimplexSolver(Tableau):

    def __init__(self):
        super(SimplexSolver, self).__init__()
        self._stayMinusErrorVars = []
        self._stayPlusErrorVars = []
        self._errorVars = {}
        self._markerVars = {}
        self._resolve_pair = [0, 0]
        self._objective = ObjectiveVariable('Z')
        self._editVarMap = {}
        self._slackCounter = 0
        self._artificialCounter = 0
        self._dummyCounter = 0
        self._epsilon = EPS
        self._fOptimizeAutomatically = True
        self._fNeedsSolving = False
        self._rows = {}
        self._rows[self._objective] = LinearExpression()
        self._stkCedcns = [0]
    
    def addLowerBound(self, var, lower):
        cn = LinearInequality(var, CL.GEQ, LinearExpression(lower))
        return self.addConstraint(cn)
    
    def addUpperBound(self, var, upper):
        cn = LinearInequality(var, CL.LEQ, LinearExpression(upper))
        return self.addConstraint(cn)
    
    def addBounds(self, var, lower, upper):
        self.addLowerBound(var, lower)
        self.addUpperBound(var, upper)
        return self
    
    def addConstraint(self, cn):
        print '->>>>>>>> adding', cn
        eplus_eminus = [None, None]
        prevEConstant = [None]
        expr = self.newExpression(cn, eplus_eminus, prevEConstant)
        prevEConstant = prevEConstant[0]

        fAddedOkDirectly = self.tryAddingDirectly(expr)
        if not fAddedOkDirectly:
            self.addWithArtificialVariable(expr)
        
        self._fNeedsSolving = True
        
        if cn.isEditConstraint():
            i = len(self._editVarMap)
            clvEplus, clvEminus = eplus_eminus
            if not isinstance(clvEplus, SlackVariable):
                print 'clvEplus not a slack variable = ' + clvEplus
            if not isinstance(clvEminus, SlackVariable):
                print 'clvEminus not a slack variable = ' + clvEminus
            self._editVarMap[cn.variable()] = EditInfo(cn, clvEplus, clvEminus, prevEConstant, i)
        
        if self._fOptimizeAutomatically:
            self.optimize(self._objective)
            self.setExternalVariables()
        
        cn.addedTo(self)

        return self
    
    def addConstraintNoException(self, cn):
        try:
            self.addConstraint(cn)
            return True
        except Exception as e:
            print 'addConstraintNotException exc', e
            return False
    
    def addEditVar(self, var, strength=Strength.strong):
        cnEdit = EditConstraint(var, strength)
        return self.addConstraint(cnEdit)
    
    def removeEditVar(self, var):
        cei = self._editVarMap.get(var)
        cn = cei.Constraint()
        self.removeConstraint(cn)
        return self
    
    def beginEdit(self):
        assert len(self._editVarMap) > 0, 'len(self._editVarMap) > 0'
        self._infeasibleRows.clear()
        self.resetStayConstants()
        self._stkCedcns.append(len(self._editVarMap))
        return self
    
    def endEdit(self):
        assert len(self._editVarMap) > 0, 'len(self._editVarMap) > 0'
        self.resolve()
        self._stkCedcns.pop()
        n = self._stkCedcns[-1]
        self.removeEditVarsTo(n)
        return self
    
    def removeAllEditVars(self):
        return self.removeEditVarsTo(0)
    
    def removeEditVarsTo(self, n):
        for var, cei in self._editVarMap.items():
            if cei.Index() >= n:
                self.removeEditVar(var)
        assert len(self._editVarMap) == n
        return self
    
    def addPointStays(self, listOfPoints):
        weight = 1.0
        multiplier = 2.0
        for point in listOfPoints:
            self.addPointStay(point, weight)
            weight *= multiplier
        return self
    
    def addPointStay(self, a1=None, a2=None, a3=None):
        if isinstance(a1, Point):
            weight = a2 if a2 is not None else 1.0
            self.addStay(a1.X(), Strength.weak, weight)
            self.addStay(a1.Y(), Strength.weak, weight)
        else:
            weight = a3 or 1.0
            self.addStay(a1, Strength.weak, weight)
            self.addStay(a2, Strength.weak, weight)
        return self
    
    def addStay(self, var, strength=Strength.weak, weight=1.0):
        cn = StayConstraint(var, strength, weight)
        return self.addConstraint(cn)
    
    def removeConstraint(self, cn):
        self.removeConstraintInternal(cn)
        cn.removedFrom(self)
        return self

    def removeConstraintInternal(self, cn):
        self._fNeedsSolving = True

        self.resetStayConstants()

        zRow = self.rowExpression(self._objective)

        eVars = self._errorVars.get(cn)
        if eVars is not None:
            for var in eVars:
                expr = self.rowExpression(var)
                if expr is None:
                    zRow.addVariable(var, -cn.weight() * cn.strength().symbolicWeight().toDouble(), self._objective, self)
                else:
                    zRow.addExpression(expr, -cn.weight() * cn.strength().symbolicWeight().toDouble(), self._objective, self)
        
        try:
            marker = self._markerVars.pop(cn)
        except KeyError:
            raise ValueError('Constraint not found')
        
        if self.rowExpression(marker) is None:
            col = self._columns[marker]
            exitVar = None
            minRatio = 0.0
            
            for var in col:
                if var.isRestricted():
                    expr = self.rowExpression(var)
                    coeff = expr.coefficientFor(marker)
                    if coeff < 0.0:
                        r = -expr.constant() / coeff
                        if exitVar is None or r < minRatio or (almost_equal(r, minRatio) and var.hasCode() < exitVar.hashCode()):
                            minRatio = r
                            exitVar = var
            
            if exitVar is None:
                for var in col:
                    if var.isRestricted():
                        expr = self.rowExpression(var)
                        coeff = expr.coefficientFor(marker)
                        r = expr.constant() / coeff
                        if exitVar is None or r < minRatio:
                            minRatio = r
                            exitVar = var
            
            if exitVar is None:
                if len(col) == 0:
                    self.removeColumn(marker)
                else:
                    for var in col:
                        if var is not self._objective:
                            exitVar = var
                            break
            
            if exitVar is not None:
                self.pivot(marker, exitVar)

        if self.rowExpression(marker) is not None:
            expr = self.removeRow(marker)
            expr = None
        
        if eVars is not None:
            for var in eVars:
                if var is not marker:
                    self.removeColumn(var)
        
        if cn.isStayConstraint():
            if eVars is not None:
                for vvar in chain(self._stayPlusErrorVars, self._stayMinusErrorVars):
                    eVars.pop(vvar, None)
        elif cn.isEditConstraint():
            assert eVars is not None, 'eVars is not None'
            clv = cn.variable()
            cei = self._editVarMap[clv]
            clvEditMinus = cei.ClvEditMinus()
            self.removeColumn(clvEditMinus)
            del self._editVarMap[clv]
        
        if eVars is not None:
            self._errorVars.pop(eVars, None)
        
        marker = None

        if self._fOptimizeAutomatically:
            self.optimize(self._objective)
            self.setExternalVariables()
        
        return self
    
    def reset(self):
        raise NotImplementedError('reset not implemented')
    
    def resolveArray(self, newEditConstants):
        for var, cei in self._editVarMap.iteritems():
            i = cei.Index()
            if i < len(newEditConstants):
                self.suggestValue(var, newEditConstants[i])
        self.resolve()
    
    def resolvePair(self, x, y):
        self._resolve_pair[:] = (x, y)
        self.resolveArray(self._resolve_pair)
    
    def resolve(self):
        self.dualOptimize()
        self.setExternalVariables()
        self._infeasibleRows.clear()
        self.resetStayContants()
    
    def suggestValue(self, var, x):
        cei = self._editVarMap.get(var)
        if cei is None:
            raise ValueError('suggest value var is not an edit variable')
        clvEditPlus = cei.ClvEditPlus()
        clvEditMinus = cei.ClvEditMinus()
        delta = x - cei.PrevEditConstant()
        cei.SetPrevEditConstant(x)
        self.deltaEditConstant(delta, clvEditPlus, clvEditMinus)
        return self
    
    def setAutosolve(self, f):
        self._fOptimizeAutomatically = f
        return self
    
    def FIsAutoSolving(self):
        return self._fOptimizeAutomatically
    
    def solve(self):
        if self._fNeedsSolving:
            self.optimize(self._objective)
            self.setExternalVariables()
        return self
    
    def setEditedValue(self, var, n):
        if not self.FContainsVariable(var):
            var.change_value(n)
            return self
        
        if not almost_equal(n, var.value()):
            self.addEditVar(var)
            self.beginEdit()
            try:
                self.suggestValue(var, n)
            except Exception as e:
                raise ValueError('Error in setEditedValue: %s' % e)
            self.endEdit()
        
        return self
    
    def FContainsVariable(self, var):
        return self.columnsHasKey(var) or self.rowExpression(var) is not None
    
    def addVar(self, var):
        if not self.FContainsVariable(var):
            try:
                self.addStay(var)
            except Exception as e:
                raise ValueError('Error in addVar %s' % e)
        return self
    
    def getInternalInfo(self):
        return 'a bunch of stuff'
    
    def getDebugInfo(self):
        return 'a bunch of stuff'
    
    def getContraintMap(self):
        return self._markerVars
    
    def addWithArtificialVariable(self, expr):
        self._artificialCounter += 1
        av = SlackVariable(self._artificialCounter, 'a')
        az = ObjectiveVariable('az')
        azRow = expr.clone()
        self.addRow(az, azRow)
        self.addRow(av, expr)
        self.optimize(az)

        azTableauRow = self.rowExpression(az)
        if not almost_equal(azTableauRow.constant(), 0.0):
            self.removeRow(az)
            self.removeColumn(av)
            raise ValueError('Required Failure')
        
        e = self.rowExpression(av)
        if e is not None:
            if e.isConstant():
                self.removeRow(av)
                self.removeRow(az)
                return
            entryVar = e.anyPivotableVariable()
            self.pivot(entryVar, av)
        
        assert self.rowExpression(av) is None, 'rowExpression(av) is None'
        self.removeColumn(av)
        self.removeColumn(az)
    
    def tryAddingDirectly(self, expr):
        subject = self.chooseSubject(expr)
        if subject is None:
            return False
        
        expr.newSubject(subject)
        if self.columnsHasKey(subject):
            self.substituteOut(subject, expr)
        
        self.addRow(subject, expr)

        return True

    def chooseSubject(self, expr):
        subject = None
        foundUnrestricted = False
        foundNewRestricted = False

        terms = expr.terms()
        for v, c in terms.iteritems():
            if foundUnrestricted:
                if not v.isRestricted():
                    if not self.columnsHasKey(v):
                        return v
            else:
                if v.isRestricted():
                    if not foundNewRestricted and not v.isDummy() and c < 0.0:
                        col = self._columns.get(v)
                        if col is None or (len(col) == 1 and self.columnsHasKey(self._objective)):
                            subject = v
                            foundNewRestricted = True
                    else:
                        subject = v
                        foundUnrestricted = True
        
        if subject is not None:
            return subject
        
        coeff = 0.0

        for v, c in terms.iteritems():
            if not v.isDummy():
                return None
            if not self.columnsHasKey(v):
                subject = v
                coeff = c
            
        if coeff > 0.0:
            expr.multiplyMe(-1.0)
        
        return subject
    
    def deltaEditConstant(self, delta, plusErrorVar, minusErrorVar):
        exprPlus = self.rowExpression(plusErrorVar)
        if exprPlus is not None:
            exprPlus.incrementConstant(delta)
            if exprPlus.constant() < 0.0:
                self._infeasibleRows.add(plusErrorVar)
            return

        exprMinus = self.rowExpression(minusErrorVar)
        if exprMinus is not None:
            exprMinus.incrementConstant(-delta)
            if exprMinus.constant() < 0.0:
                self._infeasibleRows.add(minusErrorVar)
            return
        
        columnVars = self._columns.get(minusErrorVar)
        if columnVars is None:
            print 'columnVars is None'
        else:
            for basicVar in columnVars:
                expr = self.rowExpression(basicVar)
                c = expr.coefficientFor(minusErrorVar)
                expr.incrementConstant(c * delta)
                if basicVar.isRestricted() and expr.constant() < 0.0:
                    self._infeasibleRows.add(basicVar)
    
    def dualOptimize(self):
        zRow = self.rowExpression(self._objective)
        while self._infeasibleRows:
            exitVar = self._infeasibleRows.pop()
            entryVar = None
            expr = self.rowExpression(exitVar)
            if expr is not None:
                if expr.constant() < 0.0:
                    ratio = MAX_VALUE
                    terms = expr.terms()
                    for v, c in terms.iteritems():
                        if c > 0.0 and v.isPivotable():
                            zc = zRow.coefficientFor(v)
                            r = zc / c
                            if r < ratio or (almost_equal(r, ratio) and 
                                             entryVar is not None and 
                                             v.hashCode() < entryVar.hashCode()):
                                entryVar = v
                                ratio = r
                    if ratio == MAX_VALUE:
                        raise ValueError('ratio == MAX_VALUE in dualOptimize')
                    self.pivot(entryVar, exitVar)
    
    def newExpression(self, cn, eplus_eminus, prevEConstant):
        cnExpr = cn.expression()
        expr = LinearExpression(cnExpr.constant())
        slackVar = SlackVariable()
        dummyVar = DummyVariable()
        eminus = SlackVariable()
        eplus = SlackVariable()
        cnTerms = cnExpr.terms()

        for v, c in cnTerms.iteritems():
            e = self.rowExpression(v)
            if e is None:
                expr.addVariable(v, c)
            else:
                expr.addExpression(e, c)
        
        if cn.isInequality():
            self._slackCounter += 1
            slackVar = SlackVariable(self._slackCounter, 's')
            expr.setVariable(slackVar, -1.0)
            self._markerVars[cn] = slackVar
            if not cn.isRequired():
                self._slackCounter += 1
                eminus = SlackVariable(self._slackCounter, 'em')
                expr.setVariable(eminus, 1.0)
                zRow = self.rowExpression(self._objective)
                sw = cn.strength().symbolicWeight().times(cn.weight())
                zRow.setVariable(eminus, sw.toDouble())
                self.insertErrorVar(cn, eminus)
                self.noteAddedVariable(eminus, self._objective)
        else:
            if cn.isRequired():
                self._dummyCounter += 1
                dummyVar = DummyVariable(self._dummyCounter, 'd')
                expr.setVariable(dummyVar, 1.0)
                self._markerVars[cn] = dummyVar
            else:
                self._slackCounter += 1
                eplus = SlackVariable(self._slackCounter, 'ep')
                eminus = SlackVariable(self._slackCounter, 'em')
                expr.setVariable(eplus, -1.0)
                expr.setVariable(eminus, 1.0)
                self._markerVars[cn] = eplus
                zRow = self.rowExpression(self._objective)
                sw = cn.strength().symbolicWeight().times(cn.weight())
                swCoeff = sw.toDouble()
                if swCoeff == 0.0:
                    # debug prints
                    pass
                zRow.setVariable(eplus, swCoeff)
                self.noteAddedVariable(eplus, self._objective)
                zRow.setVariable(eminus, swCoeff)
                self.noteAddedVariable(eminus, self._objective)
                self.insertErrorVar(cn, eminus)
                self.insertErrorVar(cn, eplus)
                if cn.isStayConstraint():
                    self._stayPlusErrorVars.append(eplus)
                    self._stayMinusErrorVars.append(eminus)
                elif cn.isEditConstraint():
                    eplus_eminus[0] = eplus
                    eplus_eminus[1] = eminus
                    prevEConstant[0] = cnExpr.constant()
        
        if expr.constant() < 0:
            expr.multiplyMe(-1.0)
        
        return expr

    def optimize(self, zVar):
        zRow = self.rowExpression(zVar)
        assert zRow is not None, 'zRow is not None'
        
        entryVar = None
        exitVar = None

        while True:
            objectiveCoeff = 0.0
            terms = zRow.terms()
            
            for v, c in terms.iteritems():
                if v.isPivotable() and c < objectiveCoeff:
                    objectiveCoeff = c
                    entryVar = v
                    break
            
            if objectiveCoeff >= -self._epsilon:
                return

            minRatio = MAX_VALUE
            columnVars = self._columns.get(entryVar)
            r = 0.0

            for v in columnVars:
                if v.isPivotable():
                    expr = self.rowExpression(v)
                    coeff = expr.coefficientFor(entryVar)
                    if coeff < 0.0:
                        r = -expr.constant() / float(coeff)
                        if r < minRatio or (almost_equal(r, minRatio) and v.hashCode() < exitVar.hashCode()):
                            minRatio = r
                            exitVar = v
            
            if minRatio == MAX_VALUE:
                raise ValueError('Objective function is unbounded in optimize')

            self.pivot(entryVar, exitVar)
                   
    def pivot(self, entryVar, exitVar):
        if entryVar is None:
            raise ValueError('entry var is None')
        if exitVar is None:
            raise ValueError('exit var is None')
        pexpr = self.removeRow(exitVar)
        pexpr.changeSubject(exitVar, entryVar)
        self.substituteOut(entryVar, pexpr)
        self.addRow(entryVar, pexpr)
    
    def resetStayConstants(self):
        for plusVar, minusVar in izip(self._stayPlusErrorVars, self._stayMinusErrorVars):
            expr = self.rowExpression(plusVar)
            if expr is None:
                expr = self.rowExpression(minusVar)
            if expr is not None:
                expr.set_constant(0.0)
    
    def setExternalVariables(self):
        for v in self._externalParametricVars:
            if self.rowExpression(v) is not None:
                print 'error: _externalParametericVar is basic'
            else:
                v.change_value(0.0)
        for v in self._externalRows:
            expr = self.rowExpression(v)
            v.change_value(expr.constant())
        self._fNeedsSolving = False
    
    def insertErrorVar(self, cn, aVar):
        self._errorVars.setdefault(cn, set()).add(aVar)


#------------------------------------------------------------------------------
# Edit Info
#------------------------------------------------------------------------------
@wrap_all
class EditInfo(object):
    
    def __init__(self, cn_, eplus_, eminus_, prevEditConstant_, i_):
        self.cn = cn_
        self.clvEditPlus = eplus_
        self.clvEditMinus = eminus_
        self.prevEditConst = prevEditConstant_
        self.i = i_

    def __repr__(self):
        return self.toString()
    
    def __str__(self):
        return self.toString()

    def Index(self):
        return self.i
    
    def Constraint(self):
        return self.cn
    
    def ClvEditPlus(self):
        return self.clvEditPlus
    
    def ClvEditMinus(self):
        return self.clvEditMinus
    
    def PrevEditConstant(self):
        return self.prevEditConstant
    
    def SetPrevEditConstant(self, prevEditConstant_):
        self.prevEditConstant = prevEditConstant_
    
    def toString(self):
        args = (self.cn, self.clvEditPlus, self.clvEditMinus, self.prevEditConstant, self.i)
        return '<cn=%s, ep=%s, em=%s, pec=%s, i=%s>' % args



if __name__ == '__main__':
    x = Variable('x')
    y = Variable('y')
    solver = SimplexSolver()
    solver.addConstraint(LinearInequality(x, CL.LEQ, y))
    solver.addConstraint(LinearEquation(y, CL.Plus(x, 3.0)))
    solver.addConstraint(LinearEquation(x, 10.0, Strength.weak))
    solver.addConstraint(LinearEquation(y, 10.0, Strength.weak))
    import pprint
    pprint.pprint(_calls)
    print x.value()
    print y.value()


