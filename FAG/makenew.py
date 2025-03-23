
from datetime import datetime, date
#from tkinter import E, N
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from pyparsing import unicode_set
from .models import *
from .forms import *
from django.db.models import Q
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
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.conf import settings
from io import BytesIO
from django.template.loader import get_template
import csv
from PyPDF2 import PdfFileReader
import pandas as pd
import xlwt #pip install xlwt
import os
from pprint import pprint
from .crea_da_pdf import *
from django.contrib.auth import authenticate, login, logout
from .service import *
from django import forms


@login_required
def new(request, opt):
    prs = Priorita.objects.all()
    var = 1
    u = request.user
    # try:
    #     sede= SeRep.objects.filter(Sede = u.Sede_Reparto.Sede, Reparto = u.Sede_Reparto.Reparto)

    # except:
    #     sede= ['']

    sede=SeRep.objects.filter(Sede = u.Sede_Reparto.Sede, Reparto = u.Sede_Reparto.Reparto).first()
    data = {'Compilatore': u, 'Sede_Reparto': sede if sede else 'nessuna sede trovata'} 
    if opt == '1':
        gruppo = request.user.Gruppo
        if not gruppo.FaIns:
            return HttpResponse('Non sei autorizzato')

        form1 = AttForm1(initial=data)
        # form attrezzatura
        if request.method=='POST':
            form1 = AttForm1(request.POST, initial=data)
            if form1.is_valid():
                fabb = form1.save(commit=False)
                fabb.save()
                
                crea_stato_per_richiesta(fabb, request.user)
                print(f"Stato richiesta dopo assegnazione: {fabb.StatoRic}") 

                fabb.costo_presuntoNOIVA()
                current_year_atts = Fabbisogni.objects.filter(Data__year = fabb.Data.strftime('%Y'))
                k = 0
                for year in current_year_atts:
                    k += 1
                fabb.Progressivo = str(k)+'-'+str(fabb.Data.strftime('%Y'))
                fabb.save()
                return redirect(f'/new_5/{fabb.id}/{var}')
            else:
                print(form1.errors)
    elif opt == '2':
        form1 = AttForm3(initial=data)
        # form attrezzatura
        if request.method=='POST':
            form1 = AttForm3(request.POST, initial=data)
            if form1.is_valid():
                fabb = form1.save()
                crea_stato_per_richiesta(fabb, request.user)
                fabb.costo_presuntoNOIVA()
                fabb.save()
                id_pi = fabb.ID_PianoInvestimenti
                soglia = id_pi.Costo_Presunto_IVA # soglia investimenti
            # se speso = 0, controlla i prezzi presunti
                tot = 0
                if id_pi.Speso == 0:
                    atts = MAIN.objects.filter(ID_PianoInvestimenti = id_pi)
                    for a in atts:
                        print(a.Costo_Presunto_IVA)
                        tot += a.Costo_Presunto_IVA
                    if tot + fabb.Costo_Presunto_IVA > soglia:
                        fabb.delete()
                        return HttpResponse('La richiesta supera il budget')
                        
                    elif tot + fabb.Costo_Presunto_IVA == soglia:
                        id_pi.is_full = True

                # se invece abbiamo speso qualcosa, controlla quando abbiamo speso
                else:
                    stato = Sta.objects.get(Nome='Acquisizione')
                    atts = MAIN.objects.filter(ID_PianoInvestimenti = id_pi).exclude(Stato = stato)
                    for a in atts:
                        tot += a.Costo_Presunto_IVA
                    if tot + fabb.Costo_Presunto_IVA > soglia - id_pi.Speso:
                        fabb.delete()
                        return HttpResponse('La richiesta supera il budget')
                        
                    elif tot + fabb.Costo_Presunto_IVA == soglia - id_pi.Speso:
                        id_pi.is_full = True
                
                id_pi.save()
                fabb.def_stato()
                current_year_atts = MAIN.objects.filter(Data__year = fabb.Data.strftime('%Y'))
                k = 0
                for year in current_year_atts:
                    k += 1
                fabb.Progressivo = str(k)+'-'+str(fabb.Data.strftime('%Y'))
                fabb.save()
                var = 3
                return redirect(f'/attachements/{fabb.id}/{var}')
            else:
                print(form1.errors)

    context={'form1': form1,
    'var': var, 'prs': prs, 'opt': opt}
    return render(request, 'new.html', context)

