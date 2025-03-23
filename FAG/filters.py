import django_filters #pip install django-filters
from django_filters import DateFilter, CharFilter, NumberFilter
from .models import *
from django import forms
from django_filters import FilterSet, ModelChoiceFilter





class MAINFilter(django_filters.FilterSet):
    Progressivo = CharFilter(field_name='Progressivo', lookup_expr='icontains', label='Progressivo', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Apparecchiatura = CharFilter(field_name='Apparecchiatura', lookup_expr='icontains', label='Apparecchiatura', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Qta = NumberFilter(field_name='Qta', lookup_expr='icontains', label='Qta', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Stato = CharFilter(field_name='Stato', lookup_expr='icontains', label='Stato', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Data = DateFilter(field_name='Data', label='Data', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))    
    Sede = CharFilter(field_name='Sede_Reparto', lookup_expr='icontains',label = "Sede_Reparto", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 50}))    
    
    class Meta:
        model = MAIN
        fields = ['Progressivo', 'Qta', 'Apparecchiatura', 'Stato','Data', 'Sede']

class MAINFilterRic(django_filters.FilterSet):
    StatoRic = django_filters.ChoiceFilter(
        field_name='StatoRic__StatoRic',  # Segui la ForeignKey per filtrare sul valore testuale
        choices=StatoRichiesta.choices,  # Usa le scelte già definite
        label="Stato",
        widget=forms.Select(attrs={'class': 'full-width'})  # Dropdown menu
    )
    Tipo= CharFilter(field_name='Tipo', lookup_expr='icontains', label='Tipo', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Progressivo = CharFilter(field_name='Progressivo', lookup_expr='icontains', label='Progressivo', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Apparecchiatura = CharFilter(field_name='Apparecchiatura', lookup_expr='icontains', label='Apparecchiatura', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Qta = NumberFilter(field_name='Qta', lookup_expr='icontains', label='Qta', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Stato = CharFilter(field_name='Stato', lookup_expr='icontains', label='Stato', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Data = DateFilter(field_name='Data', label='Data', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))    
    Sede = CharFilter(field_name='Sede_Reparto', lookup_expr='icontains',label = "Sede_Reparto", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 50}))    
    #StatoRic= CharFilter(field_name='StatoRic', lookup_expr='icontains',label = "StatoRic", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    class Meta:
        model = MAIN
        fields = ['StatoRic','Tipo' ,'Progressivo', 'Qta', 'Apparecchiatura', 'Stato','Data', 'Sede']


class RacFabFilter(django_filters.FilterSet):
    Progressivo = CharFilter(field_name='Progressivo', lookup_expr='icontains', label='Progressivo', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 4}))
    Priorita = CharFilter(field_name='Priorita', lookup_expr='icontains', label='Priorita', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 1}))
    Apparecchiatura = CharFilter(field_name='Apparecchiatura', lookup_expr='icontains', label='Apparecchiatura', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Qta = NumberFilter(field_name='Qta', lookup_expr='icontains', label='Qta', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 1}))
    Sede = CharFilter(field_name='Sede_Reparto', lookup_expr='icontains',label = "Sede", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 25}))    
    Compilatore = CharFilter(field_name='Compilatore', lookup_expr='icontains',label = "Compilatore", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))    
    Costo_Presunto_IVA = CharFilter(field_name='Costo_Presunto_IVA', lookup_expr='icontains',label = "Costo_Presunto_IVA", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 3}))    
    Costo_Presunto_NOIVA = CharFilter(field_name='Costo_Presunto_NOIVA', lookup_expr='icontains',label = "Costo_Presunto_NOIVA", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 3}))    
  
    class Meta:
        model = Fabbisogni
        fields = ['Progressivo', 'Priorita', 'Qta', 'Apparecchiatura', 'Sede' ,'Compilatore', 'Costo_Presunto_NOIVA', 'Costo_Presunto_IVA']

