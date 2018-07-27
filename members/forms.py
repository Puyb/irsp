from datetime import datetime
from django.forms import ModelForm
from django.forms.widgets import SelectDateWidget
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Membre, Licence

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', ]

class MembreForm(ModelForm):
    class Meta:
        model = Membre
        fields = ['sexe', 'adresse1', 'adresse2',
                  'ville', 'code_postal', 'telephone', 'date_de_naissance', ]
        widgets = {
            'date_de_naissance': SelectDateWidget(years=range(datetime.now().year , datetime.now().year - 100, -1)),
        }

class MembrePhotoForm(ModelForm):
    class Meta:
        model = Membre
        fields = ['photo', ]

class MembreContactForm(ModelForm):
    class Meta:
        model = Membre
        fields = [ 'contact_nom', 'contact_telephone', 'contact_email', ]

class LicenceForm(ModelForm):
    class Meta:
        model = Licence
        fields = ['reduction', 'autre_club', 'discipline', 'certificat', ]

