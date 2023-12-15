import sys
import platform
import numpy

bit_depth = platform.architecture()[0]
os_name = platform.architecture()[1]

if os_name == "WindowsPE":
    #only needed under windows
    import setuptools

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import Cython.Compiler.Options 

Cython.Compiler.Options.annotate = True


if sys.version_info.major == 3 and sys.version_info.minor == 10 and bit_depth == '64bit':
    module_name = 'cy_moleculab_310_64'
else:
    raise BaseException('Unsupported python version')


if os_name == "WindowsPE":
    ext_modules = [Extension(module_name, ['cy_moleculab.pyx'],extra_compile_args=['/Ox','/openmp','/GT','/arch:SSE2','/fp:fast'])]
else:
    #ext_modules = [Extension(module_name, ['cy_moleculab.pyx'],extra_compile_args=['-O3','-fopenmp','-msse4.2','-ffast-math'])]
    ext_modules = [Extension(module_name, ['cy_moleculab.pyx'],extra_compile_args=['-O3','-msse4.2','-ffast-math'])]


setup(
    name='Moleculab script',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
    include_dirs=[numpy.get_include()]
)