class RacFabFilterRic(django_filters.FilterSet):
    StatoRic = django_filters.ChoiceFilter(
        field_name='StatoRic__StatoRic',  # Segui la ForeignKey per filtrare sul valore testuale
        choices=StatoRichiesta.choices,  # Usa le scelte già definite
        label="Stato",
        widget=forms.Select(attrs={'class': 'full-width'})  # Dropdown menu
    )
    #StatoRic= CharFilter(field_name='StatoRic__StatoRic', lookup_expr='icontains',label = "StatoRic", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Tipo= CharFilter(field_name='Tipo', lookup_expr='icontains', label='Tipo', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Progressivo = CharFilter(field_name='Progressivo', lookup_expr='icontains', label='Progressivo', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 4}))
    Priorita = ModelChoiceFilter(queryset=Priorita.objects.all(), empty_label="", label="Priorità", widget=forms.Select(attrs={'class': 'full-width'}))
    #Priorita = CharFilter(field_name='Priorita', lookup_expr='icontains', label='Priorita', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 1}))
    Apparecchiatura = CharFilter(field_name='Apparecchiatura', lookup_expr='icontains', label='Apparecchiatura', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Qta = NumberFilter(field_name='Qta', lookup_expr='icontains', label='Qta', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 1}))
    Sede = CharFilter(field_name='Sede_Reparto', lookup_expr='icontains',label = "Sede", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 25}))    
    Compilatore = CharFilter(field_name='Compilatore', lookup_expr='icontains',label = "Compilatore", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))    
    Costo_Presunto_IVA = CharFilter(field_name='Costo_Presunto_IVA', lookup_expr='icontains',label = "Costo_Presunto_IVA", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 3}))    
    Costo_Presunto_NOIVA = CharFilter(field_name='Costo_Presunto_NOIVA', lookup_expr='icontains',label = "Costo_Presunto_NOIVA", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 3}))    
  
    class Meta:
        model = Fabbisogni
        fields = ['StatoRic','Tipo', 'Progressivo', 'Priorita', 'Qta', 'Apparecchiatura', 'Sede' ,'Compilatore', 'Costo_Presunto_NOIVA', 'Costo_Presunto_IVA']

class RacUrgFilter(django_filters.FilterSet):
    Progressivo = CharFilter(field_name='Progressivo', lookup_expr='icontains', label='Progressivo', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 4}))
    Priorita = CharFilter(field_name='Priorita', lookup_expr='icontains', label='Priorita', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 1}))
    Apparecchiatura = CharFilter(field_name='Apparecchiatura', lookup_expr='icontains', label='Apparecchiatura', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Qta = NumberFilter(field_name='Qta', lookup_expr='icontains', label='Qta', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 1}))
    Sede = CharFilter(field_name='Sede_Reparto', lookup_expr='icontains',label = "Sede", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 25}))    
    Compilatore = CharFilter(field_name='Compilatore', lookup_expr='icontains',label = "Compilatore", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))    
    Costo_Presunto_IVA = CharFilter(field_name='Costo_Presunto_IVA', lookup_expr='icontains',label = "Costo_Presunto_IVA", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 3}))    
    Costo_Presunto_NOIVA = CharFilter(field_name='Costo_Presunto_NOIVA', lookup_expr='icontains',label = "Costo_Presunto_NOIVA", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 3}))    
  
    class Meta:
        model = UrgenteRequest
        fields = ['Progressivo', 'Priorita', 'Qta', 'Apparecchiatura', 'Sede' ,'Compilatore', 'Costo_Presunto_NOIVA', 'Costo_Presunto_IVA']

