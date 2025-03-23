from re import M
from tkinter import EW
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from .models import *
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject, NumberObject
from PyPDF2 import PdfFileReader, PdfFileWriter
from pdfrw import *
from io import BytesIO
from django.utils import timezone
import os
import fitz
from .settings import BASE_DIR
import PyPDF2
import io
import uuid
import fitz #PyMuPDF

def crea_da_pdf1(request, fdfinfo): #nuovo fabbisogno
    att = Fabbisogni()
    print(fdfinfo)
    try: #recupera sede e reparto dell'utente corrente 
        sede = SeRep.objects.filter(Sede = request.user.Sede_Reparto.Sede, Reparto = request.user.Sede_Reparto.Reparto)
        att.Sede_Reparto = sede[0]
    except:
        pass
    #popola i campi principali di att con i dati forniti 
    att.Compilatore = request.user
    att.Direttore = fdfinfo['Direttore']
    att.Apparecchiatura = fdfinfo['Apparecchiatura']
    
    att.Qta = int(fdfinfo['Qta'])
    
    #gestione delle opzioni di acquisto, noleggio o servizio
    if fdfinfo['Acquisto'] != '':
        att.Acquisto = True
        att.Prezzo_acquisto = int(fdfinfo['Prezzo_acquisto'])
    elif fdfinfo['Noleggio'] != '':
        att.Noleggio = True
        if fdfinfo['Prezzo'] != '':
            att.Prezzo_Noleggio = int(fdfinfo['Prezzo'])
            try:
                att.NolMesi = int(fdfinfo['NolMesi'])
            except:
                pass
    elif fdfinfo['Service'] != '':
        att.Service = True
        if fdfinfo['Prezzo'] != '':
            att.Prezzo_Service = int(fdfinfo['Prezzo'])
            try:
                att.NolMesi = int(fdfinfo['NolMesi'])
            except:
                pass
    #setta i flag per i vari tipi di fabbisogno
    if fdfinfo['Tecnologico'] != '':
        att.Tecnologico = True
    if fdfinfo['Valutativo'] != '':
        att.Valutativo = True    
    if fdfinfo['Temporaneo'] != '':
        att.Temporaneo = True
    if fdfinfo['Economico'] != '':
        att.Economico = True
    if fdfinfo['Gestionale'] != '':
        att.Gestionale = True

    #gestione delle necessità infrastrutturale 
    if fdfinfo['NecInfraNO'] != '':
        att.NecInfraNO = True
        att.NecInfraSi = False
        att.NecInfraNota = fdfinfo['NecInfraNota']
    elif fdfinfo['NecInfraSI'] != '':
        att.NecInfraSi = True
        att.NecInfraNO = False

    #altri dettagli del fabbisogno
    att.NotaNoleggio = fdfinfo['NotaNoleggio']
    att.Data = timezone.now()

    #recupera la priorità se esiste
    try:
        pr = Priorita.objects.get(Numero = fdfinfo['Priorita'])
        att.Priorita = pr
    except:
        pass
    att.Anno_Previsto = fdfinfo['Anno_Previsto']

    #gestione aliquota IVA 
    try:
        att.PercIVA = int(fdfinfo['PercIVA'])
    except:
        att.PercIVA = 0
    att.DescrMass = fdfinfo['DescrMass']

    #gestione della necessità di nuovo personale 
    if fdfinfo['NecPersSI'] != '':
        att.NewPersSI = True
    elif fdfinfo['NecPersNO'] != '' :
        att.NewPersNO = True

    #gestione delle motivazioni
    if fdfinfo['Mot1_1'] != '' :
        att.Mot1_1 = True
        att.SostNota = fdfinfo['SostNota']
    if fdfinfo['Mot1_2'] != '' :
        att.Mot1_2 = True
    if fdfinfo['Mot1_3'] != '' :
        att.Mot1_3 = True
    if fdfinfo['Mot2_1'] != '' :
        att.Mot2_1 = True
    if fdfinfo['Mot2_2']!= '' :
        att.Mot2_2 = True
    att.AggNota = fdfinfo['AggNota']
    att.Fonte = fdfinfo['Fonte']

    #calcola il progressivo basato sull'anno 
    current_year_atts = Fabbisogni.objects.filter(Data__year = att.Data.strftime('%Y'))
    k = 1
    for year in current_year_atts:
        k += 1
    att.Progressivo = str(k)+'-'+str(att.Data.strftime('%Y'))
 
    att.costo_presuntoNOIVA() #calcola il costo presunto senza IVA
    att.save()

    # aggiunge lo stato predefinito
    stato = RichiestaStato.objects.create(
        StatoRic=StatoRichiesta.BOZZA,
        content_type=ContentType.objects.get_for_model(att),
        object_id=att.id,
        utente=request.user  # Assegna l'utente corrente come 'utente' dello stato
    )
    att.StatoRic = stato  # Associa lo stato appena creato alla richiesta
    att.save()  # Salva di nuovo per assicurarti che lo stato venga associato

    #gestione dei consumabili associati
    listatipo = ['tipo1', 'tipo2', 'tipo3', 'tipo4', 'tipo5', 'tipo6']
    listacu = ['CostoUnitario1', 'CostoUnitario2', 'CostoUnitario3', 'CostoUnitario4', 'CostoUnitario5', 'CostoUnitario6']
    listacm = ['ConsumoMedio1', 'ConsumoMedio2', 'ConsumoMedio3', 'ConsumoMedio4', 'ConsumoMedio5', 'ConsumoMedio6' ]
    listatot = ['Totale1', 'Totale2', 'Totale3', 'Totale4', 'Totale5', 'Totale6']
    listaper = ['Periodo1', 'Periodo2','Periodo3','Periodo4','Periodo5','Periodo6']

    #gestione di un massimo di 16 consumabili 
    for i in range(0,16):
        try:
            if fdfinfo[listatipo[i]] != '':
                
                c = ConsumabiliFabb()
                c.ID_rich = att
                c.Tipo = fdfinfo[listatipo[i]]
                print(fdfinfo[listatipo[i]])
                print(int(fdfinfo[listacu[i]]))
                c.CostoUnitario = int(fdfinfo[listacu[i]])
                c.ConsumoMedio = int(fdfinfo[listacm[i]])
                c.Periodo = int(fdfinfo[listaper[i]])
                c.Totale = c.ConsumoMedio * c.CostoUnitario / c.Periodo
                c.save()#salva il consumabile 
                print(c)
        except:
            pass

