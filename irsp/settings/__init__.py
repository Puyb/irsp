THEME_CONTACT_EMAIL = None
from .default import *
try:
    from .local import *
except ImportError as e:
    pass
if not THEME_CONTACT_EMAIL:
    try:
        THEME_CONTACT_EMAIL = DEFAULT_FROM_EMAIL
    except NameError:
        pass
