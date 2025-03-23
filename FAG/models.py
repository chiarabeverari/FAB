from .settings import AUTH_USER_MODEL
from datetime import datetime
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import  PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.functional import lazy
from turtle import end_fill
from django.conf import settings
from django.utils.timezone import now
#from . import signals



class SeRep (models.Model): #sede, reparto, subreparto
    Sede = models.CharField(max_length = 500)
    Reparto = models.CharField(max_length = 500)
    Sub_Reparto = models.CharField(max_length = 500)
    CDC = models.CharField(max_length=200, null=True)
    def __str__(self):
        return str(self.Sede)+' - '+str(self.Reparto)+' - '+str(self.Sub_Reparto)

class SeRepReg(models.Model): #sede, reparto
    Sede = models.CharField(max_length=1000)
    Reparto = models.CharField(max_length=2000)
    def __str__(self):
        return str(self.Sede)+' - '+str(self.Reparto)
 

class Sta(models.Model): #sembra una tabella
    Nome = models.CharField(max_length = 500 )
    Numero = models.IntegerField(default=0)
    def __str__(self):
        return str(self.Nome)
    
def crea_nuovo():
    if Sta.objects.filter(Nome = 'Richiesta Avviata').exists():
        pass
    else: #dall'inserimento specifiche fino alla gara 
        listastati = ['Richiesta Valutata Negativamente', 'Richiesta Avviata', 'Richiesta Completata', 'Valutata', 'Spedita al Provveditorato', 'Avvio Gara', 'Valutazione Offerte', 'Aggiudicazione', 'Acquisizione', 'Collaudo',  'Sospensione']
        c = 0
        for l in listastati:
            s = Sta()
            s.Nome = l
            s.Numero = c
            s.save()
            c += 1


class Priorita(models.Model):
    Numero = models.IntegerField(default = 0, unique = True)
    Descrizione = models.CharField(max_length = 1200, unique = True)

    def __str__(self):
        return str(self.Numero)


class Professioni(models.Model):
    Nome = models.CharField(max_length=255, unique = True)

    def __str__(self):
        return str(self.Nome)


class Gruppi(models.Model):
    Descrizione = models.CharField(max_length=500, unique=True)
    Numero = models.IntegerField(default=0, unique = True)

    # AUTORIZZAZIONI FABBISOGNI
    FaVeTu = models.BooleanField(default = False)
    FaVePr = models.BooleanField(default = False)
    FaIns = models.BooleanField(default = False)
    FaMoTu = models.BooleanField(default = False)
    FaMoPr = models.BooleanField(default = False)

    # AUTORIZZAZIONI SPECIFICHE
    SpVeTu = models.BooleanField(default = False)
    SpVePr = models.BooleanField(default = False)
    SpInsPr = models.BooleanField(default = False)
    SpInsTu = models.BooleanField(default = False)
    SpMoTu = models.BooleanField(default = False)
    SpMoPr = models.BooleanField(default = False)

    # AUTORIZZAZIONI GARE
    GaVeTu = models.BooleanField(default = False)
    GaVePr = models.BooleanField(default = False)
    GaValTec = models.BooleanField(default = False)
    GaValCli = models.BooleanField(default = False)
    GaFlu = models.BooleanField(default = False)

    # AUTORIZZAZIONE PIANO INVESTIMENTI
    PIVeTu = models.BooleanField(default = False)  
    PIVePr = models.BooleanField(default = False)
    PIIns = models.BooleanField(default = False)
    PIMod = models.BooleanField(default = False)

    # AUTORIZZAZIONI UBICAZIONI E CDC
    UbVe = models.BooleanField(default = False)
    UbIns = models.BooleanField(default = False)
    UbMod = models.BooleanField(default = False)

    # AUTORIZZAZIONI PROFILI PROFESSIONALI
    ProfVe = models.BooleanField(default = False)
    ProfIns = models.BooleanField(default = False)
    ProfMod = models.BooleanField(default = False)

    # AUTORIZZAZIONI PRIORITA'
    PrVe = models.BooleanField(default = False)
    PrIns = models.BooleanField(default = False)
    PrMod = models.BooleanField(default = False)

    # AUTORIZZAZIONI EXPORT
    ExSi = models.BooleanField(default = False)


    def __str__(self):
        return str(self.Descrizione)

def crea_gruppi():
    print('Entrato')
    print(Gruppi.objects.all())
    if len(Gruppi.objects.all()) == 0:
        print('entrato')
        listagruppi = ['MEDICO', 'ING. CLINICO', 'DIR. MEDICA', 'PROVVEDITORATO' ,'ADMIN' ,'SUPERUSER','PRIMARIO']
        c = 1
        for l in listagruppi:
            g = Gruppi()
            g.Descrizione = l
            g.Numero = c
            if l=='ADMIN':
                g.FaVeTu = True
                g.FaIns = True
                g.FaMoTu = True
                g.SpVeTu = True
                g.SpInsTu = True
                g.SpMoTu = True
                g.GaVeTu = True
                g.GaFlu = True
                g.PIVeTu = True
                g.PIIns = True
                g.PIMod = True
                g.UbVe = True
                g.UbIns = True
                g.UbMod = True
                g.ProfVe = True
                g.ProfIns = True
                g.ProfMod = True
                g.PrVe = True
                g.PrIns = True
                g.PrMod = True
                g.ExSi = True
            g.save()
            c += 1


class MyAccountManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Users must have a username")
        user = self.model(
            username = username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, username, password):
        user = self.create_user(
            username = username,
            password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

class MedicalUser(AbstractBaseUser,PermissionsMixin):
    Nome = models.CharField(max_length=500)
    username = models.CharField(max_length=30, unique=True)
    Cognome = models.CharField(max_length=500)
    Sede_Reparto = models.ForeignKey(SeRepReg, null=True, on_delete = models.SET_NULL)
    Profilo_Professionale = models.ForeignKey(Professioni, null=True, on_delete=models.SET_NULL, blank=True)
    email = models.EmailField()
    Gruppo = models.ForeignKey(Gruppi, null=True, blank=True, on_delete = models.SET_NULL)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MyAccountManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return str(self.Nome) + ' ' + str(self.Cognome)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_Label):
        return True
    
class StatoRichiesta(models.TextChoices):
    BOZZA = "BOZZA", "Bozza"
    DEFINITIVA = "DEFINITIVA", "Definitiva"
    RIFIUTATA_DA_DIR = "RIFIUTATA_DA_DIR", "Rifiutata da Direzione"
    MODIFICA = "MODIFICA", "Modifica"
    SPEDITA = "SPEDITA", "Spedita"
    NEGATA_DA_DAA = "NEGATA_DA_DAA", "Negata da DAA"
    APPROVATA = "APPROVATA", "Approvata"
    NON_APPROVATA = "NON_APPROVATA", "Non approvata"
    
class RichiestaStato(models.Model):
    StatoRic = models.CharField(
        max_length=20,
        choices=StatoRichiesta.choices,
        default=StatoRichiesta.BOZZA
    )

    #gestisce meglio il default di content_type, si riferisce al tipo di modello della richiesta  
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)  # Tipo di modello collegato
    object_id = models.PositiveIntegerField(null=True)  # ID dell'oggetto collegato, gestire meglio null
    richiesta = GenericForeignKey('content_type', 'object_id')  # Chiave dinamica
    utente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    data_modifica = models.DateTimeField(auto_now=True)
    NoteStato=models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.StatoRic}-ID{self.object_id}"
    
    #class Meta:
       #unique_together = ("richiesta_tipo", "richiesta_id")  # Assicura che ci sia un solo stato per richiesta 

class NotificaFAB(models.Model):
    utente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Destinatario notifica
    stato_richiesta = models.CharField(max_length=20, choices=StatoRichiesta.choices)  # Stato che ha generato la notifica
    messaggio = models.TextField()  # Testo della notifica
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  #(Urgente/Fabbisogni)
    object_id = models.PositiveIntegerField()  # ID della richiesta specifica
    richiesta = GenericForeignKey('content_type', 'object_id')  # Associazione dinamica
    data_creazione = models.DateTimeField(auto_now_add=True)  # Data creazione notifica
    letta = models.BooleanField(default=False)  # Flag per sapere se l'utente ha letto la notifica

    def __str__(self):
        return f"Notifica per {self.utente} - Stato: {self.stato_richiesta}"
    

