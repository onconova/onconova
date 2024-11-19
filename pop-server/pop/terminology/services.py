import cachetools
import environ
import requests 
import os 
import cachetools.func
from collections import defaultdict
from fhir.resources.R4B.valueset import ValueSet as ValueSetSchema, ValueSetComposeInclude
from fhir.resources.R4B.codesystem import CodeSystem as CodeSystemSchema
from pop.terminology.digestors import DIGESTORS, TerminologyDigestor, NCITDigestor
from pop.terminology.utils import CodedConcept, get_file_location, parent_to_children
from pop.terminology.resolver import resolve_canonical_url
from enum import Enum
from typing import List
from tqdm import tqdm 

# Generate absolute path to artifacts folder
from pop.settings import BASE_DIR
artifacts_path = os.path.join(BASE_DIR, 'pop/apps/valuesets/artifacts/')

# Load environmental variables
env = environ.Env()
environ.Env.read_env('.env', overwrite=True)

# Custom function to print with color
def printRed(skk): print("\033[91m {}\033[00m" .format(skk))
def printGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def printYellow(skk): print("\033[93m {}\033[00m" .format(skk))



class FilterOperator(str, Enum):
    EQUALS = "="
    IS_A = "is-a"
    DESCENDENT_OF = "descendent-of"
    IS_NOT_A = "is-not-a"
    REGEX = "regex"
    IN = "in"
    NOT_IN = "not-in"
    GENERALIZES = "generalizes"
    CHILD_OF = "child-of"
    DESCENDENT_LEAF = "descendent-leaf"
    EXISTS = "exists"



def request_api_endpoint_json(api_url, raw=False):
    """
    Make a GET request to an API endpoint, parse the JSON response, and return the parsed JSON data.

    Note:
        This function sets up the necessary configurations, including basic authentication,
        proxies, and certificate verification, to make a secure API request.
    """
    # Define the API endpoint basic authentication credentials
    if 'loinc.org' in api_url:
        api_username = env('LOINC_USER')
        api_password = env('LOINC_PASSWORD')
    elif 'nlm.nih.gov' in api_url:
        api_username = env('UMLS_API_USER')
        api_password = env('UMLS_API_KEY')
    else: 
        api_username, api_password = None, None

    # Define the path to the certificate bundle file
    certificate_bundle_path = env('CA_SSL_CERT_BUNDLE')

    # Create a session for making the request
    session = requests.Session()

    # Set up the proxy with authentication
    proxies = {
        'http': env('PROXY_HTTP'),
        'https': env('PROXY_HTTPS'),
    }
    session.proxies = proxies
    # Set up the basic authentication for the API
    if api_username and api_password:
        session.auth = (api_username, api_password)

    try:
        # Make a GET request to the API and parse the JSON response
        response = session.get(api_url, verify=certificate_bundle_path, proxies=proxies)

        # Check if there is an authorization issue
        if response.status_code == 401:
            # If authorization is required, the session cookies have now been set by the first request and a second request is necessary 
            response = session.get(api_url, verify=certificate_bundle_path, proxies=proxies)

        # Check for custom FHIR expansion response code
        if response.status_code == 422 and '$expand' in api_url:
            # If expansion operation is too costly, server will refuse, in that case, get non-expanded content definition
            response = session.get(api_url.replace('$expand',''), verify=certificate_bundle_path, proxies=proxies)

        # Check for unknown URL response code
        if response.status_code == 404 and 'mcode' in api_url.lower():
            # Certain mCODE valuesets use a different domain to serve the JSON representations
            response = session.get(api_url.replace("build.fhir.org/ig/HL7/fhir-mCODE-ig/", "hl7.org/fhir/us/mcode/"), verify=certificate_bundle_path, proxies=proxies)
            
        if response.status_code == 200:
            # Successfully connected to the API
            if raw:
                return response.text
            json_response = response.json()  # Parse JSON response
            # Now you can work with the JSON data
            return json_response
        else:
            print(f"Request failed with status code: {response.status_code}")
            response.raise_for_status()
            
    except requests.exceptions.RequestException as e:
        printRed(f"\rNETWORK ERROR:\n{e}\n")

