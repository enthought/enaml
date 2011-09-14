###############################################################################
# Extensions
###############################################################################

import re
import abc
from docscrape import Reader

# FIXME: This is a very agly (i.e. architecture and speed) but the first
# working implementation of my view on refactoring the source rst documentation
# so that is shpinx friendly.

# Please note that this parsing differs from numpydoc. the main idea is that
# the result follows closer the structure and form that the docstring author
# has selected.
# In more detail::
# 1. it does not change the order the sections
# 2. allows notes and other directives to exist between the sections

# TODO:
# Convert into a proper extention
# Add more sections
# Remove dependancy to docscarpe


class BaseDocString(object):
    """Base abstract docstring refactoring class"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, lines, headers, verbose=False):

        self._doc = Reader(lines)
        self.verbose = verbose
        self.headers = headers

        if self.verbose:
            print 'INPUT DOCSTRING'
            print '\n'.join(lines)

    def _refactor(self, header):
        """Heading refactor"""

        if self.verbose:
            print 'Header is', header
            print 'Line is', self._doc._l

        try:
            parser = self.headers[header]
        except KeyError:
            # No need to do anything since shpinx will flag the heading as
            # an error
            pass
        else:
            method_name = ''.join(('_refactor_', parser))
            method = getattr(self, method_name)
            method(header)

        finally:
            return

    def parse(self):
        self._doc.reset()
        self._doc.read()

        while not self._doc.eof():
            self._doc.seek_next_non_empty_line()
            header = self._is_section()
            if not header:
                self._doc.read()
            else:
                self._refactor(header)

        if self.verbose:
            print 'REFACTORED DOCSTRING'
            print '\n'.join(self._doc._str)

        return

    def is_field(self, line, indent=''):
        if self.verbose:
            print "Checking if '{0}' is a parameter field".format(line)
        match = re.match(indent + r'\w+\s:\s*', line)
        if self.verbose:
            print "Check is", bool(match)
        return match

    def is_method(self, line, indent=''):
        if self.verbose:
            print "Checking if '{0}' is a method field".format(line)
        match = re.match(indent + r'\w+\(.*\)\s*', line)
        if self.verbose:
            print "Check is", bool(match)
        return match

    def _extract_parameters(self, indent='', field_check=None):
        """Extract the parameters from the docstring

        Finds and parses the parameters into tuples of name, type and
        description in a list of strings. The strings are also removed from the
        list

        Arguments
        ---------
        indent : str, optional
            the indent argument is used to make sure that only the lines with
            the same indent are considered when checking for a parameter header
            line.

        Returns
        -------
        parameters : list of tuples
            list of parsed parameter tuples as returned from the
            :meth:`~_FunctionDocString._parse_parameter` function.

        """

        #TODO raise error when there is no parameter

        if self.verbose:
            print "PARSING PARAMETERS"

        if field_check:
            is_field = field_check
        else:
            is_field = self.is_field

        parameters = []

        start = self._doc._l

        while is_field(self._doc.peek(), indent) and (not self._doc.eof()):
            description = self._doc.read_to_next_empty_line()
            parameters.append(self._parse_parameter(description))
            self._doc.read()

        stop = self._doc._l

        # remove parsed lines
        del self._doc._str[start:stop]

        return parameters

    def _parse_parameter(self, doc_lines):
        """Parse a parameter description

        Returns
        -------
        arg_name : str
            The name of the parameter

        arg_type : str
            The type of the parameter (if defined)

        desc : list
            A list of the strings that make up the description

        """

        if self.verbose:
            print "PARSING PARAMETERS"
            print "input is: "
            print "\n".join(doc_lines)

        # separate name and type
        header = doc_lines[0].strip()
        if ' :' in header:
            arg_name, arg_type = re.split(' \:\s?', header)
        else:
            arg_name, arg_type = header, ''

        if self.verbose:
            print "name is:", arg_name, " type is:", arg_type
            print "the output of 're.split(' \:\s?', header)' was", \
                        re.split(' \:\s?', header)

        if len(doc_lines) > 1:
            return arg_name.strip(), arg_type.strip(), doc_lines[1:]
        else:
            return arg_name.strip(), arg_type.strip(), ' '

    def _indent(self, lines, indent=4):
        """ Indent list of lines

        .. info:: Code adapted from numpydoc/docscrape.py
        """
        indent_str = ' ' * indent
        if lines is None:
            return indent_str
        else:
            return [indent_str + line for line in lines]

    def _is_section(self):
        """Check if the line defines a section.

        """

        if self._doc.eof():
            return False

        # peek at line
        header = self._doc.peek()

        # is it a known header?
        if header.strip() not in self.headers:
            return False

        # peek at second line
        line2 = self._doc.peek(1)

        # check for underline type format
        underline = re.match(r'\s*\S+\s*\Z', line2)
        if underline is None:
            return False

        # is the next line an rst underline?
        striped_header = header.rstrip()

        expected_underline1 = re.sub(r'[A-Za-z]|\b\s', '-', striped_header)
        expected_underline2 = re.sub(r'[A-Za-z]|\b\s', '=', striped_header)

        if ((underline.group().rstrip() == expected_underline1) or
            (underline.group().rstrip() == expected_underline2)):
            return header.strip()

        else:
            return False

    def insert_lines(self, new_lines, index):
        """Insert refactored lines

        Arguments
        ---------
        new_lines : list
            The list of lines to insert

        index : int
            Index to start the insertion
        """
        lines = self._doc._str
        for line in reversed(new_lines):
            lines.insert(index, line)

    def get_indent(self, line):
        return re.split(r'\w', line)[0]


class FunctionDocstring(BaseDocString):
    """Docstring refactoring for functions"""

    def __init__(self, lines, headers=None, verbose=False):

        if headers is None:
            headers = {'Returns': 'returns', 'Arguments': 'arguments',
                       'Parameters': 'arguments', 'Raises': 'raises',
                       'Yields': 'returns'}

        super(FunctionDocstring, self).__init__(lines, headers, verbose)

    def _refactor_returns(self, header):
        """Refactor the return section to sphinx friendly format"""

        lines = self._doc._str
        index = self._doc._l

        # create header role
        lines[index] = re.sub(r'Returns', ':returns:', self._doc.read())
        del lines[index + 1]  # delete underline

        # get section indent
        indent = self.get_indent(self._doc.peek())

        # parse parameters
        parameters = self._extract_parameters(indent)

        if self.verbose:
            print 'Return_items'
            print parameters

        # generate sphinx friendly rst
        descriptions = []
        index += 1

        for arg_name, arg_type, desc in parameters:

            # get description indent
            description_indent = re.split(r'\w', desc[0])[0]

            # setup name
            if len(parameters) == 1:
                arg_name = description_indent + '**{0}** '.format(arg_name)
            else:
                arg_name = description_indent + '- **{0}** '.format(arg_name)

            # setup attribute type string
            if arg_type != '':
                arg_type = '({0}) - '.format(arg_type)
            else:
                arg_type = ' - '

            # setup description paragraph
            paragraph = ' '.join(desc)

            descriptions.append(arg_name + arg_type + paragraph)

            descriptions.append(' ')

        if self.verbose:
            print "REFACTORED SECTION"
            print '\n'.join(descriptions)
            print "END"

        self.insert_lines(descriptions, index)

    def _refactor_raises(self, header):
        """Refactor the raises section to sphinx friendly format"""

        lines = self._doc._str
        index = self._doc._l

        # create header role
        lines[index] = re.sub(r'Raises', ':raises:', self._doc.read())
        del lines[index + 1]  # delete underline

        # refactor parameters
        indent = re.split(r'\w', self._doc.peek())[0]
        parameters = self._extract_parameters(indent)

        if self.verbose:
            print 'raised_items'
            print parameters
        # generate sphinx friendly rst
        descriptions = []

        # multiple items are rendered as a unordered lists
        if len(parameters) > 1:
            for arg_name, arg_type, desc in parameters:
                if arg_type != '':
                    arg_type = '*(' + arg_type + ')*'
                descriptions.append(indent + \
                        '    - **{0}** {1} -'.format(arg_name, arg_type))
                for line in desc:
                    descriptions.append('    {0}'.format(line))

        # single items
        elif len(parameters) == 1:
            arg_name, arg_type, desc = parameters[0]
            if arg_type != '':
                arg_type = '*(' + arg_type + ')*'
            descriptions.append(indent + \
                    '    **{0}** {1} -'.format(arg_name, arg_type))
            for line in desc:
                descriptions.append('{0}'.format(line))

        descriptions.append(' ')
        self.insert_lines(descriptions, index)

    def _refactor_arguments(self, header):
        """Refactor the argument section to sphinx friendly format"""

        lines = self._doc._str
        index = self._doc._l

        # delete header
        del lines[index]
        del lines[index]

        # get the global indent of the section
        indent = re.split(r'\w', self._doc.peek())[0]

        # parse parameters
        parameters = self._extract_parameters(indent)

        if self.verbose:
            print 'arguments'
            print parameters
        # generate sphinx friendly rst
        descriptions = []

        # parameters exist
        for arg_name, arg_type, desc in parameters:
            descriptions.append(indent + ':param {0}:'.format(arg_name))
            for line in desc:
                descriptions.append('{0}'.format(line))
            descriptions.append(indent + ':type {0}: {1}'.format(arg_name,
                                                                    arg_type))

        descriptions.append(' ')
        self.insert_lines(descriptions, index)


class ClassDocstring(BaseDocString):
    """Docstring refactoring for classes"""

    def __init__(self, lines, headers=None, verbose=False):

        if headers is None:
            headers = {'Attributes': 'attributes', 'Methods': 'methods',
                       'See Also': 'see_also'}

        super(ClassDocstring, self).__init__(lines, headers, verbose)

    def _refactor_attributes(self, header):
        """Refactor the attributes section to sphinx friendly format"""

        lines = self._doc._str
        index = self._doc._l

        # delete header
        del lines[index]
        del lines[index]

        # get the global indent of the section
        indent = re.split(r'\w', self._doc.peek())[0]

        # parse parameters
        parameters = self._extract_parameters(indent)

        if self.verbose:
            print 'Refactoring attributes'
            print parameters

        # generate sphinx friendly rst
        descriptions = []

        # attribute formating
        for arg_name, arg_type, desc in parameters:

            # setup the .. attribute:: directive
            descriptions.append(indent + '.. attribute:: {0}'.\
                                format(arg_name))
            descriptions.append(' ')

            # get description indent
            description_indent = re.split(r'\w', desc[0])[0]

            # setup attribute type string
            if arg_type != '':
                arg_type = description_indent + '*({0})*'.format(arg_type)
                descriptions.append(arg_type)

            # setup description paragraph
            paragraph = ' '.join(desc)
            descriptions.append(paragraph)
            descriptions.append('')

        self.insert_lines(descriptions, index)
        return

    def _refactor_methods(self, header):
        """Refactor the attributes section to sphinx friendly format"""

        lines = self._doc._str
        index = self._doc._l

        # delete header
        del lines[index]
        del lines[index]

        # get the global indent of the section
        indent = re.split(r'\w', self._doc.peek())[0]

        # parse parameters
        parameters = self._extract_parameters(indent, self.is_method)

        if self.verbose:
            print 'Refactoring methods'
            print parameters

        # generate sphinx friendly rst
        descriptions = []


        # prepare table lines
        max_name_length, max_method_length, max_desc_length = \
                                                self.max_lengths(parameters)
        max_method_length += 11 + max_name_length  # to account for the
                                                   # additional rst directives
        first_column = len(indent)
        second_column = first_column + max_method_length + 1

        table_line = '{0}{1} {2}'.format(indent, '=' * max_method_length,
                                         '=' * max_desc_length)
        empty_line = table_line.replace('=', ' ')
        headings_line = empty_line[:]
        headings_line = self.replace_at('Methods', headings_line,
                                        first_column)
        headings_line = self.replace_at('Description', headings_line,
                                        second_column)

        # draw table
        descriptions.append(table_line)
        descriptions.append(headings_line)
        descriptions.append(table_line)

        # attribute formating
        for arg_name, arg_type, desc in parameters:

            #separate function name from signature
            split_result = re.split('\((.*)\)', arg_name)
            name = split_result[0]

            # and recombine them with the signature in italics
            method_text = ':meth:`{0} <{1}>`'.format(arg_name, name)

            summary = ' '.join(desc)
            # create line
            line = empty_line[:]
            line = self.replace_at(method_text, line, first_column)
            line = self.replace_at(summary, line, second_column)

            descriptions.append(line)

        descriptions.append(table_line)
        descriptions.append('')
        descriptions.append('|')
        descriptions.append('')


        self.insert_lines(descriptions, index)
        return

    def max_lengths(self, parameters):
        """ Find the max lenght of the name and discription in the
        parameters.

        Arguments
        ---------
        parameters : list of tuples
            list of parsed parameter tuples as returned from the
            :meth:`~_FunctionDocString._parse_parameter` function.

        """
        max_name_length = max([parameter[0].find('(')
                               for parameter in parameters])
        max_method_length = max([len(parameter[0])
                               for parameter in parameters])
        max_desc_length = max([len(' '.join(parameter[2]))
                               for parameter in parameters])
        return max_name_length, max_method_length, max_desc_length

    def replace_at(self, word, line, index):
        """ Replace the text in line

        The text in line is replaced with the word without changing the
        size of the line (in most cases). The replace takes place at the
        index.

        Arguments
        ---------
        word : str
            The text to copy into the :param:`line`.

        line : str
            The line where the copy takes place.

        index: int
            The index to start coping.

        Returns
        -------
        result : str
            line of text with the text replaced

        """
        word_length = len(word)
        line_list = list(line)
        line_list[index: index + word_length] = list(word)
        return ''.join(line_list)

    def _refactor_see_also(self, header):
        """Refactor the see also section to sphinx friendly format"""

        lines = self._doc._str
        index = self._doc._l

        # delete header
        del lines[index]
        del lines[index]

        # get the global indent of the section
        indent = re.split(r'\w', self._doc.peek())[0]

        if self.verbose:
            print 'Refactoring See Also'

        # generate sphinx friendly rst
        descriptions = []
        descriptions.append(indent + '**{0}**'.format(header))
        descriptions.append('')

        self.insert_lines(descriptions, index)
        return
