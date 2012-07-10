import string
from PySide.QtGui import QLabel, QApplication, QMainWindow, QVBoxLayout, \
    QWidget, QPushButton

def style_dict_to_str(style_dict):
    """ Converts a nested dictionary of stylesheets into a Qt-readable string

    """
    output = ""
    for selector in style_dict:
        style_str = selector + str(style_dict[selector])
        trans = string.maketrans(",", ";")
        # change all commas to semicolons and remove any quotes
        output += style_str.translate(trans, "'\"")
    return output

# this is how the user would specify the stylesheet
d = {
    'QLabel#lbl' : {
        'font-size' : '32px',
        'border' : '2px dashed red',
        'background' : 'blue'
    },

    '*' : {
        'background' : '#000',
        'color' : 'white',
    },

    '#change_button' : {
        'background' : 'gray',
    }
}

app = QApplication([])
window = QMainWindow()

main = QWidget()

lbl = QLabel('asdfasdfasdf', main)
lbl.setObjectName('lbl')

lbl2 = QLabel('ddddddddd', main)

button = QPushButton('Change color', main)
button.setObjectName('change_button')

def update_color():
    # properties are easily retrieved
    current_color = d['QLabel#lbl'].get('color') 
    if current_color == 'blue':
        color = 'white'
        bg = 'blue'
    else:
        color = 'blue'
        bg = 'white'
    # properties can also be easily changed/added
    d['QLabel#lbl'].update({'color':color, 'background':bg}) 
    # d['QLabel#lbl']['color'] = color also works for changing a single property
    s = style_dict_to_str(d)
    window.setStyleSheet(s)
    
button.clicked.connect(update_color)

layout = QVBoxLayout()
layout.addWidget(lbl)
layout.addWidget(lbl2)
layout.addWidget(button)

main.setLayout(layout)
s = style_dict_to_str(d)
window.setStyleSheet(s)

window.setCentralWidget(main)
window.show()

app.exec_()
