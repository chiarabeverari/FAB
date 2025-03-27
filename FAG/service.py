from .models import * 
from .not_FAB import *
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

'''
#avanzamento stato richiesta
def avanzamento_stato(self, utente, nuovo_stato): #da modificare 
        """
        Metodo per avanzare lo stato in base a chi approva.
        """
        permessi_gruppo = {
        "PRIMARIO": {
            "FaVeTu": [StatoRichiesta.DEFINITIVA, StatoRichiesta.RIFIUTATA_DA_DIR, StatoRichiesta.MODIFICA],
        },
        "DIR. MEDICA": {
            "SpVeTu": [StatoRichiesta.SPEDITA, StatoRichiesta.NEGATA_DA_DAA],
        },
        "ING. CLINICA": {
            "PIVeTu": [StatoRichiesta.APPROVATA, StatoRichiesta.NON_APPROVATA],
        }
        }
        # Verifica che l'utente abbia un gruppo valido
        gruppo_utente = getattr(utente.Gruppo, "Descrizione", None)
        if utente.Gruppo is None:
            raise PermissionError("L'utente non ha un gruppo associato e non può modificare lo stato.")
    
        gruppo_utente = utente.Gruppo.Descrizione  # Gruppo a cui l'utente appartiene
    
        # Controlla se il gruppo ha permessi per avanzare lo stato
        permessi = permessi_gruppo.get(gruppo_utente, {})
    
        # Verifica che l'utente abbia almeno un permesso valido
        if not any(getattr(utente.Gruppo, permesso, False) and nuovo_stato in stati_validi 
                for permesso, stati_validi in permessi.items()):
            raise PermissionError(f"Il ruolo {gruppo_utente} non può impostare lo stato {nuovo_stato}.")

        # Aggiorna lo stato della richiesta
        self.StatoRic = nuovo_stato
        self.save()
'''

def get_opzioni_stato(utente, ruolo_scelto=None):
    permessi_gruppo = {
        "PRIMARIO": {
            "FaVeTu": [StatoRichiesta.DEFINITIVA, StatoRichiesta.RIFIUTATA_DA_DIR, StatoRichiesta.MODIFICA],
        },
        "DIR. MEDICA": {
            "SpVeTu": [StatoRichiesta.SPEDITA, StatoRichiesta.NEGATA_DA_DAA],
        },
        "ING. CLINICA": {
            "PIVeTu": [StatoRichiesta.APPROVATA, StatoRichiesta.NON_APPROVATA],
        }
    }

    # Se è superuser, usa il ruolo scelto per restituire gli stati giusti
    if utente.is_superuser:
        if ruolo_scelto and ruolo_scelto in permessi_gruppo:
            stati_per_ruolo = []
            for stati in permessi_gruppo[ruolo_scelto].values():
                stati_per_ruolo.extend(stati)
            return stati_per_ruolo  # Restituisce gli stati validi per il ruolo selezionato
        return []  # Nessun ruolo scelto → lista vuota

    # Se l'utente non è un superuser, gestisce normalmente il suo gruppo
    if not hasattr(utente, "Gruppo") or not hasattr(utente.Gruppo, "Descrizione"):
        return []  # L'utente non ha un gruppo valido

    gruppo_utente = utente.Gruppo.Descrizione

    if gruppo_utente not in permessi_gruppo:
        return []

    stati_disponibili = []
    for permesso, stati_validi in permessi_gruppo[gruppo_utente].items():
        if getattr(utente.Gruppo, permesso, False):  
            stati_disponibili.extend(stati_validi)

    return stati_disponibili

