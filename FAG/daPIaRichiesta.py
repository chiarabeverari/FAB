from .models import *
import os

def crea(f, Qta_tot, id_pi, costo, sereps):
    att = MAIN()
    att.Sede_Reparto = ''
    for sr in sereps:
        att.Sede_Reparto += f'• {sr} \n' 
    att.ID_PianoInvestimenti = id_pi
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
    att.Fonte = f.Fonte
    att.Anno_Previsto = f.Anno_Previsto
    att.Simili = f.Simili
    att.NolMesi = f.NolMesi
    att.Prezzo_acquisto = f.Prezzo_acquisto
    att.Prezzo_Noleggio = f.Prezzo_Noleggio
    att.Prezzo_Service = f.Prezzo_Service
    att.Compilatore = f.Compilatore
    att.Apparecchiatura = f.Apparecchiatura
    att.PercIVA = f.PercIVA
    att.Qta = Qta_tot
    att.Costo_Presunto_IVA = costo
    att.Costo_Presunto_NOIVA = costo / ((100+f.PercIVA)/100)
    att.Data = timezone.now()
    att.def_stato()
    current_year_atts = MAIN.objects.filter(Data__year = att.Data.strftime('%Y'))
    k=1
    for year in current_year_atts:
        k += 1
    
    att.Progressivo = str(k)+'-'+str(att.Data.strftime('%Y'))
  
    att.save()
    return att

def crea_cons(att, listatipi, listacu, listacm, listatot, listaper):
    
    for tipo,cu,cm,tot,per in zip(listatipi, listacu, listacm, listatot, listaper):
        c = ConsumabiliMain(ID_rich = att, Tipo = tipo, CostoUnitario = cu, ConsumoMedio = cm, Periodo = per, Totale = tot)
        c.save()
    