class Fabbisogni(models.Model):
    Sede_Reparto = models.ForeignKey(SeRep, on_delete = models.SET_NULL, null=True)
    ID_PianoInvestimenti = models.CharField(max_length=200, blank=True, null=True)
    Avviato = models.BooleanField(default = False)
    Priorita = models.ForeignKey(Priorita, null=True, on_delete = models.SET_NULL)
    Progressivo = models.CharField(max_length=100, blank=True)
    Compilatore = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)
    Direttore = models.CharField(max_length=255, blank=True)
    Apparecchiatura = models.CharField(max_length=255, blank=True)
    Mot1_1 = models.BooleanField(default=False) # Sostituzione di analoga dismessa o in dismissione
    Mot1_2 = models.BooleanField(default=False) # Implementazione/Aggiornamento di Attrezzatura/Sistema
    Mot1_3 = models.BooleanField(default=False) # Inizio nuova attività
    Mot2_1 = models.BooleanField(default=False) # Mantenimento / recupero delle prestazioni e/o della sicurezza
    Mot2_2 = models.BooleanField(default=False) # Aumento/Miglioramento delle prestazioni
    AggNota = models.CharField(max_length=500, blank = True)
    Acquisto = models.BooleanField(default=False)
    Service = models.BooleanField(default=False)
    Noleggio = models.BooleanField(default=False)
    Tecnologico = models.BooleanField(default=False)
    Valutativo = models.BooleanField(default=False)
    Temporaneo = models.BooleanField(default=False)
    Economico = models.BooleanField(default=False)
    Gestionale = models.BooleanField(default=False)
    NotaNoleggio = models.CharField(max_length=500, blank =True)
    NecInfraSi = models.BooleanField(default=False)
    NecInfraNO = models.BooleanField(default=False)
    NecInfraNota = models.CharField(max_length=500, blank = True)
    SostNota = models.CharField(max_length=500, blank = True)
    Data = models.DateTimeField(default=datetime.now().strftime('%d/%m/%Y'))   
    Fonte = models.CharField(max_length=255, blank=True)
    Anno_Previsto = models.IntegerField(null=True)
    Costo_Presunto_NOIVA = models.IntegerField(null=True)
    Costo_Presunto_IVA =models.IntegerField(null=True)
    NoteGen = models.CharField(max_length=500, blank =True)
    Prezzo_acquisto = models.IntegerField (blank=True,null=True)
    Prezzo_Noleggio = models.IntegerField( blank=True,null=True)
    Prezzo_Service = models.IntegerField( blank=True,null=True)
    Qta = models.IntegerField(default = None, blank=False)
    Simili = models.BooleanField(default=False, blank=True)
    DescrMass = models.CharField(max_length=5000, null=True, blank=True)
    NolMesi = models.IntegerField(null=True, blank=True)
    NewPersSI = models.BooleanField(default=False)
    NewPersNO = models.BooleanField(default=False)
    PercIVA = models.IntegerField(null=True)
    Eliminato = models.BooleanField(default = False)
    StatoRic = models.ForeignKey(RichiestaStato, on_delete=models.CASCADE, null=True, blank=True)
    NoteStato=models.TextField(null=True, blank=True)
    AssegnPrior= models.IntegerField (blank=True,null=True)

    # Campi per tracciare chi ha modificato e quando
    primario_utente = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="primario_fabb", on_delete=models.SET_NULL, null=True, blank=True)
    primario_data = models.DateTimeField(null=True, blank=True)

    dir_medica_utente = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="dir_medica_fabb", on_delete=models.SET_NULL, null=True, blank=True)
    dir_medica_data = models.DateTimeField(null=True, blank=True)

    ing_clinico_utente = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ing_clinico_fabb", on_delete=models.SET_NULL, null=True, blank=True)
    ing_clinico_data = models.DateTimeField(null=True, blank=True)

    
    def __str__(self):
        return f'{self.Progressivo}_{self.Qta}_{self.Apparecchiatura}'

    def costo_presuntoNOIVA(self):
        if self.Prezzo_acquisto is not None:
            self.Costo_Presunto_NOIVA = self.Prezzo_acquisto
            if self.PercIVA != None:
                iva = self.PercIVA * self.Costo_Presunto_NOIVA / 100
                self.Costo_Presunto_IVA = iva + self.Costo_Presunto_NOIVA
        elif self.Prezzo_Noleggio is not None:
            self.Costo_Presunto_NOIVA = self.Prezzo_Noleggio
            if self.PercIVA != None:
                iva = self.PercIVA * self.Costo_Presunto_NOIVA / 100
                self.Costo_Presunto_IVA = iva + self.Costo_Presunto_NOIVA
        elif self.Prezzo_Service is not None:
            self.Costo_Presunto_NOIVA = self.Prezzo_Service
            if self.PercIVA != None:
                iva = self.PercIVA * self.Costo_Presunto_NOIVA / 100
                self.Costo_Presunto_IVA = iva + self.Costo_Presunto_NOIVA


class PI (models.Model):

    ID_PianoInvestimenti = models.CharField(max_length=25)
    Descrizione = models.CharField(max_length=1000, null=True, blank=True)
    Priorita = models.ForeignKey(Priorita, null=True, blank=True, on_delete=models.SET_NULL)
    Anno_Previsto = models.IntegerField(null=False, default = 0)
    Speso = models.IntegerField(null=True, default=0)
    Costo_Presunto_IVA = models.IntegerField(null=True, blank=True)
    Stato = models.CharField(max_length=500, default='Inserito Nel Piano')
    is_ext = models.BooleanField(default = False)
    is_end = models.BooleanField(default = False) #presunto = speso
    is_full = models.BooleanField(default = False) # presunto richieste  = presunto piano
    FabbRel = models.ManyToManyField(Fabbisogni, blank=True )


    def __str__(self):
        return str(self.ID_PianoInvestimenti)
    
    

