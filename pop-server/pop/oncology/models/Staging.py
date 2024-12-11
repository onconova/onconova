import re

from django.db import models
from django.utils.translation import gettext_lazy as _

from pop.core.models import BaseModel 
from pop.oncology.models import PatientCase, NeoplasticEntity 
import pop.terminology.fields as termfields 
import pop.terminology.models as terminologies 

TNM = 'tnm'
FIGO = 'figo'
BINET = 'binet'
RAI = 'rai'
BRESLOW = 'breslow'
CLARK = 'clark'
ISS = 'iss'
RISS = 'riss'
INSS = 'inss'
INRGSS = 'inrgss'
GLEASON = 'gleason'
RHABDO = 'rhabdomyosarcoma'
WILMS = 'wilms'
LYMPHOMA = 'lymphoma'

class Staging(BaseModel):

    STAGING_DOMAINS = {
        TNM: 'TNM Stage',
        FIGO: 'FIGO Stage',
        BINET: 'Binet Stage',
        RAI: 'RAI Stage',
        BRESLOW: 'Breslow Stage',
        CLARK: 'Clark Level',
        ISS: 'ISS Stage',
        RISS: 'RISS Stage',
        INSS: 'INSS Stage',
        INRGSS: 'Neuroblastoma INRGSS Stage',
        GLEASON: 'Prostate Gleason Group',
        RHABDO: 'Rhabdomyosarcoma Clinical Group',
        WILMS: 'Wilms Tumor Stage',
        LYMPHOMA: 'Lymphoma Stage',
    }
    
    case = models.ForeignKey(
        verbose_name = _('Patient case'),
        help_text = _("Indicates the case of the patient who's cancer is staged"),
        to = PatientCase,
        related_name = 'stagings',
        on_delete = models.CASCADE,
    )
    date = models.DateField(
        verbose_name = _('Staging date'),
        help_text=_("Clinically-relevant date at which the staging was performed and recorded."),
    ) 
    staged_entities = models.ManyToManyField(
        verbose_name = _('Staged neoplastic entities'),
        help_text = _("References to the neoplastic entities that were the focus of the staging."),
        to = NeoplasticEntity,
        related_name = 'stagings',
    )
    
    @property
    def description(self):
        staging = self.STAGING_DOMAINS[self.staging_domain]

        return f'{staging} {self.stage_value}'
    
    @property
    def stage_value(self):
        regex = r"(?i).+(?:Stage| Level| Group Stage| Group )\s*([a-z0-9]+)(?:.*)"
        stage_string = getattr(self, self.staging_domain).stage.display  
        matched =  re.match(regex, stage_string)
        if matched:
            stage_value = matched.group(1)
        else:
            stage_value = stage_string
        return stage_value          
    
    @property
    def staging_domain(self):
        for domain in self.STAGING_DOMAINS.keys():
            try:             
                getattr(self, domain)   
                return domain
            except:
                continue 
    
    def get_domain_staging(self):
        return getattr(self, self.staging_domain)   
    
    
class TNMStaging(Staging):
    
    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = TNM,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('TNM Stage'),
        help_text = _("The information determined as a result of making the observation, if the information has a simple value"),
        terminology = terminologies.TNMStage,  
    )
    methodology = termfields.CodedConceptField(
        verbose_name = _('TNM Staging methodology'),
        help_text = _("Methodology used for TNM staging"),
        terminology = terminologies.TNMStagingMethod,
        blank = True, null=True,
    )    
    pathological = models.BooleanField(
        verbose_name = _("Pathological staging"),
        help_text = _("Whether the staging was based on pathological (true) or clinical (false) evidence."),
        null = True, blank = True,
    )
    primaryTumor = termfields.CodedConceptField(
        verbose_name = _('T Stage'),
        help_text = _("T stage (extent of the primary tumor)"),
        terminology = terminologies.TNMPrimaryTumorCategory,  
        blank = True, null = True,
    )
    regionalNodes = termfields.CodedConceptField(
        verbose_name = _('N Stage'),
        help_text = _("N stage (degree of spread to regional lymph nodes)"),
        terminology = terminologies.TNMRegionalNodesCategory,  
        blank = True, null = True,
    )
    distantMetastases = termfields.CodedConceptField(
        verbose_name = _('M Stage'),
        help_text = _("M stage (presence of distant metastasis)"),
        terminology = terminologies.TNMDistantMetastasesCategory,  
        blank = True, null = True,
    )
    grade = termfields.CodedConceptField(
        verbose_name = _('G Stage'),
        help_text = _("G stage (grade of the cancer cells)"),
        terminology = terminologies.TNMGradeCategory,  
        blank = True, null = True,
    )
    residualTumor = termfields.CodedConceptField(
        verbose_name = _('R Stage'),
        help_text = _("R stage (extent of residual tumor cells after operation)"),
        terminology = terminologies.TNMResidualTumorCategory,
        blank = True, null = True,  
    )
    lymphaticInvasion = termfields.CodedConceptField(
        verbose_name = _('L Stage'),
        help_text = _("L stage (invasion into lymphatic vessels)"),
        terminology = terminologies.TNMLymphaticInvasionCategory,  
        blank = True, null = True,
    )
    venousInvasion = termfields.CodedConceptField(
        verbose_name = _('V Stage'),
        help_text = _("V stage (invasion into venous vessels)"),
        terminology = terminologies.TNMVenousInvasionCategory,  
        blank = True, null = True,
    )
    perineuralInvasion = termfields.CodedConceptField(
        verbose_name = _('Pn Stage'),
        help_text = _("Pn stage (invasion into adjunct nerves)"),
        terminology = terminologies.TNMPerineuralInvasionCategory, 
        blank = True, null = True, 
    )
    serumTumorMarkerLevel = termfields.CodedConceptField(
        verbose_name = _('S Stage'),
        help_text = _("S stage (serum tumor marker level)"),
        terminology = terminologies.TNMSerumTumorMarkerLevelCategory, 
        blank = True, null = True, 
    )


