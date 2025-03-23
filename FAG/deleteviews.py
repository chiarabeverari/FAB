from django.http import HttpResponse
from .models import *
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from .settings import BASE_DIR
from django.contrib.auth.decorators import login_required, user_passes_test
import os


@login_required
def deleteattachements(request, pk, var=None):
    alle = Allegati.objects.get(id=pk)
   
    id_rich = alle.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = MAIN.objects.get(Progressivo = app)
    pk = att.id

    context = {'alle': alle, 
    'att': att,
    'var': var}
    relpath = alle.File.url
    abspath = str(BASE_DIR) + relpath
    
    if request.method == 'POST':
        alle.delete()
        os.remove(abspath)
        return redirect(f'/attachements/{pk}/{var}/')
    return render(request, 'eliminazioneallegati.html', context)

#DA IMPLEMENTARE 
#@login_required
# def deleteurg(request, pk):
#    alle = AllegatiUrg.objects.get(id=pk)
   
#    id_rich = alle.ID_rich
#    b = str(id_rich)
#    app = b.split("_")
#    app = app[0]
#    att = UrgenteRequest.objects.get(Progressivo = app)
#    pk = att.id

#    context = {'alle': alle, 
#    'att': att,
#    }
#    relpath = alle.File.url
#    abspath = str(BASE_DIR) + relpath
    
#    if request.method == 'POST':
#        alle.delete()
#        os.remove(abspath)
#        return redirect(f'/attachements/{pk}/')
#    return render(request, 'eliminazioneallegati.html', context)

@login_required
def deletespecifiche(request, pk, var=None):
    specs = Specifiche.objects.get(id=pk)
    id_rich = specs.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = MAIN.objects.get(Progressivo = app)
    pk = att.id
    specs.delete()
    return redirect(f'/new_2_4/{pk}/{var}')

@login_required
def deletespecificheurg(request, pk):
    specs = SpecificheUrg.objects.get(id=pk)
    id_rich= specs.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = UrgenteRequest.objects.get(Progressivo = app)
    pk = att.id
    specs.delete()
    return redirect('new_urg_2_4', pk=id_rich.id)
    
@login_required
def deleteunicita(request, pk, var=None):
    uns = Unicita.objects.get(id=pk)
    id_rich = uns.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = MAIN.objects.get(Progressivo = app)
    pk = att.id
    uns.delete()
    return redirect(f'/new_4e2/{pk}/{var}//')

@login_required
def deleteunicitaurg(request, pk):
    uns = UnicitaUrg.objects.get(id=pk)
    id_rich = uns.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = UrgenteRequest.objects.get(Progressivo = app)
    pk = att.id
    uns.delete()
    return redirect('new_urg_4e2',pk=pk)

@login_required
def deletecriteri(request, pk, var):
    cr = Criteri.objects.get(id=pk)
    id_rich = cr.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = MAIN.objects.get(Progressivo = app)
    pk = att.id
    cr.delete()
    return redirect(f'/new_4e3/{pk}/{var}//')

@login_required
def deletecriteriurg(request, pk):
    cr = CriteriUrg.objects.get(id=pk)
    id_rich = cr.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = UrgenteRequest.objects.get(Progressivo = app)
    pk = att.id
    cr.delete()
    return redirect('new_urg_4e3', pk=id_rich.id)

@login_required
def deleteconsu(request, pk, var):
    gruppo = request.user.Gruppo
    

    if var=='1' or var=='2':
        
        con = ConsumabiliFabb.objects.get(id=pk)
        id_rich = con.ID_rich
        fabb = Fabbisogni.objects.get(Progressivo = id_rich)
        if not gruppo.SpMoTu and gruppo.SpMoPr:
            if fabb.Compilatore != request.user:
                return HttpResponse('Non sei autorizzato')
        elif not gruppo.SpMoTu and not gruppo.SpMoPr:
            return HttpResponse('Non sei autorizzato')
        con.delete()
        return redirect(f'/new_5/{fabb.id}/{var}/')

    else:
        con = ConsumabiliMain.objects.get(id=pk)
        id_rich = con.ID_rich
        b = str(id_rich)
        app = b.split("_")
        app = app[0]
        att = MAIN.objects.get(Progressivo = app)
        pk = att.id
        con.delete()
        return redirect(f'/new_5/{pk}/{var}//')
    
@login_required
def deleteconsuurg(request, pk):
    gruppo = request.user.Gruppo
    con = ConsumabiliUrg.objects.get(id=pk)
    id_rich = con.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = UrgenteRequest.objects.get(Progressivo = app)
    pk = att.id
    con.delete()
    return redirect(f'/new_5/{pk}/')

@login_required
def deleteditta(request, pk, var):
    gruppo = request.user.Gruppo
    if not (gruppo.Mod):
        return HttpResponse('Non sei autorizzato')
    d = Ditta.objects.get(id=pk)
    id_rich = d.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = MAIN.objects.get(Progressivo = app)
    pk = att.id
    d.delete()
    return redirect(f'/new_5e2/{pk}/{var}//')