class MAIN(models.Model):
    
    Sede_Reparto = models.TextField(null=False, default='')
    Priorita = models.ForeignKey(Priorita, null=True, on_delete = models.SET_NULL)
    ID_PianoInvestimenti = models.ForeignKey(PI, null=True, on_delete=models.SET_NULL)
    Progressivo = models.CharField(max_length=100, blank=True)
    Compilatore = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE,)
    Direttore = models.CharField(max_length=255, blank=True)
    Apparecchiatura = models.CharField(max_length=255, blank=True)
    Mot1_1 = models.BooleanField(default=False) # Sostituzione di analoga dismessa o in dismissione
    Mot1_2 = models.BooleanField(default=False) # Implementazione/Aggiornamento di Attrezzatura/Sistema
    Mot1_3 = models.BooleanField(default=False) # Inizio nuova attività
    ValMot = models.CharField(null=True, choices = [('1', 'Congruo'), ('0', 'Non Congruo')], max_length=255) # valutazione motivi espressi per richeiesta o implementazione agg
    ValMotNota = models.CharField(blank = True, max_length=1000)
    ValData = models.DateTimeField(null=True)
    ValUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatore')
    Mot2_1 = models.BooleanField(default=False) # Mantenimento / recupero delle prestazioni e/o della sicurezza
    Mot2_2 = models.BooleanField(default=False) # Aumento/Miglioramento delle prestazioni
    AggNota = models.CharField(max_length=500, blank = True)
    Stato = models.ForeignKey(Sta, on_delete = models.CASCADE, null=True)
    Acquisto = models.BooleanField(default=False)
    Service = models.BooleanField(default=False)
    Noleggio = models.BooleanField(default=False)
    Tecnologico = models.BooleanField(default=False)
    Valutativo = models.BooleanField(default=False)
    Temporaneo = models.BooleanField(default=False)
    Economico = models.BooleanField(default=False)
    Gestionale = models.BooleanField(default=False)
    NotaNoleggio = models.CharField(max_length=500, blank =True)
    NecInfraSi = models.BooleanField(default=False)
    NecInfraNO = models.BooleanField(default=False)
    NecInfraNota = models.CharField(max_length=500, blank = True)
    SostNota = models.CharField(max_length=500, blank = True)
    Data = models.DateTimeField(default=datetime.now())   
    Fonte = models.CharField(max_length=255, blank=True)
    Anno_Previsto = models.IntegerField(null=True)
    Costo_Presunto_NOIVA = models.IntegerField(null=True)
    Costo_Presunto_IVA = models.IntegerField(null=True)
    Data1 = models.DateTimeField(blank=True, null=True)
    Data2 = models.DateTimeField(blank=True, null=True)
    Data3 = models.DateTimeField(blank=True, null=True)
    Data4 = models.DateTimeField(blank=True, null=True)
    Data5 = models.DateTimeField(blank=True, null=True)
    Data6 = models.DateTimeField(blank=True, null=True)
    Data7 = models.DateTimeField(blank=True, null=True)
    Data8 = models.DateTimeField(blank=True, null=True)
    Data9 = models.DateTimeField(blank=True,null=True)
    NoteGen = models.CharField(max_length=500, blank =True)
    Prezzo_acquisto = models.IntegerField (blank=True,null=True)
    Prezzo_Noleggio = models.IntegerField( blank=True,null=True)
    Prezzo_Service = models.IntegerField( blank=True,null=True)
    Qta = models.IntegerField(default = 0, blank=False)
    MotivoAnnullamento = models.CharField(max_length=255,blank=True, null=True)
    FileModuloRichiestaFirmato = models.FileField(null=True)
    FileModuloValutazioneFirmato = models.FileField(null=True)
    Simili = models.BooleanField(default=False, blank=True)
    PercIVA = models.IntegerField(null=False, default = 0)
    NolMesi = models.IntegerField(null=True, blank=True)
    FabbCopiato = models.ForeignKey(Fabbisogni, on_delete = models.CASCADE, null = True, blank = True)
    StatoRic = models.ForeignKey(RichiestaStato, on_delete=models.CASCADE, null=True, blank=True)
    NoteStato=models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.Progressivo) + '_' + str(self.Apparecchiatura)
    
    
    def def_stato(self):
        Date = [self.Data, self.Data1, self.Data2, self.Data3, self.Data4,self.Data5,self.Data6,self.Data7,self.Data8, self.Data9]
        counter = 1
        for i in Date:
            if i != None:
                self.Stato= Sta.objects.get(Numero=counter)
            counter+=1
    
        return(self.Stato)   


    def costo_presuntoNOIVA(self):
        if self.Prezzo_acquisto is not None:
            self.Costo_Presunto_NOIVA = self.Prezzo_acquisto
            if self.PercIVA != None:
                iva = self.PercIVA * self.Costo_Presunto_NOIVA / 100
                self.Costo_Presunto_IVA = iva + self.Costo_Presunto_NOIVA
                print(self.PercIVA)
        elif self.Prezzo_Noleggio is not None:
            self.Costo_Presunto_NOIVA = self.Prezzo_Noleggio
            if self.PercIVA != None:
                iva = self.PercIVA * self.Costo_Presunto_NOIVA / 100
                self.Costo_Presunto_IVA = iva + self.Costo_Presunto_NOIVA
        elif self.Prezzo_Service is not None:
            self.Costo_Presunto_NOIVA = self.Prezzo_Service
            if self.PercIVA != None:
                iva = self.PercIVA * self.Costo_Presunto_NOIVA / 100
                self.Costo_Presunto_IVA = iva + self.Costo_Presunto_NOIVA

        

 


