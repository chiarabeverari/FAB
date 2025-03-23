from .models import *
from .forms import *
from .service import *
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
import pandas as pd
from .filters import *
from PyPDF2 import PdfFileReader, PdfFileWriter
from .crea_da_pdf import *
from django.contrib.auth.decorators import login_required, user_passes_test
import os
import shutil
from django.core.files.base import ContentFile
import fitz
from io import BytesIO
from django.utils import timezone

from .settings import BASE_DIR

@login_required
def sedereparti(request):

    gruppo = request.user.Gruppo
    print(gruppo.UbVe)
    if not gruppo.UbVe:
        return HttpResponse('Non sei autorizzato')
    formsedi = SeRepForm()
    sedi = SeRep.objects.all() 
    filter = SeRepFilter(request.GET, queryset=sedi)
    sedi  = filter.qs

    if request.method == "POST":
        if 'Aggiungi' in request.POST:
            formsedi = SeRepForm(request.POST)
            if gruppo.UbIns and formsedi.is_valid():
                formsedi.save()
                return redirect('/sedereparti/')

        if 'DaExcel' in request.POST:
            if not gruppo.UbIns:
                return HttpResponse('Non sei autorizzato')
            File = request.FILES['myFile']
            excel = pd.read_excel(File)
            col = excel.columns.values.tolist()
            if col != ['Sede', 'Reparto', 'Sub-Reparto', 'CDC']:
                return HttpResponse("Il formato non è corretto. Il file excel deve avere quattro colonne 'Sede', 'Reparto', 'Sub-Reparto' e 'CDC' citate nella prima riga dell'elenco. <a href='/sedereparti'>Torna indietro </a>")
            else:
                rn = len(excel.index)
                for i in range(0, rn):
                    try:
                        SeRep.objects.get(Sede = excel.at[i, 'Sede'], Reparto = excel.at[i, 'Reparto'], Sub_Reparto = excel.at[i, 'Sub-Reparto'], CDC = excel.at[i, 'CDC'])
                    except:    
                        sr = SeRep(Sede = excel.at[i, 'Sede'], Reparto = excel.at[i, 'Reparto'], Sub_Reparto = excel.at[i, 'Sub-Reparto'], CDC = excel.at[i, 'CDC'])
                        sr.save()
            return redirect('/sedereparti/')
    context = {
        'k': 1,
        'filter': filter,
        'sedi': sedi
    }
    if gruppo.UbIns:
        context = context | {'form': formsedi}
    return render(request, 'sedereparti.html', context)

@login_required
def serepreg(request):
    gruppo = request.user.Gruppo
    print(gruppo.UbVe)
    if not gruppo.UbVe:
        return HttpResponse('Non sei autorizzato')
    formsedi = SeRepRegForm()
    sedi = SeRepReg.objects.all() 
    filter = SeRepRegFilter(request.GET, queryset=sedi)
    sedi  = filter.qs

    if request.method == "POST":
        if 'Aggiungi' in request.POST:
            formsedi = SeRepRegForm(request.POST)
            if gruppo.UbIns and formsedi.is_valid():
                formsedi.save()
                return redirect('/serepreg/')

        if 'DaExcel' in request.POST:
            if not gruppo.UbIns:
                return HttpResponse('Non sei autorizzato')
            File = request.FILES['myFile']
            excel = pd.read_excel(File)
            col = excel.columns.values.tolist()
            if col != ['Sede', 'Reparto']:
                return HttpResponse("Il formato non è corretto. Il file excel deve avere quattro colonne 'Sede', 'Reparto' citate nella prima riga dell'elenco. <a href='/serepreg'>Torna indietro </a>")
            else:
                rn = len(excel.index)
                for i in range(0, rn):
                    try:
                        SeRepReg.objects.get(Sede = excel.at[i, 'Sede'], Reparto = excel.at[i, 'Reparto'])
                    except:    
                        sr = SeRepReg(Sede = excel.at[i, 'Sede'], Reparto = excel.at[i, 'Reparto'])
                        sr.save()
            return redirect('/serepreg/')
    context = {
        'k': 1,
        'filter': filter,
        'sedi': sedi
    }
    if gruppo.UbIns:
        context = context | {'form': formsedi}
    return render(request, 'sedereparti_registrazione.html', context)

'''
@login_required
def nuova(request):
    gruppo = request.user.Gruppo
    if not gruppo.FaIns:
        return HttpResponse('Non sei autorizzato')
    form = NuovaRichiestaForm()
    opt = 1
    if request.method=='POST':
        form = NuovaRichiestaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            uploaded_filename = request.FILES['File'].name
            full_filename = os.path.join(BASE_DIR, 'media/media', uploaded_filename)
            try:
                f = PdfFileReader(full_filename)
            except:
                return HttpResponse('Il file non è stato nominato correttamente. evitare spazi. <a href="/nuova">Torna indietro </a>')
            fields = f.getFields()
            fdfinfo = dict((k, v.get('/V', '')) for k, v in fields.items())
            k = crea_da_pdf1(request, fdfinfo)
            nr = NuovaRichiesta.objects.all()
            nr.delete()
            os.remove(full_filename)
            return redirect('raccoltafabbisogni') 
    context={'form':form, 'opt': opt}
    return render(request, 'nuova.html', context)'
'''

