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
from fhir.resources.R4B.valueset import ValueSet
from fhir.resources.R4B.codesystem import CodeSystem

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

def read_csv_file(file_path):
    with open(file_path) as file:
        csv.field_size_limit(sys.maxsize)
        reader = csv.reader(file)
        for row in reader:
            yield row


@cachetools.func.lru_cache(maxsize=1)
def load_SNOMED_database(reader=read_csv_file):
    """
    Loads the SNOMED terminology database and its relationships from CSV files.
    Reads the SNOMED-CT version from a text file and returns the loaded concepts, relationships, and version.
    """
    # Load SNOMED-CT concepts
    SNOMED_concepts = {}
    print('Loading SNOMED terminology...')
    for row in reader(os.path.join(artifacts_path, 'SNOMED-CT/SNOMED_terms.csv')):
        code, concept = row[:2]
        SNOMED_concepts[code] = concept
    print('Terminology loading complete')
    # Load SNOMED-CT parent-child relationships
    SNOMED_relationships = defaultdict(list)
    print('Loading SNOMED relationships...')
    for row in reader(os.path.join(artifacts_path, 'SNOMED-CT/SNOMED_is_a_relationships.csv')):
        child, parent = row[:2]
        SNOMED_relationships[parent].append(child)
    print('Relationships loading complete')
    # Load SNOMED-CT version
    with open(os.path.join(artifacts_path, 'SNOMED-CT/VERSION'), 'r') as version_file:
        SNOMED_version = version_file.read().strip()
    return SNOMED_concepts, SNOMED_relationships, SNOMED_version


