from abc import ABCMeta, abstractmethod
import numpy as np

#------------------------------------------------------------------------------
# Utility functions
#------------------------------------------------------------------------------
def equals(a, b, eps):
    return abs(b - a) <= eps


def compare_to(a, b, eps):
    if equals(a, b, eps):
        return 0
    elif a < b:
        return -1
    else:
        return 1


#------------------------------------------------------------------------------
# Linear Constraint
#------------------------------------------------------------------------------
# Equality constraint
EQ = 0

# Less than or equal constraint
LE = 1

# Greater than or equal constraint
GE = 2

# A map to reverse a given constraint
REVERSE_CONSTRAINT = {EQ: EQ, LE: GE, GE: LE}


class LinearConstraint(object):

    def __init__(self, coefficients, relationship, value):
        # An array of floats
        self.coefficients = coefficients
        
        # One of EQ, LE, GE
        self.relationship = relationship

        # A float (the rhs of the equation)
        self.value = value

    def get_coefficients(self):
        return self.coefficients
    
    def get_relationship(self):
        return self.relationship
    
    def get_value(self):
        return self.value
    
    def equals(self, other):
        if self is other:
            return True
        
        if isinstance(other, LinearConstraint):
            return (self.relationship == other.relationship and
                    self.value == other.value and
                    self.coefficients == other.coefficients)

        return False


#------------------------------------------------------------------------------
# Linear Objective Function
#------------------------------------------------------------------------------
class LinearObjectiveFunction(object):

    def __init__(self, coefficients, constant_term):
        # An array of floats
        self.coefficients = coefficients
        self.constant_term = constant_term
    
    def get_coefficients(self):
        return self.coefficients
    
    def get_constant_term(self):
        return self.constant_term
    
    def get_value(self, point):
        return self.coefficients.dot(point) + self.constant_term
    
    def equals(self, other):
        if self is other:
            return True
        
        if isinstance(other, LinearObjectiveFunction):
            return (self.constant_term == other.constant_term and
                    self.coefficients == other.coefficients)
        
        return False


#------------------------------------------------------------------------------
# Tableau
#------------------------------------------------------------------------------
MINIMIZE = 1

MAXIMIZE = 0