class RacUrgFilterRic(django_filters.FilterSet):
    StatoRic = django_filters.ChoiceFilter(
        field_name='StatoRic__StatoRic',  # Segui la ForeignKey per filtrare sul valore testuale
        choices=StatoRichiesta.choices,  # Usa le scelte già definite
        label="Stato",
        widget=forms.Select(attrs={'class': 'full-width'})  # Dropdown menu
    )
    #StatoRic= CharFilter(field_name='StatoRic__StatoRic', lookup_expr='icontains',label = "StatoRic", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Tipo= CharFilter(field_name='Tipo', lookup_expr='icontains', label='Tipo', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Progressivo = CharFilter(field_name='Progressivo', lookup_expr='icontains', label='Progressivo', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 4}))
    Priorita = ModelChoiceFilter(queryset=Priorita.objects.all(), empty_label="", label="Priorità", widget=forms.Select(attrs={'class': 'full-width'}))
    #Priorita = CharFilter(field_name='Priorita', lookup_expr='icontains', label='Priorita', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 1}))
    Apparecchiatura = CharFilter(field_name='Apparecchiatura', lookup_expr='icontains', label='Apparecchiatura', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Qta = NumberFilter(field_name='Qta', lookup_expr='icontains', label='Qta', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 1}))
    Sede = CharFilter(field_name='Sede_Reparto', lookup_expr='icontains',label = "Sede", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 25}))    
    Compilatore = CharFilter(field_name='Compilatore', lookup_expr='icontains',label = "Compilatore", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))    
    Costo_Presunto_IVA = CharFilter(field_name='Costo_Presunto_IVA', lookup_expr='icontains',label = "Costo_Presunto_IVA", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 3}))    
    Costo_Presunto_NOIVA = CharFilter(field_name='Costo_Presunto_NOIVA', lookup_expr='icontains',label = "Costo_Presunto_NOIVA", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 3}))    
  
    class Meta:
        model = UrgenteRequest
        fields = ['StatoRic','Tipo', 'Progressivo', 'Priorita', 'Qta', 'Apparecchiatura', 'Sede' ,'Compilatore', 'Costo_Presunto_NOIVA', 'Costo_Presunto_IVA']

class PianoInvFilter(django_filters.FilterSet):
    ID_PianoInvestimenti = CharFilter(field_name='ID_PianoInvestimenti', lookup_expr='icontains', label='ID_Pianoinvestimenti', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Descrizione = CharFilter(field_name='Descrizione', lookup_expr='icontains', label='Descrizione', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Priorita = NumberFilter(field_name='Priorita', lookup_expr='icontains', label='Priorita', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 1}))
    Costo_Presunto_IVA = NumberFilter(field_name='Costo_Presunto_IVA', lookup_expr='icontains',label = "Costo_Presunto_IVA", widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))    
    Stato = CharFilter(field_name='Stato', lookup_expr='icontains', label='Stato', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Speso = CharFilter(field_name='Speso', lookup_expr='icontains', label='Speso', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 4}))
    
    class Meta:
        model = PI
        fields = ['ID_PianoInvestimenti', 'Descrizione', 'Priorita', 'Stato', 'Costo_Presunto_IVA', 'Speso']

