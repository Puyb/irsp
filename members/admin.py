from django.contrib import admin

from . import models


class MembreAdmin(admin.ModelAdmin):
    """Admin settings for the Membre model"""
    list_display = (
        'user',
        'nom',
        'prenom',
    )


class LicenceAdmin(admin.ModelAdmin):
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


class SaisonAdmin(admin.ModelAdmin):
    """Admin settings for the Saison model"""
    list_display = ('__str__', 'ouvert',)


admin.site.register(models.Membre, MembreAdmin)
admin.site.register(models.Licence, LicenceAdmin)
admin.site.register(models.Saison, SaisonAdmin)
