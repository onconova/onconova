import cachetools
import json
import environ
import requests 
import sys 
import csv
import os 
import string
import cachetools.func
from datetime import datetime
import urllib
from collections import defaultdict
from fhir.resources.R4B.valueset import ValueSet as ValueSetSchema, ValueSetComposeInclude
from fhir.resources.R4B.codesystem import CodeSystem as CodeSystemSchema
from pop.terminology.digestors import DIGESTORS 
from pop.terminology.utils import CodedConcept 
from enum import Enum
from typing import List
from tqdm import tqdm 

# Generate absolute path to artifacts folder
from pop.settings import BASE_DIR
artifacts_path = os.path.join(BASE_DIR, 'pop/apps/valuesets/artifacts/')

_cache = {}

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

def find_in_tree(lst, key, value, in_check=False):
    """
    Find the index of a dictionary in a list based on a key-value pair.
    """
    return next(
        (i for i, dic in enumerate(lst) 
            if key in dic
            if (str(value) in str(dic[key]) 
            if in_check else dic[key] == value)
        )
    , None)

def parent_to_children(codesystem):
    """
    Preprocesses the codesystem to create a mapping from parent codes to their children.
    
    Args:
        codesystem (dict): A dictionary where each value is a concept with `code` and `parent` attributes.
    
    Returns:
        dict: A dictionary mapping parent codes to a list of their child concepts.
    """
    if id(codesystem) in _cache:
        return _cache[id(codesystem)]
    mapping = defaultdict(list)
    for concept in codesystem.values():
        mapping[concept.parent].append(concept)
    _cache[id(codesystem)] = mapping
    return mapping

def resolve_canonical_url_to_api_endpoint_url(canonical_url: str) -> str:

    def resolve_HL7_endpoint(canonical_url: str) -> str:
        RELEASE_VERSIONS = {
            'http://hl7.org/fhir/us/core': 'STU5.0.1',
            'http://hl7.org/fhir/us/vitals': 'STU1',
            'http://hl7.org/fhir/us/mcode': 'STU3',
            'http://hl7.org/fhir/uv/genomics-reporting': 'STU2',
            'http://hl7.org/fhir/': 'R4B',
            'http://terminology.hl7.org/': '',
        }
        for domain in RELEASE_VERSIONS:
            if canonical_url.startswith(domain):
                version = RELEASE_VERSIONS[domain]
                if 'ValueSet' in canonical_url:
                    return canonical_url.replace('/ValueSet/',f'/{version}/ValueSet-') + '.json'
                elif 'CodeSystem' in canonical_url :
                    return canonical_url.replace('/CodeSystem/',f'/{version}/CodeSystem-') + '.json'
                else:
                    return canonical_url.replace('http://hl7.org/fhir/',f'http://hl7.org/fhir/{version}/codesystem-') + '.json'
        else:
            raise KeyError(f'Unknown FHIR/HL7 resource requested in canonical URL: {canonical_url}')
    def resolve_LOINC_endpoint(canonical_url: str) -> str:
        valueset_name = canonical_url.replace('http://','https://').replace('https://loinc.org/','').replace('/','')  
        return f'http://fhir.loinc.org/ValueSet/$expand?url=http://loinc.org/vs/{valueset_name}&_format=json'

    def resolve_VSAC_endpoint(canonical_url: str) -> str:
        valueset_name = canonical_url.replace('https://vsac.nlm.nih.gov/valueset/','').split('/')[0]
        return f'https://cts.nlm.nih.gov/fhir/res/ValueSet/{valueset_name}/$expand?_format=json'

    def resolve_CTS_endpoint(canonical_url: str) -> str:
        return f'{canonical_url}/$expand?_format=json'

    def resolve_Simplifier_endpoint(canonical_url: str) -> str:
        valueset_name = canonical_url.replace('https://simplifier.net/pop','').replace('ValueSets/','',).replace('CodeSystems/','',)
        return f'https://simplifier.net/pop/{valueset_name}/$download?format=json'
        
    # Validate the input canonical_url
    if not urllib.parse.urlparse(canonical_url).scheme:
        raise ValueError("Invalid URL: " + canonical_url)

    url_resolvers = {
        'loinc.org': resolve_LOINC_endpoint,
        'hl7.org': resolve_HL7_endpoint,
        'vsac.nlm.nih.gov': resolve_VSAC_endpoint,
        'cts.nlm.nih.gov': resolve_CTS_endpoint,
        'simplifier.net/pop': resolve_Simplifier_endpoint,
    }
    
    for url_domain, resolver in url_resolvers.items():
        if url_domain in canonical_url:
            return resolver(canonical_url)
    raise KeyError(f'Unknown resource requested in canonical URL: {canonical_url}')



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
        download_url =  resolve_canonical_url_to_api_endpoint_url(canonical_url)
    else:
        download_url = canonical_url
    # Download the structure definition
    return request_api_endpoint_json(download_url)
   