@login_required
def modifica_stato_richiesta(request, richiesta_id, modello):
    # Determina il modello giusto
    if modello == "Urgente":
        modello_richiesta = UrgenteRequest
    elif modello == "Programmata":
        modello_richiesta = Fabbisogni
    else:
        return HttpResponse("Modello non valido", status=400)
    
    richiesta = get_object_or_404(modello_richiesta, id=richiesta_id)

    stato_richiesta= get_object_or_404(
        RichiestaStato, 
        content_type=ContentType.objects.get_for_model(modello_richiesta),
        object_id=richiesta_id
        )
    
    ruolo_scelto = request.GET.get("ruolo")  # L'admin sceglie un ruolo dal menu a tendina

    print("Superuser:", request.user.is_superuser)
    print("Ruolo scelto:", ruolo_scelto)

    if request.user.is_superuser:
        #ruolo_scelto = request.GET.get("ruolo")  # L'admin sceglie un ruolo dal menu a tendina
        #opzioni_stato = get_opzioni_stato(request.user).get(ruolo_scelto, [])
        opzioni_stato = get_opzioni_stato(request.user, ruolo_scelto)  # Usa il ruolo scelto
        admin_roles = ["PRIMARIO", "DIR. MEDICA", "ING. CLINICA"]  # Ruoli disponibili per il superuser
    else:
        opzioni_stato = get_opzioni_stato(request.user)
        admin_roles=None #non è superuser

    #  QUI CONVERTIAMO GLI STATI IN STRINGHE 
    opzioni_stato = [stato.value for stato in opzioni_stato]
    print("Opzioni stato disponibili (convertite in stringhe):", opzioni_stato)

    #print("Opzioni stato disponibili:", opzioni_stato)
    # Ottiene le opzioni disponibili per l'utente corrente
    #opzioni_stato = get_opzioni_stato(request.user)
    
    if request.method == "POST":
        nuovo_stato = request.POST.get("stato")
        commento=request.POST.get("commento")
        
        if nuovo_stato not in opzioni_stato:
            return HttpResponse("Non sei autorizzato a selezionare questo stato.", status=403)
        
        ''''
        # Recuperiamo l'istanza corretta di RichiestaStato
        try:
            nuovo_stato_instance = RichiestaStato.objects.get(StatoRic=nuovo_stato, content_type=ContentType.objects.get_for_model(modello_richiesta), object_id=richiesta_id)
        except RichiestaStato.DoesNotExist:
            return HttpResponse("Errore: lo stato selezionato non esiste nel database.", status=400)
        '''
        # Recupera lo stato attuale della richiesta
        stato_richiesta = get_object_or_404(
        RichiestaStato,
        content_type=ContentType.objects.get_for_model(modello_richiesta),
        object_id=richiesta_id
        )

        # Se l'admin sta modificando, usa il ruolo selezionato
        utente_modifica = request.user  
        data_modifica = now()

        if request.user.is_superuser and ruolo_scelto:
            print("L'admin sta modificando con ruolo:", ruolo_scelto)

            if ruolo_scelto == "PRIMARIO":
                richiesta.primario_utente = utente_modifica
                richiesta.primario_data = data_modifica
                print('utente:', richiesta.primario_utente)
                print('data modifica:', richiesta.primario_data)
            elif ruolo_scelto == "DIR. MEDICA":
                richiesta.dir_medica_utente = utente_modifica
                richiesta.dir_medica_data = data_modifica
                print('utente:', richiesta.dir_medica_utente)
                print('data modifica:', richiesta.dir_medica_data)
            elif ruolo_scelto == "ING. CLINICA":
                richiesta.ing_clinico_utente = utente_modifica
                richiesta.ing_clinico_data = data_modifica
                print('utente:', richiesta.ing_clinico_utente)
                print('data modifica:', richiesta.ing_clinico_data)

        elif hasattr(request.user, "Gruppo") and request.user.Gruppo:
            # Se non è un admin, usa il suo vero ruolo
            ruolo_effettivo = request.user.Gruppo.Descrizione

            if ruolo_effettivo == "PRIMARIO":
                richiesta.primario_utente = utente_modifica
                richiesta.primario_data = data_modifica
                print('utente:', richiesta.primario_utente)
                print('data modifica:', richiesta.primario_data)
            elif ruolo_effettivo == "DIR. MEDICA":
                richiesta.dir_medica_utente = utente_modifica
                richiesta.dir_medica_data = data_modifica
                print('utente:', richiesta.dir_medica_utente)
                print('data modifica:', richiesta.dir_medica_data)
            elif ruolo_effettivo == "ING. CLINICA":
                richiesta.ing_clinico_utente = utente_modifica
                richiesta.ing_clinico_data = data_modifica
                print('utente:', richiesta.ing_clinico_utente)
                print('data modifica:', richiesta.ing_clinico_data) 

        stato_richiesta.StatoRic= nuovo_stato #assegniamo l'istanza corretta
        stato_richiesta.utente=request.user
        print('utente modifica:', stato_richiesta.utente)
        
        if commento: 
            stato_richiesta.commento=commento
        stato_richiesta.save()
        richiesta.save()
        crea_notifica(request.user,richiesta,nuovo_stato)
        return redirect('success_valutazione')  # Pagina di successo

    
    context={
        "stato_richiesta": stato_richiesta,
        "opzioni_stato": opzioni_stato,
        "modello": modello,
        "admin_roles": admin_roles,
        "ruolo_scelto": ruolo_scelto
    }

    return render(request, "modifica_stato.html", context)



#crea nuovo stato per la richiesta
def crea_stato_per_richiesta(richiesta, utente):
    print(f"Creazione stato per richiesta ID: {richiesta.id}")  # Debug
    stato = RichiestaStato.objects.create(
        StatoRic=StatoRichiesta.BOZZA,
        content_type=ContentType.objects.get_for_model(richiesta),  # Indica il modello collegato
        object_id=richiesta.id,  # ID della richiesta specifica
        utente=utente
    )
    richiesta.StatoRic = stato
    richiesta.save(update_fields=['StatoRic'])
    print(f"Stato creato: {stato}")  # Debug
    return stato
'''
richiesta = UrgenteRequest.objects.get(id=1)
crea_stato_per_richiesta(richiesta, request.user)
'''

#recupera lo stato della richiesta
def get_stato_richiesta(richiesta):
    return RichiestaStato.objects.filter(
        content_type=ContentType.objects.get_for_model(richiesta),
        object_id=richiesta.id
    ).first()

'''
richiesta = MAIN.objects.get(id=10)
stato = get_stato_richiesta(richiesta)
print(stato.StatoRic)
'''

def trasferisci_fabbisogni_approvati():
    fabbisogni_approvati = Fabbisogni.objects.filter(StatoRic__StatoRic=StatoRichiesta.APPROVATA)

    for fab in fabbisogni_approvati:
        # Controlliamo se esiste già un MAIN collegato a questo Fabbisogno
        if not MAIN.objects.filter(ID_PianoInvestimenti=fab.ID_PianoInvestimenti).exists():
            MAIN.objects.create(
                ID_PianoInvestimenti=fab.ID_PianoInvestimenti,
                Progressivo=fab.Progressivo,
                Apparecchiatura=fab.Apparecchiatura,
                Sede_Reparto=fab.Sede_Reparto,
                Qta=fab.Qta,
                Costo_Presunto_NOIVA=fab.Costo_Presunto_NOIVA,
                Costo_Presunto_IVA=fab.Costo_Presunto_IVA,
                Stato="IN ATTESA",  # Impostiamo uno stato iniziale per la richiesta in MAIN
            )
