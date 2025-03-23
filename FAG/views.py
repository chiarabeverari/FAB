from datetime import datetime, date
#from tkinter import E, N
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from pyparsing import unicode_set
from .models import *
from .forms import *
from django.db.models import Q, Value, CharField
from .daPIaRichiesta import crea, crea_cons
from .settings import BASE_DIR
from django.core.files.base import ContentFile
from .filters import *
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, Http404, JsonResponse
from django.utils import timezone
from django.conf import settings
from io import BytesIO
from django.template.loader import get_template
import csv
from itertools import chain
import PyPDF2
import io
from PyPDF2 import PdfReader #PdfFileReader->PdfReader
import pandas as pd
import xlwt #pip install xlwt
import os
from pprint import pprint
from .crea_da_pdf import *
from .makenew import *
from django.contrib.auth import authenticate, login, logout
from .service import *

def register(request, *args, **kwargs):
    user = request.user
    med = Gruppi.objects.filter(Descrizione = 'Medico')
    data = {'Gruppo': med}
    if user.is_authenticated:
        return HttpResponse(f"You are already authenticated as {user.USERNAME}.")
    form = RegistrationForm(initial = data)
    context = {'form': form}

    if request.POST:
        form = RegistrationForm(request.POST, initial = data)
        if form.is_valid():
            account = form.save()
            gr = Gruppi.objects.get(Numero = 1)
            account.Gruppo = gr
            account.save()
            login(request, account)
            destination = kwargs.get("next")
            if destination:
                return redirect(destination)
            return redirect('/')
            
        else:
            print(form.errors)
            context['form'] = form
    
    return render(request, 'registration/register.html', context)

def mylogin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password = password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            print('non va')
            return redirect('/mylogin/')

    else:
        return render(request, 'registration/login.html', {})

@login_required
def index(request):
    crea_nuovo()
    crea_gruppi()
    var1 = 1
    var2 = 2
    var3 = 3
    gare = 'Gare'
    altro = 'Altro'
    nots = Notifiche.objects.filter(User=request.user)
    nots_nonlette=nots.filter(Letto=False)
    counter=0
    for nota in nots_nonlette:
        counter+=1
    u = request.user.id
    print(request.user)
    per = MedicalUser.objects.get(id = u)
    try:
        var = per.Gruppo.Numero
    except:
        if request.user.is_superuser:
            try:
                gruppo = Gruppi.objects.get(Descrizione='ADMIN')
                per.Gruppo = gruppo
                per.save()
                var = per.Gruppo.Numero
            except:
                var = 0
        else:
            var = 0
    context = {'var': str(var), 'counter': counter, 'Gare': gare, 'altro': altro, 'var1':var1, 'var2': var2, 'var3':var3}
    return render(request, 'index.html', context)
    

@login_required   
def home(request, var):
    gruppo = request.user.Gruppo
    if var == 'Gare':
        st = Sta.objects.filter(Numero__gte = 3)
        var3 = 'Gare'
        var4 = None
    else:
        st = Sta.objects.filter(Numero__lte = 2)
        var3 = 'altro'
        var4 = 2
    query = Q()
    for s in st:
        query = query | Q(Stato = s)
    tab = MAIN.objects.filter(query)

    if var == 'Gare':
        if (not gruppo.FaVeTu) and gruppo.FaVePr:
            tab = tab.filter(Compilatore = request.user)

        elif (not gruppo.FaVeTu) and (not gruppo.FaVePr):
            return HttpResponse("<html> Non sei autorizztato. <a href={% url 'home' 'Gare'%}>Torna Indietro</a></html>" )
    else:
        if (not gruppo.SpVeTu) and gruppo.SpVePr:
            tab = tab.filter(Compilatore = request.user)
        elif (not gruppo.SpVeTu) and (not gruppo.SpVePr):
            return HttpResponse("<html> Non sei autorizztato. <a href={% url 'home' 'Gare'%}>Torna Indietro</a></html>")
    var2 = 1
    
    tab = tab.order_by('Progressivo')
    specs =[]
    for a in tab:
        sp = Specifiche.objects.filter(ID_rich = a)
        specs += [len(sp)] 
      
    var = 3
    tablfilter = MAINFilter(request.GET, queryset=tab)
    tab  = tablfilter.qs

    

    context = {
        'insieme': zip(tab,specs),
        'tabFilter':tablfilter,
        'var': var,
        'var2': var2,
        'var3' : var3,
        'var4': var4,
        'opt': 2,
    }

    if gruppo.GaFlu:
        b = True
        context = context | {'b': b}
    return render(request, 'home.html', context)

def seleziona_tipo(request):
    print('funzione seleziona_tipo chiamata')
    if request.method == 'POST':
        tipo = request.POST.get('tipo')  # Ottieni il tipo selezionato (urgente o programmato)
        return redirect('nuova', tipo=tipo)  # Passa il tipo alla prossima vista

    return render(request, 'seleziona_tipo.html')  

def aggiungi_fabbisogno_programmato(request):
    print('agg_fab_programmato ok')
    return render(request, 'nuova.html')

def aggiungi_fabbisogno_urgente(request):
    print('agg_fab_urgente ok')
    return render(request, 'aggiungi_fabbisogno_urgente.html')

@login_required
def raccoltafabbisogni(request):
    var2 = 2 # per visualizzare correttamente
    var3 = 1 # per gestire le nuove richieste (differenza tra fabbisogni e gare)
  
    gruppo = request.user.Gruppo
    if gruppo.FaVeTu:
        tab = Fabbisogni.objects.all()
        urgenti=UrgenteRequest.objects.all()

    elif gruppo.FaVePr:
        tab = Fabbisogni.objects.filter(Compilatore = request.user)
        urgenti=UrgenteRequest.objects.filter(Compilatore = request.user)
    else:
        return HttpResponse('Non sei autorizzato')
    avviati = []
    tab = tab.order_by('Progressivo')
    for t in tab:
        try:
            pi = PI.objects.get(ID_PianoInvestimenti = t.ID_PianoInvestimenti)
            MAIN.objects.get(ID_PianoInvestimenti = pi)
            print('ok')
            avviati += [True]
        except:
            avviati += [False]
    
    print(avviati)
    var = 1 
    tablfilter = RacFabFilter(request.GET, queryset=tab)
    tab  = tablfilter.qs

    urgfilter= RacUrgFilter(request.GET, queryset=urgenti)
    urgenti= urgfilter.qs


    context = {
        'insieme': zip(tab, avviati),
        'tabFilter':tablfilter,
        'urgenti': urgenti,
        'urgFilter': urgfilter,
        'var': var,
        'var2':var2,
        'var4': var3,
        'opt': '1'

    }
    return render(request, 'raccoltafabbisogni.html', context)

@login_required
def attivita(request):
    var2 = 2 # per visualizzare correttamente
    var3 = 1 # per gestire le nuove richieste (differenza tra fabbisogni e gare)

    ruolo_scelto = request.GET.get("ruolo")  # L'admin sceglie un ruolo dal menu a tendina

    print("Superuser:", request.user.is_superuser)
    print("Ruolo scelto:", ruolo_scelto)

    # Ruoli che può selezionare l'admin
    admin_roles = ["PRIMARIO", "DIR. MEDICA", "ING. CLINICA"] if request.user.is_superuser else None

    if request.user.is_superuser:
        opzioni_stato = get_opzioni_stato(request.user, ruolo_scelto)  # Usa il ruolo scelto
        admin_roles = ["PRIMARIO", "DIR. MEDICA", "ING. CLINICA"]  # Ruoli disponibili per il superuser
    else:
        opzioni_stato = get_opzioni_stato(request.user)
        admin_roles=None #non è superuser
  # Se l'admin ha scelto un ruolo, lo usiamo per determinare cosa può vedere
    if ruolo_scelto:
        if ruolo_scelto == "PRIMARIO":
            stato_filtro = StatoRichiesta.BOZZA
        elif ruolo_scelto == "DIR. MEDICA":
            stato_filtro = StatoRichiesta.DEFINITIVA
        elif ruolo_scelto == "ING. CLINICA":
            stato_filtro = StatoRichiesta.SPEDITA
        else:
            return HttpResponse('Ruolo non valido')
    else:
        # Se non è admin, usiamo il suo gruppo per determinare cosa può vedere
        gruppo = request.user.Gruppo
   
        if gruppo.FaVeTu:
            tab = Fabbisogni.objects.all()
            urgenti=UrgenteRequest.objects.all()

        elif gruppo.FaVePr: #credo che questa non serve 
            tab = Fabbisogni.objects.filter(Compilatore = request.user)
            urgenti=UrgenteRequest.objects.filter(Compilatore = request.user)
    
        elif gruppo.FaVeDirMed:  # Aggiungi una condizione per Dir. Medica
           stato_filtro= StatoRichiesta.DEFINITIVA
    
        elif gruppo.FaVeIngClin:  # Aggiungi una condizione per Ing. Clinico
            stato_filtro= StatoRichiesta.SPEDITA

        else:
            return HttpResponse('Non sei autorizzato')
        
    # Se è stato scelto un filtro per lo stato, applicarlo
    if "stato_filtro" in locals():
        tab = Fabbisogni.objects.filter(StatoRic__StatoRic=stato_filtro)
        urgenti = UrgenteRequest.objects.filter(StatoRic__StatoRic=stato_filtro)
    
    avviati = []
    tab = tab.order_by('Progressivo')
    for t in tab:
        try:
            pi = PI.objects.get(ID_PianoInvestimenti = t.ID_PianoInvestimenti)
            MAIN.objects.get(ID_PianoInvestimenti = pi)
            print('ok')
            avviati += [True]
        except:
            avviati += [False]
    
    print(avviati)
    var = 1 
    tablfilter = RacFabFilter(request.GET, queryset=tab)
    tab  = tablfilter.qs

    urgfilter= RacUrgFilter(request.GET, queryset=urgenti)
    urgenti= urgfilter.qs


    context = {
        'insieme': zip(tab, avviati),
        'tabFilter':tablfilter,
        'urgenti': urgenti,
        'urgFilter': urgfilter,
        'var': var,
        'var2':var2,
        'var4': var3,
        'opt': '1', 
        'admin_roles': admin_roles,
        'ruolo_scelto': ruolo_scelto

    }
    return render(request, 'attivita.html', context)


    