_m_= 'm'
_M_ = 'M'
spec_choices = {
    (_m_, 'm'),
    (_M_, 'M')
}
OK = 'OK'
NO = 'NO'
NC = 'NC'
specvalchoices = {
    (OK, 'OK'),
    (NO, 'NO'),
    (NC, 'NC')
}


class Specifiche(models.Model):
    ID_rich = models.ForeignKey(MAIN, on_delete=models.CASCADE)
    Specifica = models.CharField(max_length=1000, blank=False)
    ValSpecCli = models.CharField(max_length = 255, choices = specvalchoices, null=True)
    ValSpecCliNota = models.CharField(max_length= 1000, blank=True, null=True)
    ValCliData = models.DateTimeField(blank=True, null=True)
    ValCliUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatoreclinicos')
    ValSpecTec = models.CharField(max_length = 255, choices = specvalchoices, null=True)
    ValSpecTecNota = models.CharField(max_length= 1000, blank=True, null=True)
    ValTecData = models.DateTimeField(blank=True, null=True)
    ValTecUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatoretecnicos')
    MotivoClinico = models.CharField(max_length=1000, blank=False)
    Un = models.BooleanField(default=False)
    rif = models.IntegerField(default=0, null=False)
    Min = models.BooleanField(default=False)
    Max = models.BooleanField(default=False)
    


    def __str__(self):
        return str(self.ID_rich)+'-'+str(self.rif)
    

class Unicita(models.Model):
    ID_rich = models.ForeignKey(MAIN, on_delete=models.CASCADE, null=True)
    rifext = models.ForeignKey(Specifiche, on_delete=models.CASCADE)
    ValCli = models.CharField(max_length = 500, null = True)
    ValCliData = models.DateTimeField(blank = True, null=True)
    ValCliUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatoreclinico')
    ValTec = models.CharField(max_length=500, null=True)
    ValTecData = models.DateTimeField(blank=True, null=True)
    ValTecUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatoretecnico')
    Nota = models.CharField(max_length=500, null=True)

    def __str__(self):
        return str(self.rifext) 

class ConsumabiliFabb(models.Model):
    ID_rich = models.ForeignKey(Fabbisogni, on_delete=models.CASCADE)
    Tipo = models.CharField(max_length=500, blank=False)
    CostoUnitario = models.IntegerField(default=0, blank =False)
    ConsumoMedio = models.IntegerField(default=0, blank =False)
    Periodo = models.IntegerField(default=0, blank = False)
    Totale = models.IntegerField(default=0, blank =False)

class ConsumabiliMain(models.Model):
    ID_rich = models.ForeignKey(MAIN, on_delete=models.CASCADE)
    Tipo = models.CharField(max_length=500, blank=False)
    CostoUnitario = models.IntegerField(default=0, blank =False)
    ConsumoMedio = models.IntegerField(default=0, blank =False)
    Periodo = models.IntegerField(default=0, blank = False)
    Totale = models.IntegerField(default=0, blank =False)


class Ditta(models.Model):
    ID_rich = models.ForeignKey(MAIN, on_delete=models.CASCADE)
    NomeDitta = models.CharField(max_length=400, blank=True)
    Rif = models.CharField(max_length=100, blank=True)
    ContattoEM = models.EmailField()
    ContattoTel = models.IntegerField()
    

class Criteri(models.Model):
    ID_rich = models.ForeignKey(MAIN, on_delete=models.CASCADE )
    Rif = models.IntegerField(default=0, null=False)
    Criterio = models.CharField(max_length=255, blank=True) 
    Peso = models.IntegerField(default=0)

class Allegati(models.Model):
    def generate_filename(self, filename):
        name = str(self.ID_rich) + '/Allegati' + '/'+str(filename)
        return name
    
    ID_rich = models.ForeignKey(MAIN, on_delete=models.CASCADE)
    Allegato = models.CharField(max_length=500, blank=True)
    N_pag = models.IntegerField(default=0)
    File = models.FileField(upload_to = generate_filename)

    def __str__(self):
        return str(self.Allegato)
    
    

class Notifiche(models.Model):
    User = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    Data = models.DateTimeField(null=True)
    Letto = models.BooleanField(default=False)
    Messaggio = models.CharField(max_length=1000)

    def invia_messaggio(self, us, mess):
        self.User = us
        self.Messaggio = mess
        self.Data = timezone.now()
        
class NuovaRichiesta(models.Model):
    File = models.FileField(upload_to='media')
    

