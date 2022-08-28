from django.contrib import admin
from django.utils.safestring import mark_safe
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
    search_fields = (
        'membre__nom',
        'membre__prenom',
        'membre__user__email',
        'saison__annee',
        'discipline',
    )
    list_display = (
        'membre',
        'nom',
        'prenom',
        'mail',
        'saison',
        'discipline',
        'ffrs',
        'paye',
        'date',
    )
    list_filter = (
        'saison',
        'discipline',
        'ffrs',
    )
    inline_type = 'stacked'
    inline_reverse = [ 'membre' ]
    inlines = [ PaiementInline ]

    def nom(self, obj):
        return obj.membre.nom

    def prenom(self, obj):
        return obj.membre.prenom

    def mail(self, obj):
        return mark_safe('<a href="mailto:%s">%s</a>' % (obj.membre.user.email, obj.membre.user.email))

    def paye(self, obj):
        if obj.paiement_complet():
            return mark_safe('<img src="/site_media/static/admin/img/icon-yes.svg" />')
        return mark_safe('<img src="/site_media/static/admin/img/icon-no.svg" />')

class SaisonAdmin(admin.ModelAdmin):
    """Admin settings for the Saison model"""
    list_display = ('__str__', 'ouvert',)


class TarifAdmin(admin.ModelAdmin):
    """Admin settings for the Tarif model"""
    list_display = ('saison', 'nom', 'prix',)


class PaiementAdmin(admin.ModelAdmin):
    """Admin settings for the Paiement model"""
    list_display = ('date', 'montant', 'description', 'type', 'licence',)


admin.site.register(models.Membre, MembreAdmin)
admin.site.register(models.Licence, LicenceAdmin)
admin.site.register(models.Saison, SaisonAdmin)
admin.site.register(models.Tarif, TarifAdmin)
admin.site.register(models.Paiement, PaiementAdmin)
