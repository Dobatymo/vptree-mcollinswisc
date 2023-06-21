import os
import os.path
import platform
import sys
import sysconfig

import enscons
import pytoml as toml
from packaging import tags

# Set up environment

with open("pyproject.toml", "rt") as fr:
    metadata = toml.load(fr)["project"]
full_tag = str(next(tags.sys_tags()))

env = Environment(
    tools=["default", "packaging", enscons.generate],
    ENV=os.environ,
    PACKAGE_METADATA=metadata,
    WHEEL_TAG=full_tag,
)

env.Tool("warningstool")

if platform.system() != "Windows":
    env.Append(LIBS=["m"])
    env.AppendUnique(CFLAGS=["-O2"], CXXFLAGS=["-O2"], LINKFLAGS=["-O2"])
    env.AppendUnique(CFLAGS=["-fPIC"], CXXFLAGS=["-fPIC"])
else:
    env.AppendUnique(CFLAGS=["/O2"], CXXFLAGS=["/O2"])
    env.Append(CPPDEFINES=["_USE_MATH_DEFINES"])

# Compile library
core_src = ["pqueue.c", "vptree.c", "geom.c", "vptree_cpp.cc"]
core_src = [os.path.join("src", f) for f in core_src]
static_lib = env.StaticLibrary("lib/vptree", core_src)
if platform.system() != "Windows":
    shared_lib = env.SharedLibrary("lib/vptree", core_src)

# Install files
env.Install("include/vptree", "src/vptree.h")
env.Install("include/vptree", "src/vptree.hh")

# Python interface
pyvptree = SConscript("python/SConscript.py", exports="static_lib")
if pyvptree is not None:
    env.Install("examples", pyvptree)

wheelfiles = env.Whl("platlib", pyvptree, root="")
env.WhlFile(source=wheelfiles)

sourcefiles = FindSourceFiles() + Glob("src/*.h") + Glob("site_scons/site_tools/*.py")
env.SDist(source=sourcefiles)

# Matlab/Python interface
mexvptree = SConscript("matlab/SConscript.py", exports="static_lib")
if mexvptree is not None:
    env.Install("examples", mexvptree)
    env.Install("examples", ["matlab/VPTree.m", "matlab/VPTreeIncNN.m"])

if platform.system() != "Windows":
    # Test code
    common_test_code = ["src/timing.c"] + static_lib
    env.Program("bin/test-vptree", ["src/test_vptree.c"] + common_test_code)

    # Examples
    env.Append(CPPPATH=[env.Dir("include")])
    env.Program("bin/cities", ["examples/cities.c"] + common_test_code)
    env.Program("bin/cities_cpp", ["examples/cities_cpp.cc"] + common_test_code)
