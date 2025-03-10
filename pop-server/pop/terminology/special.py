from pop.terminology.digestors import TerminologyDigestor, NCITDigestor
from pop.terminology.utils import CodedConcept
from pop.terminology.utils import parent_to_children, request_http_get, ensure_within_string_limits
from typing import List, Optional

class DrugCodedConcept(CodedConcept):
    drug_category: Optional[str] = None
    drug_domain: Optional[str] = None
    therapy_category: Optional[str] = None 
    atc: Optional[str] = None
    snomed: Optional[str] = None
    rxnorm: Optional[str] = None
    drugbank: Optional[str] = None


class NCTPOTDrugToClassDigestor(TerminologyDigestor):
    """
    Digestor for mapping NCTPOT drug classes to drugs.
    
    Attributes:
        LABEL (str): Identifier for the digestor.
        FILENAME (str): Name of the file containing drug to drug class mappings.
    """
    LABEL = 'nctpot'
    FILENAME = 'nctpot_drug_drugclass.tsv'

    def _digest_concept_row(self, row: dict[str, str]) -> None:
        """
        Processes a single row of drug to drug class mapping.

        Args:
            row (dict): A dictionary representing a single row with keys 'id_drugClass' and 'id_drug'.
        """
        self.concepts[row['id_drug']] = row['id_drugClass']


class NCTPOTClassesDigestor(TerminologyDigestor):
    """
    Digestor for mapping NCTPOT drug classes to their attributes.

    Attributes:
        LABEL (str): Identifier for the digestor.
        FILENAME (str): Name of the file containing drug class mappings.
        THERAPY_DISPLAY_LABELS (dict): A mapping of therapy categories to display labels.
    """
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
        'targeted radio-labelling': 'Targeted radio-labeling',
        'chemo': 'Chemotherapy',
    }

    def _digest_concept_row(self, row: dict[str, str]) -> None:
        """
        Processes a single row of drug class mapping.

        Args:
            row (dict): A dictionary representing a single row with keys 'id', 'name', 'domain', 'basket', 'targetFamily', and 'chemStructure'.
        """
        self.concepts[row['id']] = {
            'name': row['name'],
            'domain': row['domain'].replace('(anti)', '(Anti)'),
            'therapy': self.THERAPY_DISPLAY_LABELS.get(row['basket']),
            'targetFamily': row['targetFamily'],
            'chemical': row['chemStructure'],
        }

class NCTPOTDrugsDigestor(TerminologyDigestor):
    """
    Digestor for processing NCTPOT drug information from a file.

    Attributes:
        LABEL (str): Identifier for the digestor.
        FILENAME (str): Name of the file containing drug information.
    """
    LABEL = 'nctpot'
    FILENAME = 'nctpot_drug.tsv'

    def _digest_concept_row(self, row: dict[str, str]) -> None:
        """
        Processes a single row of drug information.

        Args:
            row (dict[str, str]): A dictionary representing a single row with keys 'id@ncit', 'id', 'name', and 'synonyms'.

        Returns:
            None
        """
        self.concepts[row['id@ncit']] = {
            'id': row['id'],
            'name': row['name'],
            'synonyms': row['synonyms'].split('#'),
        }

def get_drug_terminology_mappings(drug_name: str) -> tuple:
    """
    Retrieves the RxNorm, ATC, and SNOMED CT codes for a given drug name.

    Args:
        drug_name (str): The name of the drug for which to find terminology mappings.

    Returns:
        tuple: A tuple containing the RxNorm code, ATC code, and SNOMED CT code.
               Each code may be None if not found.
    """
    # Get RxNorm code
    data = request_http_get(f'https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}')
    rxnorm_code = data['idGroup'].get('rxnormId', [None])[0]
    if rxnorm_code:
        print(f'\r• Querying RxNorm API for RXCUI-{rxnorm_code}... {" "*100}', end='')
        # Get mapped coed through the RxNorm API
        data = request_http_get(f'https://rxnav.nlm.nih.gov/REST/rxcui/{rxnorm_code}/allProperties.json?prop=codes')
        get_mapped_code = lambda system: next(
            (prop['propValue'] for prop in data['propConceptGroup']['propConcept'] 
             if prop['propName'] == system), None
        )
        snomed_code = get_mapped_code('SNOMEDCT')
        atc_code = get_mapped_code('ATC')
        drugbank_code = get_mapped_code('DRUGBANK')

        brand_data = request_http_get(f'https://rxnav.nlm.nih.gov/REST/rxcui/{rxnorm_code}/related.json?tty=BN')
        brand_names = []
        for concept in brand_data['relatedGroup']['conceptGroup']:
            for property in concept.get('conceptProperties', []):
                brand_names.append(property['name'])
                if property['synonym']:
                    brand_names.append(property['synonym'])
    else:
        print(f'\r• No RxNorm entry for {drug_name}... {" "*100}', end='')
        atc_code, snomed_code, drugbank_code = None, None, None
        brand_names = []
    return brand_names, rxnorm_code, atc_code, snomed_code, drugbank_code


