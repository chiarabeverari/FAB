from datetime import datetime
from .models import *
from .forms import *
from .settings import BASE_DIR
from .filters import *
from django.http import HttpResponse, Http404
from django.utils import timezone
from io import BytesIO
from django.template.loader import get_template
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from xhtml2pdf import pisa
import csv
import xlwt #pip install xlwt
from .crea_da_pdf import *

@login_required
def export_excelpiano(request):
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition']='attachement; filename=Piano_Investimenti'+ str(datetime.now())+ '.xls'
    wb = xlwt.Workbook(encoding ="utf-8")
    ws = wb.add_sheet('Attrezzatura')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['ID_PianoInvestimenti', 'Descrizione', 'Priorità', 'Costo Presunto (IVA)']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()

    rows = PI.objects.all()
    filter = PianoInvFilter(request.GET, queryset=rows).qs
    f = filter.values_list('ID_PianoInvestimenti', 'Descrizione', 'Priorita', 'Costo_Presunto_IVA')

    for i in f:
        row_num+=1

        for col_num in range(len(i)):
            ws.write(row_num, col_num, str(i[col_num]), font_style)
        
    wb.save(response)
        
        
    return(response)

@login_required
def export_csvpiano(request):
    atts = PI.objects.all()
    filter = PianoInvFilter(request.GET, queryset=atts).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachement; filename=Attrezzatura'+ str(datetime.now())+ '.csv'

    writer=csv.writer(response)
    writer.writerow(['ID_PianoInvestimenti', 'Descrizione', 'Priorita',  'Costo Presunto (IVA)'])
    for i in filter.values_list('ID_PianoInvestimenti', 'Descrizione', 'Priorita', 'Costo_Presunto_IVA'):
        writer.writerow(i)
    return response

@login_required
def export_excelfabbisogni(request):
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition']='attachement; filename=raccoltafabbisogni'+ str(datetime.now())+ '.xls'
    wb = xlwt.Workbook(encoding ="utf-8")
    ws = wb.add_sheet('Attrezzatura')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Sede', 'Reparto', 'Sub-Reparto', 'Apparecchiatura', 'Quantità', 'Priorità', 'Costo Presunto (NO IVA)', 'Compilatore (Nome)', 'Compilatore (Cognome)']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()

    rows = Fabbisogni.objects.all()
    filter = RacFabFilter(request.GET, queryset=rows).qs
    f = filter.values_list('Sede_Reparto__Sede', 'Sede_Reparto__Reparto', 'Sede_Reparto__Sub_Reparto', 'Apparecchiatura', 'Qta', 'Priorita', 'Costo_Presunto_NOIVA', 'Compilatore__Nome', 'Compilatore__Cognome' )

    for i in f:
        row_num+=1

        for col_num in range(len(i)):
            ws.write(row_num, col_num, str(i[col_num]), font_style)
        
    wb.save(response)
        
        
    return(response)

@login_required
def export_csvfabbisogni(request):
    atts = Fabbisogni.objects.all()
    filter = RacFabFilter(request.GET, queryset=atts).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachement; filename=Attrezzatura'+ str(datetime.now())+ '.csv'

    writer=csv.writer(response)
    writer.writerow(['Sede - Reparto', 'Apparecchiatura', 'Quantità', 'Priorità', 'Costo Presunto (NO IVA)', 'Compilatore'])
    for i in filter.values_list('Sede_Reparto', 'Apparecchiatura', 'Qta', 'Priorita',  'Costo_Presunto_NOIVA', 'Compilatore'):
        writer.writerow(i)
    return response

@login_required
def export_excelass(request):
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition']='attachement; filename=assegnazionepriorita'+ str(datetime.now())+ '.xls'
    wb = xlwt.Workbook(encoding ="utf-8")
    ws = wb.add_sheet('Attrezzatura')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Priorita acquisto','Sede', 'Reparto', 'Sub-Reparto', 'Apparecchiatura', 'Quantità', 'Priorità', 'Costo Presunto (NO IVA)', 'Compilatore (Nome)', 'Compilatore (Cognome)']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()

    rows = Fabbisogni.objects.filter(StatoRic__StatoRic=StatoRichiesta.SPEDITA)
    filter = RacFabFilterRic(request.GET, queryset=rows).qs
    f = filter.values_list('AssegnPrior','Sede_Reparto__Sede', 'Sede_Reparto__Reparto', 'Sede_Reparto__Sub_Reparto', 'Apparecchiatura', 'Qta', 'Priorita', 'Costo_Presunto_NOIVA', 'Compilatore__Nome', 'Compilatore__Cognome' )

    for i in f:
        row_num+=1

        for col_num in range(len(i)):
            ws.write(row_num, col_num, str(i[col_num]), font_style)
        
    wb.save(response)
        
        
    return(response)


