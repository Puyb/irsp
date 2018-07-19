import os
from . import forms
from . import models
from django.conf import settings
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from formtools.wizard.views import SessionWizardView


def index(request):
    return TemplateResponse(request, 'step1.html', {})


class RegisterWizard(LoginRequiredMixin, SessionWizardView):

    form_list = [
        forms.UserForm,
        forms.MembreForm,
        forms.MembrePhotoForm,
        forms.MembreContactForm,
        forms.LicenceForm,
    ]

    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'photos'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._membre = None
        self._licence = None

    @property
    def user(self):
        return self.request.user

    @property
    def membre(self):
        if not self._membre:
            try:
                self._membre = self.user.membre
            except models.Membre.DoesNotExist:
                self._membre = models.Membre(user=self.user)
        return self._membre

    @property
    def licence(self):
        if not self._licence:
            saison = models.Saison.objects.filter(ouvert=True).order_by('annee').last()
            self._licence = models.Licence(saison=saison)
        return self._licence

    def get_form_instance(self, step):
        if step == '0':
            return self.user
        elif step in ['1', '2', '3']:
            return self.membre
        elif step == '4':
            return self.licence

    def done(self, form_list, **kwargs):
        form_list = list(form_list)
        with transaction.atomic():
            # User
            user = form_list[0].save()
            # Membre
            membre = form_list[1].save(commit=False)
            membre = form_list[2].save(commit=False)
            membre.nom = user.last_name
            membre.prenom = user.first_name
            membre = form_list[3].save(commit=True)
            # Licence
            form_list[4].instance.membre = membre
            form_list[4].save()
        return HttpResponseRedirect('/page-to-redirect-to-when-done/')