class DocGara(models.Model):
    def generate_filename(self, filename):
        name = str(self.ID_rich) + '/Documentazione_Di_Gara/' +str(filename)
        return name
    ID_rich = models.ForeignKey(MAIN, on_delete = models.CASCADE)
    Nome = models.CharField(max_length=255)
    N_pagine = models.IntegerField(default = 0)
    Descrizione = models.CharField(max_length=1000, null=True)
    File = models.FileField(upload_to = generate_filename, null=True, blank=True)

class DocComm(models.Model):    
    def generate_filename(self, filename):
        name = str(self.ID_rich) + '/Documentazione_Di_Commissione/' +str(filename)
        return name
    ID_rich = models.ForeignKey(MAIN, on_delete = models.CASCADE)
    Nome = models.CharField(max_length=255)
    N_pagine = models.IntegerField(default = 0)
    Descrizione = models.CharField(max_length=1000, null=True)
    File = models.FileField(upload_to = generate_filename, null=True, blank=True)


class DocAgg(models.Model):  
    def generate_filename(self, filename):
        name = str(self.ID_rich) + '/Documentazione_Di_Aggiudicazione/' +str(filename)
        return name  
    ID_rich = models.ForeignKey(MAIN, on_delete = models.CASCADE)
    Nome = models.CharField(max_length=255)
    N_pagine = models.IntegerField(default = 0)
    Descrizione = models.CharField(max_length=1000, null=True)
    File = models.FileField(upload_to = generate_filename,  null=True, blank=True)


class DocTrasp(models.Model):   
    def generate_filename(self, filename):
        name = str(self.ID_rich) + '/Documentazione_Di_Trasporto/' +str(filename)
        return name   
    ID_rich = models.ForeignKey(MAIN, on_delete = models.CASCADE)
    Nome = models.CharField(max_length=255)
    N_pagine = models.IntegerField(default = 0)
    File = models.FileField(upload_to = generate_filename, null=True, blank=True)
    Descrizione = models.CharField(max_length=1000, null=True)


class DocColl(models.Model):    
    def generate_filename(self, filename):
        name = str(self.ID_rich) + '/Documentazione_Di_Collaudo/' +str(filename)
        return name  
        
    ID_rich = models.ForeignKey(MAIN, on_delete = models.CASCADE)
    Nome = models.CharField(max_length=255)
    N_pagine = models.IntegerField(default = 0)
    Descrizione = models.CharField(max_length=1000, null=True)
    File = models.FileField(upload_to = generate_filename, null=True, blank=True)


