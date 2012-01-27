import os

import ply.lex as lex
import ply.yacc as yacc


# Get a save directory for the lex and parse tables
_enaml_dir = os.path.join(os.path.expanduser('~'), '.enaml')
try:
    if not os.path.exists(_enaml_dir):
        os.mkdir(_enaml_dir)
except OSError:
    _enaml_dir = os.getcwd()


#------------------------------------------------------------------------------
# Layout Lexer
#------------------------------------------------------------------------------
tokens = (
    'LSQB',
    'RSQB',
    'LPAR',
    'RPAR',
    'INT',
    'HYPHEN',
    'VBAR',
    'NAME',
    'EQ',
    'LE',
    'GE',
    'AT',
    'COMMA',
    'COLON',
)

t_LSQB = r'\['

t_RSQB = r'\]'

t_LPAR = r'\('

t_RPAR = r'\)'

t_INT = r'[0-9]+'

t_HYPHEN = r'-'

t_VBAR = r'\|'

t_NAME = r'[a-zA-Z_][a-zA-Z_0-9]*'

t_EQ = r'=='

t_LE = r'<='

t_GE = r'>='

t_AT = r'@'

t_COMMA = r','

t_COLON = r':'

t_ignore = ' \t'

def t_error(t):
    raise SyntaxError(t)


lex.lex()


#------------------------------------------------------------------------------
# Layout AST Nodes
#------------------------------------------------------------------------------
class VisualLayout(object):

    HORIZ = 0

    VERT = 1

    def __init__(self, orient, constraints):
        self.orient = orient
        self.constraints = constraints


class SuperView(object):
    pass


class Connection(object):
    
    def __init__(self, predicates):
        self.predicates = predicates


class View(object):
    
    def __init__(self, name, predicates):
        self.name = name
        self.predicates = predicates


class SimplePredicate(object):

    def __init__(self, value):
        self.value = value


class Predicate(object):

    EQ = 0
    LE = 1
    GE = 2

    def __init__(self, relation, predicate_obj, priority):
        self.relation = relation
        self.predicate_obj = predicate_obj
        self.priority = priority


#------------------------------------------------------------------------------
# Layout Parser
#------------------------------------------------------------------------------
def p_visual_layout1(p):
    ''' visual_layout : layout_items '''
    constraints = p[1]
    p[0] = VisualLayout(VisualLayout.HORIZ, constraints)


def p_visual_layout2(p):
    ''' visual_layout : orientation layout_items '''
    constraints = p[2]
    p[0] = VisualLayout(p[1], constraints)


def p_visual_layout3(p):
    ''' visual_layout : VBAR connection layout_items '''
    constraints = [SuperView(), p[2]] + p[3]
    p[0] = VisualLayout(VisualLayout.HORIZ, constraints)


def p_visual_layout4(p):
    ''' visual_layout : layout_items connection VBAR '''
    constraints = p[1] + [p[2], SuperView()]
    p[0] = VisualLayout(VisualLayout.HORIZ, constraints)


def p_visual_layout5(p):
    ''' visual_layout : orientation VBAR connection layout_items '''
    constraints = [SuperView(), p[3]] + p[4]
    p[0] = VisualLayout(p[1], constraints)


def p_visual_layout6(p):
    ''' visual_layout : orientation layout_items connection VBAR '''
    constraints = p[2] + [p[3], SuperView()]
    p[0] = VisualLayout(p[1], constraints)


def p_visual_layout7(p):
    ''' visual_layout : VBAR connection layout_items connection VBAR '''
    constraints = [SuperView(), p[2]] + p[3] + [p[4], SuperView()]
    p[0] = VisualLayout(VisualLayout.HORIZ, constraints)


def p_visual_layout8(p):
    ''' visual_layout : orientation VBAR connection layout_items connection VBAR '''
    constraints = [SuperView(), p[3]] + p[4] + [p[5], SuperView()]
    p[0] = VisualLayout(p[1], constraints)


orient_map = {'V': VisualLayout.VERT, 'H': VisualLayout.HORIZ}
def p_orientation(p):
    ''' orientation : NAME COLON '''
    orient = orient_map.get(p[1])
    if orient is None:
        # why can't I raise SyntaxError ply????
        raise ValueError('orientation must be `H` or `V`')
    p[0] = orient


def p_connection1(p):
    ''' connection : HYPHEN predicate_list HYPHEN '''
    p[0] = Connection(p[2])


def p_connection2(p):
    ''' connection : HYPHEN '''
    p[0] = Connection([])


def p_predicate_list1(p):
    ''' predicate_list : simple_predicate '''
    p[0] = [p[1]]


def p_predicate_list2(p):
    ''' predicate_list : predicate_list_with_parens '''
    p[0] = p[1]


def p_predicate_list_with_parens(p):
    ''' predicate_list_with_parens : LPAR predicate_paren_items RPAR '''
    p[0] = p[1]


def p_predicate_paren_items1(p):
    ''' predicate_paren_items : predicate '''
    p[0] = [p[1]]


def p_predicate_paren_items2(p):
    ''' predicate_paren_items : predicate COMMA predicate_paren_items '''
    p[0] = [p[1]] + p[3]


def p_simple_predicate1(p):
    ''' simple_predicate : NAME '''
    p[0] = SimplePredicate(p[1])


def p_simple_predicate2(p):
    ''' simple_predicate : INT '''
    p[0] = SimplePredicate(int(p[1]))


def p_predicate1(p):
    ''' predicate : predicate_obj '''
    p[0] = Predicate(None, p[1], None)


def p_predicate2(p):
    ''' predicate : relation predicate_obj '''
    p[0] = Predicate(p[1], p[2], None)


def p_predicate3(p):
    ''' predicate : predicate_obj priority '''
    p[0] = Predicate(None, p[1], p[2])


def p_predicate4(p):
    ''' predicate : relation predicate_obj priority '''
    p[0] = Predicate(p[1], p[2], p[3])


def p_relation1(p):
    ''' relation : EQ '''
    p[0] = Predicate.EQ


def p_relation2(p):
    ''' relation : LE '''
    p[0] = Predicate.LE


def p_relation3(p):
    ''' relation : GE '''
    p[0] = Predicate.GE


def p_predicate_obj1(p):
    ''' predicate_obj : NAME '''
    p[0] = p[1]


def p_predicate_obj2(p):
    ''' predicate_obj : INT '''
    p[0] = int(p[1])


def p_priority1(p):
    ''' priority : AT NAME '''
    p[0] = p[2]


def p_priority2(p):
    ''' priority : AT INT '''
    p[0] = int(p[2])


def p_layout_items1(p):
    ''' layout_items : layout_item '''
    p[0] = [p[1]]


# Not do not reverse the order of the p[1] and p[3] since that results
# in shift/reduce conficts which prevent and ending VBAR from being 
# handled properly
def p_layout_items2(p):
    ''' layout_items : layout_items connection layout_item '''
    p[0] = p[1] + [p[2], p[3]]


def p_layout_item1(p):
    ''' layout_item : LSQB NAME RSQB '''
    p[0] = View(p[2], [])


def p_layout_item2(p):
    ''' layout_item : LSQB NAME predicate_list_with_parens RSQB '''
    p[0] = View(p[2], p[4])


def p_error(p):
    raise SyntaxError(p)


_parser = yacc.yacc(debug=False, tabmodule='enaml_layout_parsetab', 
                    outputdir=_enaml_dir, errorlog=yacc.NullLogger())


def parse(txt):
    return _parser.parse(txt)