@login_required
def pianodiinvestimenti(request):
    gruppo = request.user.Gruppo
    if not(gruppo.PIVeTu) and gruppo.PIVePr:
        #fs = Fabbisogni.objects.filter(Compilatore = request.user)
        fs = Fabbisogni.objects.filter(Compilatore=request.user, StatoRic__StatoRic=StatoRichiesta.APPROVATA)
        print(fs)
        query = Q()
        for f in fs:
            try:
                id_piano = f.ID_PianoInvestimenti
                query = query | Q(ID_PianoInvestimenti = id_piano)
            except:
                pass
        tab = PI.objects.filter(query)
    elif gruppo.PIVeTu:
        tab = PI.objects.all()
    else:
        return HttpResponse('Non sei autorizzato.')
    tot = 0
    
    var2 = 3
    var = 1 

    tablfilter = PianoInvFilter(request.GET, queryset=tab)
    tab  = tablfilter.qs
    lista1 = []
    lista2 = []
    lista3 = []
    lista4 = []
    lista5 = []
    for t in tab:
        if t.Costo_Presunto_IVA is not None:
            tot += t.Costo_Presunto_IVA
        fs = Fabbisogni.objects.filter(ID_PianoInvestimenti = t.ID_PianoInvestimenti)
        if t.is_ext:
            rs = MAIN.objects.filter(ID_PianoInvestimenti = t)
            subli = []
            for r in rs:
                subli += [f'Stato di {r} = {r.Stato}'] 
            lista5 += [subli]
            
        else:
            rs = []
            try:
                g = MAIN.objects.get(ID_PianoInvestimenti = t)
                lista5 += [f'\n {g}']
            except:
                lista5 += ['']
        sublista1 = []
        sublista2 = []
        for f in fs:
            sublista1 += [str(f.Sede_Reparto) + '\n Q.tà: ' + str(f.Qta)]
            sublista2 += [f.Priorita]
        lista1 += [sublista1]
        lista2 += [sublista2]
        sublista1 = []
        sublista2 = []
        for r in rs:
            sublista1 += [f'{r.Progressivo} => n° {r.Qta} di {r.Apparecchiatura}, {r.Sede_Reparto}']
            sublista2 += [str(r.Costo_Presunto_IVA)]
        lista3 += [sublista1]
        lista4 += [sublista2]

    print(len(lista1))
    print(len(lista5))
    form = PIForm()
    TabFormSet = modelformset_factory(model = PI, fields=('ID_PianoInvestimenti', 'Priorita', 'Speso', 'FabbRel'), form = FabbPIForm, extra=0)
    formset = TabFormSet(queryset = tab)
    if request.method == 'POST':
        if 'Modifica' in request.POST:
            if not gruppo.PIMod:
                return HttpResponse('Non sei autorizzato')
            formset = TabFormSet(request.POST, queryset = tab)
            control = False
            if formset.is_valid():
                for form in formset:
                    pi = form.save()
                    sum1 = 0
                    sum2 = 0
                    sum3 = 0
                    if pi.Stato == 'Inserito Nel Piano' and not pi.is_ext:
                        fs_old = Fabbisogni.objects.filter(ID_PianoInvestimenti = pi.ID_PianoInvestimenti,StatoRic__StatoRic=StatoRichiesta.APPROVATA)
                        for f in fs_old: #resetta fabbisogni
                            f.ID_PianoInvestimenti = None
                            f.save()
                            control = False
                        # resetta proprietà pi
                      
                        pi.Descrizione = None
                        pi.Priorita = None
                        pi.Costo_Presunto_NOIVA = 0
                        pi.Costo_Presunto_IVA = 0
                        pi.save()
                        for p in pi.FabbRel.values('Progressivo'):
                            print(p['Progressivo'])
                            f = Fabbisogni.objects.get(Progressivo = p['Progressivo'])
                            f.ID_PianoInvestimenti = pi.ID_PianoInvestimenti
                            f.save()
                            control = True
                            if f.Costo_Presunto_NOIVA != None:
                                sum1 += f.Costo_Presunto_NOIVA
                            if f.Costo_Presunto_IVA != None:
                                sum2 += f.Costo_Presunto_IVA
                            sum3 += f.Qta
                        
                        pi.Costo_Presunto_NOIVA = sum1
                        pi.Costo_Presunto_IVA = sum2
                        if control:
                            pi.Descrizione = f'n° {sum3} di {f.Apparecchiatura}'
                            pr = Priorita.objects.get(Numero = f.Priorita.Numero)
                            pi.Priorita = pr
                        pi.save()
                    if pi.Speso == pi.Costo_Presunto_IVA:
                        pi.is_end = True
                        pi.save()
                return redirect('/pianodiinvestimenti/')
            else:
                print(formset.errors)

        if 'Nuovo' in request.POST:
            form = PIForm(request.POST)
            if form.is_valid():
                anno_previsto = form.cleaned_data['Anno_Previsto']

                # Cerchiamo un PI già esistente per quell'anno
                pi = PI.objects.filter(Anno_Previsto=anno_previsto).first()
                if not pi:
                     # Se non esiste, creiamo un nuovo PI
                    pi = form.save()
                    current_year_atts = PI.objects.filter(Anno_Previsto=anno_previsto)
                    k = current_year_atts.count()
                    pi.ID_PianoInvestimenti = str(k) + '-' + str(anno_previsto)
                    if pi.Descrizione is not None:
                        pi.is_ext = True
                    pi.save()

                # Assegniamo i Fabbisogni approvati a questo PI
                fab_approvati = Fabbisogni.objects.filter(Anno_Previsto=anno_previsto, StatoRic__StatoRic=StatoRichiesta.APPROVATA)
                for f in fab_approvati:
                    f.ID_PianoInvestimenti = pi.ID_PianoInvestimenti
                    f.save()

                return redirect('/pianodiinvestimenti/')

            '''
            form = PIForm(request.POST)
            if form.is_valid():
                i = form.save()
                current_year_atts = PI.objects.filter(Anno_Previsto = i.Anno_Previsto)
                k = 0
                for year in current_year_atts:
                    k += 1
                i.ID_PianoInvestimenti = str(k)+'-'+str(i.Anno_Previsto)
                if i.Descrizione != None:
                    i.is_ext = True
                i.save()
                return redirect('/pianodiinvestimenti/')
            '''
                
    context = {
        'insieme': zip(tab, formset, lista1, lista2, lista3, lista4, lista5),
        'formset': formset,
        'tabFilter':tablfilter,
        'var': var,
        'var2': var2,
        'var3': 4,
        'tot': tot,
    }
    if gruppo.PIIns:
        context = context | {'formpi': form}
    return render(request, 'pianodiinvestimenti.html', context)

@login_required
def attachements(request, pk, var=None):
    
    att = MAIN.objects.get(id=pk)
    gruppo = request.user.Gruppo
    if not(gruppo.SpMoTu) and (gruppo.SpMoPr):
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif (not gruppo.SpMoTu) and (not gruppo.SpMoPr):
        return HttpResponse('Non sei autorizzato')
    init = {'ID_rich': pk}
    form = AllegatiForm(initial=init)
    if Allegati.objects.filter(ID_rich=pk).exists():
        alls=Allegati.objects.filter(ID_rich=pk)
        context={
        'att': att,
        'form': form,
        'alls': alls,
        'var':var, 
        'altro': 'altro'
        }   
    else:
         context={
        'form': form,
        'att': att,
        'var':var,
        'altro': 'altro'
        }  

    if request.method=='POST':
        form = AllegatiForm(request.POST, request.FILES, initial=init)
        if form.is_valid():
            form.save()
        return redirect(f'/attachements/{pk}/{var}/')
 
    return render(request, 'attachements.html',context) 