def crea_da_pdf1urg(request, fdfinfo):
    print(fdfinfo)
    att = UrgenteRequest()
    # INFO GENERALI
    try: #recupera sede e reparto dell'utente corrente 
        sede = SeRep.objects.filter(Sede = request.user.Sede_Reparto.Sede, Reparto = request.user.Sede_Reparto.Reparto)
        att.Sede_Reparto = sede[0]
    except:
        pass
    att.Compilatore = request.user
    att.Direttore = fdfinfo['Direttore']
    att.Apparecchiatura = fdfinfo['Apparecchiatura']
    att.Qta = int(fdfinfo['Qta'])
    
    #calcola il progressivo basato sull'anno 
    current_year_atts = Fabbisogni.objects.filter(Data__year = att.Data.strftime('%Y'))
    k = 1
    for year in current_year_atts:
        k += 1
    att.Progressivo = str(k)+'-'+str(att.Data.strftime('%Y'))


    if fdfinfo['Acquisto'] != '':
        att.Acquisto = True
        att.Prezzo_acquisto = int(fdfinfo['Prezzo_acquisto'])
    elif fdfinfo['Noleggio']  != '':
        att.Noleggio = True
        if fdfinfo['Prezzo'] != '':
            att.Prezzo_Noleggio = int(fdfinfo['Prezzo'])
        try:
            att.NolMesi = int(fdfinfo['NolMesi'])
        except:
            pass
    elif fdfinfo['Service']!= '':
        att.Service = True
        if fdfinfo['Prezzo'] != '':
            att.Prezzo_Service = int(fdfinfo['Prezzo'])
        try:
            att.NolMesi = int(fdfinfo['NolMesi'])
        except:
            pass

    if fdfinfo['Tecnologico'] != '':
        att.Tecnologico = True
    if fdfinfo['Valutativo'] != '':
        att.Valutativo = True    
    if fdfinfo['Temporaneo'] != '':
        att.Temporaneo = True
    if fdfinfo['Economico'] != '':
        att.Economico = True
    if fdfinfo['Gestionale'] != '':
        att.Gestionale = True

    if fdfinfo['NecInfraNO'] != '':
        att.NecInfraNO = True
        att.NecInfraSi = False
        att.NecInfraNota = fdfinfo['NecInfraNota']
    elif fdfinfo['NecInfraSI'] != '':
        att.NecInfraSi = True
        att.NecInfraNO = False

    att.NotaNoleggio = fdfinfo['NotaNoleggio']
    att.Data = timezone.now()
    att.Anno_Previsto = fdfinfo['Anno_Previsto']

    try:
        att.PercIVA = int(fdfinfo['PercIVA'])
    except:
        att.PercIVA = 0

    if fdfinfo['Mot1_1'] != '' :
        att.Mot1_1 = True
        att.SostNota = fdfinfo['SostNota']
    if fdfinfo['Mot1_2'] != '' :
        att.Mot1_2 = True
    if fdfinfo['Mot1_3'] != '' :
        att.Mot1_3 = True
    if fdfinfo['Mot2_1'] != '' :
        att.Mot2_1 = True
    if fdfinfo['Mot2_2'] != '':
        att.Mot2_2 = True
    att.AggNota = fdfinfo['AggNota']

    att.costo_presuntoNOIVA()
    att.save()

    # aggiunge lo stato predefinito
    stato = RichiestaStato.objects.create(
        StatoRic=StatoRichiesta.BOZZA,
        content_type=ContentType.objects.get_for_model(att),
        object_id=att.id,
        utente=request.user  
    )
    att.StatoRic = stato  
    att.save()  
    
     # SPECIFICHE
    listaspecifiche = ['Spec1', 'Spec2', 'Spec3', 'Spec4', 'Spec5', 'Spec6', 'Spec7', 'Spec8', 'Spec9', 'Spec10', 'Spec11', 'Spec12', 'Spec13', 'Spec14', 'Spec15', 'Spec16']
    listaun = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9', 'U10', 'U11', 'U12', 'U13', 'U14', 'U15', 'U16']
    listamotivi = ['MotivoClinico1', 'MotivoClinico2', 'MotivoClinico3', 'MotivoClinico4', 'MotivoClinico5', 'MotivoClinico6', 'MotivoClinico7', 'MotivoClinico8', 'MotivoClinico9', 'MotivoClinico10', 'MotivoClinico11', 'MotivoClinico12', 'MotivoClinico13', 'MotivoClinico14', 'MotivoClinico15', 'MotivoClinico16']
    listamM = ['MinMax1', 'MinMax2', 'MinMax3', 'MinMax4', 'MinMax5', 'MinMax6', 'MinMax7', 'MinMax8', 'MinMax9', 'MinMax10', 'MinMax11', 'MinMax12', 'MinMax13', 'MinMax14', 'MinMax15', 'MinMax16']
    # UNICITA'
    listanote = ['Nota1', 'Nota2', 'Nota3', 'Nota4']
    listarif = ['rif1', 'rif2', 'rif3', 'rif4']

    print(fdfinfo)
    
    for i in range(0,14):
        if fdfinfo[listaspecifiche[i]] != '':
            s = SpecificheUrg()
            s.ID_rich = att
            s.Specifica = fdfinfo[listaspecifiche[i]]
            s.MotivoClinico = fdfinfo[listamotivi[i]]
            if fdfinfo[listaun[i]] != '':
                s.Un = True
            s.rif = i+1
            if fdfinfo[listamM[i]] == 'm':
                s.Min = True
                s.Max = False
            elif fdfinfo[listamM[i]] == 'M':
                s.Max = True
                s.Min = False
            else:
                print('specifiche')
                return 1
            s.save()
            if s.Un == True:
                for j in range(0, 4):
                    if fdfinfo[listarif[j]] != '' and int(fdfinfo[listarif[j]]) == i+1:
                        un=UnicitaUrg()
                        un.ID_rich = att
                        un.rifext = s
                        un.Nota = fdfinfo[listanote[j]]
                        un.save()
    # CONSUMABILI
    listatipo = ['Tipo1', 'Tipo2', 'Tipo3', 'Tipo4', 'Tipo5', 'Tipo6', 'Tipo7', 'Tipo8', 'Tipo9', 'Tipo10', 'Tipo11', 'Tipo12', 'Tipo13', 'Tipo14', 'Tipo15', 'Tipo16']
    listacu = ['CostoUnitario1', 'CostoUnitario2', 'CostoUnitario3', 'CostoUnitario4', 'CostoUnitario5', 'CostoUnitario6',
    'CostoUnitario7', 'CostoUnitario8', 'CostoUnitario9', 'CostoUnitario10', 'CostoUnitario11', 'CostoUnitario12', 'CostoUnitario13', 'CostoUnitario14', 'CostoUnitario15', 'CostoUnitario16']
    listacm = ['ConsumoMedio1', 'ConsumoMedio2', 'ConsumoMedio3', 'ConsumoMedio4', 'ConsumoMedio5', 'ConsumoMedio6',
    'ConsumoMedio7', 'ConsumoMedio8', 'ConsumoMedio9', 'ConsumoMedio10', 'ConsumoMedio11', 'ConsumoMedio12',
    'ConsumoMedio13', 'ConsumoMedio14', 'ConsumoMedio15', 'ConsumoMedio16']
    listatot = ['Totale1', 'Totale2', 'Totale3', 'Totale4', 'Totale5', 'Totale6', 'Totale7', 'Totale8', 'Totale9', 'Totale10', 'Totale11', 'Totale12',
    'Totale13', 'Totale14', 'Totale15', 'Totale16']
    listaper = ['Periodo1', 'Periodo2', 'Periodo3', 'Periodo4', 'Periodo5', 'Periodo6', 'Periodo7', 'Periodo8', 'Periodo9', 'Periodo10', 'Periodo11', 'Periodo12',
    'Periodo13', 'Periodo14', 'Periodo15', 'Periodo16']
    
    for i in range(0,6):
        try:
            if fdfinfo[listatipo[i]] != '':
                c = ConsumabiliUrg()
                c.ID_rich = att
                c.Tipo = fdfinfo[listatipo[i]]
                c.CostoUnitario = int(fdfinfo[listacu[i]])
                c.ConsumoMedio = int(fdfinfo[listacm[i]])
                c.Periodo = int(fdfinfo[listaper[i]])
                c.Totale = int(fdfinfo[listatot[i]])
                c.save()
        except:
            pass
    
     # DITTE
    listanomi = ['Nome1', 'Nome2', 'Nome3', 'Nome4', 'Nome5', 'Nome6', 'Nome7', 'Nome8', 'Nome9', 'Nome10']
    listaem = ['ContattoEM1', 'ContattoEM2', 'ContattoEM3', 'ContattoEM4', 'ContattoEM5', 'ContattoEM6', 'ContattoEM7', 'ContattoEM8', 'ContattoEM9', 'ContattoEM10']
    listatel = ['ContattoTel1', 'ContattoTel2', 'ContattoTel3', 'ContattoTel4', 'ContattoTel5', 'ContattoTel6', 'ContattoTel7', 'ContattoTel8', 'ContattoTel9', 'ContattoTel10']

    for i in range(0,10):
        if fdfinfo[listanomi[i]] != '':
            d = DittaUrg()
            d.ID_rich=att
            d.NomeDitta = fdfinfo[listanomi[i]]
            d.Rif = i+1
            d.ContattoEM = fdfinfo[listaem[i]]
            d.ContattoTel = int(fdfinfo[listatel[i]])
            d.save()
    
    # CRITERI
    listacr = ['Criterio1', 'Criterio2', 'Criterio3', 'Criterio4', 'Criterio5', 'Criterio6', 'Criterio7', 'Criterio8', 'Criterio9']
    listapeso = ['Peso1', 'Peso2', 'Peso3', 'Peso4', 'Peso5', 'Peso6', 'Peso7', 'Peso8', 'Peso9']

    for i in range(0,9):
        try:
            if fdfinfo[listacr[i]] != '':
                cr = CriteriUrg()
                cr.ID_rich = att
                cr.Rif = i+1
                cr.Criterio = fdfinfo[listacr[i]]
                cr.Peso = fdfinfo[listapeso[i]]
                cr.save()
        except:
            pass

