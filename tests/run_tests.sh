cd ..

echo 'Running Qt tests:'
ETS_TOOLKIT=qt4 python -m unittest discover tests.qt

echo 'Running wxPython tests:'
ETS_TOOLKIT=wx python -m unittest discover tests.wx

