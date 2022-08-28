import json
import logging
import os
import requests
import logging
from . import forms
from . import models
from .utils import MailThread
from datetime import datetime, date
from decimal import Decimal
from django.urls import reverse
from django.conf import settings
from django.db import transaction
from django.db.models import Prefetch, Sum, Q
from django.db.models.query import prefetch_related_objects
from django.forms import ValidationError
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.views.generic import TemplateView, ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from formtools.wizard.views import SessionWizardView
import stripe
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

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
        user = self.request.user
        membre = user.membre
        if user.is_staff and 'membre_id' in self.kwargs:
            membre = models.Membre.objects.get(id=self.kwargs['membre_id'])
        ret['membre'] = membre
        prefetch_related_objects([membre],
            Prefetch('licences', models.Licence.objects.annotate(_montant_paiement=Sum('paiements__montant')))
        )
        ret['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        ret['saisons'] = models.Saison.objects.filter(ouvert=True).exclude(membres__in=membre.licences.all())
        return ret

class DoneView(ProfileView):
    template_name = 'done.html'

class AlreadyRegisteredView(ProfileView):
    template_name = 'already-registered.html'


class RegisterWizard(LoginRequiredMixin, SessionWizardView):

    form_list = [
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
        try:
            if self.user.membre.licences.filter(saison=self.saison).count():
                return HttpResponseRedirect(reverse('register-already'))
        except AttributeError as e:
            pass
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

    def get_form_instance(self, step):
        if step in ['0', '1', '2']:
            return self.membre
        elif step == '3':
            return self.licence

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if isinstance(form, forms.LicenceForm):
            form.fields['tarif'].queryset = models.Tarif.objects.filter(saison=form.instance.saison).exclude(id=22)
            try:
                if hasattr(self.request.user, 'membre'):
                    licence = self.request.user.membre.licences.get(saison__annee=2020)
                    if licence.paiement_complet() and form.instance.saison.annee == 2021:
                        form.fields['tarif'].queryset = models.Tarif.objects.filter(id=22)
            except models.Licence.DoesNotExist:
                pass
        return form

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context.update({
            'form_labels': {
                0: 'Connection',
                1: 'Informations',
                2: 'Photo',
                3: 'Contact',
                4: 'Licence',
                5: 'Paiement',
            },
        })
        if isinstance(form, forms.LicenceForm):
            context['age'] = self.age()
        return context

    def age(self):
        today = date.today()
        data = self.get_cleaned_data_for_step('0') or {}
        try: 
            birthday = data['date_de_naissance'].replace(year=today.year)
        except ValueError: # raised when birth date is February 29 and the current year is not a leap year
            birthday = data['date_de_naissance'].replace(year=today.year, day=self.date_de_naissance.day-1)
        return today.year - data['date_de_naissance'].year - (birthday > today)

    def done(self, form_list, **kwargs):

        form_list = list(form_list)
        with transaction.atomic():
            # Membre
            membre = form_list[0].save(commit=False)
            membre = form_list[1].save(commit=False)
            membre = form_list[2].save(commit=True)
            # Licence
            licence = form_list[3].instance
            licence.membre = membre
            licence.prix = licence.tarif.prix
            if licence.autre_club:
                licence.prix -= models.OTHER_CLUB_DISCOUNT
            form_list[3].save()

        # Send a welcome email!
        text_content = render_to_string('register_welcome_email.txt', {})
        html_content = render_to_string('register_welcome_email.html', {})
        msg = EmailMultiAlternatives(
            subject="Bienvenue chez I Skate Paris!",
            body=text_content,
            from_email="noreply@skate.paris",
            to=[membre.user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        MailThread([msg]).start()

        return HttpResponseRedirect(reverse('register-done'))

def licencePayment(request, id=None):
    licence = None
    description = request.POST.get('description', '')
    if id:
        licence = get_object_or_404(models.Licence, id=id)
        description = '%s - Saison %s' % (request.user.get_full_name(), licence.saison)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try: 
        paiement = models.Paiement(
            licence=licence,
            type='stripe',
            montant=None, # wil l be updated when confirmation is received from stripe
            description=description,
        )
        paiement.save()

        amount = Decimal(request.POST.get('amount', 0))
        stripe_description = 'Paiement libre %d' % paiement.id
        if id:
            amount = licence.prix
            stripe_description = description

        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency='EUR',
            description=stripe_description,
        )

        paiement.stripe_intent = intent.id
        paiement.save()

        success = True

        return HttpResponse(json.dumps({
            'success': success,
            'client_secret': intent.client_secret,
            'id': paiement.id,
        }))
    except Exception as e:
        logger.exception('error handling stripe intent creation')
        return HttpResponse(json.dumps({
            'success': False,
        }), status=500)

def payed(request):
    paiement = get_object_or_404(models.Paiement, id=request.GET.get('id', 0))
    return HttpResponse(json.dumps({
        'success': paiement.montant != None,
    }))

def freePayment(request):
    if request.method == 'POST':
        return licencePayment(request)
    return TemplateResponse(request, "free-payment.html", {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    })

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK_KEY

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # invalid payload
        return HttpResponse('Invalid payload', status=400)
    except stripe.error.SignatureVerificationError as e:
        # invalid signature
        return HttpResponse('Invalid payload', status=400)

    event_dict = event.to_dict()
    if event_dict['type'] == "payment_intent.succeeded":
        intent = event_dict['data']['object']
        paiement = None
        try:
            paiement = models.Paiement.objects.get(
                stripe_intent=intent['id'],
            )
            paiement.montant = Decimal(intent['amount']) / 100
            paiement.detail = '\nConfirmed on %s' % datetime.now()
            paiement.save()
        except models.Paiement.DoesNotExist:
            logger.warning('intent not found %s %s', json.dumps(intent))
        # Fulfill the customer's purchase
    elif event_dict['type'] == "payment_intent.payment_failed":
        intent = event_dict['data']['object']
        paiement = models.Paiement.objects.get(
            stripe_intent=intent['id'],
        )
        error_message = intent['last_payment_error']['message'] if intent.get('last_payment_error') else None
        if paiement:
            paiement.detail = '\nRejected on %s\n%s' % (datetime.now(), error_message)
            paiement.save()
        else:
            logger.warning('intent not found %s %s', json.dumps(intent))

    return HttpResponse('OK')

def sso_logout(request):
    params = {
        'api_key': settings.DISCOURSE_API_KEY,
        'api_username': 'system',
        'email': request.user.email,
    }
    url = 'https://%s/admin/users/list/all.json' % (settings.DISCOURSE_HOST, )
    response = requests.request('GET', url, allow_redirects=False, params=params)
    print(response.text)
    data = response.json()
    user_id = data[0]['id']

    params = {
        'api_key': settings.DISCOURSE_API_KEY,
        'api_username': 'system',
    }
    url = 'https://%s/admin/users/%s/log_out' % (settings.DISCOURSE_HOST, user_id);
    response = requests.request('POST', url, allow_redirects=False, params=params)
    logout(request)
    return HttpResponseRedirect(reverse('register-welcome'))
    
class TrombiView(ListView):
    model = models.Licence
    context_object_name = 'licences'
    template_name = 'trombi.html'

    def get_queryset(self):
        saison = get_object_or_404(models.Saison, annee=self.kwargs['saison'])
        qs = models.Licence.objects.filter(saison=saison)
        if self.request.GET.get('q', ''):
            for w in self.request.GET['q'].split():
                if w:
                    qs = qs.filter(Q(membre__nom__icontains=w) | Q(membre__prenom__icontains=w))
        if self.request.GET.get('discipline', ''):
            qs = qs.filter(discipline=self.request.GET['discipline'])
        return qs

    def get_context_data(self, *args, **kwargs):
        ret = super().get_context_data(*args, **kwargs)
        ret['DISCIPLINE_CHOICES'] = models.DISCIPLINE_CHOICES
        return ret
