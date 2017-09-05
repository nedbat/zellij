"""Design support for Zellij.

Different patterns are implemented as subclasses of Design.
"""

import importlib
import inspect


def get_design(modname):
    """Given a module name, return a Design class."""
    fullmodname = f"zellij.design.{modname}"
    mod = importlib.import_module(fullmodname)
    classes_in_mod = []
    for _, val in inspect.getmembers(mod):
        if inspect.isclass(val):
            if inspect.getmodule(val) is mod:
                classes_in_mod.append(val)
    assert len(classes_in_mod) == 1
    return classes_in_mod[0]
