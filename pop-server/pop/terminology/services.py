import cachetools
import environ
import requests 
import os 
import cachetools.func
from collections import defaultdict
from fhir.resources.R4B.valueset import ValueSet as ValueSetSchema, ValueSetComposeInclude
from fhir.resources.R4B.codesystem import CodeSystem as CodeSystemSchema
from pop.terminology.models import CodedConcept as CodedConceptModel
from pop.terminology.digestors import DIGESTORS
from pop.terminology.utils import CodedConcept, request_http_get, parent_to_children, printYellow, printGreen, printRed
from pop.terminology.resolver import resolve_canonical_url
from pop.terminology.special import expand_AntineoplasticAgent_with_NCTPOT_mappings
from enum import Enum
from typing import List, Type
from tqdm import tqdm 

# Generate absolute path to artifacts folder
from pop.settings import BASE_DIR
artifacts_path = os.path.join(BASE_DIR, 'pop/apps/valuesets/artifacts/')

# Load environmental variables
env = environ.Env()
environ.Env.read_env('.env', overwrite=True)

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

def download_canonical_url(canonical_url: str) -> str:
    """
    Download the content from a canonical URL.

    This function resolves the given canonical URL to an appropriate endpoint
    URL if it does not end with '.json', and then downloads the content from 
    that endpoint.

    Args:
        canonical_url (str): The canonical URL from which to download content.

    Returns:
        str: The downloaded content as a string.
    """
    if not canonical_url.endswith('.json'):
        # Parse the API endpoint based on the canonical URL
        download_url =  resolve_canonical_url(canonical_url)
    else:
        download_url = canonical_url
    # Download the structure definition
    return request_http_get(download_url) 
   

@cachetools.func.lru_cache(maxsize=128)
def download_codesystem(canonical_url: str) -> List[CodedConcept]:
    """
    Downloads and digests a code system from the given canonical URL.

    Args:
        canonical_url (str): The canonical URL of the code system to download.

    Returns:
        List[CodedConcept]: A list of CodedConcept objects representing the
            concepts in the downloaded code system.
    """
    # Check if any of the built-in digestors match the given canonical URL
    digestor = next((
        digestor for digestor in DIGESTORS 
            if digestor.CANONICAL_URL == canonical_url or canonical_url in digestor.OTHER_URLS
        ), None)
    if digestor:
        # If a digestor matches, use it to digest the code system
        print(f'• Digesting code system: {canonical_url}')
        concepts = digestor().digest()        
        print(f'✓ Digestion complete and added to cache')
    else:
        # If no digestor matches, download the code system as a JSON object 
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
    """
    Downloads a value set from a given canonical URL and expands it.

    This function resolves the given canonical URL to an appropriate endpoint
    URL if it does not end with '.json', downloads the content from the endpoint,
    parses the content as a ValueSet resource, and expands it according to the
    rules defined in the ValueSet resource.

    Args:
        canonical_url (str): The canonical URL of the value set to download.

    Returns:
        List[CodedConcept]: A list of CodedConcept objects representing the
            concepts in the expanded value set.
    """
    print(f'• Resolving and downloading canonical URL: {canonical_url}')
    valueset_json = download_canonical_url(canonical_url)
    # Parse the response
    valuesetdef = ValueSetSchema.parse_obj(valueset_json)
    print(f'• Expanding ValueSet <{valuesetdef.name}>...')
    # Expand the valueset definition
    return expand_valueset(valuesetdef)

def expand_valueset(valuesetdef: ValueSetSchema) -> List[CodedConcept]:
    """
    Expands a ValueSet definition to a list of CodedConcepts.

    This function processes the given ValueSet definition and expands it to 
    include all concepts defined by its expansion or composition rules.

    Reference:
    [1] Value Set Expansion, HL7 FHIR R5 Documentation, 
    https://hl7.org/fhir/valueset.html#expansion

    Args:
        valuesetdef (ValueSetSchema): The ValueSet definition to expand.

    Returns:
        List[CodedConcept]: A list of expanded CodedConcept objects.
    """
    concepts = []
    # Check if the value set has a pre-defined expansion
    if valuesetdef.expansion and valuesetdef.expansion.contains:
        # Iterate through the existing expansion and add to concepts list
        for concept in valuesetdef.expansion.contains:
            concepts.append(
                CodedConcept(code=concept.code, system=concept.system, version=concept.version)
            )
    # Otherwise, process the composition rules
    elif valuesetdef.compose and valuesetdef.compose.include:
        # Include concepts based on the compose.include rules
        for inclusion_criteria in valuesetdef.compose.include:
            concepts.extend(
                follow_valueset_composition_rule(inclusion_criteria)
            )
    else:
        # Raise an error if neither an expansion nor composition is present
        raise ValueError('The valueset definition has neither a composition (compose.include) nor expansion (compose.exclude)')

    # Process compose.exclude rules to remove specified concepts
    if valuesetdef.compose and valuesetdef.compose.exclude:
        for exclusion_criteria in valuesetdef.compose.exclude:
            # Remove concepts that meet the exclusion criteria
            for excluded_concept in follow_valueset_composition_rule(exclusion_criteria):
                if excluded_concept in concepts:
                    concepts.remove(excluded_concept)
    
    return concepts


