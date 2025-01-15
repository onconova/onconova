from collections import defaultdict 
from django.conf import settings 
import re 
import os 
import csv
import environ 
import subprocess
import json 
import sys
from datetime import datetime 
from tqdm import tqdm 
from pop.terminology.utils import get_file_location, get_dictreader_and_size, ensure_within_string_limits, ensure_list, CodedConcept

 
# Read .env file
env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'), overwrite=True)

# Expand size limit to load heavy CSV files 
csv.field_size_limit(sys.maxsize)

class TerminologyDigestor:
    """
    A base class for digesting terminology files into CodedConcept objects.

    Attributes:
        PATH (str): The base directory path for external data files.
        FILENAME (str): The name of the file containing terminology data.
        CANONICAL_URL (str): The canonical URL of the terminology.
        OTHER_URLS (list[str]): Additional URLs associated with the terminology.
        LABEL (str): A label identifier for the terminology.

    Methods:
        __init__(verbose: bool = True) -> None:
            Initializes the TerminologyDigestor and prepares the file location.
        
        digest() -> dict[str, CodedConcept]:
            Digests the terminology's concepts and designations.
        
        _digest_concepts() -> None:
            Reads and processes each row from the file containing concepts.
        
        _digest_concept_row(row: dict[str, str]) -> None:
            Processes a single row from the concepts file.
    """

    PATH: str = os.path.join(settings.BASE_DIR, env('EXTERNAL_DATA_DIR')) 
    FILENAME: str
    CANONICAL_URL: str 
    OTHER_URLS: list[str] = []
    LABEL: str 

    def __init__(self, verbose: bool = True) -> None:
        """
        Initialize the TerminologyDigestor.

        Args:
            verbose (bool, optional): Whether to print progress messages. Defaults to True.
        """
        try:
            self.file_location = get_file_location(self.PATH, self.FILENAME)
        except FileNotFoundError:
            cmd = f'chmod +x download.sh && ./download.sh {self.LABEL}'
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            process.wait()
        self.file_location = get_file_location(self.PATH, self.FILENAME)
        self.verbose = verbose
        
    def digest(self) -> dict[str, CodedConcept]:
        """
        Digests the terminology's concepts and designations.

        Returns:
            dict[str, CodedConcept]: A dictionary with concept codes as keys
                and CodedConcept objects as values.
        """
        self.designations = defaultdict(list)
        self.concepts = {}     
        self._digest_concepts()
        for code, synonyms in self.designations.items(): 
            self.concepts[code].synonyms = synonyms
        return self.concepts
    
    def _digest_concepts(self) -> None:
        """
        Reads through a file containing concepts and processes each row.

        Returns:
            None
        """
        # Read through file containing the concepts
        with open(self.file_location) as file:
            # Go over the concepts in the file
            reader, total = get_dictreader_and_size(file)
            for row in tqdm(reader, total=total, disable=not self.verbose, desc='• Digesting concepts'):
                self._digest_concept_row(row)
        if self.verbose:
            print(f'\r✓ All concepts successfully digested')

    def _digest_concept_row(self, row: dict[str, str]) -> None:
        """
        Processes a single row in the file containing concepts.

        Args:
            row (dict[str, str]): A dictionary representing a single row in the file.

        Returns:
            None

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError()



class NCITDigestor(TerminologyDigestor):
    LABEL = 'ncit'
    FILENAME = 'ncit.tsv'
    CANONICAL_URL='http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl'
    
    def _digest_concept_row(self, row):        
        # Get core coding elements
        code = row['code']
        parent = row['parents'].split('|')[0] if row['parents'] else None
        synonyms = [ensure_within_string_limits(synonym) for synonym in row['synonyms'].split('|')] if row['synonyms'] else [None]
        display = row['display name'] or synonyms[0]
        # Add the concept
        self.concepts[code] = CodedConcept(
            code=code,
            display=display,
            definition=row['definition'],
            parent=parent,  
            synonyms=[synonym for synonym in synonyms[1:]],
            system=self.CANONICAL_URL,
        )


class SNOMEDCTDigestor(TerminologyDigestor):
    LABEL = 'snomedct'
    FILENAME = 'snomedct.tsv'
    CANONICAL_URL='http://snomed.info/sct'
    RELATIONSHIPS_FILENAME = 'snomedct_relations.tsv'
    SNOMED_IS_A = '116680003'
    SNOMED_DESIGNATION_USES = {
        '900000000000013009': 'SYNONYM',
        '900000000000003001': 'FULL',
    }

    def digest(self):
        super().digest() 
        self._digest_relationships()
        for code, concept in self.concepts.items():
            if len(concept.display) > len(concept.synonyms[0]):
                self.concepts[code].synonyms.append(concept.display)
                self.concepts[code].display = concept.synonyms[0]
        return self.concepts
    
    def _digest_relationships(self):
        file_location = get_file_location(self.PATH, self.RELATIONSHIPS_FILENAME)
        # Read through file containing the relationships
        with open(file_location) as file:
            # Go over the concepts in the file
            reader, total = get_dictreader_and_size(file)
            for row in tqdm(reader, total=total, disable=not self.verbose, desc='• Digesting relationships'):
                type = row['typeId']
                active = bool(row['active'])
                if active and type == self.SNOMED_IS_A:
                    parent = self.concepts[row['destinationId']]
                    child = self.concepts[row['sourceId']]
                    child.parent = parent.code

        if self.verbose: 
            print(f'\r✓ All relationships sucessfully digested')

    def _digest_concept_row(self, row):   
        if not bool(row['active']):
            return
        code = row['conceptId'] 
        usage = self.SNOMED_DESIGNATION_USES[row['typeId']]
        display = ensure_within_string_limits(row['term'])
        if code not in self.concepts:
            self.concepts[code] = CodedConcept( 
                code=code,
                display=display,
                system=self.CANONICAL_URL,
            )
        if usage == 'FULL':
            self.concepts[code].display = display
        else:
            self.concepts[code].synonyms.append(display)     


class LOINCDigestor(TerminologyDigestor):
    FILENAME = 'loinc.csv'
    LABEL='loinc'
    CANONICAL_URL='http://loinc.org'
    LOINC_PROPERTIES = [
        'COMPONENT',
        'PROPERTY',
        'TIME_ASPCT',
        'SYSTEM',
        'SCALE_TYP',
        'METHOD_TYP',
        'CLASS',
        'CONSUMER_NAME',
        'CLASSTYPE',
        'ORDER_OBS'
    ]
    
    def digest(self):
        super().digest() 
        self._digest_part_codes()
        self._digest_answer_lists()
        return self.concepts
    
    def _digest_concept_row(self, row):
        # Get core coding elements
        code = row['LOINC_NUM']
        display = ensure_within_string_limits(row['LONG_COMMON_NAME'])
        # Add the concept
        self.concepts[code] = CodedConcept(
            code = code,
            display = display,
            properties = {prop: row[prop] for prop in self.LOINC_PROPERTIES},
            synonyms = [ensure_within_string_limits(row['DisplayName'])] if row['DisplayName'] else [],
            system=self.CANONICAL_URL,
        )

    def _digest_part_codes(self):
        # Go over all translation files
        filename = f'loinc_parts.csv'
        with open(get_file_location(self.PATH, filename)) as file:
            reader, total = get_dictreader_and_size(file)
            # Go over the translation designations in the file
            for row in tqdm(reader, total=total, disable=not self.verbose, desc='• Digesting ansswer lists'):
                code = row['CODE']
                if not code.startswith('LP'):
                    continue
                display = row['CODE_TEXT']
                self.concepts[code] = CodedConcept(
                    code = code,
                    display = display,
                    parent = row['IMMEDIATE_PARENT'],
                    system=self.CANONICAL_URL,
                ) 
            if self.verbose:
                print(f'\r• Sucessfully digested all parts')

    def _digest_answer_lists(self):
        # Go over all translation files
        filename = f'loinc_answer_lists.csv'
        with open(get_file_location(self.PATH, filename)) as file:
            reader, total = get_dictreader_and_size(file)
            answer_lists_codes_included = []
            # Go over the translation designations in the file
            for row in tqdm(reader, total=total, disable=not self.verbose, desc='• Digesting answer lists'):
                # Get core coding elements
                list_code = row['AnswerListId']
                list_display = ensure_within_string_limits(row['AnswerListName'])
                answer_code = row['AnswerStringId']
                answer_display = ensure_within_string_limits(row['DisplayText'])
                # Add the concepts
                if list_code not in answer_lists_codes_included:
                    self.concepts[list_code] = CodedConcept(
                        code = list_code,
                        display = list_display,
                        system=self.CANONICAL_URL,
                    )     
                    answer_lists_codes_included.append(list_code)                
                self.concepts[answer_code] = CodedConcept(
                    code = answer_code,
                    display = answer_display,
                    system=self.CANONICAL_URL,
                )        
            if self.verbose:
                print(f'\r• Sucessfully digested all answer lists')
                
        
        
class ICD10Digestor(TerminologyDigestor):
    LABEL = 'icd10'
    FILENAME = 'icd10.tsv'
    CANONICAL_URL='http://hl7.org/fhir/sid/icd-10'
    
    def _digest_concept_row(self, row):        
        code = row['code'] 
        display = row['display']
        if len(display)>2000:
            display = display[:2000]
        self.concepts[code] = CodedConcept( 
            code=code,
            display=display,
            system=self.CANONICAL_URL,
        )


class ICD10CMDigestor(TerminologyDigestor):
    LABEL = 'icd10cm'
    FILENAME = 'icd10cm'
    ICD10CM_CODE_STRING_LENGTH = 7
    CANONICAL_URL='ttp://hl7.org/fhir/sid/icd-10-cm'
    
    def _digest_concept_row(self, row):     
        code = row['term'][:self.ICD10CM_CODE_STRING_LENGTH].strip() 
        display = row['term'][self.ICD10CM_CODE_STRING_LENGTH+1:].strip() 
        if len(display)>2000:
            display = display[:2000]
        self.concepts[code] = CodedConcept(
            code=code,
            display=display,
            system=self.CANONICAL_URL,
        )
        

class ICD10PCSDigestor(TerminologyDigestor):
    LABEL = 'icd10pcs'
    FILENAME = 'icd10pcs'
    ICD10PCS_CODE_STRING_LENGTH = 7
    CANONICAL_URL='http://hl7.org/fhir/sid/icd-10-pcs'
    
    def _digest_concept_row(self, row):     
        code = row['term'][:self.ICD10PCS_CODE_STRING_LENGTH].strip() 
        display = row['term'][self.ICD10PCS_CODE_STRING_LENGTH+1:].strip() 
        if len(display)>2000:
            display = display[:2000]
        self.concepts[code] = CodedConcept(
            code=code,
            display=display,
            system=self.CANONICAL_URL,
        )           


class ICDO3DifferentiationDigestor(TerminologyDigestor):
    LABEL = 'icdo3diff'
    FILENAME = 'icdo3diff.tsv'
    CANONICAL_URL='http://terminology.hl7.org/CodeSystem/icd-o-3-differentiation'
    
    def _digest_concept_row(self, row):        
        code = row['code'] 
        display = ensure_within_string_limits(row['display'])
        self.concepts[code] = CodedConcept( 
            code=code,
            display=display,
            system=self.CANONICAL_URL,
        )
                       

class ICDO3MorphologyDigestor(TerminologyDigestor):
    LABEL = 'icdo3morph'
    FILENAME = 'icdo3morph.tsv'
    CANONICAL_URL='http://terminology.hl7.org/CodeSystem/icd-o-3-morphology'
    
    def _digest_concept_row(self, row):        
        code = row['Code'] 
        display = ensure_within_string_limits(row['Label'])
        if code not in self.concepts:
            self.concepts[code] = CodedConcept( 
                code=code,
                display=display,
                system=self.CANONICAL_URL,
            )
        if row['Struct'] == 'title':
            self.concepts[code].display = display
        elif row['Struct'] == 'sub':
            self.concepts[code].synonyms.append(display)
      
class ICDO3TopographyDigestor(TerminologyDigestor):
    LABEL = 'icdo3topo'
    FILENAME = 'icdo3topo.tsv'
    CANONICAL_URL='http://terminology.hl7.org/CodeSystem/icd-o-3-topography'
    
    def _digest_concept_row(self, row):        
        code = row['Code'] 
        display = ensure_within_string_limits(row['Title'])
        if code not in self.concepts:
            self.concepts[code] = CodedConcept( 
                code=code,
                display=display,
                system=self.CANONICAL_URL,
                parent=code.split('.')[0] if len(code.split('.'))>1 else None,
            )
        if str(row['Lvl']) in ['3','4']:
            self.concepts[code].display = display.capitalize() if str(row['Lvl']) == '3' else display
        elif row['Lvl'] == 'incl':
            self.concepts[code].synonyms.append(display)

class HGNCGenesDigestor(TerminologyDigestor):
    LABEL = 'hgnc'
    FILENAME = 'hgnc.tsv'
    CANONICAL_URL='http://www.genenames.org/geneId'
    def _digest_concept_row(self, row):
        # Get core coding elements
        code = row['hgnc_id']
        display = row['symbol']
        # Compile all synonyms
        synonyms = [ensure_within_string_limits(synonym) for synonym in row['alias_symbol'].split('|') + row['alias_name'].split('|') if synonym]
        olds = [ensure_within_string_limits(synonym) for synonym in row['prev_symbol'].split('|') + row['prev_name'].split('|') if synonym]
        # Add the concept
        self.concepts[code] = CodedConcept(
            code=code,
            display=display,
            definition=row['name'],
            properties={
                'locus_group': row['locus_group'],
                'locus_type': row['locus_type'],
                'location': row['location'],
                'refseq_accession': row['refseq_accession']
            },
            synonyms=synonyms+olds,
            system=self.CANONICAL_URL,
        )
        
        

class HGNCGroupDigestor(TerminologyDigestor):
    LABEL = 'hgnc-group'
    FILENAME = 'hgnc.tsv'
    CANONICAL_URL='http://www.genenames.org/genegroup'
    
    def _digest_concept_row(self, row):
        codes = row['gene_group_id'].split('|')
        displays =  row['gene_group'].split('|')
        for code, display in zip(codes, displays):
            concept = CodedConcept(
                code=code,
                display=display,
                system=self.CANONICAL_URL,
            )
            if concept.code in self.concepts:
                continue
            # Add the concept
            self.concepts[code] = concept

                  
class SequenceOntologyDigestor(TerminologyDigestor):
    LABEL = 'so'
    FILENAME = 'so.obo'
    CANONICAL_URL = 'http://www.sequenceontology.org'
    OTHER_URLS = ['http://sequenceontology.org']

    def _digest_concept_row(self, row):
        if bool(row.get('is_obsolete')):
            return
        # Get core coding elements
        code = row['id']
        display = ensure_within_string_limits(row['name'])
        definition = row.get('def')
        if definition:
            definition = definition.split('"')[1]
        synonyms = []
        for synonym in ensure_list(row.get('synonym')):
            if not synonym: 
                continue
            SYNONYM_REGEX = r"\"(.*)\" ([A-Z]*) .*"
            matches = re.finditer(SYNONYM_REGEX, synonym)
            for match in matches:
                synonyms.append(ensure_within_string_limits(match.group(1)))
        # Add the concept
        self.concepts[code] = CodedConcept(
            code=code,
            display=display,
            definition=definition,
            parent=ensure_list(row.get('is_a'))[0].split(' ! ')[0] if row.get('is_a') else None,
            synonyms=synonyms,
            system=self.CANONICAL_URL,
        )



class CTCAEDigestor(TerminologyDigestor):
    LABEL = 'ctcae'
    FILENAME = 'ctcae.csv'
    CANONICAL_URL = '' 

    def _digest_concept_row(self, row):   
        code = row['MedDRA Code'] 
        display = row['CTCAE Term']
        self.concepts[code] = CodedConcept(
            code=code,
            display=display,
            definition=row['Definition'],
            properties={
                prop: row[prop] for prop in ['MedDRA SOC', 'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5']
            },
            system=self.CANONICAL_URL,
        )

class UCUMDigestor(TerminologyDigestor):
    LABEL = 'ucum'
    FILENAME = 'ucum.csv'
    CANONICAL_URL = 'http://unitsofmeasure.org'
    
    def _digest_concept_row(self, row):   
        code = row['UCUM_CODE'] 
        display = row['Description']
        self.concepts.append(CodedConcept(
            code=code,
            display=display,
            system=self.CANONICAL_URL,
        ))



class RxNormDigestor(TerminologyDigestor):
    LABEL = 'rxnorm'
    FILENAME = 'rxnorm.csv'
    CANONICAL_URL = 'http://www.nlm.nih.gov/research/umls/rxnorm'

    def _digest_concept_row(self, row):   
        code = row['rxcui'] 
        display = ensure_within_string_limits(row['name'])
        self.concepts[code] = CodedConcept(
            code=code,
            display=display,
            system=self.CANONICAL_URL,
        )
        
    

class WHOATCDigestor(TerminologyDigestor):
    LABEL = 'atc'
    FILENAME = 'atc.csv'
    CANONICAL_URL = 'http://www.whocc.no/atc'
    def _digest_concept_row(self, row):   
        code = row['atc_code'] 
        display = ensure_within_string_limits(row['atc_name'])
        self.concepts[code] = CodedConcept(
            code=code,
            display=display,
            properties={
                'defined_daily_dose': row['ddd'] if row['ddd']!='NA' else None,
                'defined_daily_dose_units': row['uom'] if row['uom']!='NA' else None,
                'adminsitration_route': row['adm_r'] if row['adm_r']!='NA' else None,
                'note': row['note'] if row['note']!='NA' else None,
            },
            system=self.CANONICAL_URL,
        )

class OncoTreeDigestor(TerminologyDigestor):
    LABEL = 'oncotree'
    FILENAME = 'oncotree.json'
    CANONICAL_URL='http://oncotree.mskcc.org/fhir/CodeSystem/snapshot'
    VERSION = datetime.now().strftime("%d%m%Y")

    def digest(self):
        self.concepts = {}
        with open(self.file_location) as file:
            self.oncotree = json.load(file)
        # And recursively add all its children
        for branch in self.oncotree['TISSUE']['children'].values():
            self._digest_branch(branch)
        return self.concepts

    def _digest_branch(self, branch):
        code = branch['code']
        display = ensure_within_string_limits(branch['name'])
        # Add current oncotree code
        self.concepts[code] = CodedConcept(
            code = code,
            display = display,
            parent = branch['parent'],
            properties = {'tissue': branch['tissue'], 'level': branch['level']},
            system = self.CANONICAL_URL,
            version = self.VERSION,
        )
        # And recursively add all its children
        for child_branch in branch['children'].values():
            self._digest_branch(child_branch)


DIGESTORS = [
    NCITDigestor, 
    SNOMEDCTDigestor,
    SequenceOntologyDigestor,
    CTCAEDigestor,
    UCUMDigestor,
    RxNormDigestor,
    WHOATCDigestor,
    LOINCDigestor,
    ICDO3MorphologyDigestor,
    ICDO3TopographyDigestor,
    ICDO3DifferentiationDigestor,
    ICD10Digestor,
    ICD10CMDigestor,
    ICD10PCSDigestor,
    HGNCGenesDigestor,
    HGNCGroupDigestor,
    OncoTreeDigestor,
]