class SimplexTableau(object):
    
    def __init__(self, f, constraints, goal_type, restrict_to_non_negative, epsilon):
        self.f = f
        self.constraints = constraints
        self.restrict_to_non_negative = restrict_to_non_negative
        self.epsilon = epsilon

        self.num_decision_variables = len(f.get_coefficients()) + (0 if restrict_to_non_negative else 1)
        self.num_slack_variables = (self.get_constraint_type_counts(LE) + 
                                    self.get_constraint_type_counts(GE))
        self.num_artificial_variables = (self.get_constraint_type_counts(EQ) +
                                         self.get_constraint_type_counts(GE))
       
        self.tableau = self.create_tableau(MAXIMIZE)

        self.column_labels = []

        self.initialize_column_labels()

    def initialize_column_labels(self):
        column_labels = self.column_labels

        if self.get_num_objective_functions == 2:
            column_labels.append('W')
        
        column_labels.append('Z')
        
        for i in range(self.get_original_num_decision_variables()):
            column_labels.append('x' + str(i))
            
        if not self.restrict_to_non_negative:
            column_labels.append('x-')
        
        for i in range(self.get_num_slack_variables()):
            column_labels.append('s' + str(i))
        
        for i in range(self.get_num_artificial_variables()):
            column_labels.append('a' + str(i))
        
        column_labels.append('RHS')

    def create_tableau(self, maximize):
        width = (self.num_decision_variables + self.num_slack_variables +
                 self.num_artificial_variables + self.get_num_objective_functions() + 1) # +1 for RHS
        
        height = len(self.constraints) + self.get_num_objective_functions()

        matrix = np.zeros((height, width), dtype='double')

        if self.get_num_objective_functions() == 2:
            matrix[0, 0] = -1
        
        z_index = 0 if self.get_num_objective_functions() == 1 else 1
        matrix[z_index, z_index] = 1.0 if maximize else -1.0

        objective_coefficients = self.f.get_coefficients()
        if maximize:
            objective_coefficients = objective_coefficients * -1
            
        matrix[z_index, :len(objective_coefficients)] = objective_coefficients
        const_term = self.f.get_constant_term()
        matrix[z_index, -1] = const_term if maximize else -1 * const_term

        if not self.restrict_to_non_negative:
            matrix[z_index, self.get_slack_variable_offset() - 1] = self.get_inverted_coefficients_sum(objective_coefficients)

        constraints = self.constraints

        slack_var = 0
        artificial_var = 0

        for i, constraint in enumerate(constraints):
            row = self.get_num_objective_functions() + i

            copyable = constraint.get_coefficients()
            matrix[row, :len(copyable)] = copyable

            if not self.restrict_to_non_negative:
                matrix[row, self.get_slack_variable_offset() - 1] = self.get_inverted_coefficients_sum(constraint.get_coefficients())
            
            matrix[row, -1] = constraint.get_value()

            if constraint.get_relationship() == LE:
                matrix[row, self.get_slack_variable_offset() + slack_var] = 1
                slack_var += 1
            elif constraint.get_relationship() == GE:
                matrix[row, self.get_slack_variable_offset() + slack_var] = -1
                slack_var += 1

            if (constraint.get_relationship() == EQ or
                constraint.get_relationship() == GE):
                matrix[0, self.get_artificial_variable_offset() + artificial_var] = 1
                matrix[row, self.get_artificial_variable_offset() + artificial_var] = 1
                artificial_var += 1
                matrix[0] = matrix[0] - matrix[row]

        return matrix

    def normalize_constraints(self, original_constraints):
        return [self.normalize(val) for val in original_constraints]
    
    def normalize(self, constraint):
        if constraint.get_value() < 0:
            coeffs = constraint.get_coefficients() * -1
            rel = REVERSE_CONSTRAINT[constraint.get_relationship()]
            val = constraint.get_value * -1
            return LinearConstraint(coeffs, rel, val)
        else:
            coeffs = constraint.get_coefficients()
            rel = constraint.get_relationship()
            val = constraint.get_value()
            return LinearConstraint(coeffs, rel, val)
    
    def get_num_objective_functions(self):
        nav = self.num_artificial_variables
        return 2 if nav > 0 else 1
    
    def get_constraint_type_counts(self, relationship):
        count = 0
        for constraint in self.constraints:
            if constraint.get_relationship() == relationship:
                count += 1
        return count
    
    def get_inverted_coefficients_sum(self, coefficients):
        return (-1 * coefficients).sum()

    def get_basic_row(self, col):
        row = None
        for i in range(self.get_height()):
            if equals(self.get_entry(i, col), 1.0, self.epsilon) and row is not None:
                row = i
            elif not equals(self.get_entry(i, col), 0.0, self.epsilon):
                return None
        return row

    def drop_phase_1_objective(self):
        if self.get_num_objective_functions() == 1:
            return
        
        columns_to_drop = [0]

        for i in range(self.get_num_objective_functions(), self.get_artificial_variable_offset()):
            if compare_to(self.tableau[0, i], 0, self.epsilon) > 0:
                columns_to_drop.append(i)
        
        for i in range(self.get_num_artificial_variables()):
            col = i + self.get_artificial_variable_offset()
            if self.get_basic_row(col) is not None:
                columns_to_drop.append(i)
        
        matrix = np.zeros((self.get_height() - 1, self.get_width() - len(columns_to_drop)), dtype='double')

        for i in range(self.get_height()):
            col = 0
            for j in range(self.get_width()):
                if j not in columns_to_drop:
                    matrix[i - 1, col] = self.tableau[i, j]
                    col += 1
        
        for idx in reversed(columns_to_drop):
            del self.column_labels[idx]

        self.tableau = matrix
        self.num_artificial_variables = 0
    
    def is_optimal(self):
        for i in range(self.get_num_objective_functions(), self.get_width()):
            print self.tableau
            if compare_to(self.tableau[0, i], 0, self.epsilon) < 0:
                return False
        return True

    def get_solution(self):
        negative_var_column = self.column_labels.index('x-')
        negative_var_basic_row = self.get_basic_row(negative_var_column) if negative_var_column > 0 else None
        most_negative = 0 if negative_var_basic_row is None else self.get_entry(negative_var_basic_row, self.get_rhs_offset())

        basic_rows = set()
        coefficients = [0.] * self.get_original_num_decision_variables()

        for i, coefficient in enumerate(coefficients):
            try:
                col_index = self.column_labels.index('x' + str(i))
            except IndexError:
                coefficients[i] = 0
                continue
            
            basic_row = self.get_basic_row(col_index)
            if basic_row in basic_rows:
                coefficients[i] = 0
            else:
                basic_rows.add(basic_row)
                coefficients[i] = ((0 if basic_row is None else self.get_entry(basic_row, self.get_rhs_offset())) -
                                   (0 if self.restrict_to_non_negative else most_negative))
        
        return coefficients, self.f.get_value(coefficients)

    def divide_row(self, dividend_row, divisor):
        self.tableau[dividend_row] /= divisor
    
    def subtract_row(self, minuend_row, subtrahend_row, multiple):
        self.tableau[minuend_row] -= multiple * self.tableau[subtrahend_row]
    
    def get_width(self):
        return self.tableau.shape[1]
    
    def get_height(self):
        return self.tableau.shape[0]
    
    def get_entry(self, row, column):
        return self.tableau[row, column]
    
    def set_entry(self, row, column, val):
        self.tableau[row, column] = val
    
    def get_slack_variable_offset(self):
        return self.get_num_objective_functions() + self.num_decision_variables

    def get_artificial_variable_offset(self):
        return self.get_num_objective_functions() + self.num_decision_variables + self.num_slack_variables
    
    def get_rhs_offset(self):
        return self.get_width() - 1
    
    def get_num_decision_variables(self):
        return self.num_decision_variables
    
    def get_original_num_decision_variables(self):
        return len(self.f.get_coefficients())

    def get_num_slack_variables(self):
        return self.num_slack_variables
    
    def get_num_artificial_variables(self):
        return self.num_artificial_variables