def download_canonical_url(canonical_url: str) -> str:
    if not canonical_url.endswith('.json'):
        # Parse the API endpoint based on the canonical URL
        download_url =  resolve_canonical_url(canonical_url)
    else:
        download_url = canonical_url
    # Download the structure definition
    return request_api_endpoint_json(download_url)
   

@cachetools.func.lru_cache(maxsize=128)
def download_codesystem(canonical_url) -> List[CodedConcept]:
    digestor = next((digestor for digestor in DIGESTORS if digestor.CANONICAL_URL == canonical_url or canonical_url in digestor.OTHER_URLS), None)
    if digestor:
        print(f'• Digesting code system: {canonical_url}')
        concepts = digestor().digest()        
        print(f'✓ Digestion complete and added to cache')
    else:
        print(f'• Downloading code system: {canonical_url}')
        codesystem_json = download_canonical_url(canonical_url)
        # Parse the code system FHIR structure 
        codesystem = CodeSystemSchema.parse_obj(codesystem_json)
        # Add concepts in the code system
        concepts = { 
            concept.code:
                CodedConcept(
                    code=concept.code, 
                    display=concept.display, 
                    system=codesystem.url, 
                    version=codesystem.version, 
                    definition=concept.definition,
                    synonyms=[designation.value for designation in concept.designation or []],
                    parent=next((prop.valueCode for prop in concept.property or [] if prop.code == 'subsumedBy'),None)
                ) for concept in codesystem.concept or []
        }
    return concepts

def download_valueset(canonical_url: str) -> List[CodedConcept]:   
    print(f'Downloading ValueSet definition content...')
    valueset_json = download_canonical_url(canonical_url)
    # Parse the response
    valuesetdef = ValueSetSchema.parse_obj(valueset_json)
    print(f'Expanding ValueSet <{valuesetdef.name}>...')
    # Expand the valueset definition
    return expand_valueset(valuesetdef)

def expand_valueset(valuesetdef: ValueSetSchema) -> List[CodedConcept]:
    """
    Reference
    ---------
    [1] Value Set Expansion, HL7 FHIR R5 Documentation, https://hl7.org/fhir/valueset.html#expansion
    """
    concepts = []
    # If the value set already has an expansion (e.g., a stored expansion)
    if valuesetdef.expansion and valuesetdef.expansion.contains:
        for concept in valuesetdef.expansion.contains:
            concepts.append(
                CodedConcept(code=concept.code, system=concept.system, version=concept.version)
            )
    # If the value set already has an expansion (e.g., a stored expansion)
    elif valuesetdef.compose and valuesetdef.compose.include:
        for inclusion_criteria in valuesetdef.compose.include:
            concepts.extend(
                follow_valueset_composition_rule(inclusion_criteria)
            )
    else:
        raise ValueError('The valueset definition has neither a composition (compose.include) nor expansion (compose.exclude)')
    
    # For each compose.exclude, follow the same process as for compose.include, but remove codes from the expansion in step 3 instead of adding them.
    if valuesetdef.compose and valuesetdef.compose.exclude:
        for exclusion_criteria in valuesetdef.compose.exclude:
            for excluded_concept in follow_valueset_composition_rule(exclusion_criteria):
                if excluded_concept in concepts:
                    concepts.remove(excluded_concept)
    
    return concepts