def crea_da_pdf2(request, fdfinfo, pk): #per modulo completo 
    print(fdfinfo)
    att = MAIN.objects.get(id=pk)
    # INFO GENERALI
    att.Sede_Reparto = fdfinfo['Sede']
    att.Compilatore = request.user
    att.Direttore = fdfinfo['Direttore']
    att.Apparecchiatura = fdfinfo['Apparecchiatura']
    att.Qta = int(fdfinfo['Qta'])
    if fdfinfo['Acquisto'] != '':
        att.Acquisto = True
        att.Prezzo_acquisto = int(fdfinfo['Prezzo_acquisto'])
    elif fdfinfo['Noleggio']  != '':
        att.Noleggio = True
        if fdfinfo['Prezzo'] != '':
            att.Prezzo_Noleggio = int(fdfinfo['Prezzo'])
        try:
            att.NolMesi = int(fdfinfo['NolMesi'])
        except:
            pass
    elif fdfinfo['Service']!= '':
        att.Service = True
        if fdfinfo['Prezzo'] != '':
            att.Prezzo_Service = int(fdfinfo['Prezzo'])
        try:
            att.NolMesi = int(fdfinfo['NolMesi'])
        except:
            pass
    if fdfinfo['Tecnologico'] != '':
        att.Tecnologico = True
    if fdfinfo['Valutativo'] != '':
        att.Valutativo = True    
    if fdfinfo['Temporaneo'] != '':
        att.Temporaneo = True
    if fdfinfo['Economico'] != '':
        att.Economico = True
    if fdfinfo['Gestionale'] != '':
        att.Gestionale = True
    if fdfinfo['NecInfraSI'] != '':
        att.NecInfraSI = True
        att.NecInfraNota = fdfinfo['NecInfraNota']
    elif fdfinfo['NecInfraNO'] != '':
        att.NecInfraNO = True
    att.NotaNoleggio = fdfinfo['NotaNoleggio']
    att.Data = timezone.now()
    att.Anno_Previsto = fdfinfo['Anno_Previsto']
    try:
        att.PercIVA = int(fdfinfo['PercIVA'])
    except:
        att.PercIVA = 0
    if fdfinfo['Mot1_1'] != '' :
        att.Mot1_1 = True
        att.SostNota = fdfinfo['SostNota']
    if fdfinfo['Mot1_2'] != '' :
        att.Mot1_2 = True
    if fdfinfo['Mot1_3'] != '' :
        att.Mot1_3 = True
    if fdfinfo['Mot2_1'] != '' :
        att.Mot2_1 = True
    if fdfinfo['Mot2_2'] != '':
        att.Mot2_2 = True
    att.AggNota = fdfinfo['AggNota']
    
     # SPECIFICHE
    listaspecifiche = ['Spec1', 'Spec2', 'Spec3', 'Spec4', 'Spec5', 'Spec6', 'Spec7', 'Spec8', 'Spec9', 'Spec10', 'Spec11', 'Spec12', 'Spec13', 'Spec14', 'Spec15', 'Spec16']
    listaun = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9', 'U10', 'U11', 'U12', 'U13', 'U14', 'U15', 'U16']
    listamotivi = ['MotivoClinico1', 'MotivoClinico2', 'MotivoClinico3', 'MotivoClinico4', 'MotivoClinico5', 'MotivoClinico6', 'MotivoClinico7', 'MotivoClinico8', 'MotivoClinico9', 'MotivoClinico10', 'MotivoClinico11', 'MotivoClinico12', 'MotivoClinico13', 'MotivoClinico14', 'MotivoClinico15', 'MotivoClinico16']
    listamM = ['MinMax1', 'MinMax2', 'MinMax3', 'MinMax4', 'MinMax5', 'MinMax6', 'MinMax7', 'MinMax8', 'MinMax9', 'MinMax10', 'MinMax11', 'MinMax12', 'MinMax13', 'MinMax14', 'MinMax15', 'MinMax16']
    # UNICITA'
    listanote = ['Nota1', 'Nota2', 'Nota3', 'Nota4']
    listarif = ['rif1', 'rif2', 'rif3', 'rif4']

    print(fdfinfo)
    
    for i in range(0,14):
        if fdfinfo[listaspecifiche[i]] != '':
            s = Specifiche()
            s.ID_rich = att
            s.Specifica = fdfinfo[listaspecifiche[i]]
            s.MotivoClinico = fdfinfo[listamotivi[i]]
            if fdfinfo[listaun[i]] != '':
                s.Un = True
            s.rif = i+1
            if fdfinfo[listamM[i]] == 'm':
                s.Min = True
                s.Max = False
            elif fdfinfo[listamM[i]] == 'M':
                s.Max = True
                s.Min = False
            else:
                print('specifiche')
                return 1
            s.save()
            if s.Un == True:
                for j in range(0, 4):
                    if fdfinfo[listarif[j]] != '' and int(fdfinfo[listarif[j]]) == i+1:
                        un=Unicita()
                        un.ID_rich = att
                        un.rifext = s
                        un.Nota = fdfinfo[listanote[j]]
                        un.save()
            
    # CONSUMABILI
    listatipo = ['Tipo1', 'Tipo2', 'Tipo3', 'Tipo4', 'Tipo5', 'Tipo6', 'Tipo7', 'Tipo8', 'Tipo9', 'Tipo10', 'Tipo11', 'Tipo12', 'Tipo13', 'Tipo14', 'Tipo15', 'Tipo16']
    listacu = ['CostoUnitario1', 'CostoUnitario2', 'CostoUnitario3', 'CostoUnitario4', 'CostoUnitario5', 'CostoUnitario6',
    'CostoUnitario7', 'CostoUnitario8', 'CostoUnitario9', 'CostoUnitario10', 'CostoUnitario11', 'CostoUnitario12', 'CostoUnitario13', 'CostoUnitario14', 'CostoUnitario15', 'CostoUnitario16']
    listacm = ['ConsumoMedio1', 'ConsumoMedio2', 'ConsumoMedio3', 'ConsumoMedio4', 'ConsumoMedio5', 'ConsumoMedio6',
    'ConsumoMedio7', 'ConsumoMedio8', 'ConsumoMedio9', 'ConsumoMedio10', 'ConsumoMedio11', 'ConsumoMedio12',
    'ConsumoMedio13', 'ConsumoMedio14', 'ConsumoMedio15', 'ConsumoMedio16']
    listatot = ['Totale1', 'Totale2', 'Totale3', 'Totale4', 'Totale5', 'Totale6', 'Totale7', 'Totale8', 'Totale9', 'Totale10', 'Totale11', 'Totale12',
    'Totale13', 'Totale14', 'Totale15', 'Totale16']
    listaper = ['Periodo1', 'Periodo2', 'Periodo3', 'Periodo4', 'Periodo5', 'Periodo6', 'Periodo7', 'Periodo8', 'Periodo9', 'Periodo10', 'Periodo11', 'Periodo12',
    'Periodo13', 'Periodo14', 'Periodo15', 'Periodo16']
    
    for i in range(0,6):
        try:
            if fdfinfo[listatipo[i]] != '':
                c = ConsumabiliMain()
                c.ID_rich = att
                c.Tipo = fdfinfo[listatipo[i]]
                c.CostoUnitario = int(fdfinfo[listacu[i]])
                c.ConsumoMedio = int(fdfinfo[listacm[i]])
                c.Periodo = int(fdfinfo[listaper[i]])
                c.Totale = int(fdfinfo[listatot[i]])
                c.save()
        except:
            pass
    
    # DITTE
    listanomi = ['Nome1', 'Nome2', 'Nome3', 'Nome4', 'Nome5', 'Nome6', 'Nome7', 'Nome8', 'Nome9', 'Nome10']
    listaem = ['ContattoEM1', 'ContattoEM2', 'ContattoEM3', 'ContattoEM4', 'ContattoEM5', 'ContattoEM6', 'ContattoEM7', 'ContattoEM8', 'ContattoEM9', 'ContattoEM10']
    listatel = ['ContattoTel1', 'ContattoTel2', 'ContattoTel3', 'ContattoTel4', 'ContattoTel5', 'ContattoTel6', 'ContattoTel7', 'ContattoTel8', 'ContattoTel9', 'ContattoTel10']

    for i in range(0,10):
        if fdfinfo[listanomi[i]] != '':
            d = Ditta
            d.ID_rich=att
            d.NomeDitta = fdfinfo[listanomi[i]]
            d.Rif = i+1
            d.ContattoEM = fdfinfo[listaem[i]]
            d.ContattoTel = int(fdfinfo[listatel[i]])
            d.save()
    
    # CRITERI
    listacr = ['Criterio1', 'Criterio2', 'Criterio3', 'Criterio4', 'Criterio5', 'Criterio6', 'Criterio7', 'Criterio8', 'Criterio9']
    listapeso = ['Peso1', 'Peso2', 'Peso3', 'Peso4', 'Peso5', 'Peso6', 'Peso7', 'Peso8', 'Peso9']

    for i in range(0,9):
        try:
            if fdfinfo[listacr[i]] != '':
                cr = Criteri()
                cr.ID_rich = att
                cr.Rif = i+1
                cr.Criterio = fdfinfo[listacr[i]]
                cr.Peso = fdfinfo[listapeso[i]]
                cr.save()
        except:
            pass

