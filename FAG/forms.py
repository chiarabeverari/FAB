from django import forms
from django.forms import DateField, ModelForm
from .models import *
from django.core.validators import EMPTY_VALUES
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from .settings import DATE_INPUT_FORMATS
from django.db.models import Q
from django.utils.timezone import now

#self.add_error("campo", "messaggio") per errori nel clean 

    

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text = 'Aggiungere un indirizzo email valido')
    class Meta:
        model = MedicalUser
        fields = ['username', 'Nome', 'Cognome', 'password1', 'password2', 'Profilo_Professionale', 'Sede_Reparto']
        
        labels ={
            'password1': 'Inserisci una password',
            'password2': 'Ripeti la password',
            'Profilo_Professionale': 'Profilo Professionale',
            'Sede_Reparto': 'Sede e Reparto di riferimento'
        }

        def clean_email(self):
            email = self.cleaned_data['email'].lower()
            try:
                account = MedicalUser.objects.get(email = email)
            except Exception as e:
                return email
            raise forms.ValidationError(f"Email {email} is alread in use.")
        
        def clean_username(self):
            username = self.cleaned_data['username']
            try:
                account = MedicalUser.objects.get(username = username)
            except Exception as e:
                return username
            raise forms.ValidationError(f'Username {username} is already in use.')

class EditProfileForm(UserChangeForm):
    template_name = "modificauser.html"

    class Meta:
        model = MedicalUser
        fields = ['Nome', 'Cognome', 'username', 'password', 'email', 'Sede_Reparto', 'Profilo_Professionale']

class EditProfileFormAdmin(UserChangeForm):
    template_name = "modificauser.html"

    class Meta:
        model = MedicalUser
        fields = '__all__'
        
class newuserform(UserCreationForm):
    class Meta:
        model = MedicalUser
        fields = ['username', 'Nome', 'Cognome', 'password1', 'password2', 'Gruppo', 'Profilo_Professionale', 'Sede_Reparto', 'is_active', 'is_staff', 'is_admin', 'is_superuser']

        def clean_email(self):
                email = self.cleaned_data['email'].lower()
                try:
                    account = MedicalUser.objects.get(email = email)
                except Exception as e:
                    return email
                raise forms.ValidationError(f"Email {email} is alread in use.")
            
        def clean_username(self):
            username = self.cleaned_data['username']
            try:
                account = MedicalUser.objects.get(username = username)
            except Exception as e:
                return username
            raise forms.ValidationError(f'Username {username} is already in use.')

class AttForm1(ModelForm):
    class Meta:
        model = Fabbisogni
        fields = ['NoteGen', 'Priorita', 'Sede_Reparto', 'Apparecchiatura', 'Compilatore', 'Direttore', 'Qta', 'Data', 'Fonte', 'Mot2_1', 'Mot2_2', 'AggNota', 'NoteGen', 'Mot1_1', 'Mot1_2', 'Mot1_3', 'SostNota', 'NecInfraSi', 'NecInfraNO', 'NecInfraNota',
        'Acquisto', 'Prezzo_acquisto', 'Noleggio', 'Prezzo_Noleggio', 'Service', 'Prezzo_Service', 'Tecnologico', 'Valutativo', 'Temporaneo', 'Economico', 'Gestionale', 'NotaNoleggio', 'NolMesi', 'Anno_Previsto', 'PercIVA', 'DescrMass',
        'NewPersSI', 'NewPersNO', 'StatoRic'] 

        widgets ={
            'NoteGen': forms.Textarea(attrs={'rows':3, 'cols':200}),
            'Apparecchiatura': forms.TextInput(attrs={'class': 'form-control'}),
            'Compilatore': forms.Select(attrs={'class': 'form-control'}),
            'Direttore': forms.TextInput(attrs={'class': 'form-control'}),
            'Data': forms.TextInput(attrs={'class': 'form-control'}),
            'Fonte': forms.TextInput(attrs={'class': 'form-control'}),
            'Mot2_1': forms.CheckboxInput(),
            'Mot2_2': forms.CheckboxInput(),
            'AggNota': forms.Textarea(attrs={'class': 'form-control'}),
            'NoteGen': forms.Textarea(attrs={'class': 'form-control'}),
            'Mot1_1': forms.CheckboxInput(),
            'Mot1_2': forms.CheckboxInput(),
            'Mot1_3': forms.CheckboxInput(),
            'NecInfra': forms.CheckboxInput(),
            'NecInfraNota': forms.Textarea(attrs={'class': 'form-control'}),
            'SostNota': forms.Textarea(attrs={'rows': 1, 'cols': 70}),
            'NotaNoleggio': forms.Textarea(attrs={'class': 'form-control'}),
            'DescrMass': forms.Textarea(attrs={'rows': 4, 'cols':150}),
            'StatoRic': forms.Select(attrs={'class':'form-control'}), #cambiato
        }
        labels = {
            'Mot2_1': 'Mantenimento/Recupero delle prestazioni e/o della sicurezza',
            'Mot2_2': 'Aumento/Miglioramento delle prestazioni',
            'Mot1_1': 'Sostituzione di analoga dismessa o in dismissione', 
            'Mot1_2': 'Implementazione/aggiornamento di attrezzatura/sistema',
            'Mot1_3': 'Inizio nuova attività',
        }
    def clean(self):
        ## NECESSITA' INFRASTRUTTURE
        NecInfraSi = self.cleaned_data.get('NecInfraSi', False)
        NecInfraNO = self.cleaned_data.get('NecInfraNO', False)

        if NecInfraSi:
            # validate the activity name
            NecInfraNota = self.cleaned_data.get('NecInfraNota', None)
            if NecInfraNota in EMPTY_VALUES:
                self._errors['NecInfraNota'] = self.error_class([
                    'Inserire la motivazione'])
        else:
            if not NecInfraNO:
                self._errors['NecInfraNO'] = self.error_class([
                    'Specificare la necessità di infrastrutture o meno'])
        
        ## SOSTITUZIONE
        Mot1_1 = self.cleaned_data.get('Mot1_1', False)
        if Mot1_1:
            SostNota = self.cleaned_data.get('SostNota', None)
            if SostNota in EMPTY_VALUES:
                self._errors['SostNota'] = self.error_class([
                    'Inserire il riferimento'
                ])

        ## AGGIORNAMENTO / MIGLIORAMENTO
        Mot2_2 = self.cleaned_data.get('Mot2_2', False)
        if Mot2_2:
            AggNota = self.cleaned_data.get('AggNota', None)
            if AggNota in EMPTY_VALUES:
                self._errors['AggNota'] = self.error_class([
                    "Specificare in cosa consiste l' aggiornamento"
                ])

        ## PREZZI
        Acquisto = self.cleaned_data.get('Acquisto', False)
        Noleggio = self.cleaned_data.get('Noleggio', False )
        Service = self.cleaned_data.get('Service', False)

        if Acquisto:
            Prezzo_acquisto = self.cleaned_data.get('Prezzo_acquisto', False)
            if not Prezzo_acquisto:
                self._errors['Prezzo_acquisto'] = self.error_class([
                    "Inserire il prezzo (IVA ESCLUSA)"
                ])
        
        if Service:
            Prezzo_Service = self.cleaned_data.get('Prezzo_Service', False)
            if not Prezzo_Service:
                self._errors['Prezzo_Service'] = self.error_class([
                    "Inserire il prezzo (IVA ESCLUSA)"
                ])

        if Noleggio:
            Prezzo_Noleggio = self.cleaned_data.get('Prezzo_Noleggio', False)
            if not Prezzo_Noleggio:
                self._errors['Prezzo_Noleggio'] = self.error_class([
                    "Inserire il prezzo (IVA ESCLUSA)"
                ])

        return self.cleaned_data


