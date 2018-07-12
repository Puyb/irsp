import os
from . import forms
from django.conf import settings
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
        forms.MembreForm,
        forms.MembrePhotoForm,
        forms.MembreContactForm,
        forms.LicenceForm,
    ]
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'photos'))
    
    def get_form_kwargs(self, step):
        if step < 3:
            return { 'instance': self.request.user.membre }
        return {}

    def done(self, form_list, **kwargs):
        return HttpResponseRedirect('/page-to-redirect-to-when-done/')