def follow_valueset_composition_rule(rule: ValueSetComposeInclude) -> List[CodedConcept]:
    """
    Include one or more codes from a code system or other value set(s).

    This function processes a ValueSetComposeInclude rule to determine which
    concepts to include based on specified systems, codes, and filters, as well
    as referenced value sets.

    Args:
        rule (ValueSetComposeInclude): The composition rule defining the 
        inclusion criteria.

    Returns:
        List[CodedConcept]: A list of CodedConcept objects that match the inclusion criteria.
    """
    system_concepts = []
    # Step 1: Process codes from a code system
    if rule.system:
        codesystem = download_codesystem(rule.system)

        # Add all codes if no specific codes or filters are provided
        if not rule.concept and not rule.filter:
            system_concepts.extend(codesystem.values())
        else:
            # Add specified codes if they exist in the code system
            if rule.concept:
                if codesystem:
                    system_concepts.extend([
                        codesystem.get(concept.code) for concept in rule.concept
                    ])
                else: 
                    system_concepts.extend([
                        CodedConcept(code=concept.code, system=rule.system, display=concept.display) for concept in rule.concept
                    ])


            # Process filters to include codes based on relationships
            if rule.filter:
                for rule_filter in rule.filter:
                    if rule_filter.op in [FilterOperator.IS_A, FilterOperator.DESCENDENT_OF]:
                        parent = codesystem[rule_filter.value]

                        # Include parent directly if filter is IS_A
                        if rule_filter.op == FilterOperator.IS_A:
                            system_concepts.append(parent)

                        # Recursive function to add child concepts
                        def add_children_recursively(parent):
                            for child in parent_to_children(codesystem).get(parent.code, []):
                                system_concepts.append(child)
                                add_children_recursively(child)

                        add_children_recursively(parent)

    valueset_concepts = []
    # Step 2: Process referenced value sets
    if rule.valueSet:
        for n, canonical_url in enumerate(rule.valueSet):
            # Download and collect the referenced valueset's concepts
            referenced_valueset_concepts = download_valueset(canonical_url)
            # Compute intersection if multiple value sets are referenced
            if n > 0:
                print(set(valueset_concepts) == set(referenced_valueset_concepts))
                valueset_concepts = list(set(valueset_concepts).intersection(referenced_valueset_concepts))
            else:
                valueset_concepts = list(set(referenced_valueset_concepts))

    # Combine system and value set concepts based on intersection criteria
    if system_concepts and valueset_concepts:
        return list(set(system_concepts).intersection(valueset_concepts))
    elif system_concepts:
        return system_concepts
    else:
        return valueset_concepts