_m_= 'm'
_M_ = 'M'
spec_choices = {
    (_m_, 'm'),
    (_M_, 'M')
}
OK = 'OK'
NO = 'NO'
NC = 'NC'
specvalchoices = {
    (OK, 'OK'),
    (NO, 'NO'),
    (NC, 'NC')
}
class UrgenteRequest(models.Model): 

    Progressivo = models.CharField(max_length=100, blank=True)  
    Sede_Reparto = models.ForeignKey(SeRep, on_delete= models.SET_NULL, null=True)  
    Apparecchiatura = models.CharField(max_length=255, blank=True)  
    Qta = models.IntegerField(default=1)  
    #Priorita = models.ForeignKey(Priorita, null=True, on_delete = models.SET_NULL)  
    Costo_Presunto_NOIVA = models.IntegerField(null=True, blank=True)  
    Costo_Presunto_IVA = models.IntegerField(null=True, blank=True)  
    Compilatore = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)  
    ID_PianoInvestimenti = models.ForeignKey(PI, null=True, on_delete=models.SET_NULL)  
    NoteGen = models.TextField(blank=True)  
    Direttore = models.CharField(max_length=255, blank=True)
    
    DescrMass = models.CharField(max_length=5000, null=True, blank=True)
    Criterio = models.CharField(max_length=255, blank=True)
    Peso = models.IntegerField(default=0, blank=True, null=True)
    ContattoEM= models.EmailField(null=True, blank=True)
    Tipo= models.CharField(max_length=255, blank=True)
    ConsumoMedio= models.IntegerField(default=0,blank=True, null=True)
    Periodo= models.IntegerField(default=0, blank=True, null=True)
    CostoUnitario= models.IntegerField(default=0, blank=True, null=True)
    NomeDitta= models.TextField(max_length=400, blank=True, default='')
    ContattoTel= models.IntegerField(default=0, blank=True, null=True)
    Nota = models.CharField(max_length=500, null=True)
    Eliminato = models.BooleanField(default = False)
    
    Mot1_1 = models.BooleanField(default=False) # Sostituzione di analoga dismessa o in dismissione
    Mot1_2 = models.BooleanField(default=False) # Implementazione/Aggiornamento di Attrezzatura/Sistema
    Mot1_3 = models.BooleanField(default=False) # Inizio nuova attività
    ValMot = models.CharField(null=True, choices = [('1', 'Congruo'), ('0', 'Non Congruo')], max_length=255) # valutazione motivi espressi per richeiesta o implementazione agg
    ValMotNota = models.CharField(blank = True, max_length=1000)
    ValData = models.DateTimeField(null=True)
    ValUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatore_urgente')
    Mot2_1 = models.BooleanField(default=False) # Mantenimento / recupero delle prestazioni e/o della sicurezza
    Mot2_2 = models.BooleanField(default=False) # Aumento/Miglioramento delle prestazioni
    AggNota = models.CharField(max_length=500, blank = True)
    Stato = models.ForeignKey(Sta, on_delete = models.CASCADE, null=True)
    Acquisto = models.BooleanField(default=False)
    Service = models.BooleanField(default=False)
    Noleggio = models.BooleanField(default=False)
    Tecnologico = models.BooleanField(default=False)
    Valutativo = models.BooleanField(default=False)
    Temporaneo = models.BooleanField(default=False)
    Economico = models.BooleanField(default=False)
    Gestionale = models.BooleanField(default=False)
    NotaNoleggio = models.CharField(max_length=500, blank =True)
    NecInfraSi = models.BooleanField(default=False)
    NecInfraNO = models.BooleanField(default=False)
    NecInfraNota = models.CharField(max_length=500, blank = True)
    SostNota = models.CharField(max_length=500, blank = True)
    Data = models.DateTimeField(default=now) 
    Fonte = models.CharField(max_length=255, blank=True)
    Anno_Previsto = models.IntegerField(null=True)
    StatoRic = models.ForeignKey(RichiestaStato, on_delete=models.CASCADE, null=True, blank=True)
    NoteStato=models.TextField(null=True, blank=True)

    Data1 = models.DateTimeField(blank=True, null=True)
    Data2 = models.DateTimeField(blank=True, null=True)
    Data3 = models.DateTimeField(blank=True, null=True)
    Data4 = models.DateTimeField(blank=True, null=True)
    Data5 = models.DateTimeField(blank=True, null=True)
    Data6 = models.DateTimeField(blank=True, null=True)
    Data7 = models.DateTimeField(blank=True, null=True)
    Data8 = models.DateTimeField(blank=True, null=True)
    Data9 = models.DateTimeField(blank=True,null=True)
    NoteGen = models.CharField(max_length=500, blank =True)
    Prezzo_acquisto = models.IntegerField (blank=True,null=True)
    Prezzo_Noleggio = models.IntegerField( blank=True,null=True)
    Prezzo_Service = models.IntegerField( blank=True,null=True)
    MotivoAnnullamento = models.CharField(max_length=255,blank=True, null=True)
    FileModuloRichiestaFirmatoUrgente = models.FileField(null=True, blank=True)
    FileModuloValutazioneFirmatoUrgente = models.FileField(null=True)
    Simili = models.BooleanField(default=False, blank=True)
    PercIVA = models.IntegerField(null=False, default = 0)
    NolMesi = models.IntegerField(null=True, blank=True)
    FabbCopiato = models.ForeignKey(Fabbisogni, on_delete = models.CASCADE, null = True, blank = True)

    #campi cambio stato
    primario_utente = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="primario_urgente", on_delete=models.SET_NULL, null=True, blank=True)
    primario_data = models.DateTimeField(null=True, blank=True)

    dir_medica_utente = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="dir_medica_urgente", on_delete=models.SET_NULL, null=True, blank=True)
    dir_medica_data = models.DateTimeField(null=True, blank=True)

    ing_clinico_utente = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ing_clinico_urgente", on_delete=models.SET_NULL, null=True, blank=True)
    ing_clinico_data = models.DateTimeField(null=True, blank=True)

    # Sezione Specifiche
    Specifica = models.CharField(max_length=1000,default="Non specificato", blank=True, null=True)
    ValSpecCli = models.CharField(max_length = 255, choices = specvalchoices, null=True)
    ValSpecCliNota = models.CharField(max_length= 1000, blank=True, null=True)
    ValCliData = models.DateTimeField(blank=True, null=True)
    ValCliUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatoreclinicou')
    ValSpecTec = models.CharField(max_length = 255, choices = specvalchoices, null=True)
    ValSpecTecNota = models.CharField(max_length= 1000, blank=True, null=True)
    ValTecData = models.DateTimeField(blank=True, null=True)
    ValTecUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatoretecnicou')
    MotivoClinico = models.CharField(max_length=1000, default="Non specificato",blank=True, null=True)
    Un = models.BooleanField(default=False)
    rif = models.IntegerField(default=0, blank=True,null=True)
    Min = models.BooleanField(default=False, null=True, blank=True)
    Max = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f'{self.Progressivo}_{self.Qta}_{self.Apparecchiatura}'
        #return str(self.Progressivo) + '_' + str(self.Apparecchiatura)+ '_' + str(self.rif)    
    
    def def_stato(self):
        Date = [self.Data, self.Data1, self.Data2, self.Data3, self.Data4,self.Data5,self.Data6,self.Data7,self.Data8, self.Data9]
        counter = 1
        for i in Date:
            if i != None:
                self.Stato= Sta.objects.get(Numero=counter)
            counter+=1
    
        return(self.Stato)

    def costo_presuntoNOIVA(self):
        if self.Prezzo_acquisto is not None:
            self.Costo_Presunto_NOIVA = self.Prezzo_acquisto
            if self.PercIVA != None:
                iva = self.PercIVA * self.Costo_Presunto_NOIVA / 100
                self.Costo_Presunto_IVA = iva + self.Costo_Presunto_NOIVA
                print(self.PercIVA)
        elif self.Prezzo_Noleggio is not None:
            self.Costo_Presunto_NOIVA = self.Prezzo_Noleggio
            if self.PercIVA != None:
                iva = self.PercIVA * self.Costo_Presunto_NOIVA / 100
                self.Costo_Presunto_IVA = iva + self.Costo_Presunto_NOIVA
        elif self.Prezzo_Service is not None:
            self.Costo_Presunto_NOIVA = self.Prezzo_Service
            if self.PercIVA != None:
                iva = self.PercIVA * self.Costo_Presunto_NOIVA / 100
                self.Costo_Presunto_IVA = iva + self.Costo_Presunto_NOIVA




