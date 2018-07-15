from .default import *
try:
    from .local import *
except ImportError as e:
    pass
THEME_CONTACT_EMAIL = DEFAULT_FROM_EMAIL
