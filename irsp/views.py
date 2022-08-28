import urllib
import requests
from django.http import HttpResponse, HttpResponseRedirect
from cas_server import views, models
from django.utils import timezone
from django.conf import settings

from django.contrib.auth import get_user_model
from discourse_django_sso import views as sso_views

class CasLoginView(views.LoginView):
    def get(self, request):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/login?%s' % urllib.parse.urlencode({
                'next': self.request.get_full_path(),
            }))
        username = self.request.user.username[len('$sso$'):]

        forum_url = 'https://forum.i.skate.paris/users/%s.json?api_key=%s&api_username=%s' % (
            username,
            settings.DISCOURSE_API_KEY,
            settings.DISCOURSE_API_USERNAME,
        )
        print(forum_url)
        response = requests.get(forum_url)
        if not self.check_user_groups(response.json(), settings.DISCOURSE_CAS_GROUPS):
            return HttpResponse('Acces interdit', status=403)
        self.init_get(request)
        self.request.session['warn'] = False
        self.user = models.User.objects.get_or_create(
            username=username,
            session_key=self.request.session.session_key
        )[0]
        self.user.last_login = timezone.now()
        self.user.save()
        return self.service_login()

    def check_user_groups(self, user, cas_groups):
        for group in user['user']['groups']:
            if group['id'] in cas_groups:
                return True
        return False


class SSOCreateSessionView(sso_views.SSOCreateSessionView):
    @classmethod
    def create_user_session(cls, request, user_email, external_id, username):
        """Retrieve the username through the email and change the username if needed"""

        if not user_email or not username:
            raise ValueError('Missing required field')  # pragma: no cover
        user_model = get_user_model()

        users = user_model.objects.filter(username__startswith='$sso$', email=user_email)
        django_username = '$sso$' + username
        if len(users) and  users[0].username != django_username:
            users[0].username = django_username
            users[0].save()
        return sso_views.SSOCreateSessionView.create_user_session(request, user_email, external_id, username)