@login_required
def nuova(request): #cambiata con fitz 
    gruppo = request.user.Gruppo
    if not gruppo.FaIns:
        return HttpResponse('Non sei autorizzato')

    form = NuovaRichiestaForm()
    opt = 1

    if request.method == 'POST':
        form = NuovaRichiestaForm(request.POST, request.FILES)

        if form.is_valid():
            nuova_richiesta = form.save(commit=False) 
            nuova_richiesta.save()  

            uploaded_file = request.FILES.get('File')

            if not uploaded_file:
                return HttpResponse('Errore: nessun file caricato. <a href="/nuova">Torna indietro </a>')

            # Salva il file temporaneamente
            file_path = os.path.join(BASE_DIR, 'media/media', uploaded_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            try:
                pdf_document = fitz.open(file_path)
            except Exception as e:
                return HttpResponse(f'Errore nell\'apertura del PDF: {str(e)} <a href="/nuova">Torna indietro </a>')

            # Estrai i campi del modulo PDF
            fields = {}
            for page in pdf_document:
                for widget in page.widgets():
                    if widget.field_name:
                        fields[widget.field_name] = widget.field_value

            pdf_document.close()

            if not fields:
                return HttpResponse('Errore: il file non contiene campi modulo validi. <a href="/nuova">Torna indietro </a>')

            # Crea l'oggetto da PDF con i dati letti
            crea_da_pdf1(request, fields)

            # Rimuove la richiesta temporanea e il file PDF
            NuovaRichiesta.objects.all().delete()
            os.remove(file_path)

            return redirect('raccoltafabbisogni')

    context = {'form': form, 'opt': opt}
    return render(request, 'nuova.html', context)

@login_required
def aggiungi_fabbisogno_urgente(request): #fatta con fitz
    gruppo = request.user.Gruppo
    if not gruppo.FaIns:
        return HttpResponse('Non sei autorizzato')

    form = NuovaRichiestaForm() #ok
    #opt = 1

    if request.method == 'POST':
        form = NuovaRichiestaForm(request.POST, request.FILES)

        if form.is_valid():
            nuova_richiesta = form.save(commit=False) 
            nuova_richiesta.save()  

            uploaded_file = request.FILES.get('File')

            if not uploaded_file:
                return HttpResponse('Errore: nessun file caricato. <a href="/nuova">Torna indietro </a>')

            # Salva il file temporaneamente
            file_path = os.path.join(BASE_DIR, 'media/media', uploaded_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            try:
                pdf_document = fitz.open(file_path)
            except Exception as e:
                return HttpResponse(f'Errore nell\'apertura del PDF: {str(e)} <a href="/nuova">Torna indietro </a>')

            # Estrai i campi del modulo PDF
            fields = {}
            for page in pdf_document:
                for widget in page.widgets():
                    print(f"Campo trovato: {widget.field_name}")
                    if widget.field_name:
                        fields[widget.field_name] = widget.field_value

            pdf_document.close()

            if not fields:
                return HttpResponse('Errore: il file non contiene campi modulo validi. <a href="/nuova">Torna indietro </a>')

            # Crea l'oggetto da PDF con i dati letti
            crea_da_pdf1urg(request, fields)

            # Rimuove la richiesta temporanea e il file PDF
            NuovaRichiesta.objects.all().delete()
            os.remove(file_path)

            return redirect('raccoltafabbisogni')

    context = {'form': form, }
    return render(request, 'aggiungi_fabbisogno_urgente.html', context)
'''
@login_required
def aggiungi_fabbisogno_urgente(request): #fatta con fitz 
    if request.method == 'POST' and request.FILES.get('FileModuloRichiestaFirmato'):
        file=request.FILES['FileModuloRichiestaFirmato']
        form = UrgenteRequestForm(request.POST, request.FILES)
        if form.is_valid():
            richiesta = form.save(commit=False)
            file = request.FILES['FileModuloRichiestaFirmato']
            richiesta.FileModuloRichiestaFirmato = file
            richiesta.save()

            # Estrarre i dati dal PDF
            extracted_data = extract_pdf_data(file)
            print("Dati estratti:", extracted_data)

            if extracted_data:  # Assicurati che i dati vengano effettivamente estratti
                richiesta.Progressivo = extracted_data.get("Progressivo", richiesta.Progressivo)
                richiesta.Sede_Reparto = extracted_data.get("Sede_Reparto", richiesta.Sede_Reparto)
                richiesta.Apparecchiatura = extracted_data.get("Apparecchiatura", richiesta.Apparecchiatura)
                richiesta.Qta = extracted_data.get("Qta", richiesta.Qta)
                richiesta.Priorita = extracted_data.get("Priorita", richiesta.Priorita)
                richiesta.Costo_Presunto_NOIVA = extracted_data.get("Costo_Presunto_NOIVA", richiesta.Costo_Presunto_NOIVA)
                richiesta.Costo_Presunto_IVA = extracted_data.get("Costo_Presunto_IVA", richiesta.Costo_Presunto_IVA)
                richiesta.Compilatore = extracted_data.get("Compilatore", richiesta.Compilatore)
                richiesta.ID_PianoInvestimenti = extracted_data.get("ID_PianoInvestimenti", richiesta.ID_PianoInvestimenti)

                richiesta.save()
                print('richiesta salvata con successo')

            return redirect('pagina_ricerca')  # Redirect corretto
        else:
            print('errore nel form', form.errors)

    else:
        form = UrgenteRequestForm()


    return render(request, 'aggiungi_fabbisogno_urgente.html', {'form': form})
    '''

@login_required
def completa_richiesta(request, pk):
    gruppo = request.user.Gruppo
    att=MAIN.objects.get(id = pk)
    if (not gruppo.SpMoTu) and (gruppo.SpMoPr):
        if not att.Compilatore == request.user:
            return HttpResponse('Non sei autorizzato')
    form = NuovaRichiestaForm()
    var = 3
    opt = 2
    if request.method == "POST":
        form = NuovaRichiestaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            File = request.FILES['File'].name
            print(File)
            full_filename = os.path.join(BASE_DIR, 'media/media', File)
            try:
                f = PdfFileReader(full_filename)
            except:
                return HttpResponse(f'<html> Riprovare nominando diversamente il file. Togliere eventuali parentesi e spazi dal nome del file e riprovare. <a href="/completa_richiesta/{pk}">Torna indietro </a> </html>')
            fields = f.getFields()
            fdfinfo = dict((k, v.get('/V', '')) for k, v in fields.items())
            k = crea_da_pdf2(request, fdfinfo, pk)
            if k == 1:
                return HttpResponse(f'<html> La compilazione del modulo non è avvenuta correttamente. Potrebbero essere presenti uno dei seguenti errori: <br> <ul> <li>Le specifiche possono essere di minima (m) o di massima (M). </li></ul> <a href="/completa_richiesta/{pk}">Torna indietro </a> </html>')
            nr = NuovaRichiesta.objects.all()
            
            nr.delete()
            
            os.remove(full_filename)
          
            
       

    context ={'att': att, 'var':var, 'form': form, 'opt':opt}
    return render(request, "completa_richiesta.html", context)

@login_required
def downloadfilledpdf(request, pk):
    file = compila_pdf(pk)
    response = HttpResponse(file.getvalue(), content_type='application/force-download')
    response['Content-Disposition'] = 'inline; filename="completed.pdf"'
    return response

@login_required    
def aggiungidocumenti(request, pk, stato):
    gruppo = request.user.Gruppo
    if not gruppo.GaFlu:
        return HttpResponse('Non sei autorizzato')
    data = {'ID_rich': pk}
    att = MAIN.objects.get (id =pk)
    context = {'stato': stato}

    if stato == '5':
        form = DocGaraForm(initial = data)
        objects = DocGara.objects.filter(ID_rich = pk)

        if request.method == 'POST':
            form = DocGaraForm(request.POST, request.FILES, initial = data)
            if form.is_valid():
                form.save()
            return redirect(f'/aggiungidocumenti/{pk}/{stato}')
    
    if stato == '6':
        form = DocCommForm(initial = data)
        objects = DocComm.objects.filter(ID_rich = pk)
        if request.method == 'POST':
            form = DocCommForm(request.POST, request.FILES, initial = data)
            if form.is_valid():
                form.save()
            return redirect(f'/aggiungidocumenti/{pk}/{stato}/')
    
    if stato == '7':
        form = DocAggForm(initial = data)
        objects = DocAgg.objects.filter(ID_rich = pk)
        if request.method == 'POST':
            form = DocAggForm(request.POST, request.FILES, initial = data)
            if form.is_valid():
                form.save()
            return redirect(f'/aggiungidocumenti/{pk}/{stato}/')
                
    
    if stato == '8':
        form = DocTraspForm(initial = data)
        objects = DocTrasp.objects.filter(ID_rich = pk)
        if request.method == 'POST':
            form = DocTraspForm(request.POST, request.FILES, initial = data)
            if form.is_valid():
                form.save()
            return redirect(f'/aggiungidocumenti/{pk}/{stato}/')

    if stato == '9':
        form = DocCollForm(initial = data)
        objects = DocColl.objects.filter(ID_rich = pk)
        if request.method == 'POST':
            form = DocCollForm(request.POST, request.FILES, initial = data)
            if form.is_valid():
                form.save()
            return redirect(f'/aggiungidocumenti/{pk}/{stato}/')
    
    context = context | {'form': form, 'objects': objects}
    return render(request, 'aggiungidocumenti.html', context)


