from pop.terminology.utils import get_file_location, ensure_within_string_limits, ensure_list
from pop.terminology.services import get_dictreader_and_size
from collections import defaultdict 
from django.conf import settings # type: ignore
import re 
import os 
import environ # type: ignore
from tqdm import tqdm # type: ignore

# Read .env file
env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'), overwrite=True)

class TerminologyDigestor:
    PATH: str = os.path.join(settings.BASE_DIR, env('EXTERNAL_DATA_DIR')) 
    FILENAME: str

    def __init__(self, verbose=True):
        self.file_location = get_file_location(self.PATH, self.FILENAME)
        self.verbose = verbose 
        
    def digest(self):
        self.designations = defaultdict(list)
        self.concepts = []     
        self._digest_concepts() 
        return self.concepts, self.designations 
    
    def _digest_concepts(self):
        # Read through file containing the concepts
        with open(self.file_location) as file:
            # Go over the concepts in the file
            reader, total = get_dictreader_and_size(file)
            for row in tqdm(reader, total=total, disable=not self.verbose, desc='• Digesting concepts'):
                self._digest_concept_row(row)
        if self.verbose: 
            print(f'\r✓ All concepts succesfully digested')

    def _digest_concept_row(self, row):
        raise NotImplementedError()



class NCITDigestor(TerminologyDigestor):
    FILENAME = 'ncit.tsv'
    
    def _digest_concept_row(self, row):        
        # Get core coding elements
        code = row['code']
        parent = row['parents'].split('|')[0]
        synonyms = [ensure_within_string_limits(synonym) for synonym in row['synonyms'].split('|')]
        display = row['display name'] or synonyms[0]
        # Add the concept
        self.concepts.append({
            'code': code,
            'display': display,
            'definition': row['definition'],
            'parent': parent,
        })
        # Add basic designations
        self.designations[code].append({
            'language': 'en',
            'use': 'PREFERRED',
            'display': display,
        })
        for synonym in synonyms[1:]:
            self.designations[code].append({
                'language': 'en',
                'use': 'SYNONYM',
                'display': synonym,
            })   
            
            


class SNOMEDCTDigestor(TerminologyDigestor):
    FILENAME = 'snomedct.tsv'
    RELATIONSHIPS_FILENAME = 'snomedct_relations.tsv'
    SNOMED_IS_A = '116680003'
    SNOMED_DESIGNATION_USES = {
        '900000000000013009': 'SYNONYM',
        '900000000000003001': 'FULL',
    }

    def digest(self):
        super().digest() 
        self._digest_relationships()
        return self.concepts, self.designations 
    
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
                    child = next((concept for concept in self.concepts if concept['code'] == row['sourceId']))
                    child['parent'] = row['destinationId']
        if self.verbose: 
            print(f'\r✓ All relationships sucessfully digested')

    def _digest_concept_row(self, row):   
        if not bool(row['active']):
            return
        code = row['conceptId'] 
        language = row['languageCode']
        usage = self.SNOMED_DESIGNATION_USES[row['typeId']]
        display = ensure_within_string_limits(row['term'])
        # Add the concept if it is a full specification
        if usage == 'FULL':
            self.concepts.append({
                'code': code,
                'display': display,
            })
        # Add the designation
        self.designations[code].append({
            'language': language,
            'use': usage,
            'display': display,
        })   
        