@login_required
def export_csv(request):
    atts = MAIN.objects.all()
    filter = MAINFilter(request.GET, queryset=atts).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachement; filename=Attrezzatura'+ str(datetime.now())+ '.csv'

    writer=csv.writer(response)
    writer.writerow(['Progressivo', 'Apparecchiatura', 'Data di inserimento', 'Compilazione Richiesta', 'Valutazione tecnica/clinica', 'Spedizione Provveditorato', 'Inizio Gara', 'Valutazione Offerte', 'Aggiudicazione', 'Acquisizione', 'Collaudo', 'Sospensione/annullamento', 'Sede - Reparto - SubReparto', 'Acquisto', 'Service', 'Noleggio'])
    for i in filter.values_list('Progressivo', 'Apparecchiatura', 'Data', 'Data1', 'Data2', 'Data3', 'Data4', 'Data5', 'Data6', 'Data7', 'Data8', 'Data9', 'Sede_Reparto', 'Prezzo_acquisto', 'Prezzo_Service', 'Prezzo_Noleggio'):
        writer.writerow(i)
    return response

@login_required    
def export_excel(request):
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition']='attachement; filename=Attrezzatura'+ str(datetime.now())+ '.xls'
    wb = xlwt.Workbook(encoding ="utf-8")
    ws = wb.add_sheet('Attrezzatura')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Progressivo', 'Apparecchiatura', 'Data di inserimento', 'Compilazione Richiesta', 'Valutazione tecnica/clinica', 'Spedizione Provveditorato', 'Inizio Gara', 'Valutazione Offerte', 'Aggiudicazione', 'Acquisizione', 'Collaudo', 'Sospensione/annullamento', 'Sede - Reparto - SubReparto', 'Acquisto', 'Service', 'Noleggio']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()

    rows = MAIN.objects.all()
    filter = MAINFilter(request.GET, queryset=rows).qs
    f = filter.values_list('Progressivo', 'Apparecchiatura', 'Data', 'Data1', 'Data2', 'Data3', 'Data4', 'Data5', 'Data6', 'Data7', 'Data8', 'Data9', 'Sede_Reparto', 'Prezzo_acquisto', 'Prezzo_Service', 'Prezzo_Noleggio')

    for i in f:
        row_num+=1

        for col_num in range(len(i)):
            if col_num > 1 and col_num < 12 and i[col_num] is not None:
                ws.write(row_num, col_num, i[col_num].strftime('%d/%m/%Y'), font_style)

            else:
                ws.write(row_num, col_num, str(i[col_num]), font_style)
        
    wb.save(response)
        
        
    return(response)

@login_required
def export_pdf(request, pk):
    att = MAIN.objects.get(id=pk)
    specs = Specifiche.objects.filter(ID_rich=pk)
    lista=[]
    for spec in specs:
        lista+=[spec.id]
    uns = Unicita.objects.filter(rifext__in=lista)
    crs = Criteri.objects.filter(ID_rich = pk)
    cons = ConsumabiliMain.objects.filter(ID_rich = pk)
    imagepath = os.path.join(BASE_DIR, 'FAG', 'static', 'css', 'ulss9logo.png')
    checkpath = os.path.join(BASE_DIR, 'FAG', 'static', 'css', 'checkbox_checked.png')
    uncheckpath = os.path.join(BASE_DIR, 'FAG', 'static', 'css', 'checkbox_unchecked.png')

    context = {'att': att, 'uns': uns, 'specs': specs, 'crs':crs, 'cons':cons, 'imagepath': imagepath, 'checkpath': checkpath, 'uncheckpath': uncheckpath}
    template = get_template('modulorichiesta.html')
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1", "ignore")), result)
    response = HttpResponse(result.getvalue(), content_type="application/force-download")
    filename = str(att.Apparecchiatura) + str(timezone.now())
    content = "attachement; filename  = %s.pdf"%(filename)
    response["Content-Disposition"] = content
    return response

