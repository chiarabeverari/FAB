from .models import *
from .forms import *
from .service import *
from datetime import datetime, date
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

'''
def get_utente_primario(richiesta):
    """
    Trova il primario responsabile in base alla richiesta.
    """
    if hasattr(richiesta, 'sede_reparto'):
        return richiesta.sede_reparto.primario  # Supponiamo che il reparto abbia un campo 'primario'
    return None

def get_utente_dir_medica():
    """
    Restituisce l'utente responsabile della direzione sanitaria.
    """
    return User.objects.filter(groups__name="DIR.MEDICA").first()  # Trova un utente nel gruppo Direzione

def get_utente_ing_clinica():
    """
    Trova il primario responsabile in base alla richiesta.
    """
    return User.objects.filter(groups__name="ING.CLINICA").first()  # Trova un utente nel gruppo Direzione
'''

def crea_notifica(utente, richiesta, stato):
    print(f"Chiamata a crea_notifica con stato: {stato}, richiesta ID: {richiesta.id}")

    messaggi_notifica = {
        "BOZZA": {
            "MEDICO": "La tua richiesta è stata salvata come bozza.",
            "PRIMARIO": "Richiesta valutazione modulo"
        },
        "DEFINITIVA": {
            "MEDICO": "Modulo accettato da DIR",
            "DIR. MEDICA": "Richiesta valutazione modulo"
        },
        "RIFIUTATA_DA_DIR": {
            "MEDICO": "Modulo Rifiutato da DIR",
        },
        "MODIFICA": {
            "MEDICO": "Richiesta Modifica del modulo",
        },
        "SPEDITA": {
            "MEDICO": "Modulo accettato da DAA",
            "PRIMARIO": "Modulo accettato da DAA",
            "ING. CLINICA": "Richiesta valutazione modulo"
        },
        "NEGATA_DA_DAA": {
            "MEDICO": "Modulo rifiutato da DAA",
            "PRIMARIO": "Modulo rifiutato da DAA"
        },
        "APPROVATA": {
            "MEDICO": "Modulo accettato da UIC",
            "PRIMARIO": "Modulo accettato da UIC",
            "DIR. MEDICA": "Modulo accettato da UIC",
        },
        "NON_APPROVATA": {
            "MEDICO": "Modulo rifiutata da UIC.",
            "PRIMARIO": "Modulo rifiutata da UIC.",
            "DIR. MEDICA": "Modulo rifiutata da UIC.",
        }
    }

    content_type = ContentType.objects.get_for_model(richiesta)

    # Troviamo tutti gli utenti che devono ricevere la notifica in base al loro gruppo
    utenti_destinatari = MedicalUser.objects.filter(
        Gruppo__Descrizione__in=messaggi_notifica.get(stato, {}).keys()
    )
    print(f"Utenti destinatari trovati: {utenti_destinatari.count()}")  # Debug

# Creiamo una notifica per ogni utente coinvolto
    for utente in utenti_destinatari:
        messaggio = messaggi_notifica[stato].get(utente.Gruppo.Descrizione)
        if messaggio:
            NotificaFAB.objects.create(
                utente=utente,
                stato_richiesta=stato,
                messaggio=messaggio,
                content_type=content_type,
                object_id=richiesta.id
            )


@login_required
def notificheFAB(request):
    is_admin = request.user.Gruppo and request.user.Gruppo.Descrizione == "ADMIN"
    
    gruppo_selezionato = request.GET.get('gruppo', None)
    if is_admin and gruppo_selezionato:
        notifiche = NotificaFAB.objects.filter(
            utente__Gruppo__Descrizione=gruppo_selezionato, 
            letta=False
        ).order_by('-data_creazione')
    else:
        notifiche = NotificaFAB.objects.filter(
            utente=request.user, 
            letta=False
        ).order_by('-data_creazione')

    gruppi = Gruppi.objects.filter(Descrizione__in=["MEDICO", "PRIMARIO", "DIR. MEDICA", "ING. CLINICO"])

    notifiche_info = []
    for notifica in notifiche:
        richiesta = notifica.content_type.get_object_for_this_type(id=notifica.object_id)
        
        # Determiniamo il tipo della richiesta
        if isinstance(richiesta, Fabbisogni):
            tipo_richiesta = "programmata"
        elif isinstance(richiesta, UrgenteRequest):
            tipo_richiesta = "urgente"
        else:
            tipo_richiesta = "sconosciuto"

        notifiche_info.append({
            "data_creazione": notifica.data_creazione,
            "messaggio": notifica.messaggio,
            "sede_reparto": richiesta.Sede_Reparto if hasattr(richiesta, "Sede_Reparto") else "-",
            "apparecchiatura": richiesta.Apparecchiatura if hasattr(richiesta, "Apparecchiatura") else "-",
            "compilatore": richiesta.Compilatore if hasattr(richiesta, "Compilatore") else "-",
            "url_visualizza": f"/visualizza_richiesta/{richiesta.id}/{tipo_richiesta}/" if richiesta and tipo_richiesta else None
        })
        print(f"DEBUG: richiesta.id={richiesta.id}, tipo_richiesta={tipo_richiesta}")

    context = {
        'notifiche_info': notifiche_info,
        'is_admin': is_admin,
        'gruppi': gruppi,
        'gruppo_selezionato': gruppo_selezionato
    }
    return render(request, 'notificheFAB.html', context)