@login_required
def aggiorna(request, pk, var):
    if var == '1':
        gruppo = request.user.Gruppo
        if not (gruppo.FaMoTu or gruppo.FaMoPr):
            return HttpResponse('Non sei autorizzato')
        prs = Priorita.objects.all()
        var = 2
        opt = '1'
        att = Fabbisogni.objects.get(id=pk)
        form = AttForm1(instance=att)
        if request.method == 'POST':
            form = AttForm1(request.POST, instance=att)
            if form.is_valid():
                main = form.save()
                main.costo_presuntoNOIVA()
                main.save()
                return redirect(f'/new_5/{att.id}/{var}/')
            else:
                print(form.errors)
    elif var == '2' or var == '3':
        opt ='2'
        gruppo = request.user.Gruppo
        if not (gruppo.FaMoTu or gruppo.FaMoPr):
            return HttpResponse('Non sei autorizzato')
        prs = Priorita.objects.all()
        var = 3
        att = MAIN.objects.get(id=pk)
        form = AttForm3(instance=att)
        if request.method == 'POST':
            form = AttForm3(request.POST, instance=att)
            if form.is_valid():
                main = form.save()
                main.costo_presuntoNOIVA()
                main.save()
                return redirect(f'/attachements/{att.id}/{var}/')
            else:
                print(form.errors)
    context={'form': form,
    'var':var, 'prs':prs, 'opt': opt, 'pk': pk, 'altro': 'altro'}
    return render(request, 'aggiorna.html', context )

def aggiornaurg(request, pk):

    gruppo = request.user.Gruppo
    if not (gruppo.FaMoTu or gruppo.FaMoPr):
        return HttpResponse('Non sei autorizzato')
    prs = Priorita.objects.all()

    att = UrgenteRequest.objects.get(id=pk)
    form = UrgenteRequestForm(instance=att)
    if request.method == 'POST':
        form = UrgenteRequestForm(request.POST, instance=att)
        if form.is_valid():
            urg= form.save()
            urg.costo_presuntoNOIVA()
            urg.save()
            return redirect(f'/new_urg_5/{att.id}')
        else:
            print(form.errors)
# return redirect(f'/attachements/{att.id}') vedere dove voler indirizzare la pagina
    context={'form': form, 'prs':prs,'pk': pk, 'altro': 'altro'}
    return render(request, 'aggiornaurg.html', context )

@login_required
def aggiornadata(request):
    
    atts = MAIN.objects.all()
    DataFormSet = modelformset_factory(MAIN, fields = ('Data',  'Data1', 'Data2', 'Data3', 'Data4', 'Data5', 'Data6', 'Data7', 'Data8', 'Data9'), form = DateForm, extra=0)
    formset = DataFormSet(queryset = atts)
   
    if request.method == 'POST':
        formset = DataFormSet (request.POST, queryset = atts)
        if formset.is_valid():
            i=0
            for form in formset:
                att = form.save()
                att.def_stato()
                att.save()
                i+=1
            return redirect('aggiornadata')
    
    context = {'formset': formset, 'insieme': zip(atts, formset)}

    return render(request, 'aggiornadata.html', context)



@login_required
def valutazione (request, pk):
    att = MAIN.objects.get(id=pk)
    altro = 'altro'
    specs = Specifiche.objects.filter(ID_rich = pk)
   
    SpecificheFormSetCli = modelformset_factory(Specifiche, fields=('ValSpecCli', 'ValSpecCliNota',), form=ValSpecFormCli, extra=0)
    SpecificheFormSetTec = modelformset_factory(Specifiche, fields=('ValSpecTec', 'ValSpecTecNota',), form=ValSpecFormTec, extra=0)
    UnicitaFormSetCli = modelformset_factory(Unicita, fields=('ValCli',), form=ValUnFormCli, extra=0)
    UnicitaFormSetTec = modelformset_factory(Unicita, fields=('ValTec',), form=ValUnFormTec, extra=0)
    SpecFormSetCliTec = modelformset_factory(Specifiche, fields=('ValSpecCli', 'ValSpecCliNota', 'ValSpecTec', 'ValSpecTecNota'), form=ValSpecFormCliTec, extra=0)
    UnicitaFormSetCliTec = modelformset_factory(Unicita, fields = ('ValCli', 'ValTec'), form = ValUnFormTecCli, extra = 0 )
    
    lista =[]
    for spec in specs:
        print(spec)
        lista+=[spec.id]
    uns = Unicita.objects.filter(rifext__in = lista)

    context = {'att': att,
    }

    gruppo = request.user.Gruppo
    if not (gruppo.GaValTec or gruppo.GaValCli):
        altro = 'altro'
        return HttpResponse(f"Non hai l'autorizzazione per eseguire questa operazione. <a href='/home/{altro}'>Torna indietro </a>")


    if gruppo.GaValCli and gruppo.GaValTec:
        print('entrato 1')
        b = 'ALL'
        formsetsp = SpecFormSetCliTec(queryset=specs)
        if uns.exists():
            formsetun = UnicitaFormSetCliTec(queryset=uns)
        else:
            formsetun = UnicitaFormSetCliTec()
        form = ValMotForm(instance = att)
        if att.ValMot != None:
            c = 2
            control = True
            for spec in specs:
                if spec.ValSpecTec == None or spec.ValSpecCli == None:
                    control = False
            if control == True:
                c = 3
        else:
            c = 1
        if request.method == 'POST':
            if 'Motivi' in request.POST:
                form = ValMotForm(request.POST, instance = att)
                
                if form.is_valid():
                    form.save()
                    att.ValData = timezone.now()
                    att.ValUtente = request.user
                    att.save()
                    return redirect(f'/valutazione/{pk}/')
            if 'Specifiche' in request.POST:
                formsetsp = SpecFormSetCliTec(request.POST, queryset = specs)
                if formsetsp.is_valid():
                    for formsp in formsetsp:
                        s = formsp.save()
                        s.ValCliUtente = request.user
                        s.ValCliData = timezone.now()
                        s.ValTecUtente = request.user
                        s.ValTecData = timezone.now()
                        s.save()
                    
                    return redirect(f'/valutazione/{pk}/')    
                else:
                    print(formsetsp.errors)
                    print(formsetsp.non_form_errors)

            if 'Unicita' in request.POST:
                formsetun = UnicitaFormSetCliTec(request.POST, queryset = uns)
                if formsetun.is_valid():
                    for formun in formsetun:
                        u = formun.save()
                        u.ValCliUtente = request.user
                        u.ValCliData = timezone.now()
                        u.ValTecUtente = request.user
                        u.ValTecData = timezone.now()
                        u.save()
                    
                else:
                    print(formsetun.errors)

        context = context | {'b':b, 'form': form, 'formsetsp':formsetsp, 'formsetun': formsetun, 'insiemeun': zip(uns, formsetun), 'insiemesp': zip(specs, formsetsp), 'altro': altro, 'c':c}
        co = 0
    else:
        if gruppo.GaValCli:
            print('entrato 2')
            b = 'DAA'
            print(att.ValMot)
            c = 0
            if att.ValMot != None:
                print('ciao')
                c = 2
                control = True
                for spec in specs:
                    if spec.ValSpecCli == None:
                        control = False
                if control == True:
                    c = 3
                else:
                    c = 2

            formsetsp = SpecificheFormSetCli(queryset = specs)
            
            if uns.exists():
                formsetun = UnicitaFormSetCli(queryset=uns)
            else:
                formsetun = UnicitaFormSetCli()
            form = ValMotForm(instance=att)

            if request.method == 'POST':

                if 'Motivi' in request.POST:
                    form = ValMotForm(request.POST, instance=att)
                    if form.is_valid():
                        form.save()
                        att.ValData = timezone.now()
                        att.ValUtente = request.user
                        att.save()
                        return redirect(f'/valutazione/{pk}/')
                
                if 'Specifiche' in request.POST:
                    formsetsp = SpecificheFormSetCli(request.POST, queryset = specs)
                    if formsetsp.is_valid():
                        for formsp in formsetsp:
                            s = formsp.save()
                            s.ValCliUtente = request.user
                            s.ValCliData = timezone.now()
                            s.save()
                        
                        return redirect(f'/valutazione/{pk}/')    
                    else:
                        print(formsetsp.errors)
                        print(formsetsp.non_form_errors)

                
                if 'Unicita' in request.POST:
                    formsetun = UnicitaFormSetCli(request.POST, queryset = uns)
                    if formsetun.is_valid():
                        for formun in formsetun:
                            u = formun.save()
                            u.ValCliUtente = request.user
                            u.ValCliData = timezone.now()
                            u.save()
                        
                    else:
                        print(formsetun.errors)
                    
            context = context | { 'b': b, 'form': form, 'formsetsp':formsetsp, 'formsetun': formsetun, 'insiemeun': zip(uns, formsetun), 'insiemesp': zip(specs, formsetsp), 'altro': altro, 'c':c}
            co = 0
        if gruppo.GaValTec:
            print('entrato 3')
            b = 'UIC'
            
            formsettecsp = SpecificheFormSetTec(queryset=specs)
            
            control = True
            for spec in specs:
                if spec.ValSpecCli == None:
                    control = False
            if control == True:
                c = 3
            else:
                c = 2
            
            if uns.exists():
                formsettecun = UnicitaFormSetTec(queryset=uns)
            else:
                formsettecun = UnicitaFormSetTec()
            
            if request.method == 'POST':
                if 'Specifiche' in request.POST:
                    formsettecsp = SpecificheFormSetTec(request.POST, queryset = specs)
                    if formsettecsp.is_valid():
                        for formsp in formsettecsp:
                            s = formsp.save()
                            s.ValTecUtente = request.user
                            s.ValTecData = timezone.now()
                            s.save()
                        return redirect(f'/valutazione/{pk}/')    
                    else:
                        print(formsettecsp.errors)
                        print(formsettecsp.non_form_errors)

                
                if 'Unicita' in request.POST:
                    formsettecun = UnicitaFormSetTec(request.POST, queryset = uns)
                    if formsettecun.is_valid():
                        for formun in formsettecun:
                            u=formun.save()
                            
                            u.ValTecUtente = request.user
                            u.ValTecData=timezone.now()
                            u.save()
                        
                    else:
                        print(formsettecun.errors)
                    
            context = context | {'b': b, 'c': c, 'formsetsp':formsettecsp, 'formsetun': formsettecun, 'insiemeun': zip(uns, formsettecun), 'insiemesp': zip(specs, formsettecsp), 'altro': altro}
            co = 0
    
    if att.ValData != None:
        co = 1
        print(co)
        undata = []
        specdata = []
    
        if uns.exists():
            for un in uns:
                if un.ValCliData is None or un.ValTecData is None:
                    co = 2
                else:
                    if un.ValCliData is not None:
                        undata = undata + [un.ValCliData.date()]
                    if un.ValTecData is not None:
                        undata = undata + [un.ValTecData.date()]
        for spec in specs:
            if spec.ValCliData is None or spec.ValTecData is None:
                co = 2
            else:
                if spec.ValCliData is not None:
                    if spec.ValSpecCli == 'NO':
                        co = 3

                    specdata = specdata + [spec.ValCliData.date()]

                if spec.ValTecData is not None:
                    if spec.ValSpecTec == 'NO':
                        co = 3


                    specdata = specdata + [spec.ValTecData.date()]
        print(co)
        
        if co == 1:
            if att.ValMot == '0':
                att.Stato = Sta.objects.get(Numero = 10)
                att.save()
                notifica = Notifiche()
                notifica.invia_messaggio(us = att.Compilatore, mess="La richiesta per "+str(att.Apparecchiatura)+" non è stata valutata con successo. Vai alla HOME per maggiori informazioni.")
                notifica.save()
            else:
                date = [att.ValData.date()] + undata + specdata
                date = sorted(date)
                att.Data2 = date.pop()
                att.save()
                att.Stato = att.def_stato()
                att.save()
                pi = PI.objects.get(ID_PianoInvestimenti = att.ID_PianoInvestimenti)
                pi.Stato = att.Stato.Nome
                pi.save()
                notifica = Notifiche()
                notifica.invia_messaggio(us = att.Compilatore, mess="La richiesta per "+str(att.Apparecchiatura)+" è stata valutata con successo.")
                notifica.save()
        elif co == 3:
            att.Stato = Sta.objects.get(Numero = 0)
            att.save()
            notifica = Notifiche()
            notifica.invia_messaggio(us = att.Compilatore, mess="La richiesta per "+str(att.Apparecchiatura)+" non è stata valutata con successo. Vai alla HOME per maggiori informazioni.")
            notifica.save()
                
        return render(request, 'valutazione.html', context)
  
    return render(request, 'valutazione.html', context)