@login_required
def new_2_4(request, pk, var=None):
    re = pk
    
    
    att = MAIN.objects.get(id=re)
    counter = 1
    k = 1
    
    if Specifiche.objects.filter(ID_rich=re).exists():
    
        specs = Specifiche.objects.filter(ID_rich=re)
        for spec in specs: # conta il numero di specifiche e in base a quello definisce il riferimento
            counter+=1
        context={
            'att': att,
            'specs': specs,
            'var':var,
            'k':k,
        }
           
    else:

        context = {
        'att': att,
        'var':var,
        'k': k
        }  
    data = {'ID_rich': re,
    'rif': counter,
    }
    form = SpecificheForm(initial=data)
    if request.method=='POST':
        form = SpecificheForm(request.POST, initial=data)
        if form.is_valid():
            main=form.save()
            return redirect(f'/new_2_4/{pk}/{var}/')

    context = context| {'form': form,
                'altro': 'altro'}
    return render(request, 'new_2_4.html', context)

@login_required
def new_4e2(request, pk, var=None):
    
    if Specifiche.objects.filter(ID_rich = pk).exists():
        specs = Specifiche.objects.filter(ID_rich = pk)
        choicesp =[]
        lista =[]
        for spec in specs:
            if spec.Un:
                choicesp+=[(spec.id, str(spec.rif))]
                lista+=[spec.id]
    else :
        return redirect(f'/new_4e3/{pk}/{var}//')
    
    att = MAIN.objects.get(id=pk)
    data = {'ID_rich': pk}
    form = UnicitaForm(initial=data)
    form.fields['rifext'].choices = choicesp
   
    

    if Unicita.objects.filter(rifext__in = lista).exists():
        uns=Unicita.objects.filter(rifext__in = lista)
        context={
            'att': att,
            'uns': uns,
            'var':var,
        }   
    else:
        context = {
        'att': att,
        'var':var,
        }  
   
    form = UnicitaForm(initial = data)
    form.fields['rifext'].choices = choicesp
    unform = FormUn(instance=att)
    UnFormSet = modelformset_factory(model = Specifiche, fields = ('Un',), form = Unform, extra=0)
    unformset = UnFormSet(queryset = specs)

    if request.method=='POST':
        if 'Aggiungi' in request.POST:
            form = UnicitaForm(request.POST, initial=data)
            form.fields['rifext'].choices = choicesp
            if form.is_valid():
                form.save()
                return redirect(f'/new_4e2/{pk}/{var}//')
            else:
                print(form.errors)

        if 'Simili' in request.POST:
            unform = FormUn(request.POST, instance=att)
            if unform.is_valid():
                att=unform.save()
                return redirect(f'/new_2_4/{pk}/{var}/')
            else:
                print('Stupido')
                print(unform.errors)
        if 'Uni' in request.POST:
            unformset = UnFormSet(request.POST, queryset=specs)
            if unformset.is_valid():
                unformset.save()

    context = context | {'form': form, 'unform':unform, 'unformset': unformset, 'insieme': zip(specs, unformset), 'altro': 'altro'}
    return render(request, 'new_4e2.html', context)

@login_required
def new_4e3(request, pk, var=None):
    s = Specifiche.objects.all()
    counterspec = len(s)
    data = {'ID_rich': pk}
    form = CriteriForm(initial=data)
    att = MAIN.objects.get(id=pk)
    counter = 1

    if Criteri.objects.filter(ID_rich=pk).exists():
        crs=Criteri.objects.filter(ID_rich=pk)
        s = 0
        for cr in crs:
            counter += 1
            s += cr.Peso

        if s != 100:
            b = True
        else:
            b=False
        context={
            'att': att,
            'crs': crs,
            'var':var,
            'b': b,
            'counter': counterspec
        }   
    else:
        context = {
        'att': att,
        'var': var,
        'counter': counterspec
        }  
    data = {'ID_rich': pk,
    'Rif': counter}
    form = CriteriForm(initial=data)
    if request.method=='POST':
        form = CriteriForm(request.POST, initial=data)
        if form.is_valid():
            form.save()
            return redirect(f'/new_4e3/{pk}/{var}//')
    context = context | {'form': form, 'altro': 'altro'}
    return render(request, 'new_4e3.html', context)

