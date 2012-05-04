#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import datetime
import os

import numpy as np

from chaco.api import Plot, ArrayPlotData

import enaml
from enaml.item_models.abstract_item_model import AbstractItemModel


class Node(object):
    """ A simple node class for building up a filesystem tree.

    """
    def __init__(self, parent, text, stat, files=None, children=None):
        self.parent = parent
        self.text = text
        self.stat = stat
        self.children = children or []


def make_fs_tree():
    """ Returns the root node of a filesystem tree for the directory 
    downward.

    """
    this_path = os.path.abspath(__file__)
    root_path = os.path.split(os.path.dirname(this_path))[0]
    node_cache = {}
    root = Node(None, '', '')
    node_cache[root_path] = root
    gen = os.walk(root_path)

    while True:
        try:
            dirpath, dirnames, filenames = gen.next()
        except StopIteration:
            break
        if dirpath not in node_cache:
            continue
        parent = node_cache[dirpath]
        for dn in dirnames:
            if not dn.startswith('.'):
                fd = os.path.join(dirpath, dn)
                s = os.stat(fd)
                node = Node(parent, dn, s)
                node_cache[fd] = node
                parent.children.append(node)
        for fn in filenames:
            if not fn.startswith('.'):
                s = os.stat(os.path.join(dirpath, fn))
                parent.children.append(Node(parent, fn, s))

    return root


class FSModel(AbstractItemModel):
    """ An AbstractItemModel implementation which exposes the
    filesystem tree.

    """
    fs_root = make_fs_tree()

    def index(self, row, column, parent=None):
        """ Abstract method implementation that will create a valid
        model index for the given row and column if they are valid.
        Otherwise, returns an invalid index.

        """
        if self.has_index(row, column, parent):
            if parent is None:
                parent_node = self.fs_root
            else:
                parent_node = parent.context
            child = parent_node.children[row]
            return self.create_index(row, column, child)

    def parent(self, index):
        """ Abstract method implementation that always returns None, 
        forcing the model to be flat.

        """
        if index is None:
            return
        node = index.context
        node_parent = node.parent
        if node_parent is self.fs_root:
            return None
        node_parent_parent = node.parent.parent
        idx = node_parent_parent.children.index(node_parent)
        return self.create_index(idx, index.column, node_parent)
    
    def row_count(self, idx):
        if idx is None:
            node = self.fs_root
        else:
            node = idx.context
        return len(node.children)
    
    def column_count(self, idx):
        return 3
    
    def data(self, idx):
        col = idx.column
        node = idx.context
        if col == 0:
            res = node.text
        elif col == 1:
            res = str(node.stat.st_size / 1024) + ' kb'
        else:
            dt = datetime.fromtimestamp(node.stat.st_mtime)
            res = dt.strftime('%c')
        return res
    
    def horizontal_header_data(self, section):
        return ['Name', 'Size', 'Last Modified'][section]


def make_sin_plot():
    """ Returns a chaco plot which plots a simple sin curve.

    """
    idx = np.linspace(0, np.pi * 2, 100)
    val = np.sin(idx)
    plt = Plot(ArrayPlotData(x=idx, y=val), padding_top=30, padding_bottom=30, 
               padding_left=35, padding_right=10, title='Sin Plot',
               fill_padding=False, background='transparent')
    plt.plot(('x', 'y'), color='red')
    return plt


def make_html_table():
    """ Returns a string of html table data.

    """
    html = """
    <html>
        <h1> Simple HTML </h1>
        <body>
            <h4>Cell that spans two columns:</h4>
            <table border="1">
                <tr>
                  <th>Name</th>
                  <th colspan="2">Telephone</th>
                </tr>
                <tr>
                  <td>Tony Stark</td>
                  <td>555 77 854</td>
                  <td>555 77 855</td>
                </tr>
            </table>
            <h4>Cell that spans two rows:</h4>
            <table border="1">
                <tr>
                  <th>First Name:</th>
                  <td>Pepper Potts</td>
                </tr>
                <tr>
                  <th rowspan="2">Telephone:</th>
                  <td>555 77 854</td>
                </tr>
                <tr>
                  <td>555 77 855</td>
                </tr>
            </table>
        </body>
    </html>
    """
    return html


def main():
    with enaml.imports():
        from widget_gallery import WidgetGallery

    img_path = os.path.join(os.path.dirname(__file__), 'lena.png')
    view = WidgetGallery(
        fs_model=FSModel(), sin_plot=make_sin_plot(),
        html_data=make_html_table(), img_path=img_path,
    )
    view.show()


if __name__ == '__main__':
    main()

