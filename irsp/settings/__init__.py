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
if not DISCOURSE_SSO_URL:
    DISCOURSE_SSO_URL = 'https://' + DISCOURSE_HOST + '/session/sso_provider'