class SpecificheUrg(models.Model):
    ID_rich = models.ForeignKey(UrgenteRequest, on_delete=models.CASCADE)
    Specifica = models.CharField(max_length=1000, blank=False)
    ValSpecCli = models.CharField(max_length = 255, choices = specvalchoices, null=True)
    ValSpecCliNota = models.CharField(max_length= 1000, blank=True, null=True)
    ValCliData = models.DateTimeField(blank=True, null=True)
    ValCliUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatoreclinicosurg')
    ValSpecTec = models.CharField(max_length = 255, choices = specvalchoices, null=True)
    ValSpecTecNota = models.CharField(max_length= 1000, blank=True, null=True)
    ValTecData = models.DateTimeField(blank=True, null=True)
    ValTecUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatoretecnicosurg')
    MotivoClinico = models.CharField(max_length=1000, blank=False)
    Un = models.BooleanField(default=False)
    rif = models.IntegerField(default=0, null=False)
    Min = models.BooleanField(default=False)
    Max = models.BooleanField(default=False)

    def __str__(self):
        return str(self.ID_rich)+'-'+str(self.rif)
    
class UnicitaUrg(models.Model):
    ID_rich = models.ForeignKey(UrgenteRequest, on_delete=models.CASCADE, null=True)
    rifext = models.ForeignKey(SpecificheUrg, on_delete=models.CASCADE)
    ValCli = models.CharField(max_length = 500, null = True)
    ValCliData = models.DateTimeField(blank = True, null=True)
    ValCliUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatoreclinicourg')
    ValTec = models.CharField(max_length=500, null=True)
    ValTecData = models.DateTimeField(blank=True, null=True)
    ValTecUtente = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name = 'valutatoretecnicourg')
    Nota = models.CharField(max_length=500, null=True)

    def __str__(self):
        return str(self.rifext) 
    
class ConsumabiliUrg(models.Model):
    ID_rich = models.ForeignKey(UrgenteRequest, on_delete=models.CASCADE)
    Tipo = models.CharField(max_length=500, blank=False)
    CostoUnitario = models.IntegerField(default=0, blank =False)
    ConsumoMedio = models.IntegerField(default=0, blank =False)
    Periodo = models.IntegerField(default=0, blank = False)
    Totale = models.IntegerField(default=0, blank =False)

class CriteriUrg(models.Model):
    ID_rich = models.ForeignKey(UrgenteRequest, on_delete=models.CASCADE )
    Rif = models.IntegerField(default=0, null=False)
    Criterio = models.CharField(max_length=255, blank=True) 
    Peso = models.IntegerField(default=0)

class DittaUrg(models.Model):
    ID_rich = models.ForeignKey(UrgenteRequest, on_delete=models.CASCADE)
    NomeDitta = models.CharField(max_length=400, blank=True)
    Rif = models.CharField(max_length=100, blank=True)
    ContattoEM = models.EmailField()
    ContattoTel = models.IntegerField()

class AllegatiUrg(models.Model): #se dovesse servire
    def generate_filename(self, filename):
        name = str(self.ID_rich) + '/Allegati' + '/'+str(filename)
        return name
    
    ID_rich = models.ForeignKey(UrgenteRequest, on_delete=models.CASCADE)
    Allegato = models.CharField(max_length=500, blank=True)
    N_pag = models.IntegerField(default=0)
    File = models.FileField(upload_to = generate_filename)

    def __str__(self):
        return str(self.Allegato)



    