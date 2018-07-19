from django.contrib import admin

from . import models


class MembreAdmin(admin.ModelAdmin):
    """Admin settings for the Membre model"""


class LicenceAdmin(admin.ModelAdmin):
    """Admin settings for the Licence model"""


class SaisonAdmin(admin.ModelAdmin):
    """Admin settings for the Saison model"""


admin.site.register(models.Membre, MembreAdmin)
admin.site.register(models.Licence, LicenceAdmin)
admin.site.register(models.Saison, SaisonAdmin)
