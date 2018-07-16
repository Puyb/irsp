from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from discourse_django_sso import views as sso_views
from . import settings


class FixedInMemoryNonceService(sso_views.InMemoryNonceService):

    def __init__(self):
        super().__init__()
        self.nonce_val = "e15917e0320992596f638ebff7678202"

    def generate_nonce(self) -> str:
        self.generated_nonces.add(self.nonce_val)
        return self.nonce_val

    def fixed_nonce_val(self):
        return self.nonce_val

    def clear_invalid_nonces(self):
        self.invalid_nonces.clear()

nonce_service = FixedInMemoryNonceService()

urlpatterns = [
    path('member/', include('members.urls')),
    path('admin/', admin.site.urls),
    path(
        'sso/',
        sso_views.SSOProviderView.as_view(
            sso_redirect=settings.DISCOURSE_SSO_REDIRECT,
            sso_secret=settings.DISCOURSE_SSO_KEY
        ),
        name="sso"
    ),
    path(
        'accounts/login/',
        sso_views.SSOClientView.as_view(
            sso_secret=settings.DISCOURSE_SSO_KEY,
            sso_url=settings.DISCOURSE_SSO_URL,
            nonce_service=nonce_service),
        name="client"
    ),
    path(
        'createSession/',
        sso_views.SSOCreateSessionView.as_view(
            sso_secret=settings.DISCOURSE_SSO_KEY,
            nonce_service=nonce_service),
        name="createSession"
    ),
    path("", TemplateView.as_view(template_name="homepage.html"), name="home"),
]

if settings.DEBUG:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