def follow_valueset_composition_rule(rule: ValueSetComposeInclude) -> List[CodedConcept]:
    """Include one or more codes from a code system or other value set(s)"""
    system_concepts = []
    # (Step 1) If there is a system, identify the correct version of the code system
    if rule.system:
        codesystem = download_codesystem(rule.system)
        # If there are no codes or filters, add every code in the code system to the result set.
        if not rule.concept and not rule.filter:
            system_concepts.extend(codesystem.values())
        else:
            # If codes are listed, check that they are valid, and check their active status, and if ok, add them to the result set
            if rule.concept:
                system_concepts.extend([
                    codesystem.get(concept.code) for concept in rule.concept
                ])
            # If any filters are present, process them in order (as explained above), and add the intersection of their results to the result set.
            if rule.filter:
                for rule_filter in rule.filter:
                    if rule_filter.op in [FilterOperator.IS_A, FilterOperator.DESCENDENT_OF]:
                        parent = codesystem[rule_filter.value]
                        if rule_filter.op == FilterOperator.IS_A:
                            system_concepts.append(parent)
                        def add_children_recursively(parent):
                            for child in parent_to_children(codesystem).get(parent.code, []):
                                system_concepts.append(child)
                                add_children_recursively(child)
                        add_children_recursively(parent)
                        
    # (Step 2) For each valueSet, find the referenced value set by ValueSet.url, expand that to produce a collection of result sets.
    valueset_concepts = []
    if rule.valueSet:
        for n,canonical_url in enumerate(rule.valueSet): 
            # Download and collect the referenced valueset's concepts
            referenced_valueset_concepts = download_valueset(canonical_url)             
            # Add the intersection of the result set if multiple valuesets are referenced
            if n>0:
                valueset_concepts = list(set(valueset_concepts) & set(referenced_valueset_concepts))
            else: 
                valueset_concepts = list(set(referenced_valueset_concepts))

    # Add the intersection of the result set from the system (step 1) and all of the result sets from the value sets (step 2) to the expansion
    if system_concepts and valueset_concepts:
        return list(set(system_concepts) & set(valueset_concepts))
    elif system_concepts:
        return system_concepts
    else: 
        return valueset_concepts