class SeRepFilter(django_filters.FilterSet):
    Sede = CharFilter(field_name = 'Sede', lookup_expr = 'icontains', label = 'Sede', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Reparto = CharFilter(field_name = 'Reparto', lookup_expr = 'icontains', label = 'Reparto', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Sub_Reparto = CharFilter(field_name = 'Sub_Reparto', lookup_expr = 'icontains', label = 'Sub_Reparto', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    CDC = CharFilter(field_name = 'CDC', lookup_expr = 'icontains', label = 'CDC', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))

    class Meta:
        model = SeRep
        fields = ['Sede', 'Reparto', 'Sub_Reparto', 'CDC']

class SeRepRegFilter(django_filters.FilterSet):
    Sede = CharFilter(field_name = 'Sede', lookup_expr = 'icontains', label = 'Sede', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
    Reparto = CharFilter(field_name = 'Reparto', lookup_expr = 'icontains', label = 'Reparto', widget=forms.TextInput(attrs={'class': 'full-width', 'size': 8}))
   
    class Meta:
        model = SeRepReg
        fields = ['Sede', 'Reparto']


# class RichiestaFilter(django_filters.FilterSet):
#     Progressivo = CharFilter(field_name='Progressivo', lookup_expr='icontains', label="Progressivo")
#     Sede_Reparto = CharFilter(field_name='Sede_Reparto', lookup_expr='icontains', label="Sede/Reparto")
#     Apparecchiatura = CharFilter(field_name='Apparecchiatura', lookup_expr='icontains', label="Apparecchiatura")
#     Compilatore = CharFilter(field_name='Compilatore__username', lookup_expr='icontains', label="Compilatore")
#     ID_PianoInvestimenti = CharFilter(field_name='ID_PianoInvestimenti', lookup_expr='icontains', label="ID Inv.")
#     NoteGen = CharFilter(field_name='NoteGen', lookup_expr='icontains', label="Note")

#     class Meta:
#         model = UrgenteRequest  # Puoi anche usare MAIN, dipende da quale modello vuoi filtrare
#         fields = ['Progressivo', 'Sede_Reparto', 'Apparecchiatura', 'Compilatore', 'ID_PianoInvestimenti', 'NoteGen']



# class RichiestaFilter(django_filters.FilterSet):
#     query = django_filters.CharFilter(method='filtro_personalizzato', label="Cerca in tutti i campi")
    
#     Progressivo = django_filters.CharFilter(lookup_expr='icontains', label="Progressivo")
#     Sede_Reparto = django_filters.CharFilter(lookup_expr='icontains', label="Sede/Reparto")
#     Apparecchiatura = django_filters.CharFilter(lookup_expr='icontains', label="Apparecchiatura")
#     Qta = django_filters.NumberFilter(lookup_expr='exact', label="Q.tà")
#     Priorita = django_filters.CharFilter(lookup_expr='icontains', label="Priorità")
#     Costo_Presunto_NOIVA = django_filters.NumberFilter(lookup_expr='exact', label="Costo NO IVA")
#     Costo_Presunto_IVA = django_filters.NumberFilter(lookup_expr='exact', label="Costo IVA")
#     Compilatore = django_filters.CharFilter(lookup_expr='icontains', label="Compilatore")
#     ID_PianoInvestimenti = django_filters.CharFilter(lookup_expr='icontains', label="ID Inv.")
#     NoteGen = django_filters.CharFilter(lookup_expr='icontains', label="Note")

#     class Meta:
#         model = UrgenteRequest  # Base model, ma filtra anche su MAIN
#         fields = ['Progressivo', 'Sede_Reparto', 'Apparecchiatura', 'Qta', 'Priorita', 
#                   'Costo_Presunto_NOIVA', 'Costo_Presunto_IVA', 'Compilatore', 
#                   'ID_PianoInvestimenti', 'NoteGen']

#     def filtro_personalizzato(self, queryset, name, value):
#         """
#         Permette la ricerca generale in tutti i campi.
#         """
#         urgenti = UrgenteRequest.objects.filter(
#             Q(Progressivo__icontains=value) |
#             Q(Sede_Reparto__icontains=value) |
#             Q(Apparecchiatura__icontains=value) |
#             Q(Compilatore__username__icontains=value) |
#             Q(ID_PianoInvestimenti__icontains=value) |
#             Q(NoteGen__icontains=value)
#         ).annotate(tipo_richiesta="Urgente")

#         programmate = MAIN.objects.filter(
#             Q(Progressivo__icontains=value) |
#             Q(Sede_Reparto__icontains=value) |
#             Q(Apparecchiatura__icontains=value) |
#             Q(Compilatore__username__icontains=value) |
#             Q(ID_PianoInvestimenti__icontains=value) |
#             Q(NoteGen__icontains=value)
#         ).annotate(tipo_richiesta="Programmato")

#         return urgenti.union(programmate)
