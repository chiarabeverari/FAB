from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

class AccountAdmin(UserAdmin):
    list_display = ('username', 'is_admin', 'is_staff')
    search_fields = ('username',)
    readonly_fields = ()
    filter_horizontal=()
    list_filter=()
    fieldsets = ()

admin.site.register(MedicalUser, AccountAdmin)
admin.site.register(Fabbisogni)
admin.site.register(SeRep)
admin.site.register(Sta)
admin.site.register(Priorita)
admin.site.register(PI)
admin.site.register(Professioni)
admin.site.register(Gruppi)
admin.site.register(MAIN)
admin.site.register(Specifiche)
admin.site.register(Unicita)
admin.site.register(ConsumabiliMain)
admin.site.register(ConsumabiliFabb)
admin.site.register(Ditta)
admin.site.register(Criteri)
admin.site.register(Allegati)
admin.site.register(Notifiche)
admin.site.register(NuovaRichiesta)
admin.site.register(DocGara)
admin.site.register(DocComm)
admin.site.register(DocTrasp)
admin.site.register(DocColl)
admin.site.register(DocAgg)
admin.site.register(SeRepReg)
admin.site.register(UrgenteRequest) #modello urgente
