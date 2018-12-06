import urllib
import requests
from django.http import HttpResponse, HttpResponseRedirect
from cas_server import views, models
from django.utils import timezone
from django.conf import settings

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
