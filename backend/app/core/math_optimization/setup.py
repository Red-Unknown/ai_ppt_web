from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "math_kernels",
        ["math_kernels.pyx"],
        include_dirs=[numpy.get_include()],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    )
]

setup(
    name="math_kernels",
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
)
