from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.views import LogoutView
from discourse_django_sso import views as sso_views
from . import settings

# Nonce generator service, used for authenticating with the Discourse SSO provider
nonce_service = sso_views.InMemoryNonceService()

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('profile')), name='index'),
    path('member/', include('members.urls')),
    path('admin/', admin.site.urls),
    path(
        'accounts/logout/',
        LogoutView.as_view(next_page=reverse_lazy('profile')),
        name="accounts-logout",
    ),
    path(
        'accounts/login/',
        sso_views.SSOClientView.as_view(
            sso_secret=settings.DISCOURSE_SSO_KEY,             # Discourse SSO key
            sso_url=settings.DISCOURSE_SSO_URL,                # Discourse SSO URL
            sso_redirect_url=settings.DISCOURSE_SSO_REDIRECT,  # Local redirect URL
            nonce_service=nonce_service,
        ),
        name="accounts-login",
    ),
    path(
        'accounts/sso/create-session/',
        sso_views.SSOCreateSessionView.as_view(
            sso_secret=settings.DISCOURSE_SSO_KEY,
            nonce_service=nonce_service,
        ),
        name="accounts-sso-create-session",
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
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