@login_required
def visualizza(request, pk, var):
    
    if var == '1':
        att = MAIN.objects.get(id=pk)
        if str(request.user.Gruppo) == 'Medico':
            if not att.Compilatore == request.user:
                return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")
        specs = Specifiche.objects.filter(ID_rich=pk)
        lista=[]
        for spec in specs:
            lista+=[spec.id]
        uns = Unicita.objects.filter(rifext__in=lista)
        crs = Criteri.objects.filter(ID_rich = pk)
        cons = ConsumabiliMain.objects.filter(ID_rich = pk)
        formdoc = ModRich(instance = att)
        formval = ModValut(instance = att)
        if request.method == 'POST':
            if 'Richiesta' in request.POST:
                formdoc = ModRich(request.POST, request.FILES, instance = att)
                if formdoc.is_valid():
                    formdoc.save()
                    return redirect(f'/visualizza/{pk}/{var}')
                else:
                    print(formdoc.errors)
            if 'Valutazione' in request.POST:
                formval = ModValut(request.POST, request.FILES, instance = att)
                if formval.is_valid():
                    formval.save()
                    return redirect(f'/visualizza/{pk}/{var}')
                else:
                    print(formval.errors)

    
        context = {'var':var, 'att': att, 'uns': uns, 'specs': specs, 'crs':crs, 'cons':cons, 'formdoc': formdoc, 'formval': formval}
    elif var == '2' :
        fabb = Fabbisogni.objects.get(id=pk)
        cons = ConsumabiliFabb.objects.filter(ID_rich = pk)
        if str(request.user.Gruppo)=='Medico':
            if not fabb.Compilatore == request.user:
                return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")
        context = {'att': fabb, 'var': var, 'cons': cons}
    elif var == '3':
        pi = PI.objects.get(id=pk)
        fabb = Fabbisogni.objects.filter(ID_PianoInvestimenti = pi.ID_PianoInvestimenti)
        context = {'fabb' : fabb, 'var': var}

    else:
        
        fabb = MAIN.objects.filter(ID_PianoInvestimenti = pk)
        context = {'fabb': fabb, 'var': var}

    return render(request, 'visualizza.html', context)

@login_required
def visualizzaurg(request, pk):
    att = UrgenteRequest.objects.get(id=pk)
    if str(request.user.Gruppo) == 'Medico':
        if not att.Compilatore == request.user:
            return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")
    specs = SpecificheUrg.objects.filter(ID_rich=pk)
    lista=[]
    for spec in specs:
        lista+=[spec.id]
    uns = UnicitaUrg.objects.filter(rifext__in=lista)
    crs = CriteriUrg.objects.filter(ID_rich = pk)
    cons = ConsumabiliUrg.objects.filter(ID_rich = pk)
    formdoc = ModRichUrg(instance = att)
    formval = ModValutUrg(instance = att)

    if request.method == 'POST':
        if 'Richiesta' in request.POST:
            formdoc = ModRichUrg(request.POST, request.FILES, instance = att)
            if formdoc.is_valid():
                formdoc.save()
                return redirect(f'/visualizzaurg/{pk}')
            else:
                print(formdoc.errors)
        if 'Valutazione' in request.POST:
            formval = ModValutUrg(request.POST, request.FILES, instance = att)
            if formval.is_valid():
                formval.save()
                return redirect(f'/visualizzaurg/{pk}')
            else:
                print(formval.errors)

    context = { 'att': att, 'uns': uns, 'specs': specs, 'crs':crs, 'cons':cons, 'formdoc': formdoc, 'formval': formval}

    return render(request, 'visualizzaurg.html', context)


@login_required
def visualizzaricerca(request, pk, modello):
    if modello == "Urgente" or modello=="urgente":
        return redirect('visualizzaurg', pk=pk)  # Usa il nome della URL corretta
    elif modello == "Programmata" or modello=="programmata":
        return redirect('visualizza', pk=pk, var=2)  # `var=2` indica che è una richiesta programmata
    else:
        return HttpResponse("Modello non valido", status=400)


@login_required
def download(request):
    file = compila_pdf_fabbisogno(request)
    response = HttpResponse(file.getvalue(), content_type='application/force-download')
    response['Content-Disposition'] = 'attachement; filename="completed.pdf"'
    return response