class AttForm2(ModelForm):
    class Meta:
        model = MAIN
        fields = ['Priorita', 'Sede_Reparto', 'Apparecchiatura', 'Compilatore', 'Direttore', 'Qta', 'Data', 'Fonte', 'Mot2_1', 'Mot2_2', 'AggNota', 'NoteGen', 'Mot1_1', 'Mot1_2', 'Mot1_3', 'SostNota', 'NecInfraSi', 'NecInfraNO', 'NecInfraNota',
        'Acquisto', 'Prezzo_acquisto', 'Noleggio', 'Prezzo_Noleggio', 'Service', 'Prezzo_Service', 'Tecnologico', 'Valutativo', 'Temporaneo', 'Economico', 'Gestionale', 'NotaNoleggio', 'NolMesi', 'PercIVA','StatoRic']

        widgets ={
            'Apparecchiatura': forms.TextInput(attrs={'class': 'form-control'}),
            'Compilatore': forms.Select(attrs={'class': 'form-control'}),
            'Direttore': forms.TextInput(attrs={'class': 'form-control'}),
            'Data': forms.TextInput(attrs={'class': 'form-control'}),
            'Fonte': forms.TextInput(attrs={'class': 'form-control'}),
            'Mot2_1': forms.CheckboxInput(),
            'Mot2_2': forms.CheckboxInput(),
            'AggNota': forms.Textarea(attrs={'class': 'form-control'}),
            'NoteGen': forms.Textarea(attrs={'class': 'form-control'}),
            'Mot1_1': forms.CheckboxInput(),
            'Mot1_2': forms.CheckboxInput(),
            'Mot1_3': forms.CheckboxInput(),
            'NecInfra': forms.CheckboxInput(),
            'NecInfraNota': forms.Textarea(attrs={'class': 'form-control'}),
            'SostNota': forms.Textarea(attrs={'rows': 1, 'cols': 70}),
            'NotaNoleggio': forms.Textarea(attrs={'class': 'form-control'}),
            'DescrMass': forms.Textarea(attrs={'rows': 4, 'cols':150}),
            'StatoRic': forms.Select(attrs={'value': 'BOZZA'}),
        }
        labels = {
            'Mot2_1': 'Mantenimento/Recupero delle prestazioni e/o della sicurezza',
            'Mot2_2': 'Aumento/Miglioramento delle prestazioni',
            'Mot1_1': 'Sostituzione di analoga dismessa o in dismissione', 
            'Mot1_2': 'Implementazione/aggiornamento di attrezzatura/sistema',
            'Mot1_3': 'Inizio nuova attività',
        }
    def clean(self):
        ## NECESSITA' INFRASTRUTTURE
        NecInfraSi = self.cleaned_data.get('NecInfraSi', False)
        NecInfraNO = self.cleaned_data.get('NecInfraNO', False)

        if NecInfraSi:
            # validate the activity name
            NecInfraNota = self.cleaned_data.get('NecInfraNota', None)
            if NecInfraNota in EMPTY_VALUES:
                self._errors['NecInfraNota'] = self.error_class([
                    'Inserire la motivazione'])
        else:
            if not NecInfraNO:
                self._errors['NecInfraNO'] = self.error_class([
                    'Specificare la necessità di infrastrutture o meno'])
        
        ## SOSTITUZIONE
        Mot1_1 = self.cleaned_data.get('Mot1_1', False)
        if Mot1_1:
            SostNota = self.cleaned_data.get('SostNota', None)
            if SostNota in EMPTY_VALUES:
                self._errors['SostNota'] = self.error_class([
                    'Inserire il riferimento'
                ])

        ## AGGIORNAMENTO / MIGLIORAMENTO
        Mot2_2 = self.cleaned_data.get('Mot2_2', False)
        if Mot2_2:
            AggNota = self.cleaned_data.get('AggNota', None)
            if AggNota in EMPTY_VALUES:
                self._errors['AggNota'] = self.error_class([
                    "Specificare in cosa consiste l' aggiornamento"
                ])

        ## PREZZI
        Acquisto = self.cleaned_data.get('Acquisto', False)
        Noleggio = self.cleaned_data.get('Noleggio', False )
        Service = self.cleaned_data.get('Service', False)

        if Acquisto:
            Prezzo_acquisto = self.cleaned_data.get('Prezzo_acquisto', False)
            if not Prezzo_acquisto:
                self._errors['Prezzo_acquisto'] = self.error_class([
                    "Inserire il prezzo (IVA ESCLUSA)"
                ])
        
        if Service:
            Prezzo_Service = self.cleaned_data.get('Prezzo_Service', False)
            if not Prezzo_Service:
                self._errors['Prezzo_Service'] = self.error_class([
                    "Inserire il prezzo (IVA ESCLUSA)"
                ])

        if Noleggio:
            Prezzo_Noleggio = self.cleaned_data.get('Prezzo_Noleggio', False)
            if not Prezzo_Noleggio:
                self._errors['Prezzo_Noleggio'] = self.error_class([
                    "Inserire il prezzo (IVA ESCLUSA)"
                ])

        return self.cleaned_data