@cachetools.func.lru_cache(maxsize=128)
def download_codesystem(canonical_url) -> List[CodedConcept]:
    digestor = next((digestor for digestor in DIGESTORS if digestor.CANONICAL_URL == canonical_url or canonical_url in digestor.OTHER_URLS), None)
    if digestor:
        print(f'• Digesting code system: {canonical_url}')
        concepts, designations = digestor().digest()        
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

    def compile_CTCAE_concepts(self):
        """
        Compile CTCAE (Common Terminology Criteria for Adverse Events) concepts and tree structure from a CSV file.

        This function reads a CTCAE terminology CSV file, extracts concepts, and compiles relevant information 
        into a list of dictionaries. Each dictionary represents a CTCAE concept, containing its code, display name, 
        system, version, and grades.

        Additionally, the function constructs a tree structure representing the hierarchy of CTCAE concepts.

        Returns:
            tuple: A tuple containing two elements:
                1. list: A list of dictionaries representing CTCAE concepts.
                2. list: A tree structure representing the hierarchy of CTCAE concepts.

        Note:
            - The CSV file is expected to have specific column order and delimiter (';') as defined in the function.
            - The function assumes the first row of the CSV contains headers and skips it.
        """
        # Open the CTCAE terminology CSV file for reading
        with open(os.path.join(artifacts_path,'CTCAE/CTCAE.csv')) as file:
            # Increase the CSV field size limit to handle large values
            csv.field_size_limit(sys.maxsize)
            
            # Create a CSV reader
            reader = csv.reader(file, delimiter=';')
            
            with open(os.path.join(artifacts_path,'CTCAE/VERSION'), "r") as version_file:
                version = version_file.read().strip()
            
            # Iterate through rows in the CSV file
            for rowNumber, row in enumerate(reader):
                # Skip the first row (headers)
                if rowNumber == 0:
                    continue
                # Check that the limit of concepts has not been exceeded (for debuging and testing)
                if len(self.concepts) >= self.concepts_limit: return

                # Extract data from the current row
                code, category, display = row[0:3]
                CTCAE_grades = [grade if grade != ' -' else None for grade in row[3:8]]

                # Create a dictionary representing the CTCAE concept
                concept_dict = {
                    'code': code,
                    'display': display,
                    'system': 'http://terminology.hl7.org/CodeSystem/MDRAE',
                    'version': version,
                    'grade1': CTCAE_grades[0],
                    'grade2': CTCAE_grades[1],
                    'grade3': CTCAE_grades[2],
                    'grade4': CTCAE_grades[3],
                    'grade5': CTCAE_grades[4],
                }
                # Append the concept dictionary to the concepts list
                self.concepts.append(concept_dict)

                # Create a child tree node for the concept
                child_tree = {
                    'id': code,
                    'label': display,
                    'children': [],
                }

                # Find the index of the parent node in the tree structure
                tree_index = find_in_tree(self.tree, 'label', category)

                # If the parent node doesn't exist, create it
                if tree_index is None:
                    subtree = {
                        'id': category,
                        'label': category,
                        'children': [],
                    }            
                    self.tree.append(subtree)
                    tree_index = -1

                # Add the child node to the parent node in the tree structure
                self.tree[tree_index]['children'].append(child_tree)


    def compile_LOINC_TumorMarkerTest_concepts(self):
        """
        Compiles LOINC (Logical Observation Identifiers Names and Codes) Tumor Marker Test concepts
        based on a provided FHIR model's canonical URL.

        Args:
        - model: The FHIR model representing LOINC Tumor Marker Test concepts.

        Returns:
        - concepts: A list of compiled LOINC Tumor Marker Test concepts.
        - tree: A hierarchical tree structure for the concepts.

        This function compiles LOINC Tumor Marker Test concepts by querying and processing data from a remote source
        and organizes them into a hierarchical tree structure based on their components.

        The provided 'model' should represent LOINC Tumor Marker Test concepts and specify a canonical URL.
        """    
        SYSTEM = 'http://loinc.org'
        # Prepare the correct URL for HTTP requests based on the given URL
        api_url = resolve_canonical_url_to_api_endpoint_url(self.model.canonical_url)
        # Download the FHIR resource definition
        valueset_json = request_api_endpoint_json(api_url)
        valueset = ValueSet.parse_raw(json.dumps(valueset_json))
        
        # Include all codes collected in the mCODE TumorMarkerTestCodes valueset
        included_valueset_api_url = resolve_canonical_url_to_api_endpoint_url(valueset.compose.include[0].valueSet[0])
        included_valueset_json = request_api_endpoint_json(included_valueset_api_url)
        included_valuesetvalueset = ValueSet.parse_raw(json.dumps(included_valueset_json))
        codes = [concept.code for concept in included_valuesetvalueset.compose.include[0].concept]
        # Add the extended LOINC concepts    
        codes += [concept.code for concept in valueset.compose.include[1].concept]
        
        sample_lookup = {}
        type_lookup = {}
        for n,code in enumerate(codes):
            # Check that the limit of concepts has not been exceeded (for debuging and testing)
            if len(self.concepts) >= self.concepts_limit: return

            print(f'Compiling tumor marker test concepts {n+1}/{len(codes)}\t', end='\r')        

            api_endpoint = f'https://fhir.loinc.org/CodeSystem/$lookup?code={code}&system=http%3A%2F%2Floinc.org&_format=json'
            data = request_api_endpoint_json(api_endpoint)
            data = data['parameter']
            
            for parameter in data:
                if parameter['name']=='display': 
                    display = parameter['valueString']
                    break
            
            def search_LOINC_properties(property):
                for parameter in data:
                    if parameter['name']=='property': 
                        if parameter['part'][0]['valueCode'].lower()==property:
                            return parameter['part'][1]['valueCodedConcept']['display'], parameter['part'][1]['valueCodedConcept']['code']                   
                return None, None

            VERSION, _ = search_LOINC_properties('VersionLastChanged')
            analyte, _ = search_LOINC_properties('analyte')                
            analyte = analyte.replace(' & ',' and ')
            scale, _ = search_LOINC_properties('scale_typ')
            method, _ = search_LOINC_properties('method_typ')
            
            def lookup_LOINC_property_code(code, lookup):
                if code not in lookup:
                    api_endpoint = f'https://fhir.loinc.org/CodeSystem/$lookup?system=http://loinc.org&code={code}'
                    sub_data = request_api_endpoint_json(api_endpoint)
                    display = sub_data['parameter'][-1]['part'][-1]['valueString']
                    lookup[code] = display
                    return display, lookup
                else:
                    return lookup[code], lookup
                
            _, type_code = search_LOINC_properties('property')   
            type, type_lookup = lookup_LOINC_property_code(type_code, type_lookup)
               
            _, sample_code = search_LOINC_properties('system')
            sample, sample_lookup = lookup_LOINC_property_code(sample_code, sample_lookup)
            self.concepts.append({
                'code': code,
                'display': display,
                'system': SYSTEM,
                'version': None,
                'analyte': analyte,
                'sample': sample,
                'method': method if method else 'Unspecified',
                'type': type,
            })
        
        # Add non-loinc concepts 
        NCI_tests_map = {
                'C157196': {
                    'analyte': 'Estrogen receptor',
                    'method': 'Immunohistochemistry',
                    'type': 'Number fraction',
                },
                'C157165': {
                    'analyte': 'Androgen receptor',
                    'method': 'Immunohistochemistry',
                    'type': 'Number fraction',
                },
                'C141458': {
                    'analyte': 'Progesterone receptor',
                    'method': 'Immunohistochemistry',
                    'type': 'Number fraction',
                },
                'C87051': {
                    'analyte': 'p16',
                    'method': 'Immunohistochemistry',
                    'type': 'Presence or threshold',
                },
                'C123557': {
                    'analyte': 'Ki67',
                    'method': 'Immunohistochemistry',
                    'type': 'Number fraction',
                },
                'C122807': {
                    'analyte': 'PD-L1',
                    'method': 'Immunohistochemistry',
                    'type': 'Number fraction',
                },
                'C185751': {
                    'analyte': 'HER2',
                    'method': 'Immunohistochemistry',
                    'type': 'Immunohistochemical category',
                },
                'C16152': {
                    'analyte': 'HER2',
                    'method': 'FISH',
                    'type': 'Presence or threshold',
                },
                'C165984': {
                    'analyte': 'SSTR2',
                    'method': 'Unspeficied',
                    'type': 'Number fraction',
                },
                'C159326': {
                    'analyte': 'HPV',
                    'method': 'PCR',
                    'type': 'Presence or threshold',
                },
                'C159327': {
                    'analyte': 'HPV',
                    'method': 'ISH',
                    'type': 'Presence or threshold',
                },
                'C166035': {
                    'analyte': 'Epstein Barr virus DNA',
                    'method': 'PCR',
                    'type': 'Presence or threshold',
                },
                'C138177': {
                    'analyte': 'Epstein Barr virus DNA',
                    'method': 'ISH',
                    'type': 'Presence or threshold',
                },
            }
        
        for concept in valueset.compose.include[2].concept:
            # Check that the limit of concepts has not been exceeded (for debuging and testing)
            if len(self.concepts) >= self.concepts_limit: return
                        
            code = concept.code
            self.concepts.append({
                'code': code,
                'display': concept.display,
                'system': valueset.compose.include[2].system,
                'version': valueset.compose.include[2].version,
                'analyte': NCI_tests_map[code]['analyte'],
                'sample': 'Blood or Tissue',
                'method': NCI_tests_map[code]['method'],
                'type': NCI_tests_map[code]['type'],
                'scale': None,
            })
            


    def compile_NCIT_drugs(self):
        """
        Compiles NCIT (National Cancer Institute Thesaurus) drugs data by mapping them to NCT-POT (National Cancer Trials Potentials) concepts.

        System Requirements:
            - Requires internet access for API requests.

        Example:
            To compile NCIT drugs data:
            ```
            compiler = DrugCompiler()
            compiled_drugs = compiler.compile_NCIT_drugs()
            ```

        """
        SYSTEM = 'http://ncithesaurus-stage.nci.nih.gov'
        VERSION = datetime.now().strftime("%d%m%Y")

        THERAPY_CLASS_LABEL_TO_DISPLAY = {
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

        
        # Create map of NCT-POT drug codes to drug classification
        NCTPOT_Drugs_to_DrugClasses_file = 'pop/apps/valuesets/artifacts/NCT-POT/drugs/drug_drugClass.tsv'
        NCTPOT_Drugs_to_DrugClasses = {}
        with open(NCTPOT_Drugs_to_DrugClasses_file) as tsv:
            for n,line in enumerate(csv.reader(tsv, delimiter="\t")):
                if n==0: continue
                id_drugClass, id_drug = line
                NCTPOT_Drugs_to_DrugClasses[id_drug] = id_drugClass

        # Create dictionary of NCT-POT drug classes and other properties
        NCTPOT_DrugClasses_file = 'pop/apps/valuesets/artifacts/NCT-POT/drugs/drugClass.tsv'
        NCTPOT_DrugClasses = {}
        with open(NCTPOT_DrugClasses_file) as tsv:
            for n,line in enumerate(csv.reader(tsv, delimiter="\t")):
                if n==0: continue
                id_drugClass, drugClass, drugDomain, therapyClass = line[:4]
                drugDomain = drugDomain.replace('(anti)','(Anti)')
                NCTPOT_DrugClasses[id_drugClass] = {
                    'name': drugClass,
                    'domain': drugDomain,
                    'therapy': therapyClass,
                }                     

        # Create map of drug codes from NCIT to NCT-POT
        NCTPOT_Drugs_file = 'pop/apps/valuesets/artifacts/NCT-POT/drugs/drug.tsv'
        NCTPOT_Drugs = {}
        NCTPOT_DrugNames = {}
        with open(NCTPOT_Drugs_file) as tsv:
            for n,line in enumerate(csv.reader(tsv, delimiter="\t")):
                if n==0: continue                            
                drug_id = line[0]
                drug_name = line[3]
                NCIT_code = line[7]
                NCTPOT_Drugs[NCIT_code] = drug_id
                NCTPOT_DrugNames[NCIT_code] = drug_name
                


        def compile_concept_for_NCIT_drug(ncit_code, drug, parent_ncit_code=None):
                rxnorm_code, atc_code, snomed_code, NCTPOT_drug_class = None,None,None,{}
                if ncit_code in NCTPOT_Drugs:
                    # Get RxNorm code
                    data = request_api_endpoint_json(f'https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug}')
                    rxnorm_code = data['idGroup'].get('rxnormId',[None])[0]
                    if rxnorm_code:
                        # Get ATC code through the RxNorm API
                        data = request_api_endpoint_json(f'https://rxnav.nlm.nih.gov/REST/rxcui/{rxnorm_code}/property.json?propName=ATC')
                        atc_code = data['propConceptGroup']['propConcept'][-1]['propValue'] if data else None
                        # Get SNOMED CT code through the RxNorm API
                        data = request_api_endpoint_json(f'https://rxnav.nlm.nih.gov/REST/rxcui/{rxnorm_code}/property.json?propName=SNOMEDCT')
                        snomed_code = data['propConceptGroup']['propConcept'][-1]['propValue'] if data else None 

                    # Get NCT-POT classification if available
                    drug_id = NCTPOT_Drugs.get(ncit_code)
                    drug_class_id = NCTPOT_Drugs_to_DrugClasses.get(drug_id)
                    NCTPOT_drug_class = NCTPOT_DrugClasses.get(drug_class_id, {})

                # Compile concept
                concept_data = {
                    'code': ncit_code,
                    'display': drug,
                    'system': SYSTEM,
                    'version': VERSION,
                    'parent': parent_ncit_code,
                    'drugCategory': NCTPOT_drug_class.get('name'),
                    'drugDomain': NCTPOT_drug_class.get('domain'), 
                    'therapyCategory': THERAPY_CLASS_LABEL_TO_DISPLAY.get(NCTPOT_drug_class.get('therapy')), 
                    'atc': atc_code, 
                    'snomed': snomed_code, 
                    'rxnorm': rxnorm_code, 
                }   
                if concept_data not in self.concepts:
                    print(f'({len(self.concepts)+1}/~8515)  Adding NCIT concept: {ncit_code} ({drug if len(drug)<30 else drug[:30] + "..."}) \t\t\t\t\t\t\t\t\t\t', end='\r')

                return concept_data          

        def add_ncit_tree_children(parent_ncit_code, tree, include_subtrees=True):            

            ncit_parent_tree = request_api_endpoint_json(f'https://api-evsrest.nci.nih.gov/api/v1/concept/ncit/{parent_ncit_code}/children')        
            for concept in ncit_parent_tree:
                # Get NCIT code and display
                drug = concept['name']
                ncit_code = concept['code']
                if not concept['leaf'] and not include_subtrees:
                    continue
                
                # Compile concept
                concept_data = compile_concept_for_NCIT_drug(ncit_code, drug, parent_ncit_code)

                # Check that collection limit has not been exceeded, else return current state
                if len(self.concepts) >= self.concepts_limit: 
                    return tree
                
                # If concept has not been added to the list, add it
                if concept_data not in self.concepts:
                    self.concepts.append(concept_data)
                               
                # If requested, explore the full subtree for each child
                subtree = []
                if include_subtrees and not concept['leaf']:
                    subtree = add_ncit_tree_children(ncit_code, tree=subtree)

                # Append all children subtrees to current leaf
                tree.append({
                    'id': ncit_code,
                    'label': drug,
                    'children': subtree
                })
            return tree
        
        # Compile NCIT tree for concept C274 - Antineoplastic agents
        self.tree = add_ncit_tree_children('C274', tree=[])
        
        # Compile the concepts for other codes in the NCT-POT dictionary not included in the NCIT Antineoplastic agents tree
        others_subtrees = []
        for ncit_code in NCTPOT_Drugs.keys():
            existing_drugs = [concept['code'] for concept in self.concepts]
            # If drug has already been included or there is not associated NCIT code, skip it
            if not ncit_code or ncit_code in existing_drugs:
                continue 
            drug = NCTPOT_DrugNames[ncit_code]
            # Compile information about the drug 
            concept_data = compile_concept_for_NCIT_drug(ncit_code, drug)
            self.concepts.append(concept_data)
            others_subtrees.append({
                'id': ncit_code,
                'label': drug,
                'children': [],
            })
        # If there were additional concepts added, put them all under the 'Other' classification
        if len(others_subtrees)>0:
            self.tree.append({
                'id': 'C17649',
                'label': 'Other',
                'children': others_subtrees
            })


    def compile_ICD10_comorbidities_concepts(self):

        with open('pop/apps/valuesets/artifacts/ICD-10/icdo10_code_system.tsv') as tsv:
            for line in csv.reader(tsv, delimiter="\t"):
                code, display = line[0], line[1]
                if 'neoplasm' in display.lower() or '-' in code:
                    continue 
                if not code[-1].isnumeric():
                    family = code
                    self.tree.append({'id': family, 'label': display, 'children': []})
                    continue
                elif family=='II': # Neoplasms
                    continue

                if '.' in code:
                    self.tree[-1]['children'][-1]['children'].append({'id': code, 'label': display, 'children': None} )

                else: 
                    parent = code
                    self.tree[-1]['children'].append({'id': parent, 'label': display, 'children': []}) 


                self.concepts.append({
                    'code': code,
                    'display': display,
                    'system': 'http://hl7.org/fhir/sid/icd-10',
                    'version': '2.1.0',
                })


    def compile_OncoTree_concepts(self):
        SYSTEM = 'http://oncotree.mskcc.org/fhir/CodeSystem/snapshot'            
        VERSION = datetime.now().strftime("%d%m%Y")
        
        # Download tree via the OncoTree API
        api_url = 'https://oncotree.mskcc.org/api/tumorTypes/tree'
        oncotree = request_api_endpoint_json(api_url)

        def explore_oncotree(oncotree):
            # Add current oncotree code
            self.concepts.append({
                'code': oncotree['code'],
                'display': oncotree['name'],
                'level': oncotree['level'],
                'parent': oncotree['parent'],
                'tissue': oncotree['tissue'],
                'system': SYSTEM,
                'version': VERSION,
            })
            # And recursively add all its children
            for child in oncotree['children'].values():
                explore_oncotree(child)
        for tissue in oncotree['TISSUE']['children'].values():
            explore_oncotree(tissue)


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
            'CTCAETerms': self.compile_CTCAE_concepts,
            'TumorMarkerTestCodes': self.compile_LOINC_TumorMarkerTest_concepts,
            'AntineoplasticAgents': self.compile_NCIT_drugs,
            'OncoTreeCancerClassification': self.compile_OncoTree_concepts,
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