@login_required
def new_5(request, pk, var=None):
    print(var)
    if var=='1' or var == '2':
        opt = 1
        att = Fabbisogni.objects.get(id=pk)
        data = {'ID_rich': att}
        print(att)
        form = ConsumabiliFormFabb(initial=data)
        if ConsumabiliFabb.objects.filter(ID_rich=pk).exists():
            cons=ConsumabiliFabb.objects.filter(ID_rich=pk)
            context={
                'att': att,
                'form': form,
                'cons': cons,
                'var': var,
                'altro': 'altro',
                'opt': opt,
            }   
        else:
            context = {
            'att': att,
            'form': form,
            'var':var,
            'altro': 'altro',
            'opt': opt,
            }  
        
        if request.method=='POST':
            form = ConsumabiliFormFabb(request.POST, initial=data)
            if form.is_valid():
                con = form.save()
                con.Totale = con.CostoUnitario * con.ConsumoMedio
                con.save()
                return redirect(f'/new_5/{pk}/{var}/')

            else:
                print(form.errors)
    else:
        opt = 2
        att = MAIN.objects.get(id=pk)
        data = {'ID_rich': att}
        print(att)
        form = ConsumabiliFormMain(initial=data)
        if ConsumabiliMain.objects.filter(ID_rich=pk).exists():
            cons=ConsumabiliMain.objects.filter(ID_rich=pk)
            context={
                'att': att,
                'form': form,
                'cons': cons,
                'var': var,
                'altro': 'altro',
                'opt': opt,
            }   
        else:
            context = {
            'att': att,
            'form': form,
            'var':var,
            'altro': 'altro',
            'opt': opt,
            }  
        
        if request.method=='POST':
            form = ConsumabiliFormMain(request.POST, initial=data)
            if form.is_valid():
                con = form.save()
                con.Totale = con.CostoUnitario * con.ConsumoMedio
                con.save()
                return redirect(f'/new_5/{pk}/{var}/')

            else:
                print(form.errors)        
    return render(request, 'new_5.html', context)

@login_required
def new_5e2(request, pk, var=None):

    altro = 'altro'
    att = MAIN.objects.get(id=pk)
    init = {'ID_rich': pk}
    counter = 1

    form = DittaForm(initial=init)
    if Ditta.objects.filter(ID_rich=pk).exists():
        ditte=Ditta.objects.filter(ID_rich=pk)
        for ditta in ditte:
            counter+=1
        context={
        'att': att,
        'ditte': ditte,
        'var': var
        }   
    else:
         context={
        'att': att,
        'var': var,
        }  
    init = {'ID_rich': pk,
    'Rif': counter}
    form = DittaForm(initial=init)
    if request.method=='POST':
        form = DittaForm(request.POST, request.FILES, initial=init)
        if form.is_valid():
            form.save()
        return redirect(f'/new_5e2/{pk}/{var}//')
    context = context | {'form': form, 'altro': altro, 'altro': 'altro'}
    return render(request, 'new_5e2.html',context) 