def generate_SNOMED_CT_artifacts():  
    
    # Work directory
    path = os.path.join(artifacts_path,'SNOMED-CT/')
    
    # Search for a valid file    
    files = [i for i in os.listdir(path) if os.path.isfile(os.path.join(path,i)) and 'sct2_Description_Snapshot-en_INT' in i]
    if files:
        filename = files[0]
    else: 
        raise FileNotFoundError('There is no sct2_Description_Snapshot-en_INT_YYYYMMDD.txt file in the SNOMED-CT directory.')

    # Get SNOMED CT version from file name 
    version = filename.split('_')[-1].split('.')[0]
    # Generate a VERSION file containing the SNOMED-CT version        
    with open(path + 'VERSION', 'w') as f:
        f.write(f'http://snomed.info/sct/900000000000207008/version/{version}') 
    
    with open(path + filename) as file:
        csv.field_size_limit(sys.maxsize)
        print(f'Loading file {filename}...')
        reader = csv.reader(file, delimiter="\t")
        
        print(f'Reading SNOMED CT concepts...')
        # Go over the concepts in the file
        codes,terms = [],[]
        for n,row in enumerate(reader):
            type = row[6]
            synonym = '900000000000013009'
            if type == synonym:
                codes.append(row[4])
                terms.append(row[7])
                print(f'Concept added --> ({codes[-1]}) "{terms[-1]}"')

    print(f'Writing SNOMED CT concepts...')
    with open(path + 'SNOMED_terms.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(zip(codes, terms))

    # Search for a valid file    
    files = [i for i in os.listdir(path) if os.path.isfile(os.path.join(path,i)) and f'sct2_Relationship_Snapshot_INT_{version}' in i]
    if files:
        filename = files[0]
    else: 
        raise FileNotFoundError(f'The sct2_Relationship_Snapshot_INT_{version}.txt file cannot be found.')
    
    with open(path + filename) as file:
        csv.field_size_limit(sys.maxsize)
        print('Loading file...')
        reader = csv.reader(file, delimiter="\t")
        sources = []
        destinations = []
        for n,row in enumerate(reader):
            type = row[7]
            active = bool(row[2])
            is_a = '116680003'
            if active and type == is_a:
                sources.append(row[4]) 
                destinations.append(row[5])
                print(f'Relationship added --> ({sources[-1]})-({destinations[-1]})')
        print('Loaded')
        
    with open(path + 'SNOMED_is_a_relationships.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(zip(sources, destinations))        



def resolve_canonical_url_to_api_endpoint_url(canonical_url: str) -> str:
    """
    Convert a canonical FHIR valueset URL to an API endpoint URL for accessing FHIR ValueSets.

    This function takes a canonical URL and returns an API endpoint URL that can be used to access the
    corresponding FHIR ValueSet in JSON format.
    
    Note:
        The function supports different hosting platforms for FHIR ValueSets, including LOINC, mCODE,
        cts.nlm.nih.gov, hl7.org, and pop.org. It adjusts the URL as needed to fetch the JSON definition
        of the ValueSet.
    """    
    def handle_loinc_valuesets(canonical_url: str) -> str:
        valueset_name = canonical_url.replace('http://','https://').replace('https://loinc.org/','').replace('/','')  
        api_url = f'http://fhir.loinc.org/ValueSet/$expand?url=http://loinc.org/vs/{valueset_name}&_format=json'
        return api_url

    def handle_mcode_valuesets(canonical_url: str) -> str:
        return canonical_url.replace('/ValueSet/','/STU3/ValueSet-') + '.json'

    def handle_grig_valuesets(canonical_url: str) -> str:
        if 'ValueSet' in canonical_url:
            return canonical_url.replace('/ValueSet/','/STU2/ValueSet-') + '.json'
        elif 'CodeSystem' in canonical_url :
            return canonical_url.replace('/CodeSystem/','/STU2/CodeSystem-') + '.json'
        else:
            raise KeyError(f'Unknown FHIR/HL7 resource requested in canonical URL: {canonical_url}')

    def handle_uscore_valuesets(canonical_url: str) -> str:
        return canonical_url.replace('/ValueSet/','/ValueSet-') + '.json'

    def handle_vsac_valuesets(canonical_url: str) -> str:
        valueset_name = canonical_url.replace('https://vsac.nlm.nih.gov/valueset/','').split('/')[0]
        api_url = f'https://cts.nlm.nih.gov/fhir/res/ValueSet/{valueset_name}/$expand?_format=json'
        return api_url

    def handle_cts_valuesets(canonical_url: str) -> str:
        return canonical_url + '/$expand?_format=json'

    def handle_core_valuesets(canonical_url: str) -> str:
        if 'ValueSet' in canonical_url:
            valueset_name = canonical_url.split('ValueSet/')[-1]
            api_url = f'https://tx.fhir.org/r4/ValueSet/{valueset_name}/$expand?_format=json'
        elif 'CodeSystem' in canonical_url:
            codesystem_name = canonical_url.split('CodeSystem/')[-1]
            api_url = f'https://tx.fhir.org/r4/CodeSystem/{codesystem_name}?_format=json'
        elif canonical_url.startswith('http://hl7.org/fhir/'):
            codesystem_name = canonical_url.split('hl7.org/fhir/')[-1]
            api_url = f'https://tx.fhir.org/r4/CodeSystem/{codesystem_name}?_format=json'
        else:
            raise KeyError(f'Unknown FHIR/HL7 resource requested in canonical URL: {canonical_url}')
        
        return api_url

    def handle_custom_valuesets(canonical_url: str) -> str:
        valueset_name = canonical_url.replace('https','http').replace('http://pop.org/fhir/ValueSets/','',)
        api_url = f'https://simplifier.net/pop/{valueset_name}/$download?format=json'
        return api_url
        
    # Validate the input canonical_url
    if not urllib.parse.urlparse(canonical_url).scheme:
        raise ValueError("Invalid URL: " + canonical_url)

    url_mapping = {
        'loinc.org': handle_loinc_valuesets,
        'hl7.org/fhir/us/mcode/': handle_mcode_valuesets,
        'hl7.org/fhir/uv/genomics-reporting/': handle_grig_valuesets,
        'hl7.org/fhir/us/vitals/': handle_uscore_valuesets,
        'vsac.nlm.nih.gov': handle_vsac_valuesets,
        'cts.nlm.nih.gov': handle_cts_valuesets,
        'hl7.org': handle_core_valuesets,
        'pop.org': handle_custom_valuesets
    }
    
    for url_type, conversion_function in url_mapping.items():
        if url_type in canonical_url:
            return conversion_function(canonical_url)
    raise KeyError(f'Unknown FHIR/HL7 resource requested in canonical URL: {canonical_url}')



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

    def cannot_add_concept(self,code):
        limit_exceeded = len(self.concepts) >= self.concepts_limit
        code_already_present = len(self.concepts)>0 and code in [concept['code'] for concept in self.concepts]
        code_blacklisted = code in self.blacklist
        return limit_exceeded or code_already_present or code_blacklisted
    
    def can_add_concept(self, code):
        return not self.cannot_add_concept(code)
    
    def add_concept(self,code, display, system, version):
        if self.can_add_concept(code): 
            # Compile new concept and add it to the list=
            new_concept = {'code': code, 'display': display, 'system': system, 'version': version} 
            self.concepts.append(new_concept)                       

    def add_SNOMED_filtered_concepts(self, filter_by, operator, tree):
        """
        Add a concept to the concepts list and optionally to a tree structure.
        """
        # Check that the limit of concepts has not been exceeded (for debuging and testing)
        if self.cannot_add_concept(filter_by):
            return tree
        
        # Load SNOMED concepts and relationships database into memory
        SNOMED_concepts, SNOMED_relationships, SNOMED_version = load_SNOMED_database()
        
        # Lookup code in SNOMED terminology dictonary
        code = filter_by
        display = SNOMED_concepts.get(code)
        if not display:
            printYellow(f'SNOMED code {code} not found in current loaded terminology artifact.')
            return tree

        # For 'is-a' operator include the provided concept itself (include descendant codes and self)
        if operator == 'is-a':                
            self.add_concept(code, display, system='http://snomed.info/sct', version=SNOMED_version)
        
        # Update progress
        print(f'\t|-->Add all SNOMED concepts where "{operator}" code {code}... \t\t\t\t\t\t\t\t', end='\r')
        
        # Define the current subtree for this concept
        subtree = {"id": code, "label": display, "children": []}
        
        # Get all parent-child relationships that the current code has
        children_codes = SNOMED_relationships[code]
        # Add all child codes for the current concept recursively
        for child_code in children_codes:
            subtree['children'] = self.add_SNOMED_filtered_concepts(filter_by=child_code, operator='is-a', tree=subtree['children'])

        # Add the full-depth subtree to current branch
        if operator == 'is-a':
            tree.append(subtree)
        else:
            tree += subtree['children']
            
        return tree    
    

    def compose_valueset(self, include, tree, verb):
        """
        Expand the list of concepts and tree structure based on the extension JSON.
        """
        
        # A value set include/exclude SHALL have a value set or a system
        if include.valueSet:
            # If so, inlcude all of them iteratively
            for valueset_url in include.valueSet:
                # Parse API endpoint 
                api_url = resolve_canonical_url_to_api_endpoint_url(valueset_url)    
                # Download definition of valueset
                valueset_json = request_api_endpoint_json(api_url)
                valueset = ValueSet.parse_raw(json.dumps(valueset_json))    
                print(f'|--> {verb} valueset {valueset_url}')
                # If the sub-valueset has a composition definition, include it
                if valueset.compose and valueset.compose.include:
                    # Go through all the logical inclusion routes and include their content
                    for include_compose in valueset.compose.include:
                        tree = self.compose_valueset(include_compose, tree, verb)

        # A value set include/exclude cannot have have both 'concept' and 'filter'
        if include.filter:
            for include_filter in include.filter:
                if include_filter.op in ['is-a','descendent-of']:
                    # If dealing with SNOMED codes
                    if 'snomed' in include.system.lower():
                        tree = self.add_SNOMED_filtered_concepts(filter_by=include_filter.value, operator=include_filter.op, tree=tree)
        
        elif include.concept:
            for concept in include.concept:
                self.add_concept(concept.code, concept.display, include.system, include.version)
                
        if include.system and not include.valueSet and not include.filter and not include.concept:
            # If so, include the full code system
            codesystem_url = include.system
            # Parse the API endpoint based on the canonical URL
            api_url =  resolve_canonical_url_to_api_endpoint_url(codesystem_url)
            # Get the code system structure definition from the API endpoint
            codesystem_json = request_api_endpoint_json(api_url)
            # Parse the code system FHIR structure 
            if codesystem_json:
                codesystem = CodeSystem.parse_raw(json.dumps(codesystem_json))
                print(f'|--> {verb} code system {codesystem.name} ({codesystem.url})...')
                # Add concepts in the code system
                if codesystem.concept:
                    for concept in codesystem.concept:
                        self.add_concept(concept.code, concept.display, codesystem.url, codesystem.version)
                        
        return tree    
    
    
    def collect_valueset_concepts(self):
        """
        Compose the list of concepts and tree structure from a value set model.

        Args:
            model: The value set model.

        Returns:
            The list of concepts and the tree structure.
        """
        
        # Initialize tree
        tree = []

        # Get canonical URL of the valueset
        canonical_url = self.model.canonical_url

        # If there is no canonical URL, valueset is probably not bound
        if not canonical_url: return
        
        print(f'Downloading value set StructureDefinition content...')

        if '.json' in canonical_url:
            # Directly download the valueset definition
            valueset_json = request_api_endpoint_json(canonical_url)
        else:
            # Parse the API endpoint based on the canonical URL
            api_url =  resolve_canonical_url_to_api_endpoint_url(canonical_url)
            # Download the valueset definition
            valueset_json = request_api_endpoint_json(api_url)
            
        if valueset_json.get('resourceType') == 'ValueSet':
            # Parse FHIR valueset from JSON
            valueset = ValueSet.parse_raw(json.dumps(valueset_json))

            if valueset.compose:
                """
                A set of criteria that define the contents of the value set by including or 
                excluding codes selected from the specified code system(s) that the value set 
                draws from. This is also known as the Content Logical Definition (CLD).
                """
                # Check for 'exclude' instructions
                if valueset.compose.exclude:
                    print(f'Composing "excluded" concepts...')
                    # Exclude one or more codes from the value set based on code system filters and/or other value sets.
                    for compose_exclude in valueset.compose.exclude:
                        self.compose_valueset(compose_exclude, tree=None, verb='Excluding')
                    # Simplify to list of codes 
                    self.blacklist = [concept['code'] for concept in self.concepts]
                    # Empty the list of concepts                 
                    self.concepts = []
                # Check for 'include' instructions
                if valueset.compose.include:
                    print(f'Composing "included" concepts...')
                    # Include one or more codes from a code system or other value set(s).
                    for compose_include in valueset.compose.include:
                        tree = self.compose_valueset(compose_include, tree=tree, verb='Including')

            if valueset.expansion:
                """
                A value set can also be "expanded", where the value set is turned into a simple 
                collection of enumerated codes. This element holds the expansion, if it has been performed.
                """
                print(f'Composing "expanded" concepts...\n')
                for concept in valueset.expansion.contains:
                    # Get the codes that are contained in the value set expansion.
                    self.add_concept(concept.code, concept.display, concept.system, concept.version)

        elif valueset_json.get('resourceType') == 'CodeSystem':
            # Parse FHIR valueset from JSON
            codesystem = CodeSystem.parse_raw(json.dumps(valueset_json))
            # Add concepts in the code system
            if codesystem.concept:
                for concept in codesystem.concept:
                    self.add_concept(concept.code, concept.display, codesystem.url, codesystem.version)

        # Is the valueset has been extended manually, add those concepts
        if hasattr(self.model,'extension_concepts'):
            self.concepts += self.model.extension_concepts
            print(f'Add {len(self.model.extension_concepts)} extension concepts \t\t\t\t\t\t\t\t')    
        
        self.tree = tree


    def compile_HGNC_codes(self):
        """
        Downloads and compiles HGNC (HUGO Gene Nomenclature Committee) gene concepts from their API endpoint.

        Returns:
        - A list of gene concepts, each represented as a dictionary with the following attributes:
            - 'code': The HGNC gene identifier.
            - 'display': The gene symbol.
            - 'system': The system URL, always 'http://www.genenames.org'.
            - 'alias': A string containing aliases and gene symbol.
            - 'previous': A string containing previous gene symbols.
            - 'refseq': The RefSeq identifier or None.
            - 'chromosomeLocation': The chromosome location of the gene.
        - None for the tree structure, as this valueset doesn't have a hierarchical structure.

        This function downloads HGNC gene data from the HGNC API, processes it, and compiles a list of gene concepts
        based on the approved genes. The gene concepts are represented as dictionaries and returned as a list.

        The HGNC dataset is fetched from the HGNC API endpoint, and each row of data is processed to extract relevant
        information about genes, including gene symbol, aliases, previous symbols, RefSeq IDs, and chromosome location.
        Only approved genes are included in the resulting concepts list.

        Note:
        The download and processing of HGNC data may take some time due to the size of the dataset.
        """
        # Inform of progress
        print('Downloading HGNC database entries...')    
        
        # Download HGNC dataset from their API endpoint
        data = request_api_endpoint_json(raw=True, api_url='https://www.genenames.org/cgi-bin/download/custom?col=gd_hgnc_id&col=gd_app_sym&col=gd_app_name&col=gd_status&col=gd_prev_sym&col=gd_aliases&col=gd_pub_chrom_map&col=gd_pub_acc_ids&col=gd_pub_refseq_ids&status=Approved&status=Entry%20Withdrawn&hgnc_dbtag=on&order_by=gd_hgnc_id&format=text&submit=submit')

        # Generate alphabetical tree structure
        self.tree = [{'id': letter, 'label':letter, 'children': []} for letter in list(string.ascii_uppercase)]

        # Iterate through rows in the downloaded data
        for rowNumber, row in enumerate(data.splitlines()):
            # Skip the first row (headers)
            if rowNumber == 0:
                continue
            # Check that the limit of concepts has not been exceeded (for debuging and testing)
            if len(self.concepts) >= self.concepts_limit: return

            row = row.split('\t')

            # Extract data from the current row
            gene_id, gene_symbol = row[0], row[1]
            chromosome_location, aliases, previous, refseq = row[6], row[5], row[4], row[8]
            status = row[3]

            # Append the gene symbol to the aliases and format as needed
            aliases += f', {gene_symbol},'
            previous += f','
            if refseq == '':
                refseq = None

            # Check if the gene is approved
            if 'Approved' in status:
                # Create a dictionary representing the approved gene
                gene_dict = {
                    'code': gene_id,
                    'display': gene_symbol,
                    'system': 'http://www.genenames.org',
                    'alias': aliases,
                    'previous': previous,
                    'refseq': refseq,
                    'chromosomeLocation': chromosome_location,
                }
                # Add the gene dictionary to the concepts list
                self.concepts.append(gene_dict)
                
                # Add concept to alphabetical tree categorization
                subtree = {                
                    'id': gene_id,
                    'label': gene_symbol,
                    'children':[],
                }
                tree_index = find_in_tree(self.tree, 'id', gene_symbol[0].capitalize())
                self.tree[tree_index]['children'].append(subtree)
                
        # Inform that downlaod is complete, and that processing might take a moment
        print('Processing HGNC database entries...')    


    def compile_ICDO3_concepts(self):
        """
        Compile concepts for ICD-O-3 valuesets based on the specified model.

        This function compiles concepts for ICD-O-3 valuesets, including HistologyMorphologyBehavior, CancerBodyLocation,
        HistologyBehavior, and HistologyDifferentiation. It loads concept data from the appropriate artifacts file and 
        generates a tree structure for certain models.

        Args:
            model (type): A Python class representing the ICD-O-3 valueset model to be compiled.

        Returns:
            tuple: A tuple containing two elements:
                - A list of dictionaries representing the compiled concepts.
                - A tree structure for certain models (HistologyMorphologyBehavior).

        Raises:
            KeyError: If the specified model is not a valid ICD-O-3 valueset.

        Note:
            - The function reads concept data from different artifact files based on the model.
            - It generates a tree structure for the HistologyMorphologyBehavior model using morphology categories.
            - The concepts are compiled as dictionaries with code, display, system, and version attributes.
        """
        SYSTEM = 'http://terminology.hl7.org/CodeSystem/icd-o-3'   
        with open(os.path.join(artifacts_path,'ICD-O-3/VERSION'), 'r') as version_file:
            VERSION = version_file.read().strip()
        
        # Determine the appropriate artifact file based on the model
        if self.model.__name__=='HistologyMorphologyBehavior':
            artifact = 'ICD-O-3/Morphenglish.txt'
        elif self.model.__name__=='CancerBodyLocation':
            artifact = 'ICD-O-3/Topoenglish.txt'
        elif self.model.__name__=='HistologyBehavior':
            artifact = 'ICD-O-3/Morphology_behavior.csv'
        elif self.model.__name__=='HistologyDifferentiation':
            artifact = 'ICD-O-3/Morphology_differentiation.csv'
        else:
            raise KeyError(f'The <{self.model.__name__}> valueset is not a valid ICD-O-3 valueset.')
        # Generate full path
        artifact = os.path.join(artifacts_path, artifact)

        # Handle specific logic for the HistologyMorphologyBehavior model
        if self.model.__name__=='HistologyMorphologyBehavior':
            with open(os.path.join(artifacts_path,'ICD-O-3/Morphology_categories.csv')) as file:
                reader = list(csv.reader(file, delimiter=';'))
                for rowNumber, row in enumerate(reader):
                    # Skip first row
                    if rowNumber==0: continue
                    codeRange,category = list(row)
                    # Parse range of values
                    if '-' in codeRange:
                        codeRange = [int(val) for val in codeRange.split('-')]
                        codeRange = list(range(codeRange[0],codeRange[1]+1))
                    # Prepopulate the tree with non-coded categories of ICD-O-3 morphologies
                    self.tree.append({  
                        "id": codeRange,
                        "label": category,
                        "children": [],
                    })
        
        codes, displays = [],[]
        with open(artifact) as file:
            # Load file with codes and concepts
            csv.field_size_limit(sys.maxsize)
            reader = csv.reader(file, delimiter='\t' if '.txt' in artifact else ';')
            for row in reader:
                code, display = None,None

                if 'Morphenglish' in artifact:
                    entry_type = row[1]
                    if entry_type=='title':
                        code = row[0].split('\n')[0]
                        display =  row[2].replace('"','')

                elif 'Topoenglish' in artifact:
                    entry_type = row[1]     
                    if entry_type in ['3','4']:
                        code = row[0]
                        display =  row[2].title()

                else:
                    code = row[0]
                    display =  row[1]
                
                if code and display:
                    codes.append(code)
                    displays.append(display)

        if 'Morphenglish' in artifact:
            for morphology_code in [code.split('/')[0] for code in codes]:
                behavior_codes = {
                    '/0': ', benign',
                    '/1': ', uncertain whether benign or malignant',
                    '/2': ', in situ',
                    '/3': ', primary',
                    '/6': ', metastatic',
                    '/9': ', uncertain whether primary or metastatic',
                }
                base_display = displays[codes.index([morphology_code+b for b in behavior_codes.keys() if morphology_code+b in codes][0])]
                for behavior in behavior_codes.keys():
                    matrix_code = morphology_code + behavior
                    if matrix_code not in codes:
                        nos = ', NOS' if ', NOS' in base_display else ''
                        matrix_display = base_display.replace(', benign','').replace(', malignant','') + behavior_codes[behavior]
                        displays.append(matrix_display)
                        codes.append(matrix_code)
                    else:
                        base_display = displays[codes.index(matrix_code)]

        for code, display in zip(codes, displays):
            # Check that the limit of concepts has not been exceeded (for debuging and testing)
            if len(self.concepts) >= self.concepts_limit: return

            self.concepts.append({
                'code': code,
                'display': display,
                'system': SYSTEM,
                'version': VERSION,
            })                
                    
            subtree = {  
                "id": code,
                "label": display,
                "children": [],
            }
            
            if 'Morphenglish' in artifact:
                tree_index = find_in_tree(self.tree, 'id', code[:3], in_check=True)
                self.tree[tree_index]['children'].append(subtree)

            elif 'Topoenglish' in artifact:
                if '.' in code:
                    tree_index = find_in_tree(self.tree, 'id', code.split('.')[0], in_check=True)                        
                    self.tree[tree_index]['children'].append(subtree)
                else:
                    self.tree.append(subtree)
            else:                     
                self.tree.append(subtree)
    

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
                            return parameter['part'][1]['valueCoding']['display'], parameter['part'][1]['valueCoding']['code']                   
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
            
    def compile_RxNorm_concepts(self):
        """
        Compile RxNorm concepts and tree structure from a JSON file.

        This function reads a JSON file containing RxNorm class tree data, extracts concepts, and constructs a tree 
        structure representing the hierarchy of RxNorm concepts.

        Returns:
            tuple: A tuple containing two elements:
                1. list: A list of dictionaries representing RxNorm concepts.
                2. list: A tree structure representing the hierarchy of RxNorm concepts.

        Note:
            - The JSON file structure is expected to have specific keys, as defined in the function.
        """
        # RxNorm HL7 Standards (Source: https://terminology.hl7.org/RxNorm.html)
        SYSTEM = 'http://www.nlm.nih.gov/research/umls/rxnorm'
        VERSION = datetime.now().strftime("%d%m%Y")

        NCTPOT_DrugClasses_file = 'pop/apps/valuesets/artifacts/NCT-POT/drugs/drugClass.tsv'
        NCTPOT_Drugs_file = 'pop/apps/valuesets/artifacts/NCT-POT/drugs/drug.tsv'
        NCTPOT_Drugs_to_DrugClasses_file = 'pop/apps/valuesets/artifacts/NCT-POT/drugs/drug_drugClass.tsv'
        NCTPOT_DrugClasses = {}
        NCTPOT_Drugs_to_DrugClasses = {}
        NCTPOT_Drugs = {}
        with open(NCTPOT_Drugs_to_DrugClasses_file) as tsv:
            for n,line in enumerate(csv.reader(tsv, delimiter="\t")):
                if n==0: continue
                id_drugClass, id_drug = line
                NCTPOT_Drugs_to_DrugClasses[id_drug] = {
                    'id_drugClass': id_drugClass,
                }
        with open(NCTPOT_Drugs_file) as tsv:
            for n,line in enumerate(csv.reader(tsv, delimiter="\t")):
                if n==0: continue
                id_drug, _, _, name = line[:4]
                if id_drug in NCTPOT_Drugs_to_DrugClasses:
                    NCTPOT_Drugs[name] = {
                        'id_drugClass': NCTPOT_Drugs_to_DrugClasses[id_drug]['id_drugClass'],
                    }
        with open(NCTPOT_DrugClasses_file) as tsv:
            for n,line in enumerate(csv.reader(tsv, delimiter="\t")):
                if n==0: continue
                id_drugClass, drugClass, _, therapyClass = line[:4]
                NCTPOT_DrugClasses[id_drugClass] = {
                    'name': drugClass,
                    'therapy': therapyClass,
                }
        
        # Download RxNorm class tree via UMLS API
        api_url = 'https://rxnav.nlm.nih.gov/REST/rxclass/classTree.json?classId=0'
        rxnorm_tree = request_api_endpoint_json(api_url)

        # Skip the first level of the class tree
        rxnorm_tree = rxnorm_tree['rxclassTree'][0]['rxclassTree']       

        def add_RxNorm_subtree(concepts, tree, RxNormSubTree):
            """
            Recursively add RxNorm subtrees to the tree structure and concepts list.

            Args:
                concepts (list): A list of dictionaries representing RxNorm concepts.
                tree (list): A tree structure representing the hierarchy of RxNorm concepts.
                RxNormSubTree (dict): A dictionary representing an RxNorm subtree.

            Returns:
                tuple: A tuple containing two elements:
                    1. list: The updated list of dictionaries representing RxNorm concepts.
                    2. list: The updated tree structure.
            """
            classId = RxNormSubTree['rxclassMinConceptItem']['classId']
            classDisplay = RxNormSubTree['rxclassMinConceptItem']['className'].title()
            subtree = {
                "id": classId,
                "label": classDisplay,
                "children": [],
            }
            concepts.append({
                'code': classId,
                'display': classDisplay,
                'system': SYSTEM,
                'version': VERSION,
            })
            if 'rxclassTree' in RxNormSubTree:
                for RxNormSubSubTree in RxNormSubTree['rxclassTree']:
                    if len(concepts) >= self.concepts_limit: break
                    concepts, subtree['children'] = add_RxNorm_subtree(concepts, subtree['children'], RxNormSubSubTree)
            else:
                data = request_api_endpoint_json(f'https://rxnav.nlm.nih.gov/REST/rxclass/classMembers.json?classId={subtree["id"]}&relaSource=ATC')
                if 'drugMemberGroup' in data:
                    for drug in data['drugMemberGroup']['drugMember']:
                        if len(concepts) >= self.concepts_limit: break
                        # Get concept code and display
                        code = drug['minConcept']['rxcui']
                        display = drug['minConcept']['name'].title()
                        
                        # Get the oncological drug classification if available
                        drug_class = NCTPOT_DrugClasses.get(NCTPOT_Drugs.get(display,{}).get('id_drugClass'),{})
                        
                        # Add concept to list and tree
                        subtree['children'].append({
                            "id": code,
                            "label": display,
                            "children": [],
                        })
                        concepts.append({
                            'code': code,
                            'display': display,
                            'system': SYSTEM,
                            'version': VERSION,
                            'drugCategory': drug_class.get('name'),
                            'therapyCategory': drug_class.get('therapy'), 
                        })
                            
            # Add the full-depth subtree to the current branch
            tree.append(subtree)
            return concepts, tree

        for RxNormSubTree in rxnorm_tree:
            # Check that the limit of concepts has not been exceeded (for debuging and testing)
            if len(self.concepts) >= self.concepts_limit: 
                return
            self.concepts, self.tree = add_RxNorm_subtree(self.concepts, self.tree, RxNormSubTree)



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
            
        

    def compile_HumanSpecimenTypes_concepts(self):
        """
        Compile USZ (University Hospital Zurich) specimen types concepts from a CSV file.

        This function reads a CSV file containing USZ specimen types data, extracts concepts, and compiles relevant 
        information into a list of dictionaries. Each dictionary represents a specimen type concept, containing its 
        code, display name, system, version (None in this case), and PathoProCode.

        Returns:
            tuple: A tuple containing two elements:
                1. list: A list of dictionaries representing USZ specimen types concepts.
                2. None: The function does not return a tree structure; therefore, this element is always None.
        
        Note:
            - The CSV file is expected to have specific column order and delimiter (';') as defined in the function.
        """

        self.collect_valueset_concepts()

        # Load PathoPro SNOMED Terminology from the CSV file
        with open(os.path.join(artifacts_path,'PathoPro/PathoPro_Pcodes_SNOMED_CT_map.csv')) as file:
            reader = csv.reader(file, delimiter=';')
            
            # Iterate through rows in the CSV file
            for row in reader:
                # Check that the limit of concepts has not been exceeded (for debuging and testing)
                if len(self.concepts) >= self.concepts_limit: return

                self.concepts.append({
                    'code': row[3],
                    'display': row[2],
                    'system': 'http://snomed.info/sct',
                    'version': None,  # No specific version for SNOMED CT
                    'PathoProCode': row[0]
                })



    def compile_USZ_specimenSites_concepts(self):
        """
        Compile USZ (University Hospital Zurich) specimen sites concepts from CSV and SNOMED CT data.

        This function reads a CSV file containing USZ specimen sites data and compiles relevant information into a list 
        of dictionaries. Each dictionary represents a specimen site concept, containing its code, display name, system, 
        version (None in this case), and PathoProCode.

        Additionally, the function adds predefined SNOMED CT specimen sites concepts to the list.

        Returns:
            tuple: A tuple containing two elements:
                1. list: A list of dictionaries representing USZ and SNOMED CT specimen sites concepts.
                2. None: The function does not return a tree structure; therefore, this element is always None.
        
        Note:
            - The CSV file is expected to have specific column order and delimiter (';') as defined in the function.
        """

        # Load USZ specimen sites data from a CSV file
        with open(os.path.join(artifacts_path,'PathoPro/PathoPro_Tcodes_SNOMED_CT_map.csv')) as file:
            reader = csv.reader(file, delimiter=';')
            
            # Iterate through rows in the CSV file
            for row in reader:
                # Check that the limit of concepts has not been exceeded (for debuging and testing)
                if len(self.concepts) > self.concepts_limit: return

                self.concepts.append({
                    'code': row[3],
                    'display': row[2],
                    'system': 'http://snomed.info/sct',
                    'version': None,  # No specific version for SNOMED CT
                    'PathoProCode': row[0]
                })

        # Load SNOMED CT Terminology
        SNOMED_concepts, _, version = load_SNOMED_database()

        # Predefined SNOMED CT specimen sites codes
        FMI_specimenSites = [40689003, 15425007, 3120008, 28231008, 72410000, 774007, 71252005, 30315005, 15776009, 64033007,
                            41216001, 76752008, 78961009, 421060004, 23451007, 34402009, 261665006, 13648007, 9875009, 87953007,
                            44567001, 87784001, 8911002, 39937001, 31435000, 45292006, 10200004, 56329008, 69695003, 82849001, 272673000,
                            71854001, 12738006, 400112001, 81745001, 15497006, 14016003, 87612001, 111002, 89837001, 80891009, 69748006,
                            76784001, 66754008, 76848001, 39607008, 385294005, 32849002, 35039007, 53505006, 59441001, 28273000]
        
        # Add predefined SNOMED CT specimen sites concepts to the list
        for snomed_code in FMI_specimenSites:
            if len(self.concepts) > self.concepts_limit: return
            if snomed_code in  SNOMED_concepts:
                snomed_term = SNOMED_concepts[snomed_code]
                self.concepts.append({
                    'code': snomed_code,
                    'display': snomed_term,
                    'system': 'http://snomed.info/sct',
                    'version': version,
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



    def compile_SO_concepts(self):
        """
        Compile Sequence Ontology (SO) concepts and tree structure based on a given model.

        This function retrieves SO concepts and constructs a tree structure representing the hierarchy of Sequence Ontology
        concepts based on the provided model. It also compiles relevant information into a list of dictionaries for each concept.

        Args:
            model (type): A Python class representing the Sequence Ontology model.

        Returns:
            tuple: A tuple containing two elements:
                1. list: A list of dictionaries representing Sequence Ontology concepts.
                2. list: A tree structure representing the hierarchy of Sequence Ontology concepts.

        Note:
            - The function fetches data from the Sequence Ontology website based on the provided model.
        """
        version = 'current_release'
        url_base = f"http://www.sequenceontology.org/browser/{version}/export/term_only/csv_text/"

        # Define the SO code for the provided model
        is_a_code = {
            'DNAChangeType': 'SO:0002072',
            'MolecularConsequence': 'SO:0001537',
            'FunctionalEffect': 'SO:0001536',
        }[self.model.__name__]
            
        

        def add_SO_subtree(concepts, tree, code): 
            """
            Recursively add Sequence Ontology subtrees to the tree structure and concepts list.

            Args:
                concepts (list): A list of dictionaries representing Sequence Ontology concepts.
                tree (list): A tree structure representing the hierarchy of Sequence Ontology concepts.
                code (str): The code of the current Sequence Ontology concept.

            Returns:
                tuple: A tuple containing two elements:
                    1. list: The updated list of dictionaries representing Sequence Ontology concepts.
                    2. list: The updated tree structure.
            """
            # Get tab-delimited data from SequenceOntology
            data = request_api_endpoint_json(url_base + code, raw=True)
            # Convert to list of rows
            data = list(csv.reader(data.splitlines(), delimiter='\t'))
            # Drop header
            data.pop(0)
            # Get list of columns of single row
            data = data[0]
            # Extract columns of interest
            code, display, children = data[0], data[1], data[4]
            # Parse the list of children        
            if children!='':
                children = children.split(',')
            else:
                children = []

            # Create subtree            
            subtree = {  
                "id": code,
                "label": display,
                "children": [],
            }
            
            concepts.append({
                'code': code,
                'display': display,
                'system': 'http://www.sequenceontology.org/',
                'version': version,
            })
            # Add children recursively
            for child in children:
                # Check that the limit of concepts has not been exceeded (for debuging and testing)
                if len(concepts) >= self.concepts_limit: return concepts, tree

                if child not in concepts:
                    print(f'\tDownloading concept {child} child from {code} \t\t\t\t\t\t\t\t', end='\r')        
                    concepts, subtree['children']  = add_SO_subtree(concepts, subtree['children'], child)

            # Add the full-depth subtree to current branch
            tree.append(subtree)        
                    
            return concepts, tree

        # Add all concepts that are children of main code
        self.concepts, self.tree = add_SO_subtree([], [], is_a_code)    
                


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
            'HGNC': self.compile_HGNC_codes,
            'HumanSpecimenType': self.compile_HumanSpecimenTypes_concepts,
            'CTCAETerms': self.compile_CTCAE_concepts,
            'TumorMarkerTestCodes': self.compile_LOINC_TumorMarkerTest_concepts,
            'MedicationClinicalDrugsIngredients': self.compile_RxNorm_concepts,
            'AntineoplasticAgents': self.compile_NCIT_drugs,
            'HumanSpecimenCollectionSite': self.compile_USZ_specimenSites_concepts,
            'HistologyMorphologyBehavior': self.compile_ICDO3_concepts,
            'CancerBodyLocation': self.compile_ICDO3_concepts,
            'HistologyBehavior': self.compile_ICDO3_concepts,
            'HistologyDifferentiation': self.compile_ICDO3_concepts,
            'MolecularConsequence': self.compile_SO_concepts,
            'ICD10Comorbidities': self.compile_ICD10_comorbidities_concepts,
            'FunctionalEffect': self.compile_SO_concepts,
            'DNAChangeType': self.compile_SO_concepts,
            'OncoTreeCancerClassification': self.compile_OncoTree_concepts,
        }
        if self.model.__name__ in special_composer_function:
            special_composer_function[self.model.__name__]()
        else:
            if not self.model.canonical_url:
                printYellow(f'⬤ - Skipping valueset <{self.model.__name__}> without an associated canonical URL. \t\t\t')
                return None            
            self.collect_valueset_concepts()
        print(f'\nCollected a total of {len(self.concepts)} concepts.')
        # Remove duplicate entries (valueset models must have unique entries)
        self.concepts = [
            dictionary for index, dictionary in enumerate(self.concepts)
            if dictionary not in self.concepts[index + 1:]
        ]
        
        print(f'\tProcessing concepts before database update... \t\t\t\t\t\t\t\t', end='\r')
        new_concepts = []
        updated_concepts = []
        deleted_dangling_concepts = 0        
        # Check and update concepts in the database
        dangling_concepts = list(self.model.objects.all())
        for concept in self.concepts:
            queried_concept = self.model.objects.filter(code=concept['code'])
            if queried_concept.exists():
                queried_concept = queried_concept.first()
                updated = False
                for attribute in concept.keys():
                    if getattr(queried_concept,attribute) != concept[attribute]:
                        setattr(queried_concept,attribute,concept[attribute])
                        updated = True
                if updated:
                    updated_concepts.append(queried_concept)
                if queried_concept in dangling_concepts:
                    dangling_concepts.remove(queried_concept)
            else:
                new_concepts.append(self.model(**concept))

        # Bulk create new concepts and bulk update updated concepts
        if new_concepts and not self.debug_mode:
            self.model.objects.bulk_create(new_concepts, ignore_conflicts=False)    
        if updated_concepts and not self.debug_mode:
            self.model.objects.bulk_update(updated_concepts, [key for key in self.concepts[0].keys() if key!='code'])    
        if self.concepts and dangling_concepts and self.prune_dangling and not self.debug_mode:
            for concept in dangling_concepts: 
                try: 
                    concept.delete()
                    deleted_dangling_concepts += 1
                except:
                    printRed(f'❌ - Dangling concept <{concept.code} - {concept.display}> could not be deleted as it is referenced in the database by another object. \t\t\t')
        # print('total_concepts', len(self.model.objects.all()))
        # print('new_concepts', len(new_concepts))
        # print('updated_concepts', len(updated_concepts))
        # print('dangling_concepts', len(dangling_concepts))
        # print('deleted_dangling_concepts', deleted_dangling_concepts)
        print(new_concepts)
        # Notify successful operation
        if len(new_concepts)>0:
            printGreen(f'✓ - Succesfully synchronized {len(new_concepts)} concepts in the <{self.model.__name__}> valueset table. \t\t\t')
        if deleted_dangling_concepts>0:
            printGreen(f'✓ - Succesfully deleted {deleted_dangling_concepts} dangling concepts in the <{self.model.__name__}> valueset table. \t\t\t')
        if len(updated_concepts)>0:
            printGreen(f'✓ - Succesfully updated {len(updated_concepts)} concepts in the <{self.model.__name__}> valueset table. \t\t\t')
        if len(dangling_concepts)>0 and not self.prune_dangling:
            printYellow(f'⬤ - Ignored {len(dangling_concepts)} dangling concepts already present in the <{self.model.__name__}> valueset table. \t\t\t')
        if (len(self.concepts) - len(new_concepts) - len(updated_concepts))>0:
            printYellow(f'⬤ - Ignored {len(self.concepts) - len(new_concepts)} collected concepts already present in the <{self.model.__name__}> valueset table. \t\t\t')
        if len(self.concepts)==0:
            printRed(f'❌ - Something went wrong. No concepts were found for this valueset. \t\t\t')
        return None