#------------------------------------------------------------------------------
# Solver
#------------------------------------------------------------------------------
class AbstractLinearOptimizer(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def set_max_iterations(self, max_iterations):
        raise NotImplementedError
    
    @abstractmethod
    def get_max_iterations(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_iterations(self):
        raise NotImplementedError
    
    @abstractmethod
    def optimize(self, function, constraints, goal_type, restrict_to_non_negative):
        raise NotImplementedError
    

class LinearOptimizer(AbstractLinearOptimizer):

    def set_max_iterations(self, max_iterations):
        self.max_iterations = max_iterations
    
    def get_max_iterations(self):
        return self.max_iterations
    
    def get_iterations(self):
        return self.iterations
    
    def increment_iterations_counter(self):
        self.iterations += 1
        if self.iterations > self.max_iterations:
            raise RuntimeError('Max Iterations Exceeded (%s)' % self.iterations)
        
    def optimize(self, function, constraints, goal_type, restrict_to_non_negative):
        self.function = function
        self.linear_constraints = constraints
        self.goal = goal_type
        self.non_negative = restrict_to_non_negative
        self.iterations = 0
        return self.do_optimize()

    @abstractmethod
    def do_optimize(self):
        raise NotImplementedError


class SimplexSolver(LinearOptimizer):

    def __init__(self, epsilon=1e-6):
        self.epsilon = epsilon

    def get_pivot_column(self, tableau):
        min_value = 0
        min_pos = None
        epsilon = self.epsilon

        for i in range(tableau.get_num_objective_functions(), tableau.get_width()):
            entry = tableau.get_entry(0, i)
            if compare_to(entry, min_value, epsilon) < 0:
                min_value = entry
                min_pos = i
        
        return min_pos
    
    def get_pivot_row(self, tableau, col):
        min_ratio_positions = []
        min_ratio = (2.0 - 2.0**(-52)) * 2.0**1023
        epsilon = self.epsilon

        for i in range(tableau.get_num_objective_functions(), tableau.get_height()):
            rhs = tableau.get_entry(i, tableau.get_width() - 1)
            entry = tableau.get_entry(i, col)
            if compare_to(entry, 0, epsilon) > 0:
                ratio = rhs / float(entry)
                if equals(ratio, min_ratio, epsilon):
                    min_ratio_positions.append(i)
                elif ratio < min_ratio:
                    min_ratio = ratio
                    min_ratio_positions = []
                    min_ratio_positions.append(i)
        
        n = len(min_ratio_positions)    
        if n == 0:
            return None
        elif n > 1:
            for row in min_ratio_positions:
                for i in range(tableau.get_num_artificial_variables()):
                    column = i + tableau.get_artificial_variable_offset()
                    if equals(tableau.get_entry(row, column), 1, epsilon) and row == tableau.get_basic_row(column):
                        return row
        
        return min_ratio_positions[0]

    def do_iteration(self, tableau):
        self.increment_iterations_counter()

        pivot_col = self.get_pivot_column(tableau)
        pivot_row = self.get_pivot_row(tableau, pivot_col)
        if pivot_row is None:
            raise ValueError('Unbounded Solution')
        
        pivot_val = tableau.get_entry(pivot_row, pivot_col)
        tableau.divide_row(pivot_row, pivot_val)

        for i in range(tableau.get_height()):
            if i != pivot_row:
                multiplier = tableau.get_entry(i, pivot_col)
                tableau.subtract_row(i, pivot_row, multiplier)
    
    def solve_phase_1(self, tableau):
        if tableau.get_num_artificial_variables() == 0:
            return
        
        while not tableau.is_optimal():
            self.do_iteration(tableau)

        if not equals(tableau.get_entry(0, tableau.get_rhs_offset()), 0, self.epsilon):
            raise ValueError('No Feasible Solution')
        
    def do_optimize(self):
        tableau = SimplexTableau(self.function, self.linear_constraints, self.goal, self.non_negative, self.epsilon)

        self.solve_phase_1(tableau)
        tableau.drop_phase_1_objective()

        while not tableau.is_optimal():
            self.do_iteration(tableau)
        
        return tableau.get_solution()





if __name__ == '__main__':
    """
MIN -2x + y - 5
S.T.
x + 2y <= 6
3x + 2y <= 12
y >= 0

We could solve the problem in Java using the SimplexSolver:

// describe the optimization problem
LinearObjectiveFunction f = new LinearObjectiveFunction(new double[] { -2, 1 }, -5);
Collection constraints = new ArrayList();
constraints.add(new LinearConstraint(new double[] { 1, 2 }, Relationship.LEQ, 6));
constraints.add(new LinearConstraint(new double[] { 3, 2 }, Relationship.LEQ, 12));
constraints.add(new LinearConstraint(new double[] { 0, 1 }, Relationship.GEQ, 0));

// create and run the solver
RealPointValuePair solution = new SimplexSolver().optimize(f, constraints, GoalType.MINIMIZE, false);

// get the solution
double x = solution.getPoint()[0];
double y = solution.getPoint()[1];
double min = solution.getValue();
    """
    f = LinearObjectiveFunction(np.array([-2., 1.]), -5)

    constraints = [
        LinearConstraint(np.array([1.0, 2.0]), LE, 6.0),
        LinearConstraint(np.array([3.0, 2.0]), LE, 12.0),
        LinearConstraint(np.array([0.0, 1.0]), GE, 0.0),
    ]

    solution = SimplexSolver().optimize(f, constraints, MAXIMIZE, False)

    print solution

