class LOINCDigestor(TerminologyDigestor):
    FILENAME = 'loinc.csv'
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
        self._digest_translations()
        self._digest_answer_lists()
        self._digest_part_codes()
        return self.concepts, self.designations 
    
    def _digest_concept_row(self, row):
        # Get core coding elements
        code = row['LOINC_NUM']
        display = ensure_within_string_limits(row['LONG_COMMON_NAME'])
        # Add the concept
        self.concepts.append({
            'code': code,
            'display': display,
            'properties': {prop: row[prop] for prop in self.LOINC_PROPERTIES}
        })
        # Add basic designations
        self.designations[code].append({
            'language': 'en',
            'use': 'FULL',
            'display': display,
        })
        if row['DisplayName']:
            self.designations[code].append({
                'language': 'en',
                'use': 'SYNONYM',
                'display': ensure_within_string_limits(row['DisplayName']),
            })  

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
                self.concepts.append({
                    'code': code,
                    'display': display,
                    'parent': row['IMMEDIATE_PARENT']
                }) 
                # Add designation
                self.designations[code].append({
                    'language': 'en',
                    'use': 'FULL',
                    'display': display
                })     
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
                    self.concepts.append({
                        'code': list_code,
                        'display': list_display,
                    })               
                    # Add designation
                    self.designations[list_code].append({
                        'language': 'en',
                        'use': 'FULL',
                        'display': list_display
                    })      
                    answer_lists_codes_included.append(list_code)                
                self.concepts.append({
                    'code': answer_code,
                    'display': answer_display,
                }) 
                # Add designation
                self.designations[answer_code].append({
                    'language': 'en',
                    'use': 'FULL',
                    'display': answer_display
                })             
            if self.verbose:
                print(f'\r• Sucessfully digested all answer lists')
                


    def _digest_translations(self):
        # Go over all translation files
        for loincLang in ['deDE15','frFR18','itIT16']:
            filename = f'loinc_{loincLang}.csv'
            with open(get_file_location(self.PATH, filename)) as file:
                reader, total = get_dictreader_and_size(file)
                # Go over the translation designations in the file
                for row in tqdm(reader, total=total, disable=not self.verbose, desc=f'• Digesting <{loincLang}> translations'):
                    # Add translation
                    self.designations[row['LOINC_NUM']].append({
                        'language': loincLang[:2],
                        'use': 'FULL',
                        'display': ensure_within_string_limits(row['LONG_COMMON_NAME']),
                        'properties': {prop: row[prop] for prop in self.LOINC_PROPERTIES if prop in row}
                    })   
                if self.verbose:             
                    print(f'\r• Sucessfully digested all <{loincLang}> translations')
        
    @classmethod
    def import_LOINC_valuesets(cls, codesystem, verbose=True):
        # Go over all translation files
        filename = f'Loinc_answer_list_codes.csv'
        with open(get_file_location(cls.PATH, filename)) as file:
            reader, total = get_dictreader_and_size(file)
            valuesets = dict()
            # Go over the translation designations in the file
            for row in tqdm(reader, total=total, disable=not verbose, desc='• Digesting answer lists as valuesets'):
                print(f'\r• Digesting answer lists as valuesets {n/total*100:.2f}%', end='')
                # Get core coding elements
                list_code = row['AnswerListId']
                list_display = ensure_within_string_limits(row['AnswerListName'])
                if list_code not in valuesets:
                    valuesets[list_code] = {
                        'concepts': [],
                        'title': list_display,
                        'code': list_code,
                    }
                valuesets[list_code]['concepts'].append(row['AnswerStringId'])
            print(f'\r• Sucessfully digested all answer lists')
            
            from terminologyServer.terminologies.models import ValueSet
            for n,valueset in enumerate(valuesets.values()):
                print(f'\r• Updating valuesets in database {n/len(valuesets)*100:.2f}%', end='')
                canonical_url = f'http://loinc.org/vs/{valueset["code"]}'
                version = f'Loinc_{codesystem.version}-{codesystem.version}'
                concepts = [codesystem.concepts.get(code=member) for member in valueset['concepts']]
                valueset_instance,_ = ValueSet.objects.update_or_create(
                    url=canonical_url,
                    version=version,
                    defaults=dict(
                        url=canonical_url,
                        version=version,
                        name=''.join([word.capitalize() for word in valueset["title"].split(' ')]),
                        title=valueset["title"],
                        copyright="This material contains content from LOINC (http://loinc.org). LOINC is copyright Regenstrief Institute, Inc. and the Logical Observation Identifiers Names and Codes (LOINC) Committee and is available at no cost under the license at http://loinc.org/license. LOINC® is a registered United States trademark of Regenstrief Institute, Inc.",
                        publisher="Regenstrief Institute, Inc.",
                        inclusionCriteria={
                            "system": "http://loinc.org",
                            "version": codesystem.version,
                            "concept": [
                                {
                                    "code": concept.code,
                                    "display": concept.display,
                                } for concept in concepts
                            ]
                        },
                    )
                )
                valueset_instance.concepts.set(concepts)
            print(f'\r• Sucessfully imported all answer lists as ValueSets')

        
        
