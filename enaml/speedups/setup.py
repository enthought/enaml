from distutils.core import setup, Extension
from Cython.Distutils import build_ext


extensions = [
    Extension('quad_tree', ['quad_tree.pyx']),
    Extension('model_index', ['model_index.pyx']),
]


setup(
     name='quad_tree', version='0.1a',
     cmdclass = {'build_ext': build_ext},
     ext_modules=extensions,
)