@login_required
def copiafabbisogno(request):
    fabbs = Fabbisogni.objects.all()
    tablfilter = RacFabFilter(request.GET, queryset=fabbs)
    fabbs  = tablfilter.qs
    pis = PI.objects.filter(is_ext = True)
    data = {'Compilatore': request.user, 'Data': timezone.now()}
    form = CopiaFabbForm(initial = data)
    if request.method == 'POST':
        form = CopiaFabbForm(request.POST, initial = data)
        if form.is_valid():
            att = form.save()
            f = att.FabbCopiato
            id_pi = att.ID_PianoInvestimenti
            att.Prezzo_acquisto = f.Prezzo_acquisto
            att.Prezzo_Noleggio = f.Prezzo_Noleggio
            att.Prezzo_Service = f.Prezzo_Service
            att.Costo_Presunto_NOIVA = f.Costo_Presunto_NOIVA
            att.Costo_Presunto_IVA = f.Costo_Presunto_IVA
            soglia = id_pi.Costo_Presunto_IVA # soglia investimenti
            # se speso = 0, controlla i prezzi presunti
            tot = 0
            if id_pi.Speso == 0:
                atts = MAIN.objects.filter(ID_PianoInvestimenti = id_pi)
                for a in atts:
                    if a.Costo_Presunto_IVA is not None:
                        tot += a.Costo_Presunto_IVA
                if tot + att.Costo_Presunto_IVA > soglia:
                    return HttpResponse('La richiesta supera il budget')
                elif tot + att.Costo_Presunto_IVA == soglia:
                    id_pi.is_full = True

            # se invece abbiamo speso qualcosa, controlla quando abbiamo speso
            else:
                stato = Sta.objects.get(Nome='Acquisizione')
                atts = MAIN.objects.filter(ID_PianoInvestimenti = id_pi).exclude(Stato = stato)
                for a in atts:
                    tot += att.Costo_Presunto_IVA
                if tot + att.Costo_Presunto_IVA > soglia - id_pi.Speso:
                    return HttpResponse('La richiesta supera il budget')
                elif tot + att.Costo_Presunto_IVA == soglia - id_pi.Speso:
                    id_pi.is_full = True
            
            id_pi.save()

            
            att.Mot1_1 = f.Mot1_1
            att.Mot1_2 = f.Mot1_2
            att.Mot1_3 = f.Mot1_3
            att.Mot2_1 = f.Mot2_1
            att.Mot2_2 = f.Mot2_2
            att.AggNota = f.AggNota
            att.Acquisto = f.Acquisto
            att.Noleggio = f.Noleggio
            att.Service = f.Service
            att.Tecnologico = f.Tecnologico
            att.Valutativo = f.Valutativo
            att.Temporaneo = f.Temporaneo
            att.Economico = f.Economico
            att.Gestionale = f.Gestionale
            att.NotaNoleggio = f.NotaNoleggio
            att.NecInfraSi = f.NecInfraSi
            att.NecInfraNO = f.NecInfraNO
            att.NecInfraNota = f.NecInfraNota
            att.SostNota = f.SostNota
            att.Simili = f.Simili
            att.NolMesi = f.NolMesi
            
            att.Compilatore = f.Compilatore
            att.Apparecchiatura = f.Apparecchiatura
            att.PercIVA = f.PercIVA
            att.Qta = f.Qta
            att.Data = timezone.now()
            att.def_stato()
            att.costo_presuntoNOIVA()
            current_year_atts = MAIN.objects.filter(Data__year = att.Data.strftime('%Y'))
            k = 0
            for year in current_year_atts:
                k += 1
                print(k)
            
            att.Progressivo = str(k)+'-'+str(att.Data.strftime('%Y'))
            altro = 'altro'
            att.save()


            return redirect(f'/home/{altro}')
        else:
            print(form.errors)
    context = {'form': form, 'fabbs': fabbs, 'pis': pis, 'tabFilter': tablfilter}
    return render(request, 'copiafabbisogno.html', context)


### NUOVA RICHIESTA URGENTE 

@login_required
def new_urgente(request):
    
    u = request.user

    sede=SeRep.objects.filter(Sede = u.Sede_Reparto.Sede, Reparto = u.Sede_Reparto.Reparto).first()
    sedi_disponibili=SeRep.objects.all()
    data = {'Compilatore': u, 'Sede_Reparto': sede if sede else 'nessuna sede trovata'}

    #controllo 
    print(f"Utente: {u.username}")
    print(f"Data: {data}")
    print(f"Sede_Reparto dell'utente: {u.Sede_Reparto}")
    if u.Sede_Reparto:
        print(f"Sede: {u.Sede_Reparto.Sede}, Reparto: {u.Sede_Reparto.Reparto}")
    sede = SeRep.objects.filter(Sede=u.Sede_Reparto.Sede, Reparto=u.Sede_Reparto.Reparto).first()
    print(f"Sede trovata: {sede}")
    #fine controllo 

    gruppo=request.user.Gruppo
    if not gruppo.FaIns:
        return HttpResponse('Non sei autorizzato')
    
    form1 = UrgenteRequestForm(initial=data)

    if request.method=='POST':
        form1 = UrgenteRequestForm(request.POST, initial=data)
        if form1.is_valid():
            urgent_req = form1.save(commit=False)
            print(f"DEBUG - Sede_Reparto salvata: {urgent_req.Sede_Reparto}")
            urgent_req.save()

            crea_stato_per_richiesta(urgent_req, request.user)
            print(f"Stato richiesta dopo assegnazione: {urgent_req.StatoRic}")  

            urgent_req.costo_presuntoNOIVA()
            current_year_atts = UrgenteRequest.objects.filter(Data__year = urgent_req.Data.strftime('%Y'))
            k = 0
            for year in current_year_atts:
                k += 1
            urgent_req.Progressivo = str(k)+'-'+str(urgent_req.Data.strftime('%Y'))
            urgent_req.save()
            request.session['urgent_req_id'] = urgent_req.id #?
            return redirect('new_urg_2_4', urgent_req.id) 
            
        else:
            form=UrgenteRequestForm()
            print('Form non valido')
            print(form1.errors)

    context={'form1': form1,
    'sedi_disponibili': sedi_disponibili}
    return render(request, 'new_urgente.html', context)