class ValueSetComposer(object):

    def __init__(self, model, skip_existing=False, force_reset=False, prune_dangling=False, concepts_limit=None, debug_mode=False):
        self.concepts = []
        self.tree = []
        self.blacklist = []        
        self.model = model
        self.skip_existing = skip_existing
        self.force_reset = force_reset 
        self.prune_dangling = prune_dangling
        self.concepts_limit = concepts_limit or 999999999999
        self.debug_mode = debug_mode



    def expand_AntineoplasticAgent_with_NCTPOT_mappings(self):

        class NCTPOTDrugToClassDigestor(TerminologyDigestor):
            LABEL = 'nctpot'
            FILENAME = 'nctpot_drug_drugclass.tsv'
            def _digest_concept_row(self, row):
                self.concepts[row['id_drugClass']] = row['id_drug']

        class NCTPOTClassesDigestor(TerminologyDigestor):
            LABEL = 'nctpot'
            FILENAME = 'nctpot_drugclass.tsv'
            THERAPY_DISPLAY_LABELS = {
                'pi3k-akt-mtor': 'PI3K/AKT/mTOR pathway inhibitors',
                'tk': 'TK inhibitors',
                'DNA damage repair': 'DNA damage repair inhibitors',
                'developmental pathway': 'Developmental pathway inhibitors',
                'immune response': 'Immunotherapy',
                'cell cycle': 'Cell cycle inhibitors',
                'other function': 'Others',
                'epigenetic modulation': 'Epigenetic modulators',
                'metabolic control': 'Metabolic therapy',
                'targeted immune-mediated ablation': 'Targeted immunomediated ablation therapy',
                'BiTE': 'BiTE',
                'CAR-T': 'CAR-T',
                'targeted irradiation': 'Targeted radiopharmaceutics',
                'targeted immune pathway activation': 'Targeted immunoactivation',
                'targeted apoptose': 'Targeted apoptosis modulators',
                'targeted chemo': 'Targeted chemotherapy',
                'targeted radio-labelling': 'Targeted radioa-labeling',
                'chemo': 'Chemotherapy',
            }
            def _digest_concept_row(self, row):
                self.concepts[row['id']] = {
                    'name': row['name'],
                    'domain': row['domain'].replace('(anti)','(Anti)'),
                    'therapy': self.THERAPY_DISPLAY_LABELS.get(row['basket']),
                    'targetFamily': row['targetFamily'],
                    'chemical': row['chemStructure'],
                }                     

        class NCTPOTDrugsDigestor(TerminologyDigestor):
            LABEL = 'nctpot'
            FILENAME = 'nctpot_drug.tsv'
            def _digest_concept_row(self, row):
                self.concepts[row['id@ncit']] = {
                    'id': row['id'],
                    'name': row['name'],
                    'synonyms': row['synonyms'].split('#'),
                }

        def _get_drug_terminology_mappings(drug_name):
            # Get RxNorm code
            data = request_api_endpoint_json(f'https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}')
            rxnorm_code = data['idGroup'].get('rxnormId',[None])[0]
            if rxnorm_code:
                # Get ATC code through the RxNorm API
                data = request_api_endpoint_json(f'https://rxnav.nlm.nih.gov/REST/rxcui/{rxnorm_code}/property.json?propName=ATC')
                atc_code = data['propConceptGroup']['propConcept'][-1]['propValue'] if data else None
                # Get SNOMED CT code through the RxNorm API
                data = request_api_endpoint_json(f'https://rxnav.nlm.nih.gov/REST/rxcui/{rxnorm_code}/property.json?propName=SNOMEDCT')
                snomed_code = data['propConceptGroup']['propConcept'][-1]['propValue'] if data else None 
            else:
                atc_code, snomed_code = None, None
            return rxnorm_code, atc_code, snomed_code

        def _add_concept_with_NCTPOT_properties(concept):
            # Get NCT-POT classification if available
            nctpot_drug = nctpot_drugs.get(concept.code, {})
            nctpot_drug_class_id = nctpot_map.get(nctpot_drug.get('id'))
            nctpot_drug_class = nctpot_drug_classes.get(nctpot_drug_class_id, {})
            # Get RxNorm, ATC and SNOMED CT codes
            rxnorm_code, atc_code, snomed_code = _get_drug_terminology_mappings(concept.display)
            # Compose concept
            concepts[concept.code] = CodedConcept(
                code = concept.code,
                display = concept.display,
                system = concept.system,
                version = concept.version,
                parent = concept.parent,
                synonyms = concept.synonyms + nctpot_drug.get('synonyms', []),
                drugCategory = nctpot_drug_class.get('name'),
                drugDomain = nctpot_drug_class.get('domain'), 
                therapyCategory = nctpot_drug_class.get('therapy'), 
                atc = atc_code, 
                snomed = snomed_code, 
                rxnorm = rxnorm_code, 
            )

        def get_children_recursively(parent):
            for child in ncit_children[parent]:
                _add_concept_with_NCTPOT_properties(child)
                get_children_recursively(child)

        concepts = {}
        # Prepare the NCIT codesystem and its tree structre
        ncit_codesystem = download_codesystem(NCITDigestor.CANONICAL_URL)
        ncit_children = parent_to_children(ncit_codesystem)
        # Digest the NCTPOT maps
        nctpot_drugs = NCTPOTDrugsDigestor().digest()
        nctpot_map = NCTPOTDrugToClassDigestor().digest()
        nctpot_drug_classes = NCTPOTClassesDigestor().digest()
        # Add the concepts from the NCIT Antineoplastic agents tree
        ANTINEOPLASTIC_AGENTS_CODE = 'C274'
        get_children_recursively(ANTINEOPLASTIC_AGENTS_CODE)

        # Add other NCTPOT concepts not in the NCT Antineoplastic agents tree
        for ncit_code in nctpot_drugs.keys():
            # If drug has already been included or there is not associated NCIT code, skip it
            if ncit_code not in concepts and ncit_code in ncit_codesystem:
                concept = ncit_codesystem.get(ncit_code)
                _add_concept_with_NCTPOT_properties(concept)
        return concepts 
    

    def compose(self):
        """
        Synchronize valueset concepts with the database for a given model.

        This function synchronizes valueset concepts for a specified model by fetching and updating concept data. 
        It supports various valueset models and handles different synchronization scenarios based on the provided parameters.

        Args:
            model (django.db.models.Model): A Python class representing the valueset Django model to be synchronized.
            skip_existing (bool, optional): If True, skip synchronization for models with existing entries.
            force_reset (bool, optional): If True, delete all existing entries for the model before synchronization.

        Returns:
            None: The function performs database synchronization but does not return any values.

        Note:
            - The function supports various valueset models and handles each one differently based on the model's name.
            - It ensures that concepts in the valueset are unique and updates existing entries when necessary.
            - It also manages the tree structure for certain models and prints status messages for the synchronization process.
        """
        # Print title of current valueset being synchronized
        print(f'\n{self.model.__name__}\n-----------------------------------------------')
                
        # Reset all model entries if requested    
        if self.force_reset and not self.debug_mode:
            self.model.objects.all().delete()
            print(f"Removed all valueset entries")
        
        # Skip valuesets that already contain entries, if requested
        if self.skip_existing and self.model.objects.count()>0:
            printYellow(f'⬤  - Valueset <{self.model.__name__}> skipped as it already contains {self.model.objects.count()} entries (skip_existing - enabled).')
            return None 

        # Determine which valueset model to synchronize and compile concepts accordingly
        special_composer_function = {
            'AntineoplasticAgent': self.expand_AntineoplasticAgent_with_NCTPOT_mappings,
        }
        if self.model.__name__ in special_composer_function:
            special_composer_function[self.model.__name__]()
        else:
            if not getattr(self.model,'valueset', None) and not getattr(self.model,'codesystem', None):
                printYellow(f'⬤ - Skipping model <{self.model.__name__}> without an associated canonical URL. \t\t\t')
                return None           
            if getattr(self.model,'valueset', None):    
                self.concepts = download_valueset(self.model.valueset)
            else:
                self.concepts = download_codesystem(self.model.codesystem).values()
        print(f'\n✓ Collected a total of {len(self.concepts)} concepts.')
        new_concepts = []
        updated_concepts = []
        deleted_dangling_concepts = 0        
        # Check and update concepts in the database
        dangling_concepts = [concept.pk for concept in self.model.objects.all()]
        for concept in tqdm(self.concepts, total=len(self.concepts), desc='• Writing into database'):
            if not concept.display: continue
            instance, created = self.model.objects.update_or_create(
                code=concept.code, system=concept.system,
                defaults={
                    key: value for key, value in concept.model_dump().items() 
                        if key not in ['parent']
                },
            )
            if created:
                new_concepts.append(instance)
            else: 
                updated_concepts.append(instance)
                if instance.pk in dangling_concepts:
                    dangling_concepts.remove(instance.pk)

        # Update relationships
        for concept in tqdm(self.concepts, total=len(self.concepts), desc='• Updating relationships'):
            if concept.parent:
                child = self.model.objects.get(code=concept.code, system=concept.system)
                parent = self.model.objects.filter(code=concept.parent,system=concept.system).first()
                if parent:
                    child.parent = parent
                    child.save()
        print('✓ - All concepts written into the database')
        # Delete dangling concepts
        if self.concepts and dangling_concepts and self.prune_dangling:
            for concept_pk in dangling_concepts: 
                try: 
                    self.model.objects.get(pk=concept_pk).delete()
                    deleted_dangling_concepts += 1
                except:
                    printRed(f'❌ - Dangling concept <{concept.code} - {concept.display}> could not be deleted as it is referenced in the database by another object. \t\t\t')
        # Notify successful operation
        if len(new_concepts)>0:
            printGreen(f'✓ - Succesfully synchronized {len(new_concepts)} concepts in the <{self.model.__name__}> model table. \t\t\t')
        if deleted_dangling_concepts>0:
            printGreen(f'✓ - Succesfully deleted {deleted_dangling_concepts} dangling concepts in the <{self.model.__name__}> model table. \t\t\t')
        if len(updated_concepts)>0:
            printGreen(f'✓ - Succesfully updated {len(updated_concepts)} concepts in the <{self.model.__name__}> model table. \t\t\t')
        if len(dangling_concepts)>0 and not self.prune_dangling:
            printYellow(f'⬤ - Ignored {len(dangling_concepts)} dangling concepts already present in the <{self.model.__name__}> model table. \t\t\t')
        if (len(self.concepts) - len(new_concepts) - len(updated_concepts))>0:
            printYellow(f'⬤ - Ignored {len(self.concepts) - len(new_concepts)} collected concepts already present in the <{self.model.__name__}> model table. \t\t\t')
        if len(self.concepts)==0:
            printRed(f'❌ - Something went wrong. No concepts were found for this model. \t\t\t')
        return None