@login_required
def conferma_richiesta(request, pk):
    att = MAIN.objects.get(id=pk)
    att.Data0 = timezone.now()
    att.def_stato()
    att.save()
    notifica = Notifiche()
    notifica.invia_messaggio(us = att.Compilatore, mess="La richiesta per "+str(att.Apparecchiatura)+" è stata passata al piano di investimenti.")
    notifica.save()
    return redirect('/pianodiinvestimenti/')

@login_required
def avvio_richiesta(request, pk):

    if str(request.user.Gruppo) == 'Medico':
        return HttpResponse("<html>Non hai l' autorizzazione per questa operazione </html>")
    id_pi = PI.objects.get(id=pk)
    
   
    # tutti i fabbisogni associati:
    fabbs = Fabbisogni.objects.filter(ID_PianoInvestimenti = id_pi.ID_PianoInvestimenti,StatoRic__StatoRic=StatoRichiesta.APPROVATA)

    if not fabbs.exists():
        return HttpResponse(f"<html>Non c'è alcun fabbisogno associato al piano di investimenti. <a href='/avvio_richiesta/{pk}'>Torna indietro </a></html>")
    Qta_tot = 0
    Sereps = []
    listatipi =[]
    listacu = []
    listacm = []
    listatot = []
    listaper = []
    for f in fabbs:
        Qta_tot += f.Qta
        Sereps += [f.Sede_Reparto]
        f.Avviato = True
        f.save()
        # tutti i consumabili associati
        cons = ConsumabiliFabb.objects.filter(ID_rich = f)
        for c in cons:
            listatipi += [c.Tipo]
            listaper += [c.Periodo]
            listacu += [c.CostoUnitario]
            listacm += [c.ConsumoMedio]
            listatot += [c.Totale]

    # crea attrezzatura
    att = crea(fabbs[0], Qta_tot, id_pi, costo = id_pi.Costo_Presunto_IVA, sereps = Sereps)

    # crea consumabili 
    crea_cons(att, listatipi, listacu, listacm, listatot, listaper)
    id_pi.Stato = att.Stato.Nome

    id_pi.save()
    for f in fabbs:
        notifica = Notifiche()
        notifica.invia_messaggio(us = f.Compilatore, mess="La richiesta per "+str(att.Apparecchiatura)+" è stata avviata.")
        notifica.save()
    return redirect('/home/altro')

@login_required
def richiesta_invalutazione(request,pk):
    att = MAIN.objects.get(id=pk)
    
    crs = Criteri.objects.filter(ID_rich = pk)
    s = 0
    for cr in crs:
        s += cr.Peso
    if s!=100:
        return HttpResponse(f'<html>La somma dei pesi inseriti nei criteri di valutazione qualità non soddifa il requisito = 100. Modificare i pesi per arrivare ad una somma complessiva di 100. <a href="/richiesta_invalutazione/{pk}">Torna indietro </a></html>')

    if not Specifiche.objects.filter(ID_rich = pk).exists():
        return HttpResponse(f'<html><b>ERRORE</b>: La richiesta non può essere valutata fino a che non si inserisce almeno una specifica. <a href="/richiesta_invalutazione/{pk}">Torna indietro </a></html>')
    else:
        specs = Specifiche.objects.filter(ID_rich = pk)
        for sp in specs:
            if sp.Un:
                try:
                    u = Unicita.objects.get(ID_rich = pk, rifext = sp)
                except:
                    return HttpResponse(f'<html> Non è stata descritta il motivo di unicità assegnato ad alcune delle specifiche inserite. <a href="/richiesta_invalutazione/{pk}">Torna indietro </a> </html>')
    att.Data1 = timezone.now()
    att.def_stato()
    att.save()
    notifica = Notifiche()
    notifica.invia_messaggio(us = att.Compilatore, mess="La richiesta per "+str(att.Apparecchiatura)+" è stata completata ed ora è in attesa di valutazione.")
    notifica.save()
    return redirect('/')

@login_required
def invioProvv(request, pk):
    gruppo = request.user.Gruppo
    if not (gruppo.GaFlu):
        return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")

    att = MAIN.objects.get(id=pk)
    att.Data3 = timezone.now()
    att.def_stato()
    att.save()
    pi = PI.objects.get(ID_PianoInvestimenti = att.ID_PianoInvestimenti)
    pi.Stato = att.Stato.Nome
    pi.save()
    notifica = Notifiche()
    notifica.invia_messaggio(us = att.Compilatore, mess='La richiesta per '+str(att.Apparecchiatura)+' è stata spedita al Provveditorato')
    notifica.save()
    Gare = 'Gare'
    return redirect(f'/home/{Gare}')

@login_required
def garainiz(request, pk):
    gruppo = request.user.Gruppo
    if not (gruppo.GaFlu):
        return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")

    att = MAIN.objects.get(id=pk)
    att.Data4 = timezone.now()
    att.def_stato()
    att.save()
    notifica = Notifiche()
    notifica.invia_messaggio(us = att.Compilatore, mess="E' iniziata la gara per la richiesta di "+str(att.Apparecchiatura))
    notifica.save()
    Gare = 'Gare'
    return redirect(f'/home/{Gare}')

@login_required
def delibera(request, pk):
    gruppo = request.user.Gruppo
    if not (gruppo.GaFlu):
        return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")
    att = MAIN.objects.get(id=pk)
    att.Data6 = timezone.now()
    att.def_stato()
    att.save()
    pi = PI.objects.get(ID_PianoInvestimenti = att.ID_PianoInvestimenti)
    pi.Stato = att.Stato.Nome
    pi.save()
    notifica = Notifiche()
    notifica.invia_messaggio(us = att.Compilatore, mess="E' disponibile la delibera di "+str(att.Apparecchiatura))
    notifica.save()
    Gare = 'Gare'
    return redirect(f'/home/{Gare}')

@login_required
def comissione(request, pk):
    gruppo = request.user.Gruppo
    if not (gruppo.GaFlu):
        return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")
    att = MAIN.objects.get(id=pk)
    att.Data5 = timezone.now()
    att.def_stato()
    att.save()
    pi = PI.objects.get(ID_PianoInvestimenti = att.ID_PianoInvestimenti)
    pi.Stato = att.Stato.Nome
    pi.save()
    notifica = Notifiche()
    notifica.invia_messaggio(us = att.Compilatore, mess="E' stat nominata la comissione per "+str(att.Apparecchiatura))
    notifica.save()
    Gare = 'Gare'
    return redirect(f'/home/{Gare}')

@login_required
def acquisto(request, pk):
    gruppo = request.user.Gruppo
    if not (gruppo.GaFlu):
        return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")
    att = MAIN.objects.get(id=pk)
    att.Data7 = timezone.now()
    att.def_stato()
    att.save()
    pi = PI.objects.get(ID_PianoInvestimenti = att.ID_PianoInvestimenti)
    pi.Stato = att.Stato.Nome
    pi.save()
    notifica = Notifiche()
    notifica.invia_messaggio(us = att.Compilatore, mess=str(att.Apparecchiatura)+"E' stata acquistata.")
    notifica.save()
    Gare = 'Gare'
    return redirect(f'/home/{Gare}')

@login_required
def collaudo(request, pk):
    gruppo = request.user.Gruppo
    if not (gruppo.GaFlu):
        return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")
    att = MAIN.objects.get(id=pk)
    att.Data8 = timezone.now()
    att.def_stato()
    att.save()
    pi = PI.objects.get(ID_PianoInvestimenti = att.ID_PianoInvestimenti)
    pi.Stato = att.Stato.Nome
    pi.save()    
    notifica = Notifiche()
    notifica.invia_messaggio(us = att.Compilatore, mess="E' iniziato il collaudo "+str(att.Apparecchiatura))
    notifica.save()
    Gare = 'Gare'
    return redirect(f'/home/{Gare}')

@login_required
def sospensione(request, pk):
    gruppo = request.user.Gruppo
    if not (gruppo.GaFlu):
        return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")
    att = MAIN.objects.get(id = pk)
    form = SospensioneForm(instance = att)
    if request.method == 'POST':
        form = SospensioneForm(request.POST, instance = att)
        if form.is_valid():
            att = form.save()
            att.Data9 = timezone.now()
            att.def_stato()
            att.save()
            pi = PI.objects.get(ID_PianoInvestimenti = att.ID_PianoInvestimenti)
            pi.Stato = att.Stato.Nome
            pi.save()
            notifica = Notifiche()
            notifica.invia_messaggio(us = att.Compilatore, mess="La richiesta per "+str(att.Apparecchiatura)+" è stata sospesa. Per il seguente motivo: "+str(att.MotivoAnnullamento))
            notifica.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'sospensione.html', context)