def collect_codedconcept_terminology(
    CodedConceptModel: Type[CodedConceptModel], 
    skip_existing: bool = False, 
    force_reset: bool = False, 
    prune_dangling: bool = False, 
    write_db: bool = True
) -> None:
    """
    Collects and synchronizes a CodedConcept model with its associated FHIR ValueSet.

    This function downloads and digests a FHIR ValueSet, and then processes its
    concepts according to the FHIR ValueSet composition rules. It then updates
    the associated CodedConcept model with the processed concepts.

    Args:
        CodedConceptModel: The model class to synchronize.
        skip_existing: If True, skip synchronizing the model if it already contains entries.
        force_reset: If True, reset all model entries prior to synchronization.
        prune_dangling: If True, delete all dangling concepts in the model.
        write_db: If False, skip writing into the database.
    """
    CodedConcept_name = CodedConceptModel.__name__
    print(f'\n{CodedConcept_name}\n-----------------------------------------------')
    
    # Reset all model entries if requested    
    if force_reset and write_db:
        CodedConceptModel.objects.all().delete()
        print(f"\n✓ Removed all valueset entries")
    
    # Skip valuesets that already contain entries, if requested
    if skip_existing and CodedConceptModel.objects.count() > 0:
        printYellow(f'⬤  - Valueset <{CodedConcept_name}> skipped as it already contains {CodedConceptModel.objects.count()} entries (skip_existing - enabled).')
        return None 

    # Determine which valueset model to synchronize and compile concepts accordingly
    special_composer_function = {
        'AntineoplasticAgent': expand_AntineoplasticAgent_with_NCTPOT_mappings,
    }
    if CodedConcept_name in special_composer_function:
        concepts = special_composer_function[CodedConcept_name]()
    else:
        if not getattr(CodedConceptModel,'valueset', None) and not getattr(CodedConceptModel,'codesystem', None):
            printYellow(f'⬤ - Skipping model <{CodedConcept_name}> without an associated valueset or codesystem. \t\t\t')
            return None           
        if getattr(CodedConceptModel,'valueset', None):    
            concepts = download_valueset(CodedConceptModel.valueset)
        else:
            concepts = download_codesystem(CodedConceptModel.codesystem).values()

    for concept in CodedConceptModel.extension_concepts:
        concepts.append(concept)
    print(f'\n✓ Collected a total of {len(concepts)} concepts.')


    if hasattr(CodedConceptModel,'transform'):
        for concept in tqdm(concepts, total=len(concepts), desc='• Transforming displays'):
            if concept and concept.display:
                concept.synonyms.append(concept.display)
                concept = CodedConceptModel.transform(concept)    
                print(concept.code, concept.display)            

    # Keep track of the update process
    new_concepts = 0
    updated_concepts = 0
    deleted_dangling_concepts = 0        
    dangling_concepts = [concept.pk for concept in CodedConceptModel.objects.all()]
    # Start updating the database
    for concept in tqdm(concepts, total=len(concepts), desc='• Writing into database'):
        if not write_db or not concept or not concept.display: 
            continue
        instance, created = CodedConceptModel.objects.update_or_create(
            code=concept.code, system=concept.system,
            defaults={
                key: value for key, value in concept.model_dump().items() 
                    if key not in ['parent']
            },
        )
        if created:
            new_concepts += 1
        else: 
            updated_concepts += 1
            if instance.pk in dangling_concepts:
                dangling_concepts.remove(instance.pk)

    # Update relationships
    for concept in tqdm(concepts, total=len(concepts), desc='• Updating relationships'):
        if concept and concept.parent:
            child = CodedConceptModel.objects.get(code=concept.code, system=concept.system)
            parent = CodedConceptModel.objects.filter(code=concept.parent,system=concept.system).first()
            if parent:
                child.parent = parent
                if write_db:
                    child.save()
    print('✓ - All concepts written into the database')
    # Delete dangling concepts
    if concepts and dangling_concepts and prune_dangling:
        for concept_pk in dangling_concepts: 
            try: 
                CodedConceptModel.objects.get(pk=concept_pk).delete()
                deleted_dangling_concepts += 1
            except:
                printRed(f'❌ - Dangling concept <{concept.code} - {concept.display}> could not be deleted as it is referenced in the database by another object. \t\t\t')
    # Notify successful operation
    if new_concepts > 0:
        printGreen(f'✓ - Succesfully synchronized {new_concepts} concepts in the <{CodedConcept_name}> model table. \t\t\t')
    if deleted_dangling_concepts > 0:
        printGreen(f'✓ - Succesfully deleted {deleted_dangling_concepts} dangling concepts in the <{CodedConcept_name}> model table. \t\t\t')
    if updated_concepts > 0:
        printGreen(f'✓ - Succesfully updated {updated_concepts} concepts in the <{CodedConcept_name}> model table. \t\t\t')
    if len(dangling_concepts) > 0 and not prune_dangling:
        printYellow(f'⬤ - Ignored {len(dangling_concepts)} dangling concepts already present in the <{CodedConcept_name}> model table. \t\t\t')
    if (len(concepts) - new_concepts - updated_concepts) > 0:
        printYellow(f'⬤ - Ignored {len(concepts) - new_concepts} collected concepts already present in the <{CodedConcept_name}> model table. \t\t\t')
    if len(concepts) == 0:
        printRed(f'❌ - Something went wrong. No concepts were found for this model. \t\t\t')