def new_urg_2_4(request, pk=None):
    # Recupera l'ID della richiesta urgente dalla sessione
    urgent_req_id = request.session.get('urgent_req_id')
    if urgent_req_id:
        # Se c'è un ID nella sessione, recuperiamo la richiesta urgente
        urgent_req = UrgenteRequest.objects.get(id=urgent_req_id)
    else:
        # Se non esiste, reindirizza alla prima pagina
        return redirect('new_urgente')
    
    #controllo
    if pk is None:
        pk=urgent_req_id
    if not pk: 
        return redirect('new_urgente')
    #fine controllo

    # Recupera le specifiche associate alla richiesta
    specs = SpecificheUrg.objects.filter(ID_rich=urgent_req)
    counter = specs.count() + 1  # Numero progressivo per la prossima specifica
 
    data = {'ID_rich': urgent_req_id,'rif': counter}
    #form = SpecificheUrgForm(initial=data)
    
    context={
        'pk':pk,
        'specs': specs,
        'urgent_req':urgent_req,
        'altro': 'altro'
    }

    if request.method=='POST':
        if 'save' in request.POST:
            form = SpecificheUrgForm(request.POST)
            if form.is_valid():
                spec=form.save(commit=False)
                spec.ID_rich=urgent_req
                spec.save()
                print('pk',pk)
                print('urgent_req_id',urgent_req_id)
                return redirect('new_urg_2_4', pk=urgent_req_id)
            else: 
                print(form.errors)
                context['form'] = form
    else:
        data={'ID_rich': urgent_req_id, 'rif': counter}
        form = SpecificheUrgForm(initial=data)
        context['form'] = form
            
        #if 'next' in request.POST:
        #    return redirect('new_urg_4e2', pk=urgent_req_id)
    
    return render(request, 'new_urg_2_4.html', context)

def new_urg_4e2(request, pk):

    if SpecificheUrg.objects.filter(ID_rich = pk).exists():
        specs = SpecificheUrg.objects.filter(ID_rich = pk)
        choicesp =[]
        lista =[]
        for spec in specs:
            if spec.Un:
                choicesp+=[(spec.id, str(spec.rif))]
                lista+=[spec.id]
    else :
        return redirect(f'/new_urg_4e3/{pk}/') 
    
    att = UrgenteRequest.objects.get(id=pk)
    data = {'ID_rich': pk}
    form = UnicitaUrgForm(initial=data)
    form.fields['rifext'].choices = choicesp

    if UnicitaUrg.objects.filter(rifext__in = lista).exists():
        uns=UnicitaUrg.objects.filter(rifext__in = lista)
        context={
            'att': att,
            'uns': uns,
        }   
    else:
        context = {
        'att': att,
        }  
   
    form = UnicitaUrgForm(initial = data)
    form.fields['rifext'].choices = choicesp
    unform = FormUrgUn(instance=att)
    UnFormSet = modelformset_factory(model = SpecificheUrg, fields = ('Un',), form = Unformurg, extra=0)
    unformset = UnFormSet(queryset = specs)

    if request.method=='POST':
        if 'Aggiungi' in request.POST:
            form = UnicitaUrgForm(request.POST, initial=data)
            form.fields['rifext'].choices = choicesp
            if form.is_valid():
                form.save()
                return redirect(f'/new_urg_4e2/{pk}/')
            else:
                print(form.errors)

        if 'Simili' in request.POST:
            unform = FormUrgUn(request.POST, instance=att)
            if unform.is_valid():
                att=unform.save()
                return redirect('new_urg_2_4', pk=pk) #DA CAPIRE LA LOGICA 
            else:
                print('Stupido')
                print(unform.errors)

        if 'Uni' in request.POST:
            unformset = UnFormSet(request.POST, queryset=specs)
            if unformset.is_valid():
                unformset.save()
                return redirect('new_urg_4e2', pk=pk)

    context = context | {'form': form, 
                         'unform':unform, 
                         'unformset': unformset,
                         'insieme': zip(specs, unformset), 
                         'altro': 'altro'}
    
    print("Lista Specifiche Unicità:", lista)
    print("Choicesp:", choicesp)
    #print("Oggetti UnicitaUrg (uns):", uns)

    return render(request, 'new_urg_4e2.html', context)