@login_required
def modificasedereparti(request, pk):
    gruppo = request.user.Gruppo
    if not gruppo.UbMod:
        print('Entrato')
        return HttpResponse('Non sei autorizzato')
    s = SeRep.objects.get(id=pk)
    formsedi = SeRepForm(instance=s)
    sedi = SeRep.objects.all()
    if request.method == 'POST':
        formsedi = SeRepForm(request.POST, instance=s)
        if formsedi.is_valid():
            formsedi.save()
            return redirect('/sedereparti/')
        else:
            print(formsedi.errors)
    context = {
        'form' : formsedi,
        'sedi': sedi,
        'k': 2,
        's': s,
    }
    return render(request, 'sedereparti.html', context)


@login_required
def useraccount(request):

    var = 0
    
    nots = Notifiche.objects.filter(User=request.user)
    nots_nonlette=nots.filter(Letto=False)
    counter=0
    for nota in nots_nonlette:
        counter+=1

    context={'nots':nots, 'counter':counter, 'var':var}
    if request.user.Gruppo.FaIns:
        Int = 'ELENCO RICHIESTE EFFETTUATE:'
        att = MAIN.objects.filter(Compilatore = request.user)
        context = context | {
            'Int': Int,
            'att': att,
            
        }
    if request.user.Gruppo.GaValTec == 5:
        Int = 'ELENCO RICHIESTE VALUTATE:'
        specs = Specifiche.objects.filter(ValTecUtente = request.user)

        lista = []
        for spec in specs:
            id_rich = spec.ID_rich
            b = str(id_rich)
            app = b.split("_")
            lista += [app[0]]
        att = MAIN.objects.filter(Progressivo__in = lista)
        context = context | {
            'Int': Int,
            'att': att,
    
        }
    if request.user.Gruppo.GaValCli:
        Int = 'ELENCO RICHIESTE VALUTATE:'
        specs = Specifiche.objects.filter(ValCliUtente = request.user)
        lista = []
        for spec in specs:
            id_rich = spec.ID_rich
            b = str(id_rich)
            app = b.split("_")
            lista += [app[0]]
        att = MAIN.objects.filter(Progressivo__in = lista)
        context = context | {
            'Int': Int,
            'att': att,
        }
    
   
    
    return render(request, 'userhome.html', context)

@login_required
def modificauser(request, var):
    if var == '0':
        utente = request.user
        form = EditProfileForm(instance=utente)
        
    else:
        utente = MedicalUser.objects.get(id = var)
        form = EditProfileFormAdmin(instance = utente)

    if request.method=="POST":
            if var == '0':
                form = EditProfileForm(request.POST, instance=utente)
            else:
                form = EditProfileFormAdmin(request.POST, instance = utente)
            if form.is_valid():
                form.save()
                if var == '0':
                    return redirect('useraccount')
                else:
                    return redirect('tuttiprofili')
            else:
                print(form.errors)
    context = {'form': form}
    return render(request, 'modificauser.html', context)

class PasswordsChangeView(PasswordChangeView):
    form = PasswordChangeForm
    success_url = reverse_lazy('useraccount')

@login_required
def tuttiprofili(request):
    profili = MedicalUser.objects.all()
    var = 2
    context = {'profili': profili, 'var': var}
    return render(request, 'tuttiprofili.html', context)

@login_required
def letto(request, pk):
    notifica = Notifiche.objects.get(id=pk)
    notifica.Letto = True
    notifica.save()
    return redirect('useraccount')

@login_required
def non_letto(request, pk):
    notifica = Notifiche.objects.get(id=pk)
    notifica.Letto = False
    notifica.save()
    return redirect('useraccount')

@login_required
def tuttoletto(request):
    notifiche = Notifiche.objects.filter(User = request.user)
    for notifica in notifiche:
        notifica.Letto = True
        notifica.save()
    return redirect('useraccount')




def update4(request, pk):
    att = MAIN.objects.get(id = pk)
    gruppo = request.user.Gruppo
    if not gruppo.SpMoTu and gruppo.SpMoPr:
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif not gruppo.SpMoTu and not gruppo.SpMoPr:
        return HttpResponse('Non sei autorizzato')

    form = ModMot(instance = att)

    specs = Specifiche.objects.filter(ID_rich = pk)
    rifs =[]
    min = []
    max = []
    b = []
    for spec in specs:
        rifs += [spec.rif]
        min += [spec.Min]
        max += [spec.Max]
        if spec.ValSpecTec == 'NO':
            b += [True]
        elif spec.ValSpecCli == 'NO':
            b += [True]
        else:
            b += [False]
    SpecFormSet = modelformset_factory(Specifiche, fields=('Specifica', 'MotivoClinico', 'Min', 'Max'), form=SpecificheForm, extra=0)
    formset = SpecFormSet(queryset=specs)
    
    if request.method == 'POST':
        if 'Specifiche' in request.POST:
            formset = SpecFormSet(request.POST, queryset=specs)
            if formset.is_valid():
                i=0
                for form in formset:
                    form.ID_rich = pk
                    form.Min = min[i]
                    form.Max = max[i]
                    form.rif = rifs[i]
                    s = form.save()
                    if s.ValSpecCli == 'NO':
                        s.ValSpecCli = None
                        s.ValCliData = None
                        s.ValCliUtente = None
                        s.ValSpecCliNota = None
                    if s.ValSpecTec == 'NO':
                        s.ValTecData = None
                        s.ValSpecTec = None
                        s.ValTecUtente = None
                        s.ValSpecTecNota = None
                    s.save()
                    i += 1
            else:
                print('ERROR', formset.non_form_errors())
                print(formset.errors)
        
        if 'Motivi' in request.POST:
            form = ModMot(request.POST, instance = att)
            if form.is_valid():
                a = form.save()
                if a.ValMot == '0':
                    a.ValData = None
                    a.ValUtente = None
                    a.ValMot = None
                    a.ValMotNota = ''
                a.save()
        altro = 'altro'
        return redirect(f'/home/{altro}')
    
    context = {'insieme':zip(specs, formset, b), 'formset': formset, 'formmot': form}
    return render(request, 'update4.html', context)

def modificaspecifica(request, pk, var):
    s = Specifiche.objects.get(id=pk)
    id_rich = s.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = MAIN.objects.get(Progressivo = app)
    gruppo = request.user.Gruppo
    if not gruppo.SpMoTu and gruppo.SpMoPr:
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif not gruppo.SpMoTu and not gruppo.SpMoPr:
        return HttpResponse('Non sei autorizzato')
    formsp = SpecificheForm(instance=s)
    specs = Specifiche.objects.filter(ID_rich = id_rich)
    print(len(specs))
    
    if request.method == 'POST':
        formsp = SpecificheForm(request.POST, instance = s)
        if formsp.is_valid():
            formsp.save()
            return redirect(f'/new_2_4/{att.id}/{var}/')
        else:
            print(formsp.errors)

    context = {
        'form' : formsp,
        'specs': specs,
        'k': 2,
        's': s,
        'var': var,
        'att': att,
        'altro': 'altro'
    }
    return render(request, 'new_2_4.html', context)

def modificaunicita(request, pk, var):
    u = Unicita.objects.get(id=pk)
    id_rich = u.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = MAIN.objects.get(Progressivo = app)
    gruppo = request.user.Gruppo
    if not gruppo.SpMoTu and gruppo.SpMoPr:
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif not gruppo.SpMoTu and not gruppo.SpMoPr:
        return HttpResponse('Non sei autorizzato')
    formun = UnicitaForm(instance=u)
    uns = Unicita.objects.filter(ID_rich = id_rich)
    
    if request.method == 'POST':
        formun = UnicitaForm(request.POST, instance = u)
        if formun.is_valid():
            formun.save()
            return redirect(f'/new_4e2/{att.id}/{var}//')
        else:
            print(formun.errors)

    context = {
        'form' : formun,
        'uns': uns,
        'k': 2,
        'u': u,
        'var': var,
        'att': att
    }
    return render(request, 'new_4e2.html', context)

def modificacriteri(request, pk, var):
    c = Criteri.objects.get(id=pk)
    id_rich = c.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = MAIN.objects.get(Progressivo = app)
    gruppo = request.user.Gruppo
    if not gruppo.SpMoTu and gruppo.SpMoPr:
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif not gruppo.SpMoTu and not gruppo.SpMoPr:
        return HttpResponse('Non sei autorizzato')
    formcr = CriteriForm(instance=c)
    crs = Criteri.objects.filter(ID_rich = id_rich)
    
    if request.method == 'POST':
        formcr = CriteriForm(request.POST, instance = c)
        if formcr.is_valid():
            formcr.save()
            return redirect(f'/new_4e3/{att.id}/{var}//')
        else:
            print(formcr.errors)

    context = {
        'form' : formcr,
        'crs': crs,
        'k': 2,
        'c': c,
        'var': var,
        'att': att,
        'altro': 'altro'
    }
    return render(request, 'new_4e3.html', context)

