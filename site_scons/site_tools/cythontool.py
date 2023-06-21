import os.path
import sys

import SCons
from SCons.Action import Action
from SCons.Builder import Builder


def cython_callable(target, source, env):
    from Cython.Build import cythonize

    cythonize(str(source[0]))
    assert os.path.exists(str(target[0]))


cython_action = Action(cython_callable)


def create_builder(env):
    try:
        cython = env["BUILDERS"]["Cython"]
    except KeyError:
        cython = SCons.Builder.Builder(
            action=cython_action,
            emitter={},
            suffix=cython_suffix_emitter,
            single_source=1,
        )
        env["BUILDERS"]["Cython"] = cython

    return cython


def cython_suffix_emitter(env, source):
    return ".c"


def generate(env):
    c_file, cxx_file = SCons.Tool.createCFileBuilders(env)

    c_file.suffix[".pyx"] = cython_suffix_emitter
    c_file.add_action(".pyx", cython_action)

    c_file.suffix[".py"] = cython_suffix_emitter
    c_file.add_action(".py", cython_action)

    create_builder(env)


def exists(env):
    try:
        import Cython

        return True
    except ImportError:
        return False