class AttForm3(ModelForm):
    class Meta:
        model = MAIN
        fields = ['Anno_Previsto', 'Sede_Reparto', 'Apparecchiatura', 'Compilatore', 'Direttore', 'Qta', 'Data', 'Fonte', 'NecInfraSi', 'NecInfraNO', 'NecInfraNota',
        'Acquisto', 'Prezzo_acquisto', 'Noleggio', 'Prezzo_Noleggio', 'Service', 'Prezzo_Service', 'Tecnologico', 'Valutativo', 'Temporaneo', 'Economico', 'Gestionale',
        'NotaNoleggio', 'NolMesi', 'PercIVA', 'ID_PianoInvestimenti','StatoRic'] 

        widgets ={
            'Anno_Previsto': forms.TextInput(attrs={'class': 'form-control'}),
            'Apparecchiatura': forms.TextInput(attrs={'class': 'form-control'}),
            'Compilatore': forms.Select(attrs={'class': 'form-control'}),
            'Direttore': forms.TextInput(attrs={'class': 'form-control'}),
            'Data': forms.TextInput(attrs={'class': 'form-control'}),
            'Fonte': forms.TextInput(attrs={'class': 'form-control'}),
            'NecInfra': forms.CheckboxInput(),
            'NecInfraNota': forms.Textarea(attrs={'class': 'form-control'}),
            'SostNota': forms.Textarea(attrs={'rows': 1, 'cols': 70}),
            'NotaNoleggio': forms.Textarea(attrs={'class': 'form-control'}),
            'Sede_Reparto': forms.Textarea(attrs={'class': 'form-control'}),
            'StatoRic': forms.Select(attrs={'value': 'BOZZA'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(AttForm3, self).__init__(*args, **kwargs)

        query = Q(Speso = 0, is_full = False, is_ext = True)
        query = query | Q(Speso__gte = 1, is_end = False, is_ext = True)

        sample_choices = list(PI.objects.filter(query).values_list('id', 'ID_PianoInvestimenti'))
        self.fields['ID_PianoInvestimenti'].choices = sample_choices

    def clean(self):
        ## NECESSITA' INFRASTRUTTURE
        NecInfraSi = self.cleaned_data.get('NecInfraSi', False)
        NecInfraNO = self.cleaned_data.get('NecInfraNO', False)

        if NecInfraSi:
            # validate the activity name
            NecInfraNota = self.cleaned_data.get('NecInfraNota', None)
            if NecInfraNota in EMPTY_VALUES:
                self._errors['NecInfraNota'] = self.error_class([
                    'Inserire la motivazione'])
        else:
            if not NecInfraNO:
                self._errors['NecInfraNO'] = self.error_class([
                    'Specificare la necessità di infrastrutture o meno'])
        
        ## SOSTITUZIONE
        Mot1_1 = self.cleaned_data.get('Mot1_1', False)
        if Mot1_1:
            SostNota = self.cleaned_data.get('SostNota', None)
            if SostNota in EMPTY_VALUES:
                self._errors['SostNota'] = self.error_class([
                    'Inserire il riferimento'
                ])

        ## AGGIORNAMENTO / MIGLIORAMENTO
        Mot2_2 = self.cleaned_data.get('Mot2_2', False)
        if Mot2_2:
            AggNota = self.cleaned_data.get('AggNota', None)
            if AggNota in EMPTY_VALUES:
                self._errors['AggNota'] = self.error_class([
                    "Specificare in cosa consiste l' aggiornamento"
                ])

        ## PREZZI
        Acquisto = self.cleaned_data.get('Acquisto', False)
        Noleggio = self.cleaned_data.get('Noleggio', False )
        Service = self.cleaned_data.get('Service', False)

        if Acquisto:
            Prezzo_acquisto = self.cleaned_data.get('Prezzo_acquisto', False)
            if not Prezzo_acquisto:
                self._errors['Prezzo_acquisto'] = self.error_class([
                    "Inserire il prezzo (IVA ESCLUSA)"
                ])
        
        if Service:
            Prezzo_Service = self.cleaned_data.get('Prezzo_Service', False)
            if not Prezzo_Service:
                self._errors['Prezzo_Service'] = self.error_class([
                    "Inserire il prezzo (IVA ESCLUSA)"
                ])

        if Noleggio:
            Prezzo_Noleggio = self.cleaned_data.get('Prezzo_Noleggio', False)
            if not Prezzo_Noleggio:
                self._errors['Prezzo_Noleggio'] = self.error_class([
                    "Inserire il prezzo (IVA ESCLUSA)"
                ])

        return self.cleaned_data

class PIForm(ModelForm):
    class Meta:
        model = PI
        fields = ['Anno_Previsto', 'Descrizione', 'Priorita', 'Costo_Presunto_IVA']
    
        labels ={
            'Costo_Presunto_IVA': 'Costo Presunto IVA INCLUSA'
        }
class SpecificheForm(ModelForm):
    class Meta:
        model = Specifiche
        fields = ['ID_rich', 'rif', 'Specifica', 'MotivoClinico', 'Min', 'Max']

        widgets={
            'Specifica': forms.Textarea(attrs={'rows': 1, 'cols': 50}),
            'MotivoClinico': forms.Textarea(attrs={'rows': 1, 'cols': 50}),

        }
        labels ={
            'MotivoClinico': 'Motivo Clinico'
        }
    
    def clean(self):
        Min = self.cleaned_data.get('Min', False)
        if Min:
            Max = self.cleaned_data.get('Max', None)
            if Max:
                self._errors['Max'] = self.error_class([
                    "La specifica o è di minima o è di massima. Non può essere entrambe."
                ])
        
        else:
            Max = self.cleaned_data.get('Max', None)
            if not Max:
                self._errors['Max'] = self.error_class([
                    "La specifica è di minima o è di massima. Selezionare una delle due."
                ])

        return self.cleaned_data


class UnicitaForm(ModelForm):
    class Meta:
        model = Unicita
        fields =['ID_rich','rifext', 'Nota']

        widgets = {
            'Nota': forms.Textarea(attrs={'rows': 1, 'cols': 150}),
            
        }

class CriteriForm(ModelForm):
    class Meta:
        model = Criteri
        fields ='__all__'

        widgets = {
            'Criterio': forms.Textarea(attrs={'rows':4, 'cols':150})
        }

class ConsumabiliFormFabb(ModelForm):
    class Meta:
        model = ConsumabiliFabb
        exclude = ['Totale']

        widgets={
            'Tipo': forms.Textarea(attrs={'rows':1, 'cols': 100})
        }

class ConsumabiliFormMain(ModelForm):
    class Meta:
        model = ConsumabiliMain
        exclude = ['Totale']

        widgets={
            'Tipo': forms.Textarea(attrs={'rows':1, 'cols': 100})
        }

class DittaForm(ModelForm):
    class Meta:
        model = Ditta
        fields = '__all__'
  

class AllegatiForm(ModelForm):
    class Meta:
        model = Allegati
        fields = '__all__'

class DateForm(ModelForm):
    class Meta:
        model = MAIN
        fields = ['Data', 'Data1', 'Data2', 'Data3', 'Data4', 'Data5', 'Data6', 'Data7', 'Data8', 'Data9']


class ValMotForm(ModelForm):
    class Meta:
        model = MAIN
        fields = ['ValMot', 'ValMotNota']

        widgets = {
            'ValMotNota': forms.Textarea(attrs={'rows': 3, 'cols': 200})
        }
        labels = {
            'ValMot': 'Valutazione (CONGRUO/NON CONGRUO)',
            'ValMotNota': 'Nota'
        }
    
    def clean(self):
        ValMot = self.cleaned_data.get('ValMot', False)
        if ValMot == '0':
            ValMotNota = self.cleaned_data.get('ValMotNota', None)
            if not ValMotNota:
                self._errors['ValMotNota'] = self.error_class([
                    "Specificare il motivo."
                ])

class ValSpecFormCli(ModelForm):
    class Meta:
        model = Specifiche
        fields = ['ValSpecCli', 'ValSpecCliNota']

        widgets ={
            'ValSpecCliNota': forms.Textarea(attrs={'rows': 1, 'cols': 100})
        }
    
    def clean(self):
        ValSpecCli = self.cleaned_data.get('ValSpecCli', False)
        if ValSpecCli == 'NO':
            ValSpecCliNota = self.cleaned_data.get('ValSpecCliNota', None)
            if not ValSpecCliNota:
                self._errors['ValSpecCliNota'] = self.error_class([
                    "Specificare il motivo."
                ])

class ValSpecFormTec(ModelForm):
    class Meta:
        model = Specifiche
        fields = ['ValSpecTec', 'ValSpecTecNota']
    
    def clean(self):
        ValSpecTec = self.cleaned_data.get('ValSpecTec', False)
        if ValSpecTec == 'NO':
            ValSpecTecNota = self.cleaned_data.get('ValSpecTecNota', None)
            if not ValSpecTecNota:
                self._errors['ValSpecTecNota'] = self.error_class([
                    "Specificare il motivo."
                ])
         

class ValUnFormCli(ModelForm):
    class Meta:
        model = Unicita
        fields = ['ValCli']

class ValUnFormTec(ModelForm):
    class Meta:
        model = Unicita
        fields = ['ValTec']

class Data1Form(ModelForm):
    class Meta:
        model = MAIN
        fields = ['Data1']
    
    widgets ={
            'Data1': forms.DateInput()
        }
        
    labels = {
            'Data1': 'Data',
        }

class NuovaRichiestaForm(ModelForm):
    class Meta:
        model = NuovaRichiesta
        fields = ['File']

class FormUn(ModelForm):
    class Meta:
        model = MAIN
        fields = ['Simili', 'NoteGen']

        widgets = {
            'Simili': forms.CheckboxInput()
        }

class Unform(ModelForm):
    class Meta:
        model = Specifiche
        fields =['Un']

class Unformurg(ModelForm):
    class Meta:
        model = SpecificheUrg
        fields =['Un']

class SeRepForm(ModelForm):
    class Meta:
        model = SeRep
        fields = '__all__'

        widgets = {
            'Sede' : forms.Textarea(attrs={'rows': 1, 'cols': 50}),
            'Reparto' : forms.Textarea(attrs={'rows': 1, 'cols': 50}),
            'Sub_Reparto' : forms.Textarea(attrs={'rows': 1, 'cols': 50}),
            'CDC': forms.Textarea(attrs = {'rows':1, 'cols': 10})
        }

class SeRepRegForm(ModelForm):
    class Meta:
        model = SeRepReg
        fields = '__all__'

        widgets = {
            'Sede' : forms.Textarea(attrs={'rows': 1, 'cols': 50}),
            'Reparto' : forms.Textarea(attrs={'rows': 1, 'cols': 50}),
        }

class FabbPIForm(ModelForm):
    class Meta:
        model = PI
        fields = ['FabbRel', 'Speso', 'ID_PianoInvestimenti', 'Priorita']
    
    FabbRel = forms.ModelMultipleChoiceField(
        queryset=Fabbisogni.objects.filter(Avviato = False, Eliminato = False),
        widget=forms.CheckboxSelectMultiple, required = False
    )
    

class ModMot(ModelForm):
    class Meta:
        model = Fabbisogni
        fields = ['Mot2_1', 'Mot2_2', 'AggNota', 'Mot1_1', 'Mot1_2', 'Mot1_3', 'SostNota'] 

        widgets ={
           
            'Mot2_1': forms.CheckboxInput(),
            'Mot2_2': forms.CheckboxInput(),
            'AggNota': forms.Textarea(attrs={'class': 'form-control'}),
            'Mot1_1': forms.CheckboxInput(),
            'Mot1_2': forms.CheckboxInput(),
            'Mot1_3': forms.CheckboxInput(),
            'SostNota': forms.Textarea(attrs={'rows': 1, 'cols': 20}),

        }

class DocGaraForm(ModelForm):
    class Meta:
        model = DocGara
        fields = '__all__'
        widgets = {
            'Descrizione' : forms.Textarea(attrs={'rows': 3, 'cols': 150})
        }

class DocCommForm(ModelForm):
    class Meta:
        model = DocComm
        fields = '__all__'
        widgets = {
            'Descrizione' : forms.Textarea(attrs={'rows': 3, 'cols': 150})
        }

class DocAggForm(ModelForm):
    class Meta:
        model = DocAgg
        fields = '__all__'
        widgets = {
            'Descrizione' : forms.Textarea(attrs={'rows': 3, 'cols': 150})
        }

class DocTraspForm(ModelForm):
    class Meta:
        model = DocTrasp
        fields = '__all__'

        widgets = {
            'Descrizione' : forms.Textarea(attrs={'rows': 3, 'cols': 150})
        }

class DocCollForm(ModelForm):
    class Meta:
        model = DocColl
        fields = '__all__'

        widgets = {
            'Descrizione' : forms.Textarea(attrs={'rows': 3, 'cols': 150})
        }

class ModRich(ModelForm):
    class Meta:
        model = MAIN
        fields = ['FileModuloRichiestaFirmato']

        labels = {
            'FileModuloRichiestaFirmato': 'Inserisci il modulo richiesta firmato'
        }

class ModRichUrg(ModelForm):
    class Meta:
        model = UrgenteRequest
        fields = ['FileModuloRichiestaFirmatoUrgente']

        labels = {
            'FileModuloRichiestaFirmatoUrgente': 'Inserisci il modulo richiesta firmato'
        }

class ModValut(ModelForm):
    class Meta:
        model = MAIN
        fields = ['FileModuloValutazioneFirmato']

        labels = {
            'FileModuloValutazioneFirmato': 'Inserisci il modulo valutazione firmato'
        }

class ModValutUrg(ModelForm):
    class Meta:
        model = UrgenteRequest
        fields = ['FileModuloValutazioneFirmatoUrgente']

        labels = {
            'FileModuloValutazioneFirmatoUrgente': 'Inserisci il modulo valutazione firmato'
        }

class PrForm(ModelForm):
    class Meta:
        model = Priorita
        fields ='__all__'
    
        widgets = {
            'Descrizione': forms.Textarea(attrs={'rows':3, 'cols':150})

        }

class ProfessioniForm(ModelForm):
    class Meta:
        model = Professioni
        fields ='__all__'
    
        widgets = {
            'Nome': forms.Textarea(attrs={'rows':3, 'cols':150})

        }

class GruppiForm(ModelForm):
    class Meta:
        model = Gruppi
        fields ='__all__'
    
        widgets = {
            'Descrizione': forms.Textarea(attrs={'rows':3, 'cols':150})

        }

        labels = {
            'FaVeTu': 'Vede tutti i fabbisogni',
            'FaVePr': 'Vede solo i suoi fabbusogni',
            'FaIns': 'Inserisce fabbisogni',
            'FaMoTu': 'Modifica tutti i fabbisogni',
            'FaMoPr': 'Modifica solo i suoi fabbisogni',
            'SpVeTu': 'Vede le specifiche di tutte le richieste',
            'SpVePr': 'Vede le specifiche solo delle proprie richieste',
            'SpInsPr': 'Inserisce le specifiche solo delle proprie richieste',
            'SpInsTu': 'Inserisce le specifiche di tutte le richieste',
            'SpMoTu': 'Modifica le specifiche di tutte le richiesta',
            'SpMoPr': 'Modifica le specifiche solo delle proprie richieste',
            'GaVeTu': 'Vede tutte le gare',
            'GaVePr': 'Vede le gare collegate alle sole proprie richieste',
            'GaValTec': 'Esegue le valutazioni tecniche',
            'GaValCli': 'Esegue le valutazioni cliniche',
            'GaFlu': 'Manovra le operazioni di flusso',
            'PIVeTu': 'Vede tutti gli investimenti', 
            'PIVePr': 'Vede gli investimenti legati alle sole proprie richieste',
            'PIIns': 'Inserisce un investimento',
            'PIMod': 'Modifica gli investimenti',
            'UbVe': 'Vede le ubicazioni e centri di costo',
            'UbIns': 'Inserisce le ubicazioni e centri di costo',
            'UbMod': 'Modifica le ubicazioni e centri di costo',
            'ProfVe': 'Vede i profili professionali',
            'ProfIns': 'Inserisce i profili professionali',
            'ProfMod': 'Modifica i profili professionali',
            'DiVe': 'Vede le ditte fornitrici',
            'DiIns': 'Inserisce le ditte fornitrici',
            'DiMod': 'Modifica le ditte fornitrici',
            'PrVe': 'Vede le priorità',
            'PrIns': 'Inserisce le priorità',
            'PrMod': 'Modifica le priorità',
            'ExSi': 'Può effettuare esportazioni'



        }

class CopiaFabbForm(ModelForm):
    class Meta:
        model = MAIN
        fields = ['ID_PianoInvestimenti', 'FabbCopiato', 'Compilatore', 'Data']

    def __init__(self, *args, **kwargs):
        super(CopiaFabbForm, self).__init__(*args, **kwargs)

        query = Q(Speso = 0, is_full = False, is_ext = True)
        query = query | Q(Speso__gte = 1, is_end = False, is_ext = True)

        sample_choices = list(PI.objects.filter(query).values_list('id', 'ID_PianoInvestimenti'))
        self.fields['ID_PianoInvestimenti'].choices = sample_choices

class SospensioneForm(ModelForm):
    class Meta:
        model = MAIN
        fields = ['MotivoAnnullamento']

        widgets = {
            'MotivoAnnullamento': forms.Textarea(attrs={'class': 'form-control'})
        }

class ValSpecFormCliTec(ModelForm):
    class Meta:
        model = Specifiche
        fields = ['ValSpecCli', 'ValSpecCliNota', 'ValSpecTec', 'ValSpecTecNota']
        
    def clean(self):
        ValSpecTec = self.cleaned_data.get('ValSpecTec', False)
        if ValSpecTec == 'NO':
            ValSpecTecNota = self.cleaned_data.get('ValSpecTecNota', None)
            if not ValSpecTecNota:
                self._errors['ValSpecTecNota'] = self.error_class([
                    "Specificare il motivo."
                ])
        
        ValSpecCli = self.cleaned_data.get('ValSpecCli', False)
        if ValSpecCli == 'NO':
            ValSpecCliNota = self.cleaned_data.get('ValSpecCliNota', None)
            if not ValSpecCliNota:
                self._errors['ValSpecCliNota'] = self.error_class([
                    "Specificare il motivo."
                ])

class ValUnFormTecCli(ModelForm):
    class Meta:
        model = Unicita
        fields = ['ValCli', 'ValTec']
        
class UrgenteRequestForm(forms.ModelForm):
    class Meta:
        model = UrgenteRequest
        fields = ['Sede_Reparto', 'Apparecchiatura', 'Compilatore', 'Direttore', 'Qta', 'Data', 'Fonte', 
                  'Mot2_1', 'Mot2_2', 'AggNota', 'NoteGen', 'Mot1_1', 'Mot1_2', 'Mot1_3', 'SostNota', 
                  'NecInfraSi', 'NecInfraNO', 'NecInfraNota', 'Acquisto', 'Prezzo_acquisto', 'Noleggio', 
                  'Prezzo_Noleggio', 'Service', 'Prezzo_Service', 'Tecnologico', 'Valutativo', 'Temporaneo', 
                  'Economico', 'Gestionale', 'NotaNoleggio', 'NolMesi', 'PercIVA', 'rif', 'Specifica', 
                  'MotivoClinico', 'Min', 'Max','FileModuloRichiestaFirmatoUrgente', 'Anno_Previsto', 
                  'Criterio','Peso', 'Tipo', 'CostoUnitario', 'ConsumoMedio','Periodo',
                  'NomeDitta','ContattoEM','ContattoTel', 'Nota','StatoRic']

        widgets = {
            'Anno_Previsto': forms.TextInput(attrs={'class': 'form-control'}),
            'Apparecchiatura': forms.TextInput(attrs={'class': 'form-control'}),
            'Compilatore': forms.Select(attrs={'class': 'form-control'}),
            'Direttore': forms.TextInput(attrs={'class': 'form-control'}),
            'Data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Fonte': forms.TextInput(attrs={'class': 'form-control'}),
            'Mot2_1': forms.CheckboxInput(),
            'Mot2_2': forms.CheckboxInput(),
            'AggNota': forms.Textarea(attrs={'class': 'form-control'}),
            'NoteGen': forms.Textarea(attrs={'class': 'form-control'}),
            'Mot1_1': forms.CheckboxInput(),
            'Mot1_2': forms.CheckboxInput(),
            'Mot1_3': forms.CheckboxInput(),
            'NecInfraSi': forms.CheckboxInput(),
            'NecInfraNO': forms.CheckboxInput(),
            'NecInfraNota': forms.Textarea(attrs={'class': 'form-control'}),
            'SostNota': forms.Textarea(attrs={'rows': 1, 'cols': 70}),
            'NotaNoleggio': forms.Textarea(attrs={'class': 'form-control'}),
            'Specifica': forms.Textarea(attrs={'rows': 1, 'cols': 50}),
            'MotivoClinico': forms.Textarea(attrs={'rows': 1, 'cols': 50}),
            'Prezzo_acquisto': forms.NumberInput(attrs={'class': 'form-control'}),
            'Prezzo_Noleggio': forms.NumberInput(attrs={'class': 'form-control'}),
            'Prezzo_Service': forms.NumberInput(attrs={'class': 'form-control'}),
            'PercIVA': forms.NumberInput(attrs={'class': 'form-control'}),
            #'Sede_Reparto': forms.Select(attrs={'class': 'form-control'}),
            'DescrMass': forms.Textarea(attrs={'rows': 4, 'cols':150}),
            'Criterio':forms.Textarea(attrs={'rows': 4, 'cols':150}),
            'Peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'Tipo': forms.Textarea(attrs={'rows':1,'cols':100}),
            'CostoUnitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'ConsumoMedio': forms.NumberInput(attrs={'class': 'form-control'}),
            'Periodo': forms.NumberInput(attrs={'class': 'form-control'}),
            'NomeDitta': forms.TextInput(attrs={'class': 'form-control'}),
            'ContattoEM': forms.TextInput(attrs={'class': 'form-control'}),
            'ContattoTel': forms.TextInput(attrs={'class': 'form-control'}),
            'Nota': forms.Textarea(attrs={'rows': 1, 'cols': 150}),
            'StatoRic': forms.Select(attrs={'value': 'BOZZA'}),
        }


        labels = {
            'Mot2_1': 'Mantenimento/Recupero delle prestazioni e/o della sicurezza',
            'Mot2_2': 'Aumento/Miglioramento delle prestazioni',
            'Mot1_1': 'Sostituzione di analoga dismessa o in dismissione', 
            'Mot1_2': 'Implementazione/aggiornamento di attrezzatura/sistema',
            'Mot1_3': 'Inizio nuova attività',
            'MotivoClinico': 'Motivo Clinico',
        }

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user', None)   
        super(UrgenteRequestForm, self).__init__(*args, **kwargs)
        # super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['Data'].initial=timezone.now().date()

        if user:
            sede_reparto = SeRep.objects.filter(Sede=user.Sede_Reparto.Sede, Reparto=user.Sede_Reparto.Reparto).first()
            print(f"DEBUG - Sede_Reparto trovata: {sede_reparto}") 
            self.fields['Sede_Reparto'].initial = sede_reparto  # Assegna direttamente l'istanza
        
        self.fields['Data'].initial=timezone.now().date()    

    def clean(self):
        cleaned_data = super().clean()
        self._validate_nec_infra(cleaned_data)
        self._validate_sostituzione(cleaned_data)
        self._validate_aggiornamento(cleaned_data)
        self._validate_prezzi(cleaned_data)
        #self._validate_specifiche(cleaned_data)

        return cleaned_data
    
    def _validate_nec_infra(self, cleaned_data):
        # NECESSITÀ INFRASTRUTTURE
        nec_infra_si = cleaned_data.get('NecInfraSi', False)
        nec_infra_no = cleaned_data.get('NecInfraNO', False)
        nec_infra_nota = cleaned_data.get('NecInfraNota', None)

        if nec_infra_si and nec_infra_no:
            self.add_error('NecInfraSI','non puoi selezionare entrambi i campi')
            self.add_error('NecInfraNO','non puoi selezionare entrambi i campi')

        if nec_infra_si and not nec_infra_nota:
            self.add_error('NecInfraNota', "Inserire la motivazione.")

    def _validate_sostituzione(self,cleaned_data):    # SOSTITUZIONE
        mot1_1 = cleaned_data.get('Mot1_1', False)
        sost_nota = cleaned_data.get('SostNota', None)

        if mot1_1 and not sost_nota:
            self.add_error('SostNota', "Inserire il riferimento per la sostituzione.")

    def _validate_aggiornamento(self,cleaned_data):    # AGGIORNAMENTO / MIGLIORAMENTO
        mot2_2 = cleaned_data.get('Mot2_2', False)
        agg_nota = cleaned_data.get('AggNota', None)

        if mot2_2 and not agg_nota:
            self.add_error('AggNota', "Specificare in cosa consiste l'aggiornamento.")

    def _validate_prezzi(self,cleaned_data):    # PREZZI
        acquisto = cleaned_data.get('Acquisto', False)
        noleggio = cleaned_data.get('Noleggio', False)
        service = cleaned_data.get('Service', False)

        if acquisto and not cleaned_data.get('Prezzo_acquisto'):
            self.add_error('Prezzo_acquisto', "Inserire il prezzo (IVA ESCLUSA).")

        if noleggio and not cleaned_data.get('Prezzo_Noleggio'):
            self.add_error('Prezzo_Noleggio', "Inserire il prezzo (IVA ESCLUSA).")

        if service and not cleaned_data.get('Prezzo_Service'):
            self.add_error('Prezzo_Service', "Inserire il prezzo (IVA ESCLUSA).")

    #def _validate_specifiche(self,cleaned_data):    # SPECIFICHE (Min vs Max)
    #    min_selected = cleaned_data.get('Min', False)
    #    max_selected = cleaned_data.get('Max', False)

    #    if min_selected and max_selected:
    #        self.add_error('Max', "La specifica o è di minima o è di massima. Non può essere entrambe.")

    #    elif not min_selected and not max_selected:
    #        self.add_error('Max', "La specifica è di minima o è di massima. Selezionare una delle due.")

class SpecificheUrgForm(ModelForm):
    class Meta:
        model = SpecificheUrg
        fields = ['ID_rich', 'rif', 'Specifica', 'MotivoClinico', 'Min', 'Max']

        widgets={
            'Specifica': forms.Textarea(attrs={'rows': 1, 'cols': 50}),
            'MotivoClinico': forms.Textarea(attrs={'rows': 1, 'cols': 50}),

        }
        labels ={
            'MotivoClinico': 'Motivo Clinico'
        }
    
    def clean(self): #aggiornato
        cleaned_data = super().clean()
        Min = cleaned_data.get('Min', False)
        Max = cleaned_data.get('Max', False)

        if Min and Max:
            self.add_error('Max', "La specifica o è di minima o è di massima. Non può essere entrambe.")

        if not Min and not Max:
            self.add_error('Max', "La specifica è di minima o è di massima. Selezionare una delle due.")

        return cleaned_data

class UnicitaUrgForm(ModelForm):
    class Meta:
        model = UnicitaUrg
        fields =['ID_rich','rifext', 'Nota']

        widgets = {
            'Nota': forms.Textarea(attrs={'rows': 1, 'cols': 150}),
            
        }

class CriteriUrgForm(ModelForm):
    class Meta:
        model = CriteriUrg
        fields ='__all__'

        widgets = {
            'Criterio': forms.Textarea(attrs={'rows':4, 'cols':150})
        }

class ConsumabiliUrgForm(ModelForm):
    class Meta:
        model = ConsumabiliUrg
        exclude = ['Totale']

        widgets={
            'Tipo': forms.Textarea(attrs={'rows':1, 'cols': 100})
        }

class DittaUrgForm(ModelForm):
    class Meta:
        model = DittaUrg
        fields = '__all__'

class AllegatiUrgForm(ModelForm):
    class Meta:
        model = AllegatiUrg
        fields = '__all__'

class DateUrgForm(ModelForm):
    class Meta:
        model = UrgenteRequest
        fields = ['Data', 'Data1', 'Data2', 'Data3', 'Data4', 'Data5', 'Data6', 'Data7', 'Data8', 'Data9']

class ValMotUrgForm(ModelForm):
    class Meta:
        model = UrgenteRequest
        fields = ['ValMot', 'ValMotNota']

        widgets = {
            'ValMotNota': forms.Textarea(attrs={'rows': 3, 'cols': 200})
        }
        labels = {
            'ValMot': 'Valutazione (CONGRUO/NON CONGRUO)',
            'ValMotNota': 'Nota'
        }
    
    def clean(self):
        ValMot = self.cleaned_data.get('ValMot', False)
        if ValMot == '0':
            ValMotNota = self.cleaned_data.get('ValMotNota', None)
            if not ValMotNota:
                self._errors['ValMotNota'] = self.error_class([
                    "Specificare il motivo."
                ])

class ValSpecUrgFormCli(ModelForm):
    class Meta:
        model = SpecificheUrg
        fields = ['ValSpecCli', 'ValSpecCliNota']

        widgets ={
            'ValSpecCliNota': forms.Textarea(attrs={'rows': 1, 'cols': 100})
        }
    
    def clean(self):
        ValSpecCli = self.cleaned_data.get('ValSpecCli', False)
        if ValSpecCli == 'NO':
            ValSpecCliNota = self.cleaned_data.get('ValSpecCliNota', None)
            if not ValSpecCliNota:
                self._errors['ValSpecCliNota'] = self.error_class([
                    "Specificare il motivo."
                ])

class ValSpecUrgFormTec(ModelForm):
    class Meta:
        model = SpecificheUrg
        fields = ['ValSpecTec', 'ValSpecTecNota']
    
    def clean(self):
        ValSpecTec = self.cleaned_data.get('ValSpecTec', False)
        if ValSpecTec == 'NO':
            ValSpecTecNota = self.cleaned_data.get('ValSpecTecNota', None)
            if not ValSpecTecNota:
                self._errors['ValSpecTecNota'] = self.error_class([
                    "Specificare il motivo."
                ])

class ValUnUrgFormCli(ModelForm):
    class Meta:
        model = UnicitaUrg
        fields = ['ValCli']

class ValUnUrgFormTec(ModelForm):
    class Meta:
        model = UnicitaUrg
        fields = ['ValTec']

class Data1UrgForm(ModelForm):
    class Meta:
        model = UrgenteRequest
        fields = ['Data1']
    
    widgets ={
            'Data1': forms.DateInput()
        }
        
    labels = {
            'Data1': 'Data',
        }
class FormUrgUn(ModelForm):
    class Meta:
        model = UrgenteRequest
        fields = ['Simili', 'NoteGen']

        widgets = {
            'Simili': forms.CheckboxInput()
        }

class UnUrgform(ModelForm):
    class Meta:
        model = SpecificheUrg
        fields =['Un']
        

TIPO_RICHIESTA_CHOICES = [
    ("", "Tutte"),
    ("Urgente", "Urgente"),
    ("Programmato", "Programmato"),
    ("Fabbisogno", "Fabbisogno"),
]

class RicercaForm(forms.Form):
    q = forms.CharField(
        required=False, 
        label="Cerca", 
        widget=forms.TextInput(attrs={'class': 'full-width', 'size': 20})
    )
    tipo_richiesta = forms.ChoiceField(
        choices=TIPO_RICHIESTA_CHOICES, 
        required=False, 
        label="Tipo di Richiesta",
        widget=forms.Select(attrs={'class': 'full-width'})
    )

class AssPriorForm(forms.ModelForm):
    class Meta: 
        model=Fabbisogni
        fields= ['AssegnPrior']