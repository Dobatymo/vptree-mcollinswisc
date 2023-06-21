from __future__ import print_function

import os

Import("static_lib")

env = Environment(ENV=os.environ)

if env.WhereIs("matlab") is not None and env.WhereIs("mex") is not None:
    env.Tool("mex")
    # env.AppendUnique(MEXFLAGS = ['-g'])

    mexvptree = env.Mex(
        "vptree_mex", ["vptree_mex.c", "mex_interface.c", "mex_convert.c"] + static_lib
    )
else:
    print("Warning: could not find Matlab or mex, skipping...")
    mexvptree = None

Return("mexvptree")