def compila_pdf_fabbisogno(request): #fatta con PyMuPDF
    file_path = os.path.join(BASE_DIR, 'nuovofabbisogno_form.pdf')

    # Apri il PDF con PyMuPDF
    pdf_reader = fitz.open(file_path)

    # Non esiste trailer in PyMuPDF, si accede direttamente ai campi del modulo (AcroForm)
    
    try:
        # Ottieni informazioni dal database es sede e reparto
        sede = SeRep.objects.filter(Sede=request.user.Sede_Reparto.Sede, Reparto=request.user.Sede_Reparto.Reparto)
        Sede = sede[0].Sede
        Reparto = sede[0].Reparto
        Sub_Reparto = sede[0].Sub_Reparto
    except:
        Sede = ''
        Reparto = ''
        Sub_Reparto = '' 

    #dizionario contenete i dati da inserire nei campi del modulo
    data_dict1 = {
        'Sede': f'{Sede} - {Reparto} - {Sub_Reparto} ',
        'Compilatore': str(request.user),
        'Data': str(timezone.now().date().strftime('%d/%m/%Y'))
    }

    #itera su tutte le pagine del PDF per aggiornare i campi del modulo
    # Modifica i campi del modulo su ogni pagina
    for page_num in range(pdf_reader.page_count):
        page = pdf_reader.load_page(page_num)  # Carica la pagina

        # Accedi ai widget (campi del modulo)
        for field_name, field_value in data_dict1.items():
            for widget in page.widgets():
                if widget.field_name == field_name:
                    print(f"Aggiornando {field_name} con {field_value}")
                    widget.field_value = field_value  # Imposta il valore del campo
                    widget.update()  # Aggiorna il widget

    # Crea un nuovo PDF come output
    output_stream = BytesIO()
    pdf_reader.save(output_stream)  # Salva il PDF nel buffer
    pdf_reader.close()  # Chiudi il documento PDF

    output_stream.seek(0)  # Reimposta il puntatore del buffer all'inizio
    return output_stream