class ICD10Digestor(TerminologyDigestor):
    PATH = 'ICD-10/'
    FILENAME = 'icdo10_code_system.tsv'
    
    def _digest_concept_row(self, row):        
        code = row['code'] 
        display = row['display']
        if len(display)>2000:
            display = display[:2000]
        self.concepts.append({
            'code': code,
            'display': display,
        })
        self.designations[code].append({
            'language': 'en',
            'use': 'FULL',
            'display': display,
        })    


class ICD10CMDigestor(TerminologyDigestor):
    FILENAME = 'icd10cm'
    ICD10CM_CODE_STRING_LENGTH = 7
    
    def _digest_concept_row(self, row):     
        code = row['term'][:self.ICD10CM_CODE_STRING_LENGTH].strip() 
        display = row['term'][self.ICD10CM_CODE_STRING_LENGTH+1:].strip() 
        if len(display)>2000:
            display = display[:2000]
        self.concepts.append({
            'code': code,
            'display': display,
        })
        self.designations[code].append({
            'language': 'en',
            'use': 'FULL',
            'display': display,
        })                  
       
class ICD10PCSDigestor(TerminologyDigestor):
    FILENAME = 'icd10pcs'
    ICD10PCS_CODE_STRING_LENGTH = 7
    
    def _digest_concept_row(self, row):     
        code = row['term'][:self.ICD10PCS_CODE_STRING_LENGTH].strip() 
        display = row['term'][self.ICD10PCS_CODE_STRING_LENGTH+1:].strip() 
        if len(display)>2000:
            display = display[:2000]
        self.concepts.append({
            'code': code,
            'display': display,
        })
        self.designations[code].append({
            'language': 'en',
            'use': 'FULL',
            'display': display,
        })               
                  
                  
class HGNCGenesDigestor(TerminologyDigestor):
    FILENAME = 'hgnc.tsv'
    
    def _digest_concept_row(self, row):
        # Get core coding elements
        code = row['hgnc_id']
        display = row['symbol']
        # Add the concept
        self.concepts.append({
            'code': code,
            'display': display,
            'definition': row['name'],
            'properties': {
                'locus_group': row['locus_group'],
                'locus_type': row['locus_type'],
                'location': row['location'],
                'refseq_accession': row['refseq_accession']
            }
        })
        # Add basic designations
        self.designations[code].extend([
            {
                'language': 'en',
                'use': 'PREFERRED',
                'display': display,
            },
            {
                'language': 'en',
                'use': 'FULL',
                'display': row['name'],
            }
        ])
        # Compile all synonyms
        synonyms = [ensure_within_string_limits(synonym) for synonym in row['alias_symbol'].split('|') + row['alias_name'].split('|')]
        self.designations[code].extend([{
            'language': 'en',
            'use': 'SYNONYM',
            'display': synonym,
        } for synonym in synonyms])    
        # Compile all deprecated synonyms
        olds = [ensure_within_string_limits(synonym) for synonym in row['prev_symbol'].split('|') + row['prev_name'].split('|')]
        self.designations[code].extend([{
            'language': 'en',
            'use': 'DEPRECATED',
            'display': old,
        } for old in olds])    
        
        

class HGNCGroupDigestor(TerminologyDigestor):
    FILENAME = 'hgnc.tsv'
    
    def _digest_concept_row(self, row):
        codes = row['gene_group_id'].split('|')
        displays =  row['gene_group'].split('|')
        for code, display in zip(codes, displays):
            concept = {
                'code': code,
                'display': display,
            }  
            if concept in self.concepts:
                continue
            # Add the concept
            self.concepts.append(concept)
            # Add basic designations
            self.designations[code].extend([
                {
                    'language': 'en',
                    'use': 'PREFERRED',
                    'display': display,
                }
            ])
            
                  