def modificaconsumabili(request, pk, var):
    if var == '1' or var == '2':
        c = ConsumabiliFabb.objects.get(id=pk)
        id_rich = c.ID_rich
        fabb = Fabbisogni.objects.get(Progressivo = id_rich)
        gruppo = request.user.Gruppo
        if not gruppo.FaMoTu and gruppo.FaMoPr:
            if fabb.Compilatore != request.user:
                return HttpResponse('Non sei autorizzato')
        elif not gruppo.FaMoTu and not gruppo.FaMoPr:
            return HttpResponse('Non sei autorizzato')
        formcon = ConsumabiliFormFabb(instance = c)
        cons = ConsumabiliFabb.objects.filter(ID_rich = id_rich)
        if request.method == 'POST':
            formcon = ConsumabiliFormFabb(request.POST, instance = c)
            if formcon.is_valid():
                formcon.save()
                return redirect(f'/new_5/{fabb.id}/{var}/')
            else:
                print(formcon.errors)
        context = {
            'form' : formcon,
            'cons': cons,
            'k': 2,
            'c': c,
            'var': var,
            'fabb': fabb,
        }
    else:
        c = ConsumabiliMain.objects.get(id=pk)
        id_rich = c.ID_rich
        b = str(id_rich)
        app = b.split("_")
        app = app[0]
        att = MAIN.objects.get(Progressivo = app)
        gruppo = request.user.Gruppo
        if not gruppo.SpMoTu and gruppo.SpMoPr:
            if att.Compilatore != request.user:
                return HttpResponse('Non sei autorizzato')
        elif not gruppo.SpMoTu and not gruppo.SpMoPr:
            return HttpResponse('Non sei autorizzato')
        formcon = ConsumabiliFormMain(instance = c)
        cons = ConsumabiliMain.objects.filter(ID_rich = id_rich)
        
        
        if request.method == 'POST':
            formcon = ConsumabiliFormMain(request.POST, instance = c)
            if formcon.is_valid():
                formcon.save()
                return redirect(f'/new_5/{att.id}/{var}/')
            else:
                print(formcon.errors)

        context = {
            'form' : formcon,
            'cons': cons,
            'k': 2,
            'c': c,
            'var': var,
            'att': att,
            'altro': 'altro'
        }
    return render(request, 'new_5.html', context)

def modificaditteinserite(request, pk, var):
    d = Ditta.objects.get(id=pk)
    id_rich = d.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = MAIN.objects.get(Progressivo = app)
    gruppo = request.user.Gruppo
    if not gruppo.SpMoTu and gruppo.SpMoPr:
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif not gruppo.SpMoTu and not gruppo.SpMoPr:
        return HttpResponse('Non sei autorizzato')
    formd = DittaForm(instance=d)
    ds = Ditta.objects.filter(ID_rich = id_rich)
    
    if request.method == 'POST':
        formd = DittaForm(request.POST, instance = d)
        if formd.is_valid():
            formd.save()
            return redirect(f'/new_5e2/{att.id}/{var}//')
        else:
            print(formd.errors)

    context = {
        'form' : formd,
        'ds': ds,
        'k': 2,
        'd': d,
        'var': var,
        'att': att
    }
    return render(request, 'new_5e2.html', context)


def priorita(request, var):
    gruppo = request.user.Gruppo
    if var == '1':
        print(gruppo.PrVe)
        if not gruppo.PrVe:
            return HttpResponse('Non sei autorizzato')
        prs = Priorita.objects.all()
        form = PrForm()
        if request.method == 'POST':
            form = PrForm(request.POST)
            if form.is_valid():
                form.save()

        print(gruppo.PrIns)
        if not gruppo.PrIns:
            context = {'prs': prs, 'k':1, 'var': var}
        else:
            context ={'prs': prs, 'form':form, 'k':1, 'var':var}
     
    elif var == '2':
        prs = Gruppi.objects.all()
        form = GruppiForm()
        if request.method == 'POST':
            form = GruppiForm(request.POST)
            if form.is_valid():
                form.save()

        context ={'prs': prs, 'form':form, 'k':1, 'var':var}
       
    elif var == '3':
        if not gruppo.ProfVe:
            return HttpResponse('Non sei autorizzato')
        prs = Professioni.objects.all()
        form = ProfessioniForm()
        if request.method == 'POST':
            form = ProfessioniForm(request.POST)
            if form.is_valid():
                form.save()

        if not gruppo.ProfIns:
            context ={'prs': prs, 'k':1, 'var':var}
        else:
            context ={'prs': prs, 'form':form, 'k':1, 'var':var}
    
    return render(request, 'priorita.html', context)

def modificapriorita(request, pk, var):
    if var == '1':
        gruppo = request.user.Gruppo
        if not gruppo.PrMod:
            return HttpResponse('Non sei autorizzato')
        pr = Priorita.objects.get(id=pk)
        form = PrForm(instance=pr)
        prs = Priorita.objects.all()
        if request.method == 'POST':
            form = PrForm(request.POST, instance=pr)
            if form.is_valid():
                form.save()
                return redirect(f'/priorita/{var}')
            else:
                print(form.errors)
    elif var == '2':
        pr = Gruppi.objects.get(id=pk)
        form = GruppiForm(instance=pr)
        prs = Gruppi.objects.all()
        if request.method == 'POST':
            form = GruppiForm(request.POST, instance=pr)
            if form.is_valid():
                form.save()
                return redirect(f'/priorita/{var}')
            else:
                print(form.errors)
    
    else:
        gruppo = request.user.Gruppo 
        if not gruppo.ProfMod:
            return HttpResponse('Non sei autorizzato')
        pr = Professioni.objects.get(id=pk)
        form = ProfessioniForm(instance=pr)
        prs = Professioni.objects.all()
        if request.method == 'POST':
            form = ProfessioniForm(request.POST, instance=pr)
            if form.is_valid():
                form.save()
                return redirect(f'/priorita/{var}')
            else:
                print(form.errors)

    context = {
        'form' : form,
        'prs': prs,
        'k': 2,
        'pr': pr,
    }
    return render(request, 'priorita.html', context)