def compila_pdf_fabbisogno_urgente(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'modulo_offline.pdf')
    print(file_path)

    # Controlla se il file esiste
    if not os.path.exists(file_path):
        raise FileNotFoundError("Il file PDF originale non è stato trovato nei media.")

    # Apri il PDF con PyMuPDF
    pdf_reader = fitz.open(file_path)

    # DEBUG: Controlla l'oggetto request.user
    print(f"Utente attuale: {request.user}")
    print(f"Sede_Reparto: {getattr(request.user, 'Sede_Reparto', None)}")

    # Recupera i dati dell'utente per compilare il modulo
    try:
        # Ottieni informazioni dal database es sede e reparto
        sede = SeRep.objects.filter(Sede=request.user.Sede_Reparto.Sede, Reparto=request.user.Sede_Reparto.Reparto)
        Sede = sede[0].Sede
        Reparto = sede[0].Reparto
        Sub_Reparto = sede[0].Sub_Reparto

    except:
        Sede = ''
        Reparto = ''
        Sub_Reparto = '' 

    # Dizionario con i dati da inserire nei campi del modulo
    data_dict1 = {
        'Sede': f'{Sede} - {Reparto} - {Sub_Reparto} ',
        'Compilatore': str(request.user),
        'Data': str(timezone.now().date().strftime('%d/%m/%Y'))
    }

    # Itera sulle pagine per aggiornare i campi del modulo
    for page_num in range(pdf_reader.page_count):
        page = pdf_reader[page_num]  # Carica la pagina
        for widget in page.widgets():  # Accedi ai campi del modulo
            if widget.field_name in data_dict1:
                widget.field_value = data_dict1[widget.field_name]
                widget.update()  

    # Salva il file aggiornato in MEDIA_ROOT
    output_path = os.path.join(settings.MEDIA_ROOT, f'modulo_offline_aggiornato_{uuid.uuid4().hex}.pdf')
    pdf_reader.save(output_path)
    pdf_reader.close()

    return FileResponse(open(output_path, 'rb'), as_attachment=True, content_type='application/pdf')

import os
from io import BytesIO
from django.http import HttpResponse
from pdfrw import PdfReader, PdfWriter, IndirectPdfDict
from .models import MAIN, PI, ConsumabiliMain

