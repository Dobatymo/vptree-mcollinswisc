from __future__ import print_function

import distutils.sysconfig
import os
import platform
from distutils.command import build_ext
from distutils.core import Distribution

Import("static_lib")
env = Environment(ENV=os.environ)

# Cythonize
env.Tool("cythontool")
pyvptree_c = env.Cython("pyvptree.c", "pyvptree.pyx")
env.Depends(pyvptree_c, "vptree.pxd")
env.Depends(pyvptree_c, "#/include/vptree/vptree.h")

# Set up python-friendly compilation environment
config_vars = distutils.sysconfig.get_config_vars()

if "CC" in config_vars:
    env["CC"] = config_vars["CC"]
if "BASECFLAGS" in config_vars:
    env["CFLAGS"] = config_vars["BASECFLAGS"].split()
if "OPT" in config_vars:
    env.AppendUnique(CFLAGS=config_vars["OPT"].split())
if "SO" in config_vars:
    env["SHLIBSUFFIX"] = config_vars["SO"]

if platform.system() == "Windows":
    b = build_ext.build_ext(Distribution())
    b.finalize_options()
    env["LIBPATH"] = b.library_dirs
env.AppendUnique(CPPPATH=[distutils.sysconfig.get_python_inc()])

try:
    env["SHLINK"] = config_vars["LDSHARED"]
except KeyError:
    pass
env["SHLIBPREFIX"] = ""

env["STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME"] = True

# Build module
pyvptree = env.SharedLibrary(
    "#/pyvptree", pyvptree_c + static_lib, no_import_lib=True
)

Return("pyvptree")