@login_required
def deletedittaurg(request, pk):
    gruppo = request.user.Gruppo
    if not (gruppo.Mod):
        return HttpResponse('Non sei autorizzato')
    d = DittaUrg.objects.get(id=pk)
    id_rich = d.ID_rich
    b = str(id_rich)
    app = b.split("_")
    app = app[0]
    att = UrgenteRequest.objects.get(Progressivo = app)
    pk = att.id
    d.delete()
    return redirect(f'/new_5e2/{pk}/')

@login_required
def eliminazioneDoc(request, pk, var):
   
    if var == '5':
        doc = DocGara.objects.get(id=pk)

    elif var == '6':
        doc = DocComm.objects.get(id=pk)
    
    elif var == '7':
        doc = DocAgg.objects.get(id=pk)
        
    elif var == '8':
        doc = DocTrasp.objects.get(id=pk)
       
    elif var == '9':
        doc = DocColl.objects.get(id=pk)
        
    idrich = doc.ID_rich
    b = str(idrich)
    app = b.split("_")
    app = app[0]
    att = MAIN.objects.get(Progressivo = app)
    stato = att.Stato.Numero
    print(doc.File)
    try:
        relpath = doc.File.url
        abspath = str(BASE_DIR) + relpath
        os.remove(abspath)
    except:
        pass
    doc.delete()
    return redirect(f'/aggiungidocumenti/{att.id}/{stato}/')


@login_required
def deletesedereparti(request, pk):
    gruppo = request.user.Gruppo
    if not gruppo.UbMod:
        return HttpResponse('Non sei autorizzato')
    s = SeRep.objects.get(id=pk)
   
    context = {'s' : s}
    if request.method == 'POST':
        s.delete()
        return redirect('/sedereparti/')
    return render(request, 'eliminazionesedereparti.html', context)    

@login_required
def deletepriorita(request, pk, var):
    gruppo = request.user.Gruppo
    if var == '1':
        if not(gruppo.PrMod):
            return HttpResponse('Non sei autorizzato')
        s = Priorita.objects.get(id=pk)
    elif var == '2':
        s = Gruppi.objects.get(id=pk)
    elif var == '3':
        s = Professioni.objects.get(id=pk)
    s.delete()
   
    return redirect('/priorita/')

@login_required
def cancellatutto(request):
    notifiche = Notifiche.objects.filter(User = request.user)
    for notifica in notifiche:
        notifica.delete()
    return redirect('useraccount')

@login_required
def rimuovi(request, pk):
    gruppo = request.user.Gruppo
    att = Fabbisogni.objects.get(id = pk)
    if not(gruppo.FaMoTu) and gruppo.FaMoPr:
        if request.user != att.Compilatore:
            return HttpResponse('Non sei autorizzato')
    elif not(gruppo.FaMoTu) and not(gruppo.FaMoPr):
        return HttpResponse('Non sei autorizzato')
    
    context = {'att': att, 'altro': 'altro'}
    if request.method == 'POST':
        att.Eliminato = True
        att.save()
        return redirect('/raccoltafabbisogni/')
    return render(request, 'rimuovi.html', context)

@login_required
def rimuoviurg(request, pk):
    gruppo = request.user.Gruppo
    att = UrgenteRequest.objects.get(id = pk)
    if not(gruppo.FaMoTu) and gruppo.FaMoPr:
        if request.user != att.Compilatore:
            return HttpResponse('Non sei autorizzato')
    elif not(gruppo.FaMoTu) and not(gruppo.FaMoPr):
        return HttpResponse('Non sei autorizzato')
    
    context = {'att': att, 'altro': 'altro'}
    if request.method == 'POST':
        att.Eliminato = True
        att.save()
        return redirect('/raccoltafabbisogni/')
    return render(request, 'rimuoviurg.html', context)

@login_required
def rimuoviPI(request, pk):
    gruppo = request.user.Gruppo
    if not gruppo.PIMod:
        return HttpResponse('<html>Non sei autorizzato ad eseguire questa operazione</html>')
    pi = PI.objects.get(id = pk)
    pi.delete()
    return redirect('/pianodiinvestimenti/')

@login_required
def rimuoviuser(request, pk):
    profilo = MedicalUser.objects.get(id=pk)
    context = {'profilo': profilo}
    if request.method == 'POST':
        profilo.delete()
        return redirect('tuttiprofili')
    return render(request, 'rimuoviutente.html', context)

@login_required
def rimuovirichiesta(request, pk):
    gruppo = request.user.Gruppo
    att = MAIN.objects.get(id = pk)
    if not(gruppo.SpMoTu) and gruppo.SpMoPr:
        if request.user != att.Compilatore:
            return HttpResponse('Non sei autorizzato')
    elif not(gruppo.SpMoTu) and not(gruppo.SpMoPr):
        return HttpResponse('Non sei autorizzato')
    
    pi = PI.objects.get(ID_PianoInvestimenti = att.ID_PianoInvestimenti)
    
    pi.is_full = False
    pi.save()
    att.delete()
    altro = 'altro'
    return redirect(f'/home/{altro}')
 