def compila_pdf(pk):
    # Ottiene il record principale da modificare basandosi sulla chiave
    att = MAIN.objects.get(id=pk)
    # Ottiene il PI associato al record principale
    pi = PI.objects.get(ID_PianoInvestimenti=att.ID_PianoInvestimenti)

    # Percorso PDF che deve essere compilato
    file_path = os.path.join(BASE_DIR, 'nuova_formword.pdf')

    # Carica il PDF esistente
    reader = PdfReader(file_path)
    writer = PdfWriter()

    # Dizionario per i campi da compilare nel PDF
    data_dict1 = {
        'Sede': str(att.Sede_Reparto),
        'Compilatore': str(att.Compilatore),
        'Direttore': str(att.Direttore),
        'Apparecchiatura': att.Apparecchiatura,
        'Qta': str(att.Qta),
        'Data': str(att.Data.strftime('%d/%m/%Y')),
        'SostNota': str(att.SostNota),
        'NotaNoleggio': att.NotaNoleggio,
        'NolMesi': str(att.NolMesi),
        'NoteGen': att.NoteGen,
        'Anno_Previsto': att.Anno_Previsto,
        'PercIVA': int(att.PercIVA),
    }

    # Aggiunge il campo FONTE in base al valore del piano di investimenti
    if pi.is_ext:
        data_dict1['Fonte'] = f'P.I. : {att.ID_PianoInvestimenti}'
    else:
        data_dict1['Fonte'] = str(att.Fonte)

    # Aggiungi i consumabili al dizionario
    cons = ConsumabiliMain.objects.filter(ID_rich=att)
    i = 1
    for con in cons:
        data_dict1[f'tipo{i}'] = con.Tipo
        data_dict1[f'CostoUnitario{i}'] = con.CostoUnitario
        data_dict1[f'ConsumoMedio{i}'] = con.ConsumoMedio
        data_dict1[f'Periodo{i}'] = con.Periodo
        data_dict1[f'Totale{i}'] = con.Totale
        i += 1

    # Carica la prima pagina (modifica le altre se necessario)
    page = reader.pages[0]

    # Ottieni i campi del modulo (informazioni sulla struttura del modulo)
    annotations = page['/Annots']

    for annot in annotations:
        field = annot.get_object()

        # Se il campo è un campo di tipo "Text" o "Button" (modulo PDF)
        if '/T' in field:
            field_name = field['/T'][1:-1]  # Nome del campo (senza gli slash)
            if field_name in data_dict1:
                field.update({
                    PdfName("/V"): PdfString(data_dict1[field_name])  # Aggiungi il valore
                })

        # Se il campo è una checkbox
        if '/CheckBox' in field:
            field_name = field['/T'][1:-1]  # Nome del campo (senza gli slash)
            if field_name in data_dict1:
                checkbox_value = "/Yes" if data_dict1[field_name] == "/S#EC" else "/Off"
                field.update({
                    PdfName("/V"): PdfString(checkbox_value)  # Aggiorna la checkbox
                })

    # Aggiungi la pagina modificata al writer
    writer.addpage(page)

    # Scrivi il PDF finale in memoria
    output_stream = BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)

    # Restituisce il PDF compilato come risposta
    response = HttpResponse(output_stream.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="modulo_compilato.pdf"'
    return response

'''
def compila_pdf(pk):
    # Ottiene il record principale da modificare basandosi sulla chiave
    att = MAIN.objects.get(id=pk)
    # Ottiene il PI associato al record principale
    pi = PI.objects.get(ID_PianoInvestimenti=att.ID_PianoInvestimenti)

    # Percorso PDF che deve essere compilato
    file_path = os.path.join(BASE_DIR, 'nuova_formword.pdf')

    # Carica il PDF esistente
    pdf_reader = PyPDF2.PdfReader(file_path)
    pdf_writer = PyPDF2.PdfWriter()

    # Dizionario per i campi da compilare nel PDF
    data_dict1 = {
        'Sede': str(att.Sede_Reparto),
        'Compilatore': str(att.Compilatore),
        'Direttore': str(att.Direttore),
        'Apparecchiatura': att.Apparecchiatura,
        'Qta': str(att.Qta),
        'Data': str(att.Data.strftime('%d/%m/%Y')),
        'SostNota': str(att.SostNota),
        'NotaNoleggio': att.NotaNoleggio,
        'NolMesi': str(att.NolMesi),
        'NoteGen': att.NoteGen,
        'Anno_Previsto': att.Anno_Previsto,
        'PercIVA': int(att.PercIVA),
    }

    # Aggiunge il campo FONTE in base al valore del piano di investimenti
    if pi.is_ext:
        data_dict1['Fonte'] = f'P.I. : {att.ID_PianoInvestimenti}'
    else:
        data_dict1['Fonte'] = str(att.Fonte)

    # Aggiungi i consumabili al dizionario
    cons = ConsumabiliMain.objects.filter(ID_rich=att)
    i = 1
    for con in cons:
        data_dict1[f'tipo{i}'] = con.Tipo
        data_dict1[f'CostoUnitario{i}'] = con.CostoUnitario
        data_dict1[f'ConsumoMedio{i}'] = con.ConsumoMedio
        data_dict1[f'Periodo{i}'] = con.Periodo
        data_dict1[f'Totale{i}'] = con.Totale
        i += 1

    # Dizionario per i campi checkbox
    data_dict2 = {}

    # Compila i campi relativi all'acquisto
    if att.Acquisto:
        data_dict2['Acquisto'] = "/S#EC"
        data_dict1['Prezzo_acquisto'] = str(att.Prezzo_acquisto)
    else:
        data_dict2['Acquisto'] = "/Off"

    # Compila i campi relativi al noleggio
    if att.Noleggio:
        data_dict2['Noleggio'] = "/S#EC"
        data_dict1['Prezzo'] = str(att.Prezzo_Noleggio)
    else:
        data_dict2['Noleggio'] = "/Off"

    # Compila i campi relativi al service
    if att.Service:
        data_dict2['Service'] = "/S#EC"
        data_dict1['Prezzo'] = str(att.Prezzo_Service)
    else:
        data_dict2['Service'] = "/Off"

    # Compila i campi relativi alle altre opzioni
    if att.Tecnologico:
        data_dict2['Tecnologico'] = '/S#EC'
    else:
        data_dict2['Tecnologico'] = '/Off'

    if att.Valutativo:
        data_dict2['Valutativo'] = '/S#EC'
    else:
        data_dict2['Valutativo'] = '/Off'

    if att.Temporaneo:
        data_dict2['Temporaneo'] = '/S#EC'
    else:
        data_dict2['Temporaneo'] = '/Off'

    if att.Economico:
        data_dict2['Economico'] = '/S#EC'
    else:
        data_dict2['Eocnomico'] = '/Off'

    if att.Gestionale:
        data_dict2['Gestionale'] = '/S#EC'
    else:
        data_dict2['Gestionale'] = '/Off'

    # Campi per la necessità infrastrutturali
    if att.NecInfraSi:
        data_dict2['NecInfraSI'] = '/S#EC'
        data_dict1['NecInfraNota'] = str(att.NecInfraNota)
    elif att.NecInfraNO:
        data_dict2['NecInfraNO'] = '/S#EC'
        data_dict1['NecInfraNota'] = ""

    # Aggiungi altre opzioni (Mot1_1, Mot1_2, ecc.)
    if att.Mot1_2:
        data_dict2['Mot1_2'] = '/S#EC'
    if att.Mot1_1:
        data_dict2['Mot1_1'] = '/S#EC'
    if att.Mot1_3:
        data_dict2['Mot1_3'] = '/S#EC'
    if att.Mot2_1:
        data_dict2['Mot2_1'] = '/S#EC'
    if att.Mot2_2:
        data_dict2['Mot2_2'] = '/S#EC'
        data_dict1['AggNota'] = att.AggNota

    # Modifica il PDF
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        # Copia la pagina nel writer
        pdf_writer.add_page(page)

        # Ciclo attraverso tutti i campi del modulo
        for field_name, field_value in data_dict1.items():
            try:
                field = page.get_field(field_name)  # Ottieni il campo
                field.update({"/V": field_value})  # Aggiorna il valore del campo
            except KeyError:
                pass  # Se il campo non esiste, continua senza errore

        # Aggiorna i checkbox
        for checkbox_name, checkbox_value in data_dict2.items():
            try:
                checkbox_field = page.get_field(checkbox_name)  # Ottieni il campo checkbox
                checkbox_field.update({"/V": checkbox_value})  # Aggiorna il valore della checkbox
            except KeyError:
                pass  # Se il campo non esiste, continua senza errore

    # Scrive il nuovo PDF in memoria
    output_stream = BytesIO()
    pdf_writer.write(output_stream)
    output_stream.seek(0)

    # Restituisce il PDF compilato come risposta
    response = HttpResponse(output_stream.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="modulo_compilato.pdf"'
    return response
'''
'''
def compila_pdf(pk):
    # Ottiene il record principale da modificare basandosi sulla chiave
    att = MAIN.objects.get(id=pk)
    # Ottiene il PI associato al record principale
    pi = PI.objects.get(ID_PianoInvestimenti=att.ID_PianoInvestimenti)

    # Percorso PDF che deve essere compilato
    file_path = os.path.join(BASE_DIR, 'nuova_formword.pdf')

    # Carica il PDF con fitz
    pdf_document = fitz.open(file_path)

    # Dizionario per i campi da compilare nel PDF
    data_dict1 = {
        'Sede': str(att.Sede_Reparto),
        'Compilatore': str(att.Compilatore),
        'Direttore': str(att.Direttore),
        'Apparecchiatura': att.Apparecchiatura,
        'Qta': str(att.Qta),
        'Data': str(att.Data.strftime('%d/%m/%Y')),
        'SostNota': str(att.SostNota),
        'NotaNoleggio': att.NotaNoleggio,
        'NolMesi': str(att.NolMesi),
        'NoteGen': att.NoteGen,
        'Anno_Previsto': att.Anno_Previsto,
        'PercIVA': int(att.PercIVA),
    }

    # Aggiunge il campo FONTE in base al valore del piano di investimenti
    if pi.is_ext:
        data_dict1['Fonte'] = f'P.I. : {att.ID_PianoInvestimenti}'
    else:
        data_dict1['Fonte'] = str(att.Fonte)

    # Aggiungi i consumabili al dizionario
    cons = ConsumabiliMain.objects.filter(ID_rich=att)
    i = 1
    for con in cons:
        data_dict1[f'tipo{i}'] = con.Tipo
        data_dict1[f'CostoUnitario{i}'] = con.CostoUnitario
        data_dict1[f'ConsumoMedio{i}'] = con.ConsumoMedio
        data_dict1[f'Periodo{i}'] = con.Periodo
        data_dict1[f'Totale{i}'] = con.Totale
        i += 1

    # Dizionario per i campi checkbox
    data_dict2 = {}

    # Compila i campi relativi all'acquisto
    if att.Acquisto:
        data_dict2['Acquisto'] = "/S#EC"
        data_dict1['Prezzo_acquisto'] = str(att.Prezzo_acquisto)
    else:
        data_dict2['Acquisto'] = "/Off"

    # Compila i campi relativi al noleggio
    if att.Noleggio:
        data_dict2['Noleggio'] = "/S#EC"
        data_dict1['Prezzo'] = str(att.Prezzo_Noleggio)
    else:
        data_dict2['Noleggio'] = "/Off"

    # Compila i campi relativi al service
    if att.Service:
        data_dict2['Service'] = "/S#EC"
        data_dict1['Prezzo'] = str(att.Prezzo_Service)
    else:
        data_dict2['Service'] = "/Off"

    # Compila i campi relativi alle altre opzioni
    if att.Tecnologico:
        data_dict2['Tecnologico'] = '/S#EC'
    else:
        data_dict2['Tecnologico'] = '/Off'

    if att.Valutativo:
        data_dict2['Valutativo'] = '/S#EC'
    else:
        data_dict2['Valutativo'] = '/Off'

    if att.Temporaneo:
        data_dict2['Temporaneo'] = '/S#EC'
    else:
        data_dict2['Temporaneo'] = '/Off'

    if att.Economico:
        data_dict2['Economico'] = '/S#EC'
    else:
        data_dict2['Eocnomico'] = '/Off'

    if att.Gestionale:
        data_dict2['Gestionale'] = '/S#EC'
    else:
        data_dict2['Gestionale'] = '/Off'

    # Campi per la necessità infrastrutturali
    if att.NecInfraSi:
        data_dict2['NecInfraSI'] = '/S#EC'
        data_dict1['NecInfraNota'] = str(att.NecInfraNota)
    elif att.NecInfraNO:
        data_dict2['NecInfraNO'] = '/S#EC'
        data_dict1['NecInfraNota'] = ""

    # Aggiungi altre opzioni (Mot1_1, Mot1_2, ecc.)
    if att.Mot1_2:
        data_dict2['Mot1_2'] = '/S#EC'
    if att.Mot1_1:
        data_dict2['Mot1_1'] = '/S#EC'
    if att.Mot1_3:
        data_dict2['Mot1_3'] = '/S#EC'
    if att.Mot2_1:
        data_dict2['Mot2_1'] = '/S#EC'
    if att.Mot2_2:
        data_dict2['Mot2_2'] = '/S#EC'
        data_dict1['AggNota'] = att.AggNota

    # Modifica il PDF
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)

        # Ciclo attraverso tutti i campi del modulo (forms) nella pagina
        for field in page.widgets():
            field_name = field.field_name
            if field_name in data_dict1:
                field.update_text(str(data_dict1[field_name]))
                #field.text = str(data_dict1[field_name])
            if field_name in data_dict2:
                field.check = True if data_dict2[field_name] == "/S#EC" else False

    # Scrive il nuovo PDF in memoria
    output_stream = BytesIO()
    pdf_document.save(output_stream)
    output_stream.seek(0)

    # Restituisce il PDF compilato come risposta
    response = HttpResponse(output_stream.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="modulo_compilato.pdf"'
    return response
'''
        
'''
def compila_pdf(pk):
    #ottiene il record principale da modificare basandosi sulla chiave
    att = MAIN.objects.get(id = pk)
    #ottiene il PI associato al record principale
    pi = PI.objects.get(ID_PianoInvestimenti = att.ID_PianoInvestimenti)

    #percorso pdf che deve essere compilato 
    file_path = os.path.join(BASE_DIR, 'nuova_formword.pdf')

    pdf_reader = fitz.open(file_path)

    #input_stream = open(file_path, "rb")
    #pdf_reader = PdfReader(input_stream)
    if "/AcroForm" in pdf_reader.trailer["/Root"]:
        pdf_reader.trailer["/Root"]["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})

    #crea un pdfFile Writer per scrivere i dati nel PDF
    pdf_writer = PdfFileWriter()
    set_need_appearances_writer(pdf_writer)
    if "/AcroForm" in pdf_writer._root_object:
        # Acro form is form field, set needs appearances to fix printing issues
        pdf_writer._root_object["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})


    #dizionario per i campi da compilare nel PDF 
    data_dict1 = {
        'Sede': str(att.Sede_Reparto),
        'Compilatore': str(att.Compilatore),
        'Direttore': str(att.Direttore),
        'Apparecchiatura': att.Apparecchiatura,
        'Qta': str(att.Qta),
        'Data': str(att.Data.strftime('%d/%m/%Y')),
        'SostNota': str(att.SostNota),
        'NotaNoleggio': att.NotaNoleggio,
        'NolMesi': str(att.NolMesi),
        
        'NoteGen': att.NoteGen,
        'Anno_Previsto': att.Anno_Previsto,
        'PercIVA': int(att.PercIVA)
    }

    #aggiunge il campo FONTE in base al valore del piano di investimenti
    if pi.is_ext:
        data_dict1 = data_dict1 | {'Fonte': f'P.I. : {att.ID_PianoInvestimenti}'}
    else:
        data_dict1 = data_dict1 | {'Fonte': str(att.Fonte)}
    cons = ConsumabiliMain.objects.filter(ID_rich = att)
    i=1
    for con in cons:
        data_dict1 = data_dict1 | {f'tipo{i}': con.Tipo, f'CostoUnitario{i}': con.CostoUnitario, f'ConsumoMedio{i}': con.ConsumoMedio, f'Periodo{i}': con.Periodo, f'Totale{i}': con.Totale}
        i = i+1    
    
    #dizionario per i campi checkbox
    data_dict2 = {}

    #compila i campi relativi all'acquisto
    if att.Acquisto:
        print("acquistato")
        data_dict2 = data_dict2 | {
            'Acquisto': "/S#EC"}
        data_dict1 = data_dict1 | {'Prezzo_acquisto': str(att.Prezzo_acquisto)}
    
    
    else:
        data_dict2 = data_dict2 | {
            'Acquisto': "/Off",
        }

    #compila i campi realtivi al noleggio
    if att.Noleggio:
        print("noleggiato")
        data_dict2 = data_dict2 | {
            'Noleggio': "/S#EC"}
        
        data_dict1 = data_dict1 | { 'Prezzo': str(att.Prezzo_Noleggio)} 
            
    else:
        data_dict2 = data_dict2 | {
            'Noleggio': "/Off",
        }

    #compila i campi relativi al service
    if att.Service:
        data_dict2 = data_dict2 | {
            'Service': "/S#EC"}
        data_dict1 = data_dict1 | {
            'Prezzo': str(att.Prezzo_Service) 
            }
    else:
        data_dict2 = data_dict2 | {
            'Service': "/Off",
        }

    if att.Tecnologico:
        data_dict2 = data_dict2 | {
            'Tecnologico': '/S#EC'
        }
    else:
        data_dict2 = data_dict2 | {
            'Tecnologico': '/Off'
        }
    if att.Valutativo:
        data_dict2 = data_dict2 | {
            'Valutativo': '/S#EC'
        }
    else:
        data_dict2 = data_dict2 | {
            'Valutativo': '/Off'
        }
    if att.Temporaneo:
        data_dict2 = data_dict2 | {
            'Temporaneo': '/S#EC'
        }
    else:
        data_dict2 = data_dict2 | {
            'Temporaneo': '/Off'
        }   
    if att.Economico:
        data_dict2 = data_dict2 | {
            'Economico': '/S#EC'
        }
    else:
        data_dict2 = data_dict2 | {
            'Eocnomico': '/Off'
        }  
    if att.Gestionale:
        data_dict2 = data_dict2 | {
            'Gestionale': '/S#EC'
        }
    else:
        data_dict2 = data_dict2 | {
            'Gestionale': '/Off'
        }

    #campi per la necessità infrastrutturali
    if att.NecInfraSi:
        data_dict2 = data_dict2 | {
            'NecInfraSI': '/S#EC'}
        data_dict1 = data_dict1 | {
            'NecInfraNota':str(att.NecInfraNota)
        }
    elif att.NecInfraNO:
        data_dict2 = data_dict2 | {
            'NecInfraNO': '/S#EC'}
        data_dict1 = data_dict1 | {
            'NecInfraNota': ""
        }  
    
    if att.Mot1_2:
        data_dict2 = data_dict2 | {
            'Mot1_2': '/S#EC'}
    if att.Mot1_1:
        data_dict2 = data_dict2 | {
            'Mot1_1': '/S#EC'}
    if att.Mot1_3:
        data_dict2 = data_dict2 | {'Mot1_3': '/S#EC'}
    if att.Mot2_1:
        data_dict2 = data_dict2 | {'Mot2_1': '/S#EC'}
    if att.Mot2_2:
        data_dict2 = data_dict2 | {'Mot2_2': '/S#EC'}
        data_dict1 = data_dict1 | {'AggNota': att.AggNota}


    # Modifica il PDF
    for page_num in range(pdf_reader.page_count):
        page = pdf_reader.load_page(page_num)

        # Aggiorna i campi di testo (data_dict1)
        for field_name, field_value in data_dict1.items():
            page.update_text(field_name, field_value)

        # Aggiorna i checkbox (data_dict2)
        for checkbox_name, checkbox_value in data_dict2.items():
            page.update_checkbox(checkbox_name, checkbox_value)

    # Scrive il nuovo PDF in memoria
    output_stream = BytesIO()
    pdf_reader.save(output_stream)
    output_stream.seek(0)

    # Restituisce il PDF compilato come risposta
    response = HttpResponse(output_stream.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="modulo_compilato.pdf"'
    return response
'''
'''
    #aggiorni i campi del PDF o aggiunge le pagine del PDF 
    for i in range(0,7):
        pdf_writer.addPage(pdf_reader.getPage(i))
        page = pdf_writer.getPage(i)
        
        
        # update form fields
        pdf_writer.updatePageFormFieldValues(page, data_dict1)
        
        # update checkbox fields
        updateCheckboxValues(page, data_dict2)

    output_stream = BytesIO()
    pdf_writer.write(output_stream)

    return output_stream
# output_stream is your flattened PDF'
'''


def set_need_appearances_writer(writer):
    # basically used to ensured there are not 
    # overlapping form fields, which makes printing hard
    try:
        catalog = writer._root_object
        # get the AcroForm tree and add "/NeedAppearances attribute
        if "/AcroForm" not in catalog:
            writer._root_object.update({
                NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})

        need_appearances = NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)


    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))

    return writer 

