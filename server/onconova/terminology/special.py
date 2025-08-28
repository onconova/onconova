import json
import os
from collections import defaultdict
from typing import List

from tqdm import tqdm

from onconova.terminology.digestors import (
    EnsemblExonsDigestor,
    NCITDigestor,
    TerminologyDigestor,
)
from onconova.terminology.models import AntineoplasticAgent, Gene, GeneExon
from onconova.terminology.schemas import CodedConcept
from onconova.terminology.utils import ensure_within_string_limits, request_http_get


class DrugCodedConcept(CodedConcept):
    therapy_category: str | None = None


class NCITAntineoplasticAgentsSubsetDigestor(TerminologyDigestor):

    LABEL = "ncit-antineoplastic"
    FILENAME = "ncit_antineoplastic.tsv"

    def digest(self, *args, **kwargs) -> dict[str, str]:
        self.designations = defaultdict(list)
        self.concepts = {}
        self._digest_concepts()
        for code, synonyms in self.designations.items():
            self.concepts[code].synonyms = synonyms
        return self.concepts

    def _digest_concept_row(self, row: dict[str, str]) -> None:
        """
        Processes a single row of drug to drug class mapping.

        Args:
            row (dict): A dictionary representing a single row with keys 'id_drugClass' and 'id_drug'.
        """
        self.concepts[row["Code"]] = row["Code"]


def expand_antineoplastic_agent_concepts() -> List[DrugCodedConcept]:
    """
    Expands the AntineoplasticAgent concepts.

    Returns:
        dict[str, DrugCodedConcept]: A dictionary of DrugCodedConcept objects.
    """
    current_path = os.path.dirname(__file__)
    cache_file = (
        f"{current_path}/external-sources/ncit_antineoplastic_descendants.cache.json"
    )
    if not os.path.exists(cache_file):
        # Create an empty cache file if it does not exist
        with open(cache_file, "w") as f:
            json.dump({}, f)
    with open(cache_file, "r") as f:
        cache = json.load(f)

    def _get_NCIT_descendant_codes(codes):
        descendant_codes = []
        for code in codes:
            if code in cache:
                descendants = cache[code]
            else:
                # Fetch the descendants from the NCIT API
                print(f"• Fetching descendants for {code} from NCIT API...")
                descendants = [
                    concept["code"]
                    for concept in request_http_get(
                        f"https://api-evsrest.nci.nih.gov/api/v1/concept/ncit/{code}/descendants?fromRecord=0&pageSize=50000&maxLevel=10000"
                    )
                ]
                cache[code] = descendants
                with open(cache_file, "w") as f:
                    json.dump(cache, f, indent=2)
            descendant_codes.extend(descendants)
        return descendant_codes

    from onconova.terminology.services import download_codesystem

    concepts = {}
    # Prepare the NCIT codesystem and its tree structre
    ncit_codesystem = download_codesystem(NCITDigestor.CANONICAL_URL)
    # Digest the NCTPOT maps
    ncit_antineoplastic_drugs = list(
        NCITAntineoplasticAgentsSubsetDigestor().digest().values()
    )
    # Add the concepts from the NCIT Antineoplastic agents tree
    print(f"• Updating antineoplastic agent classifications...")

    therapy_categories = AntineoplasticAgent.TherapyCategory
    categories = {
        therapy_categories.IMMUNOTHERAPY: _get_NCIT_descendant_codes(
            ["C308", "C20401"]
        ),
        therapy_categories.HORMONE_THERAPY: _get_NCIT_descendant_codes(
            ["C147908", "C29701"]
        ),
        therapy_categories.METABOLIC_THERAPY: _get_NCIT_descendant_codes(["C177430"]),
        therapy_categories.ANTIMETASTATIC_THERAPY: _get_NCIT_descendant_codes(
            ["C2196"]
        ),
        therapy_categories.TARGETED_THERAPY: _get_NCIT_descendant_codes(
            ["C163758", "C1742", "C471", "C2189", "C177298", "C129839"]
        ),
        therapy_categories.CHEMOTHERAPY: _get_NCIT_descendant_codes(["C186664"]),
        therapy_categories.RADIOPHARMACEUTICAL_THERAPY: _get_NCIT_descendant_codes(
            ["C1446"]
        ),
    }

    # Add other NCTPOT concepts not in the NCT Antineoplastic agents tree

    print(f"• Processing antineoplastic agents metadata...")
    for ncit_code in ncit_antineoplastic_drugs:
        concept = ncit_codesystem.get(ncit_code)
        if not concept:
            continue
        concepts[concept.code] = DrugCodedConcept(**concept.model_dump())
        concepts[concept.code].therapy_category = therapy_categories.UNCLASSIFIED
        for category, category_codes in categories.items():
            if concept.code in category_codes:
                concepts[concept.code].therapy_category = category
                break

        ancestor = ncit_codesystem.get(concept.parent or "")
        while ancestor and ancestor.code != "C1909":  # Pharmacologic Substance
            concepts[ancestor.code] = ancestor
            ancestor = ncit_codesystem.get(ancestor.parent or "")

    return list(concepts.values())


class CTCAETermsDigestor(TerminologyDigestor):
    """
    Digestor for CTCAE MedDRA terms.

    Attributes:
        LABEL (str): Identifier for the digestor.
        FILENAME (str): Name of the file containing drug to drug class mappings.
    """

    LABEL = "ctcae"
    FILENAME = "ctcae.csv"
    CANONICAL_URL = "http://terminology.hl7.org/CodeSystem/MDRAE"

    def _digest_concept_row(self, row: dict[str, str]) -> None:
        """
        Processes a single row of drug to drug class mapping.

        Args:
            row (dict): A dictionary representing a single row with keys 'id_drugClass' and 'id_drug'.
        """
        # Get core coding elements
        code = row["MedDRA Code"]
        display = ensure_within_string_limits(row["CTCAE Term"])
        # Add the concept
        self.concepts[code] = CodedConcept(
            code=code,
            display=display,
            definition=row["Definition"],
            properties={f"grade{n}": row[f"Grade {n}   "] for n in range(1, 6)},
            system=self.CANONICAL_URL,
        )


def expand_ctcae_terms() -> List[CodedConcept]:
    return list(CTCAETermsDigestor().digest().values())


def add_gene_exons():
    exons_map = EnsemblExonsDigestor().digest()
    for gene_symbol in tqdm(
        exons_map, total=len(exons_map), desc="• Updating gene exons"
    ):
        gene = Gene.objects.filter(display=gene_symbol).first()
        if gene:
            for exon in exons_map[gene_symbol]:
                GeneExon.objects.get_or_create(
                    gene=gene,
                    rank=exon.rank,
                    defaults=dict(
                        coding_dna_region=(exon.coding_dna_start, exon.coding_dna_end),
                        coding_genomic_region=(
                            exon.coding_genomic_start,
                            exon.coding_genomic_end,
                        ),
                    ),
                )