def registranew(request): #utente
    form = newuserform()
    if request.method == 'POST':
        form = newuserform(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/tuttiprofili/')
        else:
            print(form.errors)
    context = {'form': form}
    return render(request, 'registration/newregister.html', context)

def download_offline(request): #urgente scarico modulo
    """ Scarica il PDF per la modalità offline """
    file = compila_pdf_fabbisogno_urgente(request)
    response = HttpResponse(file.getvalue(), content_type='application/force-download')
    response['Content-Disposition'] = 'attachement; filename="modulo_offline.pdf"'
    return response

def nuova_richiesta_urgente(request): #carico modulo offline
    if request.method == 'POST':
        # Aggiungi request.FILES per gestire i file inviati
        form = UrgenteRequestForm(request.POST, request.FILES)
        if form.is_valid():
            richiesta = form.save(commit=False)
            # Gestisci il file che è stato caricato
            # Per esempio, se hai un campo FileModuloRichiestaFirmato:
            if 'FileModuloRichiestaFirmato' in request.FILES:
                richiesta.FileModuloRichiestaFirmato = request.FILES['FileModuloRichiestaFirmato']
            if 'FileModuloValutazioneFirmato' in request.FILES:
                richiesta.FileModuloValutazioneFirmato = request.FILES['FileModuloValutazioneFirmato']
            
            # Salva la richiesta nel database
            richiesta.save()
            return redirect('raccolta_fabbisogni')  # Modifica con il percorso che desideri dopo il salvataggio
    else:
        form = UrgenteRequestForm()

    return render(request, 'modulorichiesta.html', {'form': form})


@login_required
def pagina_ricerca(request):
    query = request.GET.get('q', '')
    # Recupero richieste URGENTI
    urgenti_qs = UrgenteRequest.objects.all().annotate(tipo_richiesta=Value("Urgente",output_field=CharField()))
    fabbisogno_qs= Fabbisogni.objects.all().annotate(tipo_richiesta=Value("Programmata",output_field=CharField()))
    prog_qs= MAIN.objects.all().annotate(tipo_richiesta=Value("Programmata",output_field=CharField()))

    fabfilter=RacFabFilterRic(request.GET, queryset=fabbisogno_qs)
    fab=fabfilter.qs

    urgrfilter=RacUrgFilterRic(request.GET, queryset=urgenti_qs)
    urgr=urgrfilter.qs

    mainfilter=MAINFilterRic(request.GET, queryset=prog_qs)
    main=mainfilter.qs

    tutte_richieste= list(chain(urgr, fab))

    user_group = request.user.Gruppo.Descrizione if request.user.Gruppo else None
    puo_vedere_tasto = user_group in ["ING. CLINICO", "ADMIN"]    

    context= {
        'richieste': tutte_richieste,
        'urgrfilter': urgrfilter,
        'fabfilter': fabfilter,
        'main': main,
        'mainfilter': mainfilter,
        'query': query,
        'puo_vedere_tasto': puo_vedere_tasto

    }

    return render(request,'pagina_ricerca.html', context)

def modificaspecificaurg(request, pk):
    s = SpecificheUrg.objects.get(id=pk)
    id_rich = s.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = UrgenteRequest.objects.get(Progressivo = app)
    gruppo = request.user.Gruppo
    if not gruppo.SpMoTu and gruppo.SpMoPr:
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif not gruppo.SpMoTu and not gruppo.SpMoPr:
        return HttpResponse('Non sei autorizzato')
    formsp = SpecificheUrgForm(instance=s)
    specs = SpecificheUrg.objects.filter(ID_rich = id_rich)
    print(len(specs))
    
    if request.method == 'POST':
        formsp = SpecificheUrgForm(request.POST, instance = s)
        if formsp.is_valid():
            formsp.save()
            return redirect(f'/new_urg_2_4/{att.id}/')
        else:
            print(formsp.errors)

    context = {
        'form' : formsp,
        'specs': specs,
        'k': 2,
        's': s,
        'att': att,
        'altro': 'altro',
        'pk': pk
    }
    return render(request, 'new_urg_2_4.html', context)

def modificacriteriurg(request, pk):
    c = CriteriUrg.objects.get(id=pk)
    id_rich = c.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = UrgenteRequest.objects.get(Progressivo = app)
    gruppo = request.user.Gruppo
    if not gruppo.SpMoTu and gruppo.SpMoPr:
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif not gruppo.SpMoTu and not gruppo.SpMoPr:
        return HttpResponse('Non sei autorizzato')
    formcr = CriteriUrgForm(instance=c)
    crs = CriteriUrg.objects.filter(ID_rich = id_rich)
    
    if request.method == 'POST':
        formcr = CriteriUrgForm(request.POST, instance = c)
        if formcr.is_valid():
            formcr.save()
            return redirect(f'/new_urg_4e3/{att.id}/')
        else:
            print(formcr.errors)

    context = {
        'form' : formcr,
        'crs': crs,
        'k': 2,
        'c': c,
        'att': att,
        'altro': 'altro',
        'pk': pk
    }
    return render(request, 'new_urg_4e3.html', context)

def modificaconsumabiliurg(request, pk):
    c = ConsumabiliUrg.objects.get(id=pk)
    id_rich = c.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = UrgenteRequest.objects.get(Progressivo = app)
    gruppo = request.user.Gruppo
    if not gruppo.SpMoTu and gruppo.SpMoPr:
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif not gruppo.SpMoTu and not gruppo.SpMoPr:
        return HttpResponse('Non sei autorizzato')
    formcon = ConsumabiliUrgForm(instance = c)
    cons = ConsumabiliUrg.objects.filter(ID_rich = id_rich)
        
        
    if request.method == 'POST':
        formcon = ConsumabiliUrgForm(request.POST, instance = c)
        if formcon.is_valid():
            formcon.save()
            return redirect(f'/new_5/{att.id}/')
        else:
            print(formcon.errors)

    context = {
            'form' : formcon,
            'cons': cons,
            'k': 2,
            'c': c,
            'pk': pk,
            'att': att,
            'altro': 'altro'
        }
    return render(request, 'new_urg_5.html', context)

def modificaditteinserite_urg(request, pk):
    d = DittaUrg.objects.get(id=pk)
    id_rich = d.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = UrgenteRequest.objects.get(Progressivo = app)
    gruppo = request.user.Gruppo
    if not gruppo.SpMoTu and gruppo.SpMoPr:
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif not gruppo.SpMoTu and not gruppo.SpMoPr:
        return HttpResponse('Non sei autorizzato')
    formd = DittaUrgForm(instance=d)
    ds = DittaUrg.objects.filter(ID_rich = id_rich)
    
    if request.method == 'POST':
        formd = DittaUrgForm(request.POST, instance = d)
        if formd.is_valid():
            formd.save()
            return redirect(f'/new_urg_5e2/{att.id}/')
        else:
            print(formd.errors)

    context = {
        'form' : formd,
        'ds': ds,
        'k': 2,
        'd': d,
        'pk': pk,
        'att': att
    }
    return render(request, 'new_urg_5e2.html', context)

def modificaunicitaurg(request, pk):
    u = UnicitaUrg.objects.get(id=pk)
    id_rich = u.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = UrgenteRequest.objects.get(Progressivo = app)
    gruppo = request.user.Gruppo
    if not gruppo.SpMoTu and gruppo.SpMoPr:
        if att.Compilatore != request.user:
            return HttpResponse('Non sei autorizzato')
    elif not gruppo.SpMoTu and not gruppo.SpMoPr:
        return HttpResponse('Non sei autorizzato')
    formun = UnicitaUrgForm(instance=u)
    uns = UnicitaUrg.objects.filter(ID_rich = id_rich)
    
    if request.method == 'POST':
        formun = UnicitaUrgForm(request.POST, instance = u)
        if formun.is_valid():
            formun.save()
            return redirect(f'/new_urg_4e2/{att.id}/')
        else:
            print(formun.errors)

    context = {
        'form' : formun,
        'uns': uns,
        'k': 2,
        'u': u,
        'pk':pk,
        'att': att
    }
    return render(request, 'new_urg_py4e2.html', context)

@login_required
def valutazioneprogram(request, pk, var):

    fabb = Fabbisogni.objects.get(id=pk)
    cons = ConsumabiliFabb.objects.filter(ID_rich = pk)
    if str(request.user.Gruppo)=='Medico':
        if not fabb.Compilatore == request.user:
            return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")
    modello='Programmata'
    context = {'att': fabb, 'var': var, 'cons': cons, 'modello': modello}


    return render(request, 'valutazioneprogram.html', context)

@login_required

def valutazioneurg(request, pk):

    att = UrgenteRequest.objects.get(id=pk)
    modello='Urgente'
    if str(request.user.Gruppo) == 'Medico':
        if not att.Compilatore == request.user:
            return HttpResponse("Non hai l'autorizzazione per eseguire questa operazione.")
    specs = SpecificheUrg.objects.filter(ID_rich=pk)
    lista=[]
    for spec in specs:
        lista+=[spec.id]
    uns = UnicitaUrg.objects.filter(rifext__in=lista)
    crs = CriteriUrg.objects.filter(ID_rich = pk)
    cons = ConsumabiliUrg.objects.filter(ID_rich = pk)
    formdoc = ModRichUrg(instance = att)
    formval = ModValutUrg(instance = att)

    if request.method == 'POST':
        if 'Richiesta' in request.POST:
            formdoc = ModRichUrg(request.POST, request.FILES, instance = att)
            if formdoc.is_valid():
                formdoc.save()
                return redirect(f'/valutazioneurg/{pk}')
            else:
                print(formdoc.errors)
        if 'Valutazione' in request.POST:
            formval = ModValutUrg(request.POST, request.FILES, instance = att)
            if formval.is_valid():
                formval.save()
                return redirect(f'/valutazioneurg/{pk}')
            else:
                print(formval.errors)
    

    context = { 
        'att': att, 
        'uns': uns, 
        'specs': specs, 
        'crs':crs, 
        'cons':cons, 
        'formdoc': formdoc, 
        'formval': formval,
        'modello': modello}

    return render(request, 'valutazioneurg.html', context)

@login_required
def tab_assegnazioneprior(request):
    var2=2
    #richieste_fabbisogni = Fabbisogni.objects.filter(StatoRic__StatoRic=StatoRichiesta.SPEDITA).order_by("AssegnPrior")
    richieste_fabbisogni = Fabbisogni.objects.filter(StatoRic__StatoRic=StatoRichiesta.SPEDITA)
    print("Numero di richieste trovate:", richieste_fabbisogni.count())
    context = {
        "richieste_fabbisogni": richieste_fabbisogni,
        'var2':var2,
        'opt': '1', 
    }

    return render(request, "tab_assegnazioneprior.html", context)

@login_required
def assegn1(request, pk, var):
    
    fabb = Fabbisogni.objects.get(id=pk)
    cons = ConsumabiliFabb.objects.filter(ID_rich = pk)

    modello='Programmata'
    context = {'att': fabb, 'var': var, 'cons': cons, 'modello': modello}

    return render(request, 'assegn1.html', context)


@login_required
def assegn2(request, pk, var):
    richiesta = get_object_or_404(Fabbisogni, id=pk)

    if request.method == "POST":
        form = AssPriorForm(request.POST, instance=richiesta)
        if form.is_valid():
            form.save()
            return redirect('tab_assegnazioneprior')  # Torna all'elenco principale
    else:
        form = AssPriorForm(instance=richiesta)

    context = {
        'form': form,
        'richiesta': richiesta
    }
    return render(request, 'assegn2.html', context)