# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
import logging

logger = logging.getLogger(__name__)

SEXE_CHOICES = (
    ('H', _(u'Homme')),
    ('F', _(u'Femme')),
)

TAILLES_CHOICES = (
    ('XS', _('XS')),
    ('S', _('S')),
    ('M', _('M')),
    ('L', _('L')),
    ('XL', _('XL')),
    ('XXL', _('XXL')),
)

DISCIPLINE_CHOICES = (
    ('rando init', _('Randonnée initiation')),
    ('Roller Freestyle', _('Slalom')),
    ('Course', _('Course')),
    #('hockey', _('Hockey')),
)

REDUCTION_CHOICES = (
    ('actif', _('Actif ou retraité')),
    ('enfant', _('Enfant')),
    ('etudiant', _('Étudiant')),
    ('chomeur', _('Chômeur')),
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
    "souhaitez faire des compétitions. Si vous le pouvez, scannez le certificat "
    "et ajoutez le (formats PDF ou JPEG)."
)

PHOTO_HELP = _(
    """Si vous le pouvez, ajoutez la photo (formats JPEG). """
)

CONTACT_HELP = _(
    """Personne a contacter en cas de problème ou responsable légale pour un mineur"""
)

COURS_HELP = _(
    "Cochez la ou les sessions auxquelles vous souhaitez participer. Cette "
    "selection n'est pas définitive. Vous pouvez changer d'avis en "
    "cours d'année..."
)

LICENCE_HELP = _(
    """Si vous le connaissez"""
)

class Membre(models.Model):
    user              = models.OneToOneField(User, on_delete=models.CASCADE)
    sexe              = models.CharField(_('Sexe'), max_length=1, choices=SEXE_CHOICES)
    adresse1          = models.CharField(_('Adresse'), max_length=200, blank=True)
    adresse2          = models.CharField(_('Adresse'), max_length=200, blank=True)
    ville             = models.CharField(max_length=200)
    code_postal       = models.CharField(max_length=200)
    telephone         = models.CharField(max_length=200)
    date_de_naissance = models.DateField(_('Date de naissance'))
    photo             = models.FileField(_('Photo d\'identité'), upload_to='photos', blank=True, help_text=PHOTO_HELP)
    contact_nom       = models.CharField(_('Nom d\'un contact en cas d\'urgence'), max_length=200, help_text=CONTACT_HELP)
    contact_telephone = models.CharField(_('Téléphone d\'un contact en cas d\'urgence'), max_length=200)
    contact_email     = models.EmailField(_('E-mail d\'un contact en cas d\'urgence'), max_length=200, blank=True)

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
        return f"{self.nom} {self.prenom}".strip()

class Licence(models.Model):
    membre            = models.ForeignKey(Membre, related_name='licences', on_delete=models.CASCADE)
    saison            = models.ForeignKey(Saison, related_name='membres', on_delete=models.PROTECT)
    num_licence       = models.CharField(_('Numéro de licence'), max_length=15, blank=True, help_text=LICENCE_HELP)
    tarif             = models.ForeignKey(Tarif, related_name='membres', on_delete=models.PROTECT)
    autre_club        = models.BooleanField(_("J'ai une licence dans un autre club et je souhaite rester licencié dans ce club."), default=False)
    discipline        = models.CharField(_('Discipline'), max_length=20, choices=DISCIPLINE_CHOICES)
    certificat        = models.FileField(_('Certificat médical'), upload_to='certificats', blank=True, help_text=CERTIFICAT_HELP)
    certificat_valide = models.BooleanField(_(u'Certificat valide'), default=False)
    paiement_info     = models.CharField(_('Détails'), max_length=1000, blank=True)
    prix              = models.DecimalField(_('Prix'), max_digits=5, decimal_places=2, default=Decimal(0))
    paiement          = models.DecimalField(_('Paiement reçu'), max_digits=5, decimal_places=2, null=True, blank=True)
    date              = models.DateTimeField(_("Date d'insciption"), auto_now_add=True)
    ffrs              = models.BooleanField(default=False)

    def paiement_complet(self):
        return (self.paiement or Decimal(0)) >= self.prix

    def paiement_info2(self):
        return self.paiement_info or 'Chèque'
    paiement_info2.verbose_name = 'paiement'