def expand_AntineoplasticAgent_with_NCTPOT_mappings() -> List[DrugCodedConcept]:
    """
    Expands the AntineoplasticAgent concept with NCTPOT mappings.

    Returns:
        dict[str, DrugCodedConcept]: A dictionary of DrugCodedConcept objects expanded with NCTPOT mappings.
    """
    ANTINEOPLASTIC_AGENTS_CODE = 'C274'

    def _add_concept_with_NCTPOT_properties(concept: DrugCodedConcept) -> None:
        """
        Adds a concept with NCTPOT properties to the concepts dictionary.

        Args:
            concept (DrugCodedConcept): The concept to add.
        """
        # Get NCT-POT classification if available
        nctpot_drug = nctpot_drugs.get(concept.code, {})
        nctpot_drug_class_id = nctpot_map.get(nctpot_drug.get('id'))
        nctpot_drug_class = nctpot_drug_classes.get(nctpot_drug_class_id, {})
        # Get RxNorm, ATC and SNOMED CT codes
        brand_names, rxnorm_code, atc_code, snomed_code, drugbank_code = get_drug_terminology_mappings(concept.display)
        # Compose concept
        concepts[concept.code] = DrugCodedConcept(
            code = concept.code,
            display = concept.display,
            system = concept.system,
            version = concept.version,
            parent = concept.parent,
            synonyms = concept.synonyms + nctpot_drug.get('synonyms', []) + brand_names,
            drug_category = nctpot_drug_class.get('name'),
            drug_domain = nctpot_drug_class.get('domain'), 
            therapy_category = nctpot_drug_class.get('therapy'), 
            atc = atc_code, 
            snomed = snomed_code, 
            rxnorm = rxnorm_code, 
            drugbank = drugbank_code, 
        )

    def get_children_recursively(parent_code: str) -> None:
        """
        Recursively gets the children of a parent concept.

        Args:
            parent (str): The parent concept code.
        """
        for child in ncit_children[parent_code]:
            _add_concept_with_NCTPOT_properties(child)
            get_children_recursively(child.code)

    from pop.terminology.services import download_codesystem

    concepts = {}
    # Prepare the NCIT codesystem and its tree structre
    ncit_codesystem = download_codesystem(NCITDigestor.CANONICAL_URL)
    ncit_children = parent_to_children(ncit_codesystem)
    # Digest the NCTPOT maps
    nctpot_drugs = NCTPOTDrugsDigestor().digest()
    nctpot_map = NCTPOTDrugToClassDigestor().digest()
    nctpot_drug_classes = NCTPOTClassesDigestor().digest()
    # Add the concepts from the NCIT Antineoplastic agents tree
    print(f'• Synchronizing antineoplastic agents...')
    get_children_recursively(ANTINEOPLASTIC_AGENTS_CODE)

    # Add other NCTPOT concepts not in the NCT Antineoplastic agents tree
    for n,ncit_code in enumerate(nctpot_drugs.keys()):
        # If drug has already been included or there is not associated NCIT code, skip it
        if ncit_code not in concepts and ncit_code in ncit_codesystem:
            concept = ncit_codesystem.get(ncit_code)
            _add_concept_with_NCTPOT_properties(concept)
    return list(concepts.values())
    
    


class CTCAETermsDigestor(TerminologyDigestor):
    """
    Digestor for CTCAE MedDRA terms.
    
    Attributes:
        LABEL (str): Identifier for the digestor.
        FILENAME (str): Name of the file containing drug to drug class mappings.
    """
    LABEL = 'ctcae'
    FILENAME = 'ctcae.csv'
    CANONICAL_URL = 'http://terminology.hl7.org/CodeSystem/MDRAE'

    def _digest_concept_row(self, row: dict[str, str]) -> None:
        """
        Processes a single row of drug to drug class mapping.

        Args:
            row (dict): A dictionary representing a single row with keys 'id_drugClass' and 'id_drug'.
        """
        # Get core coding elements
        code = row['MedDRA Code']
        display = ensure_within_string_limits(row['CTCAE Term'])
        # Add the concept
        self.concepts[code] = CodedConcept(
            code = code,
            display = display,
            definition = row['Definition'],
            properties = {
                f'grade{n}': row[f'Grade {n}   '] for n in range(1,6)
            },
            system=self.CANONICAL_URL,
        )

def expand_ctcae_terms() -> List[CodedConcept]:
    return CTCAETermsDigestor().digest().values()