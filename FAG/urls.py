"""FAG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import *
from .exportviews import *
from .uploadviews import *
from .deleteviews import *
from .makenew import *
from .not_FAB import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from . import views
from django.views.generic import TemplateView
from .service import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('home/<str:var>', home, name='home'),
    path('seleziona_tipo/', views.seleziona_tipo, name='seleziona_tipo'),
    path('new/<str:opt>', new, name="new"),
    path('new_urgente/', views.new_urgente, name='new_urgente'), #modulo urgente online
    path('new_urg_2_4/<int:pk>', views.new_urg_2_4, name='new_urg_2_4'), #modulo urgente online 2.4
    path('new_urg_4e2/<int:pk>', views.new_urg_4e2, name='new_urg_4e2'), #modulo urgente online 4e2
    path('new_urg_4e3/<int:pk>', views.new_urg_4e3, name='new_urg_4e3'), #modulo urgente online 4e3
    path('new_urg_5/<int:pk>', views.new_urg_5, name='new_urg_5'), #modulo urgente online 5
    path('new_urg_5e2/<int:pk>', views.new_urg_5e2, name='new_urg_5e2'), #modulo urgente online 5e2
    path('attachements/<str:pk>/<str:var>/', attachements, name="attachements"),
    path('new_2_4/<str:pk>/<str:var>/', new_2_4, name="new_2_4"),
    path('modificaspecifica/<str:pk>/<str:var>/', modificaspecifica, name="modificaspecifica"),
    path('new_4e2/<str:pk>/<str:var>//', new_4e2, name="new_4e2"),
    path('modificaunicita/<str:pk>/<str:var>/', modificaunicita, name="modificaunicita"),
    path('new_4e3/<str:pk>/<str:var>//', new_4e3, name="new_4e3"),
    path('modificacriteri/<str:pk>/<str:var>/', modificacriteri, name="modificacriteri"),
    path('new_5/<str:pk>/<str:var>/', new_5, name="new_5"),
    path('modificaconsumabili/<str:pk>/<str:var>/', modificaconsumabili, name="modificaconsumabili"),
    path('raccoltafabbisogni/', raccoltafabbisogni, name="raccoltafabbisogni"),
    path('pianodiinvestimenti/', pianodiinvestimenti, name="pianodiinvestimenti"),
    path('new_5e2/<str:pk>/<str:var>//', new_5e2, name="new_5e2"),
    path('modificaditteinserite/<str:pk>/<str:var>/', modificaditteinserite, name="modificaditteinserite"),
    path('aggiorna/<str:pk>/<str:var>', aggiorna, name="aggiorna"),
    path('aggiornadata/', aggiornadata, name="aggiornadata"),
    path('deleteattachements/<str:pk>/<str:var>', deleteattachements, name='deleteattachements'),
    path('deleteditta/<str:pk>/<str:var>', deleteditta, name='deleteditta'),
    path('deletespecifiche/<str:pk>/<str:var>', deletespecifiche, name='deletespecifiche'),
    path('deleteunicita/<str:pk>/<str:var>', deleteunicita, name='deleteunicita'),
    path('deletecriteri/<str:pk>/<str:var>', deletecriteri, name='deletecriteri'),
    path('deleteconsu/<str:pk>/<str:var>', deleteconsu, name='deleteconsu'),
    path('deletepriorita/<str:pk>/<str:var>', deletepriorita, name='deletepriorita'),
    path('valutazione/<str:pk>/', valutazione, name='valutazione'),
    path('visualizza/<str:pk>/<str:var>', visualizza, name='visualizza'),
    path('visualizzaricerca/<int:pk>/<str:modello>/', visualizzaricerca, name='visualizzaricerca'),
    path('register/', register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('mylogin/', mylogin, name='mylogin'),
    path('export_csv/', export_csv, name="export-csv" ),
    path('export_excel/', export_excel, name="export-excel" ),
    path('export_csvpiano/', export_csvpiano, name="export-csvpiano" ),
    path('export_excelpiano/', export_excelpiano, name="export-excelpiano" ),
    path('export_csvfabbisogni/', export_csvfabbisogni, name="export-csvfabbisogni" ),
    path('export_excelfabbisogni/', export_excelfabbisogni, name="export-excelfabbisogni" ),
    path('export_excelass/', export_excelass, name="export-excelass" ),
    path('export_pdf/<str:pk>', export_pdf, name="export_pdf" ),
    path('export_pdf_valutazione/<str:pk>', export_pdf_valutazione, name="export_pdf_valutazione" ),
    path('conferma_richiesta/<str:pk>', conferma_richiesta, name="conferma_richiesta"),
    path('richiesta_invalutazione/<str:pk>', richiesta_invalutazione, name="richiesta_invalutazione"),
    path('_richiesta/<str:pk>', avvio_richiesta, name="avvio_richiesta"),
    path('invioProvv/<str:pk>', invioProvv, name="invioProvv"),
    path('garainiz/<str:pk>', garainiz, name="garainiz"),
    path('sospensione/<str:pk>', sospensione, name="sospensione"),
    path('collaudo/<str:pk>', collaudo, name="collaudo"),
    path('acquisto/<str:pk>', acquisto, name="acquisto"),
    path('comissione/<str:pk>', comissione, name="comissione"),
    path('delibera/<str:pk>', delibera, name="delibera"),
    path('sedereparti/', sedereparti, name="sedereparti"),
    path('serepreg/', serepreg, name="serepreg"),
    path('priorita/<str:var>', priorita, name="priorita"),
    path('modificasedereparti/<str:pk>', modificasedereparti, name="modificasedereparti"),
    path('modificapriorita/<str:pk>/<str:var>', modificapriorita, name="modificapriorita"),
    path('deletesedereparti/<str:pk>', deletesedereparti, name="deletesedereparti"),
    path('rimuovi/<str:pk>', rimuovi, name="rimuovi"),
    path('useraccount', useraccount, name="useraccount"),
    path('letto/<str:pk>', letto, name="letto"),
    path('non_letto/<str:pk>', non_letto, name="non_letto"),
    path('tuttoletto/', tuttoletto, name="tuttoletto"),
    path('cancellatutto/', cancellatutto, name="cancellatutto"),
    path('nuova/', nuova, name="nuova"), #programmato
    #path('nuovaurg/', nuovaurg, name="nuovaurg"), 
    path('aggiungi/urgente', aggiungi_fabbisogno_urgente, name='aggiungi_fabbisogno_urgente'), 
    path('completa_richiesta/<str:pk>/', completa_richiesta, name="completa_richiesta"),
    path('download/', download, name="download"),
    path('downloadfilledpdf/<str:pk>', downloadfilledpdf, name="downloadfilledpdf"),
    path('aggiungidocumenti/<str:pk>/<str:stato>/', aggiungidocumenti, name="aggiungidocumenti"),
    path('eliminazioneDoc/<str:pk>/<str:var>/', eliminazioneDoc, name="eliminazioneDoc"),
    path('update4/<str:pk>', update4, name="update4"),
    path('rimuoviPI/<str:pk>', rimuoviPI, name="rimuoviPI"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("modificauser/<str:var>", modificauser, name="modificauser"),
    path("tuttiprofili/", tuttiprofili, name="tuttiprofili"),
    path("rimuoviuser/<str:pk>", rimuoviuser, name="rimuoviuser"),
    path("rimuovirichiesta/<str:pk>", rimuovirichiesta, name="rimuovirichiesta"),
    path('tuttidocumenti/<str:pk>', tuttidocumenti, name="tuttidocumenti"),
    path("password/", PasswordsChangeView.as_view(template_name = "registration/modificapassword.html")),
    path('registranew/', registranew, name="registranew"),
    path('copiafabbisogno/', copiafabbisogno, name="copiafabbisogno"),
    path('download/offline/', views.download_offline, name='download_offline'),
    path('success_page/<int:pk>',TemplateView.as_view(template_name='success_page.html'), name='success_page'),
    path('deletespecificheurg/<int:pk>', deletespecificheurg, name='deletespecificheurg'), 
    path('modificaspecificaurg/<int:pk>', views.modificaspecificaurg, name='modificaspecificaurg'), #manca html
    path('deletecriteriurg/<int:pk>', deletecriteriurg, name='deletecriteriurg'),
    path('modificacriteriurg/<int:pk>', views.modificacriteriurg, name='modificacriteriurg'), #manca html
    path('deleteunicitaurg/<int:pk>', deleteunicitaurg, name='deleteunicitaurg'),
    path('modificaunicitaurg/<int:pk>', views.modificaunicitaurg, name='modificaunicitaurg'), #manca html
    path('deleteconsuurg/<int:pk>', deleteconsuurg, name='deleteconsuurg'),
    path('modificaconsumabiliurg/<int:pk>', views.modificaconsumabiliurg, name='modificaconsumabiliurg'), #manca html
    path('deletedittaurg/<int:pk>', deletedittaurg, name='deletedittaurg'),
    path('modificaditteinserite_urg/<int:pk>', views.modificaditteinserite_urg, name='modificaditteinserite_urg'), #manca html
    path('visualizzaurg/<int:pk>', views.visualizzaurg, name='visualizzaurg'),
    path('aggiornaurg/<int:pk>', views.aggiornaurg, name='aggiornaurg'),
    path('rimuoviurg/<int:pk>', rimuoviurg, name='rimuoviurg'),
    path('export_pdf_urg/<int:pk>', export_pdf_urg, name='export_pdf_urg'),
    path('export_pdf_valutazione_urg/<int:pk>', export_pdf_valutazione_urg, name='export_pdf_valutazione_urg'),
    path('ricerca/', pagina_ricerca, name='pagina_ricerca'), #pagina ricerca
    path('attivita/', attivita, name='attivita'), #pagina attivita
    path('valutazioneprogram/<int:pk>/<int:var>/',views.valutazioneprogram, name='valutazioneprogram'),
    path('valutazioneurg/<int:pk>',views.valutazioneurg, name='valutazioneurg'),
    path('modifica_stato_richiesta/<int:richiesta_id>/<str:modello>/', modifica_stato_richiesta, name='modifica_stato_richiesta'),
    path('success_valutazione/', TemplateView.as_view(template_name='success_valutazione.html'), name='success_valutazione'),
    path('tab_assegnazioneprior', tab_assegnazioneprior, name='tab_assegnazioneprior'),
    path('assegn1/<int:pk>/<int:var>/', views.assegn1, name='assegn1'),
    path('assegn2/<int:pk>/<int:var>/', assegn2, name='assegn2'), 
    path('notificheFAB/',notificheFAB, name='notificheFAB'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
