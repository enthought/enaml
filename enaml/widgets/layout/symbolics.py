from casuarius import STRENGTH_MAP, Strength, SymbolicWeight, ConstraintVariable, LinearExpression, LinearSymbolic, LinearConstraint


class MultiConstraint(object):
    """ A combination of LinearConstraints.

    """

    def __init__(self, constraints):
        self.constraints = constraints

    def __repr__(self):
        lines = ['<%s:' % type(self).__name__]
        for constraint in self.constraints:
            lines.append('    %s | %r, %r' % (constraint, constraint.strength, constraint.weight))
        lines.append('  >')
        return '\n'.join(lines)

    def __str__(self):
        lines = [str(c) for c in self.constraints]
        lines[0] = '(' + lines[0]
        for i, line in enumerate(lines[1:], 1):
            lines[i] = ' ' + line
        lines[-1] += ')'
        return '\n'.join(lines)

    def __and__(self, other):
        if isinstance(other, LinearConstraint):
            if other not in self.constraints:
                return MultiConstraint(self.constraints + [other])
            else:
                return self
        elif isinstance(other, MultiConstraint):
            return MultiConstraint(self.constraints + other.constraints)
        else:
            msg = 'Can only combine other LinearConstraints and MultiConstraints. Got %s instead.' % type(other)
            raise TypeError(msg)

    def __rand__(self, other):
        return self.__and__(other)

    def __or__(self, other):
        """ Set the strength of all of the constraints to a common strength.

        """

        if isinstance(other, (float, int, long)):
            pass
        elif isinstance(other, basestring):
            mapping = STRENGTH_MAP
            if other not in mapping:
                raise ValueError('Invalid strength `%s`' % other)
        elif isinstance(other, Strength):
            pass
        else:
            msg = 'Strength must be a string. Got %s instead.' % type(other)
            raise TypeError(msg)
        constraints = []
        for constraint in self.constraints:
            constraints.append(constraint | other)
        return MultiConstraint(constraints)

    def __ror__(self, other):
        return self.__or__(other)

    def __len__(self):
        return len(self.constraints)

    def __iter__(self):
        return iter(self.constraints)

