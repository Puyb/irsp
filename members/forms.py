from datetime import datetime
from django.forms import ModelForm, ModelChoiceField, CharField
from django.forms.widgets import SelectDateWidget, RadioSelect
from django.utils.translation import ugettext_lazy as _
from .models import Membre, Licence, Tarif

class MembreForm(ModelForm):
    class Meta:
        model = Membre
        fields = ['nom', 'prenom', 'sexe', 'adresse1', 'adresse2',
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
        fields = ['tarif', 'num_licence', 'autre_club', 'discipline', 'certificat', 'cerfa_non']
    tarif = ModelChoiceField(
        queryset=Tarif.objects.all(),
        required=True,
        widget=RadioSelect,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tarif'].queryset = Tarif.objects.filter(saison=self.instance.saison)
        self.fields['tarif'].widget.attrs['class'] = 'form-radio' # fix error display