def updateCheckboxValues(page, fields):

    for j in range(0, len(page['/Annots'])):
        writer_annot = page['/Annots'][j].getObject()
        for field in fields:
            if writer_annot.get('/T') == field:
                writer_annot.update({
                    NameObject("/V"): NameObject(fields[field]),
                    NameObject("/AS"): NameObject(fields[field])
                })

# def extract_pdf_data(file):
#     """ Estrai dati testuali da un file PDF """
#     extracted_data = {}

#     with io.BytesIO(file.read()) as open_pdf:
#         reader = PyPDF2.PdfReader(open_pdf)
#         text = ""
#         for page in reader.pages:
#             text += page.extract_text() + "\n"

#         #Estrae i dati chiave dal testo
#         if "Progressivo:" in text:
#             extracted_data["Progressivo"] = text.split("Progressivo:")[1].split("\n")[0].strip()

#         if "Sede Reparto:" in text:
#             extracted_data["Sede_Reparto"] = text.split("Sede Reparto:")[1].split("\n")[0].strip()

#         if "Apparecchiatura:" in text:
#             extracted_data["Apparecchiatura"] = text.split("Apparecchiatura:")[1].split("\n")[0].strip()

#         if "Quantità:" in text:
#             extracted_data["Qta"] = int(text.split("Quantità:")[1].split("\n")[0].strip())