class SequenceOntologyDigestor(TerminologyDigestor):
    FILENAME = 'so.obo'
    
    def _digest_concept_row(self, row):
            if bool(row.get('is_obsolete')):
                return
            # Get core coding elements
            code = row['id']
            display = ensure_within_string_limits(row['name'])
            definition = row.get('def')
            if definition:
                definition = definition.split('"')[1]
            # Add the concept
            self.concepts.append({
                'code': code,
                'display': display,
                'definition': definition,
                'parent': ensure_list(row.get('is_a'))[0].split(' ! ')[0] if row.get('is_a') else None
            })
            # Add basic designations
            self.designations[code].append({
                'language': 'en',
                'use': 'FULL',
                'display': display,
            })
            for synonym in ensure_list(row.get('synonym')):
                if not synonym: continue
                SYNONYM_REGEX = r"\"(.*)\" ([A-Z]*) .*"
                matches = re.finditer(SYNONYM_REGEX, synonym)
                for match in matches:
                    self.designations[code].append({
                        'language': 'en',
                        'use': 'PREFERRED' if match.group(2) == 'EXACT' else 'SYNONYM',
                        'display': ensure_within_string_limits(match.group(1)),
                    })    


class CVXDigestor(TerminologyDigestor):
    FILENAME = 'cvx.tsv'
    
    def _digest_concept_row(self, row):        
        code = row['CVX Code'] 
        display = row['CVX Short Description']
        self.concepts.append({
            'code': code,
            'display': display,
            'description': row['Note'] or None,
            'properties': {
                'VaccineStatus': row['VaccineStatus'],
                'nonvaccine': row['nonvaccine'],
                'update_date': row['update_date'],
            }
        })
        self.designations[code].append({
            'language': 'en',
            'use': 'PREFERRED',
            'display': display,
        })    
        self.designations[code].append({
            'language': 'en',
            'use': 'FULL',
            'display': ensure_within_string_limits(row['Full Vaccine Name']),
        })    



class CTCAEDigestor(TerminologyDigestor):
    FILENAME = 'ctcae.csv'
    
    def _digest_concept_row(self, row):   
        code = row['MedDRA Code'] 
        display = row['CTCAE Term']
        self.concepts.append({
            'code': code,
            'display': display,
            'description': row['Definition'],
            'properties': {
                prop: row[prop] for prop in ['MedDRA SOC', 'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5']
            }
        })
        self.designations[code].append({
            'language': 'en',
            'use': 'FULL',
            'display': display,
        })    

class UCUMDigestor(TerminologyDigestor):
    FILENAME = 'ucum.csv'
    
    def _digest_concept_row(self, row):   
        code = row['UCUM_CODE'] 
        display = row['Description']
        self.concepts.append({
            'code': code,
            'display': display,
        })
        self.designations[code].append({
            'language': 'en',
            'use': 'PREFERRED',
            'display': display,
        })    



class RxNormDigestor(TerminologyDigestor):
    FILENAME = 'rxnorm.csv'
    
    def _digest_concept_row(self, row):   
        code = row['rxcui'] 
        display = ensure_within_string_limits(row['name'])
        self.concepts.append({
            'code': code,
            'display': display,
        })
        self.designations[code].append({
            'language': 'en',
            'use': 'FULL',
            'display': display,
        })    
    
    

class WHOATCDigestor(TerminologyDigestor):
    FILENAME = 'atc.csv'
    
    def _digest_concept_row(self, row):   
        code = row['atc_code'] 
        display = ensure_within_string_limits(row['atc_name'])
        self.concepts.append({
            'code': code,
            'display': display,
            'properties': {
                'defined_daily_dose': row['ddd'] if row['ddd']!='NA' else None,
                'defined_daily_dose_units': row['uom'] if row['uom']!='NA' else None,
                'adminsitration_route': row['adm_r'] if row['adm_r']!='NA' else None,
                'note': row['note'] if row['note']!='NA' else None,
            }
        })
        self.designations[code].append({
            'language': 'en',
            'use': 'FULL',
            'display': display,
        })    