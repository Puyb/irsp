# -*- coding: utf-8 -*-
import logging
from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)

SEXE_CHOICES = (
    ('H', _(u'Homme')),
    ('F', _(u'Femme')),
)

DISCIPLINE_CHOICES = (
    ('rando init', _('Randonnée initiation')),
    ('Roller Freestyle', _('Slalom')),
    ('Course', _('Course')),
    #('hockey', _('Hockey')),
)

class Saison(models.Model):
    annee = models.IntegerField()
    ouvert = models.BooleanField()

    def __str__(self):
        return '%s - %s' % (self.annee, self.annee + 1)

class Tarif(models.Model):
    saison = models.ForeignKey(Saison, related_name='tarifs', on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    prix = models.DecimalField(_('Prix'), max_digits=5, decimal_places=2, default=Decimal(0))

    def __str__(self):
        return '%s - %s (%s€)' % (self.saison, self.nom, self.prix)


CERTIFICAT_HELP = _(
    "Votre certificat médical doit dater de moins de 1 ans et doit mentionner "
    "que vous êtes \"aptes à la pratique du roller\" et \"en compétition\" si vous "
    "souhaitez faire des compétitions (formats PDF, PNG ou JPEG)."
)

PHOTO_HELP = _(
    """(formats PDF, PNG ou JPEG). """
)

CONTACT_HELP = _(
    """Personne a contacter en cas de problème ou responsable légale pour un mineur"""
)

LICENCE_HELP = _(
    """Si vous avez déjà été licencié et que vous le connaissez"""
)

class Membre(models.Model):
    user              = models.OneToOneField(User, on_delete=models.CASCADE)
    nom               = models.CharField(_('Nom'), max_length=30)
    prenom            = models.CharField(_('Prénom'), max_length=150)
    sexe              = models.CharField(_('Sexe'), max_length=1, choices=SEXE_CHOICES)
    adresse1          = models.CharField(_('Adresse'), max_length=200, blank=True)
    adresse2          = models.CharField(_('Adresse'), max_length=200, blank=True)
    ville             = models.CharField(max_length=200)
    code_postal       = models.CharField(max_length=200)
    telephone         = models.CharField(max_length=200)
    date_de_naissance = models.DateField(_('Date de naissance'))
    photo             = models.FileField(_('Photo d\'identité'), upload_to='photos', help_text=PHOTO_HELP)
    contact_nom       = models.CharField(_('Nom d\'un contact en cas d\'urgence'), max_length=200, help_text=CONTACT_HELP)
    contact_telephone = models.CharField(_('Téléphone d\'un contact en cas d\'urgence'), max_length=200)
    contact_email     = models.EmailField(_('E-mail d\'un contact en cas d\'urgence'), max_length=200, blank=True)
    num_licence       = models.CharField(_('Numéro de licence'), max_length=15, blank=True, help_text=LICENCE_HELP)

    date              = models.DateTimeField(_("Date d'insciption"), auto_now_add=True)

    def age(self, today=None):
        if not today:
            today = date.today()
        try:
            birthday = self.date_de_naissance.replace(year=today.year)
        except ValueError: # raised when birth date is February 29 and the current year is not a leap year
            birthday = self.date_de_naissance.replace(year=today.year, day=self.date_de_naissance.day-1)
        return today.year - self.date_de_naissance.year - (birthday > today)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()

OTHER_CLUB_DISCOUNT = Decimal('35')

class Licence(models.Model):
    membre            = models.ForeignKey(Membre, related_name='licences', on_delete=models.CASCADE)
    saison            = models.ForeignKey(Saison, related_name='membres', on_delete=models.PROTECT)
    tarif             = models.ForeignKey(Tarif, related_name='membres', on_delete=models.PROTECT)
    autre_club        = models.BooleanField(_("J'ai une licence dans un autre club et je souhaite rester licencié dans ce club (remise de %s€).") % OTHER_CLUB_DISCOUNT, default=False)
    discipline        = models.CharField(_('Discipline'), max_length=20, choices=DISCIPLINE_CHOICES)
    certificat        = models.FileField(_('Certificat médical'), upload_to='certificats', help_text=CERTIFICAT_HELP, blank=True, null=True)
    cerfa_non         = models.BooleanField(_(u'Je certifie sur l\'honneur avoir renseigner le questionnaire de santé QS-SPORT Cerfa N°15699*01 et avoir répondu par la négative à l’ensemble des questions'), default=False)
    prix              = models.DecimalField(_('Prix'), max_digits=5, decimal_places=2, default=Decimal(0))
    date              = models.DateTimeField(_("Date d'insciption"), auto_now_add=True)
    ffrs              = models.BooleanField(default=False)

    @property
    def montant_paiement(self):
        if hasattr(self, '_montant_paiement'):
            return self._montant_paiement
        return self.paiements.aggregate(sum=models.Sum('montant'))['sum']

    def paiement_complet(self):
        return (self.montant_paiement or Decimal(0)) >= self.prix

    @property
    def paiement_en_attente(self):
        return self.paiements.filter(montant__isnull=True).aggregate(sum=models.Sum('strip_charge__amount'))['sum']

    def paiement_complet_en_attente(self):
        montant = self.montant_paiement or Decimal(0)
        montant += self.paiement_en_attente or Decimal(0)
        return montant >= self.prix

    def __str__(self):
        return '%s - %s' % (self.saison, self.membre)

class Paiement(models.Model):
    licence       = models.ForeignKey(Licence, related_name='paiements', on_delete=models.CASCADE)
    date          = models.DateTimeField(auto_now_add=True)
    type          = models.CharField(max_length=100, default='Chèque')
    montant       = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stripe_intent = models.CharField(max_length=200, blank=True, null=True)
    detail = models.TextField(blank=True)
