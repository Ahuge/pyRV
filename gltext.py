"""
gltext is a wrapper around the Mu interface into the gltext library.
It uses rv.runtime.eval to resolve functions on the fly. It may raise a glText.MuException if the runtime.eval failed.
"""

import sys
from rv import runtime


class glText(object):
    """
    glText is a lie. It is just mapping to Mu dynamically.
    """
    class MuException(Exception): pass

    def __getattr__(self, item):
        def f(*args, **kwargs):
            message = "gltext.{name}({args})".format(
                name=item,
                args=", ".join(list(args) + ["%s=%s" % (k, kwargs[k]) for k in kwargs])
            )
            try:
                return runtime.eval(
                    message,
                    ["gltext"]
                )
            except Exception:
                raise glText.MuException("Could not successfully call %s. An exception was raised." % message)
        return f

sys.modules[__name__] = glText()