@login_required
def export_pdf_urg(request, pk):
    att = UrgenteRequest.objects.get(id=pk)
    specs = SpecificheUrg.objects.filter(ID_rich=pk)
    lista=[]
    for spec in specs:
        lista+=[spec.id]
    uns = UnicitaUrg.objects.filter(rifext__in=lista)
    crs = CriteriUrg.objects.filter(ID_rich = pk)
    cons = ConsumabiliUrg.objects.filter(ID_rich = pk)
    imagepath = os.path.join(BASE_DIR, 'FAG', 'static', 'css', 'ulss9logo.png')
    checkpath = os.path.join(BASE_DIR, 'FAG', 'static', 'css', 'checkbox_checked.png')
    uncheckpath = os.path.join(BASE_DIR, 'FAG', 'static', 'css', 'checkbox_unchecked.png')

    context = {'att': att, 'uns': uns, 'specs': specs, 'crs':crs, 'cons':cons, 'imagepath': imagepath, 'checkpath': checkpath, 'uncheckpath': uncheckpath}
    template = get_template('modulorichiesta.html') #da controllare se va bene
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1", "ignore")), result)
    response = HttpResponse(result.getvalue(), content_type="application/force-download")
    filename = str(att.Apparecchiatura) + str(timezone.now())
    content = "attachement; filename  = %s.pdf"%(filename)
    response["Content-Disposition"] = content
    return response

@login_required
def export_pdf_valutazione(request, pk):
    att = MAIN.objects.get(id=pk)
   
    specs = Specifiche.objects.filter(ID_rich=pk)
    lista=[]
    for spec in specs:
        lista+=[spec.id]
    inclinico = specs[0].ValTecUtente
    uns = Unicita.objects.filter(rifext__in=lista)
    crs = Criteri.objects.filter(ID_rich = pk)
    cons = ConsumabiliMain.objects.filter(ID_rich = pk)
    imagepath = os.path.join(BASE_DIR, 'newgestion', 'static', 'css', 'ulss9logo.png')
    checkpath = os.path.join(BASE_DIR, 'newgestion', 'static', 'css', 'checkbox_checked.png')
    uncheckpath = os.path.join(BASE_DIR, 'newgestion', 'static', 'css', 'checkbox_unchecked.png')

    context = {'att': att, 'uns': uns, 'specs': specs, 'crs':crs, 'cons':cons, 'inclinico': inclinico, 'imagepath': imagepath, 'checkpath': checkpath, 'uncheckpath': uncheckpath}
    template = get_template('modulovalutazione.html')
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1", "ignore")), result)
    response = HttpResponse(result.getvalue(), content_type="application/force-download")
    filename = str(att.Apparecchiatura) + str(timezone.now())
    content = "attachement; filename=%s.pdf"%(filename)
    response["Content-Disposition"] = content
    return response

@login_required
def export_pdf_valutazione_urg(request, pk):
    att = UrgenteRequest.objects.get(id=pk)
   
    specs = SpecificheUrg.objects.filter(ID_rich=pk)
    lista=[]
    for spec in specs:
        lista+=[spec.id]
    inclinico = specs[0].ValTecUtente
    uns = UnicitaUrg.objects.filter(rifext__in=lista)
    crs = CriteriUrg.objects.filter(ID_rich = pk)
    cons = ConsumabiliUrg.objects.filter(ID_rich = pk)
    imagepath = os.path.join(BASE_DIR, 'newgestion', 'static', 'css', 'ulss9logo.png')
    checkpath = os.path.join(BASE_DIR, 'newgestion', 'static', 'css', 'checkbox_checked.png')
    uncheckpath = os.path.join(BASE_DIR, 'newgestion', 'static', 'css', 'checkbox_unchecked.png')

    context = {'att': att, 'uns': uns, 'specs': specs, 'crs':crs, 'cons':cons, 'inclinico': inclinico, 'imagepath': imagepath, 'checkpath': checkpath, 'uncheckpath': uncheckpath}
    template = get_template('modulovalutazione.html') #da controllare se va bene
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1", "ignore")), result)
    response = HttpResponse(result.getvalue(), content_type="application/force-download")
    filename = str(att.Apparecchiatura) + str(timezone.now())
    content = "attachement; filename=%s.pdf"%(filename)
    response["Content-Disposition"] = content
    return response

@login_required
def tuttidocumenti(request, pk):
    att = MAIN.objects.get(id = pk)
    stato = att.Stato.Numero
    docgara = []
    doccomm = []
    doctrasp = []
    doccoll = []
    docagg = []
    if stato >= 5:
        docgara = DocGara.objects.filter(ID_rich = att)
    if stato >=6:
        doccomm = DocComm.objects.filter(ID_rich = att)
    if stato >=7:
        docagg = DocAgg.objects.filter(ID_rich = att)
    if stato >= 8:
        doctrasp = DocTrasp.objects.filter(ID_rich = att)
    if stato >= 9:
        doccoll = DocColl.objects.filter(ID_rich = att)

    context = {
        'docgara' : docgara,
        'st5': '5',
        'doccomm' : doccomm,
        'st6': '6',
        'doctrasp' : doctrasp,
        'st7': '7',
        'doccoll' : doccoll,
        'st8': '8',
        'docagg' : docagg,
        'st9': '9',
        'att': att
    }

    return render(request, 'tuttidocumenti.html', context)
