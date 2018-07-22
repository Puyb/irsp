import os
from . import forms
from . import models
from django.urls import reverse
from django.conf import settings
from django.db import transaction
from django.forms import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from formtools.wizard.views import SessionWizardView


class RegistrationRequiredMixin(AccessMixin):
    """Require a user to have completed registration"""

    def handle_no_registration(self):
        return HttpResponseRedirect(reverse('register-welcome'))

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            request.user.membre
        except models.Membre.DoesNotExist:
            return self.handle_no_registration()
        return super().dispatch(request, *args, **kwargs)


class RegisterWelcomeView(TemplateView):

    template_name = 'register_welcome.html'

    @property
    def saison(self):
        return models.Saison.objects.filter(ouvert=True).order_by('annee').last()

    def get_context_data(self, *args, **kwargs):
        ret = super().get_context_data(*args, **kwargs)
        ret['saison'] = self.saison
        return ret


class ProfileView(RegistrationRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, *args, **kwargs):
        ret = super().get_context_data(*args, **kwargs)
        ret['user'] = self.request.user
        return ret


class RegisterWizard(LoginRequiredMixin, SessionWizardView):

    form_list = [
        forms.UserForm,
        forms.MembreForm,
        forms.MembrePhotoForm,
        forms.MembreContactForm,
        forms.LicenceForm,
    ]

    template_name = 'register_form.html'

    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'photos'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._membre = None
        self._licence = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.licence.saison
        except models.Saison.DoesNotExist:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

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
            self._licence = models.Licence(saison=self.saison)
        return self._licence

    @property
    def saison(self):
        return models.Saison.objects.filter(ouvert=True).order_by('annee').last()

    def get_context_data(self, form, **kwargs):

        # Retrieve original context data
        ret = super().get_context_data(form, **kwargs)

        # Determine the full name of the user
        if self.user:
            user_full_name = f"{self.user.last_name} {self.user.first_name}".strip()
            if not user_full_name:
                user_full_name = self.user.username.replace("$sso$", "")
        else:
            user_full_name = None
        ret.update(user_full_name=user_full_name)

        # Return the modified context data
        return ret

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

        return HttpResponseRedirect(reverse('profile'))