class FIGOStaging(Staging):
    
    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = FIGO,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('FIGO Stage'),
        help_text = _('The value of the FIGO stage'),
        terminology = terminologies.FIGOStage,
    )
    methodology = termfields.CodedConceptField(
        verbose_name = _("FIGO staging methodology"),
        help_text = _("Methodology used for the FIGO staging"),
        terminology = terminologies.FIGOStagingMethod,
        null = True, blank = True,
    )
    

class BinetStaging(Staging):
    
    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = BINET,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('Binet Stage'),
        help_text = _('The value of the Binet stage'),
        terminology = terminologies.BinetStage,
    )
    
    
class RaiStaging(Staging):
    
    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = RAI,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('Rai Stage'),
        help_text = _('The value of the Rai stage'),
        terminology = terminologies.RaiStage,
    )
    methodology = termfields.CodedConceptField(
        verbose_name = _("Rai staging methodology"),
        help_text = _("Methodology used for the Rai staging"),
        terminology = terminologies.RaiStagingMethod,
        null = True, blank = True,
    )
    

class BreslowDepth(Staging):
    
    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = BRESLOW,
        parent_link = True,
        primary_key = True,
    )
    depth = models.FloatField(
        verbose_name = _("Breslow depth"),
        help_text = _("Breslow depth given in milimeters"),
    )
    is_ulcered = models.BooleanField(
        verbose_name='Ulcered',
        help_text=_("Whether the primary tumour presents ulceration"),
        null=True, blank=True,
    )
    
    @property
    def stage(self):
        if self.depth < 0.76:
            # Breslow measurement - depth less than 0.76 mm
            stage_code = '86069005' 
        elif self.depth > 1.75:
             # Breslow measurement - greater than 1.75 mm
            stage_code = '44815009'
        else:
            # Breslow measurement - depth  from 0.76 to 1.75 mm
            stage_code = '17456000' 
        return terminologies.BreslowDepthStage.objects.get(code=stage_code)
    

    
class ClarkStaging(Staging):
    
    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = CLARK,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('Clark Level Stage'),
        help_text = _('The value of the Clark level stage'),
        terminology = terminologies.ClarkLevel,
    )
        
        
class ISSStaging(Staging):
    
    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = ISS,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('ISS Stage'),
        help_text = _('The value of theISS stage'),
        terminology = terminologies.MyelomaISSStage,
    )

        
class RISSStaging(Staging):
    
    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = RISS,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('RISS Stage'),
        help_text = _('The value of the RISS stage'),
        terminology = terminologies.MyelomaRISSStage,
    )


class INSSStage(Staging):

    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = INSS,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('INSS Stage'),
        help_text = _('The value of the INSS stage'),
        terminology = terminologies.NeuroblastomaINSSStage,
    )
    
    
class INRGSSStage(Staging):

    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = INRGSS,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('INRGSS Stage'),
        help_text = _('The value of the INRGSS stage'),
        terminology = terminologies.NeuroblastomaINRGSSStage,
    )
    
class GleasonGrade(Staging):
    
    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = GLEASON,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('Gleason grade Stage'),
        help_text = _('The value of the Gleason grade stage'),
        terminology = terminologies.GleasonGradeGroupStage,
    )
    
class WilmsStage(Staging):

    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = WILMS,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('Wilms Stage'),
        help_text = _('The value of the Wilms stage'),
        terminology = terminologies.WilmsTumorStage,
    )
    
class RhabdomyosarcomaClinicalGroup(Staging):

    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = RHABDO,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('Rhabdomyosarcoma clinical group'),
        help_text = _('The value of the rhabdomyosarcoma clinical group'),
        terminology = terminologies.RhabdomyosarcomaClinicalGroup,
    )
    
class LymphomaStaging(Staging):
    
    staging = models.OneToOneField(
        to = Staging,
        on_delete = models.CASCADE,
        related_name = LYMPHOMA,
        parent_link = True,
        primary_key = True,
    )
    stage = termfields.CodedConceptField(
        verbose_name = _('Lymphoma Stage'),
        help_text = _('The value of the Lymphoma stage'),
        terminology = terminologies.LymphomaStage,
    )
    methodology = termfields.CodedConceptField(
        verbose_name = _("Lymphoma staging methodology"),
        help_text = _("Methodology used for the Lymphoma staging"),
        terminology = terminologies.LymphomaStagingMethod,
        null = True, blank = True,
    )
    bulky = models.BooleanField(
        verbose_name = _("Bulky disease modifier"),
        help_text = _("Bulky modifier indicating if the lymphoma has the presence of bulky disease."),
        null = True, blank = True,
    )
    pathological = models.BooleanField(
        verbose_name = _("Pathological staging"),
        help_text = _("Whether the staging was based on clinical or pathologic evidence."),
        null = True, blank = True,
    )
    modifiers = termfields.CodedConceptField(
        verbose_name = _("Lymphoma stage modifier"),
        help_text = _("Qualifier acting as modifier for the lymphoma stage"),
        terminology = terminologies.LymphomaStagingMethod,
        multiple = True,
    )