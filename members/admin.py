from django.contrib import admin
from django_reverse_admin import ReverseModelAdmin

from . import models


class MembreAdmin(admin.ModelAdmin):
    """Admin settings for the Membre model"""
    list_display = (
        'nom', 'prenom', 'user',
    )

class PaiementInline(admin.TabularInline):
    model = models.Paiement
    fields = ['date', 'type', 'montant', ]
    readonly_fields = ['date', 'type', 'montant' ]
    extra = 0

class LicenceAdmin(ReverseModelAdmin):
    """Admin settings for the Licence model"""
    list_display = (
        'membre',
        'saison',
        'discipline',
        'certificat_valide',
        'paiement_complet',
        'date',
    )
    list_filter = (
        'saison',
        'discipline',
        'certificat_valide',
    )
    inline_type = 'stacked'
    inline_reverse = [ 'membre' ]
    inlines = [ PaiementInline ]

class SaisonAdmin(admin.ModelAdmin):
    """Admin settings for the Saison model"""
    list_display = ('__str__', 'ouvert',)


class TarifAdmin(admin.ModelAdmin):
    """Admin settings for the Tarif model"""
    list_display = ('saison', 'nom', 'prix',)


class PaiementAdmin(admin.ModelAdmin):
    """Admin settings for the Paiement model"""
    list_display = ('date', 'montant', 'type', 'licence',)


admin.site.register(models.Membre, MembreAdmin)
admin.site.register(models.Licence, LicenceAdmin)
admin.site.register(models.Saison, SaisonAdmin)
admin.site.register(models.Tarif, TarifAdmin)
admin.site.register(models.Paiement, PaiementAdmin)