#         if "Priorità:" in text:
#             extracted_data["Priorita"] = text.split("Priorità:")[1].split("\n")[0].strip()

#         if "Costo Presunto NO IVA:" in text:
#             extracted_data["Costo_Presunto_NOIVA"] = float(text.split("Costo Presunto NO IVA:")[1].split("\n")[0].strip())

#         if "Costo Presunto IVA:" in text:
#             extracted_data["Costo_Presunto_IVA"] = float(text.split("Costo Presunto IVA:")[1].split("\n")[0].strip())

#         if "Compilatore:" in text:
#             extracted_data["Compilatore"] = text.split("Compilatore:")[1].split("\n")[0].strip()

#         if "ID Piano Investimenti:" in text:
#             extracted_data["ID_PianoInvestimenti"] = text.split("ID Piano Investimenti:")[1].split("\n")[0].strip()

#     return extracted_data

def extract_pdf_data(file):
    data = {
        "Priorita": "Alta",  # Sostituisci con l'estrazione reale
        "Sede_Reparto": "Reparto Generale",
        "Compilatore": "Dr. Rossi",
        "Qta": 2,
        "Data": "2025-02-10",
        "PercIVA": 22,
        "rif": "123456",
        "Specifica": "Dettagli",
        "MotivoClinico": "Urgenza medica",
        "Max": "Massima"
    }
    print("Dati estratti dal PDF:", data)  # DEBUG
    return data