def new_urg_4e3(request, pk):
    s = SpecificheUrg.objects.all()
    counterspec = len(s)
    data = {'ID_rich': pk}
    form = CriteriUrgForm(initial=data)
    att = UrgenteRequest.objects.get(id=pk)
    counter = 1

    if CriteriUrg.objects.filter(ID_rich=pk).exists():
        crs=CriteriUrg.objects.filter(ID_rich=pk)
        s = 0
        for cr in crs:
            counter += 1
            s += cr.Peso

        if s != 100:
            b = True
        else:
            b=False
        context={
            'att': att,
            'crs': crs,
            'b': b,
            'counter': counterspec
        }   
    else:
        context = {
        'att': att,
        'counter': counterspec
        }  
    data = {'ID_rich': pk,'Rif': counter}
    form = CriteriUrgForm(initial=data)

    if request.method=='POST':
        form = CriteriUrgForm(request.POST, initial=data)
        if form.is_valid():
            form.save()
            return redirect('new_urg_4e3', pk=pk)
        
    context = context | {'form': form, 'altro': 'altro','pk':pk}
    return render(request, 'new_urg_4e3.html', context)

def new_urg_5(request,pk):
    att = UrgenteRequest.objects.get(id=pk)
    data = {'ID_rich': att}
    print(att)
    form = ConsumabiliUrgForm(initial=data)
    if ConsumabiliUrg.objects.filter(ID_rich=pk).exists():
        cons=ConsumabiliUrg.objects.filter(ID_rich=pk)
        context={
                'att': att,
                'form': form,
                'cons': cons,
                'altro': 'altro',
                
            }   
    if request.method=='POST':
            form = ConsumabiliUrgForm(request.POST, initial=data)
            if form.is_valid():
                con = form.save()
                con.Totale = con.CostoUnitario * con.ConsumoMedio
                con.save()
                return redirect(f'/new_urg_5/{pk}/')

            else:
                print(form.errors)

    return render(request, 'new_urg_5.html', context)


def new_urg_5e2(request, pk):
    #altro = 'altro'
    att = UrgenteRequest.objects.get(id=pk)
    init = {'ID_rich': pk}
    counter = 1

    form = DittaUrgForm(initial=init)
    if DittaUrg.objects.filter(ID_rich=pk).exists():
        ditte=DittaUrg.objects.filter(ID_rich=pk)
        for ditta in ditte:
            counter+=1
        context={
        'att': att,
        'ditte': ditte,
        }   
    else:
         context={
        'att': att,
        }  
         
    init = {'ID_rich': pk,'Rif': counter} #aggiorna il contatore per la nuova ditta
    form = DittaUrgForm(initial=init)
    if request.method=='POST':
        if "Aggiungi" in request.POST:            
            form = DittaUrgForm(request.POST, request.FILES, initial=init)
            if form.is_valid():
                form.save()
                return redirect('new_urg_5e2',pk=pk)
        if "Termina" in request.POST:
            return redirect('success_page', pk=pk)
    context |= context | {'form': form, 'altro': 'altro','pk':pk}
    return render(request, 'new_urg_5e2.html',context) 



