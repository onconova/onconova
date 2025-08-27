import math
from collections import Counter
from datetime import datetime
from statistics import NormalDist
from typing import Dict, List, Self

from django.db.models import F, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from ninja import Field, Schema
from pop.core.anonymization import anonymize_age
from pop.core.types import Nullable
from pop.oncology.models import (
    GenomicVariant,
    PatientCase,
    SystemicTherapy,
    TherapyLine,
    TreatmentResponse,
)
from pop.research.models import Cohort
from pop.research.schemas.cohort import CohortTraitCounts
from pydantic import AliasChoices


class AnalysisMetadata(Schema):
    cohortId: str = Field(
        title="Cohort ID",
        description="The ID of the cohort for which the analysis was performed.",
    )
    analyzedAt: datetime = Field(
        title="Analyzed At",
        description="The datetime at which the analysis was performed.",
    )
    cohortPopulation: int = Field(
        title="Population",
        description="The effective number of valid patient cases in the cohort used for the analysis.",
    )


class AnalysisMetadataMixin:

    metadata: AnalysisMetadata | None = Field(
        default=None,
        title="Metadata",
        description="Metadata for the Kaplan-Meier curve.",
    )

    def add_metadata(self, cohort: Cohort):
        self.metadata = AnalysisMetadata(
            cohortId=str(cohort.id),
            analyzedAt=datetime.now(),
            cohortPopulation=cohort.valid_cases.count(),
        )
        return self


class KaplanMeierCurve(Schema, AnalysisMetadataMixin):
    """
    Kaplan-Meier survival curve
    """

    months: List[float] = Field(
        title="Months",
        description="List of time points (in months) for survival probability estimates.",
    )
    probabilities: List[float] = Field(
        title="Probabilities", description="Survival probabilities at each time point."
    )
    lowerConfidenceBand: List[float] = Field(
        title="Lower Confidence Band",
        description="Lower bound of the survival probability confidence interval at each time point.",
    )
    upperConfidenceBand: List[float] = Field(
        title="Upper Confidence Band",
        description="Upper bound of the survival probability confidence interval at each time point.",
    )

    @classmethod
    def calculate(
        cls,
        survivals: List[float | None],
        confidence_level: float = 0.95,
    ) -> Self:
        """
        Performs Kappler-Maier analysis to estimate survival probabilities and 95% confidence intervals
        and initializes a Kaplan-Meier curve.

        Args:
            survivals (List[float | None]): Array containing the number of months survived for each
                patient.
            confidence_level (float): Confidence level for the confidence interval (0.95 default).

        Notes:
            Uses the analytical Kaplan-Meier estimator 1_ and computes the asymptotic 95%
            confidence intervals 2_ using the log-log approach 3_.

        References:
        .. [1]  https://en.wikipedia.org/wiki/Kapla-Meier_estimator
        .. [2]  Fisher, Ronald (1925), Statistical Methods for Research Workers, Table 1
        .. [3]  Borgan, Liestøl (1990). Scandinavian Journal of Statistics 17, 35-41
        """
        # Remove None values and convert to floats
        survivals = [float(m) for m in survivals if m is not None]
        # Check that there are values in the array left
        if len(survivals) == 0:
            raise ValueError("The input argument cannot be empty or None")

        # Round months to integers
        survivals = [round(m) for m in survivals]

        # Generate the axis of survived months
        max_month = int(max(survivals))
        survival_axis = list(range(0, max_month + 1))

        # Determine the number of alive patients along the axis
        alive = [sum(m >= month for m in survivals) for month in survival_axis]

        # Determine the number of death events along the axis
        events = [sum(m == month for m in survivals) for month in survival_axis]

        # Truncate the axis regions where nothing more happens
        valid_indices = [i for i, a in enumerate(alive) if a > 0]
        survival_axis = [survival_axis[i] for i in valid_indices]
        alive = [alive[i] for i in valid_indices]
        events = [events[i] for i in valid_indices]

        # Evaluate the KM survival probability estimator
        est_survival_prob = []
        cumulative_product = 1.0

        for e, a in zip(events, alive):
            cumulative_product *= 1 - e / a
            est_survival_prob.append(cumulative_product)

        # Evaluate its standard deviation
        cumulative_sum = 0.0
        std = []
        for p, e, a in zip(est_survival_prob, events, alive):
            if a == 0 or a - e == 0:
                std.append(0.0)
                continue
            increment = e / (a * (a - e))
            if increment <= 0:
                std.append(0.0)
                continue
            cumulative_sum += increment
            std_val = math.sqrt(cumulative_sum / math.log(p) ** 2)
            std.append(std_val)

        # Set the normal inverse CDF value for confidence level
        z = NormalDist().inv_cdf(1 - (1 - confidence_level) / 2)

        # Compute the 95%-confidence intervals
        confidence_bands = {
            "lower": [p ** math.exp(+z * s) for p, s in zip(est_survival_prob, std)],
            "upper": [p ** math.exp(-z * s) for p, s in zip(est_survival_prob, std)],
        }

        return cls(
            # Return the Kaplan-Meier curve
            months=survival_axis,
            probabilities=est_survival_prob,
            lowerConfidenceBand=confidence_bands["lower"],
            upperConfidenceBand=confidence_bands["upper"],
        )


class OncoplotVariant(Schema):
    gene: str
    caseId: str = Field(
        alias="pseudoidentifier",
        validation_alias=AliasChoices("caseId", "pseudoidentifier"),
    )
    hgvsExpression: str = Field(
        alias="is_pathogenic",
        validation_alias=AliasChoices("hgvsExpression", "hgvs_expression"),
    )
    isPathogenic: Nullable[bool] = Field(
        alias="is_pathogenic",
        validation_alias=AliasChoices("isPathogenic", "is_pathogenic"),
    )


class OncoplotDataset(Schema, AnalysisMetadataMixin):
    genes: List[str] = Field(
        title="Genes", description="List of most frequently encountered genes"
    )
    cases: List[str] = Field(title="Cases", description="List of patient cases")
    variants: List[OncoplotVariant] = Field(
        title="Variants", description="Variants included in the Oncoplot"
    )

    @classmethod
    def calculate(cls, cases: QuerySet[PatientCase]) -> Self:
        variants = GenomicVariant.objects.filter(case__in=cases)
        genes = [
            gene
            for gene, _ in Counter(
                variants.values_list("genes__display", flat=True)
            ).most_common(25)
        ]
        variants = (
            variants.filter(genes__display__in=genes)
            .annotate(
                pseudoidentifier=F("case__pseudoidentifier"),
                gene=F("genes__display"),
                hgvs_expression=Coalesce(F("protein_hgvs"), F("dna_hgvs"), Value("?")),
            )
            .values("pseudoidentifier", "gene", "hgvs_expression", "is_pathogenic")
        )
        return cls(
            genes=genes,
            cases=list(cases.values_list("pseudoidentifier", flat=True)),
            variants=[OncoplotVariant.model_validate(variant) for variant in variants],
        )


class CategorizedSurvivals(Schema, AnalysisMetadataMixin):
    survivals: Dict[str, List[float]]

    @classmethod
    def calculate(cls, cohort: Cohort, therapyLine: str, categorization: str) -> Self:
        if categorization == "drugs":
            return cls(
                survivals=cls._calculate_by_combination_therapy(cohort, therapyLine)
            )
        elif categorization == "therapies":
            return cls(
                survivals=cls._calculate_by_therapy_classification(cohort, therapyLine)
            )

    @classmethod
    def _calculate_by_combination_therapy(
        cls, cohort: Cohort, therapyLine: str
    ) -> Dict[str, List[float]]:
        drug_combinations = (
            cohort.valid_cases.annotate(
                drug_combination=Subquery(
                    SystemicTherapy.objects.filter(
                        case_id=OuterRef("id"), therapy_line__label=therapyLine
                    )
                    .annotate(drug_combination=F("drug_combination"))
                    .values_list("drug_combination", flat=True)[:1]
                )
            )
            .filter(drug_combination__isnull=False)
            .values_list("drug_combination", flat=True)
        )

        survival_per_combination = {
            combo[0]: None for combo in Counter(drug_combinations).most_common(4)
        }
        for combination in survival_per_combination.keys():
            survival_per_combination[combination] = (
                cls._get_progression_free_survival_for_therapy_line(
                    cohort,
                    label=therapyLine,
                    systemic_therapies__drug_combination=combination,
                )
            )
        survival_per_combination["Others"] = (
            cls._get_progression_free_survival_for_therapy_line(
                cohort,
                label=therapyLine,
                exclude_filters=dict(
                    systemic_therapies__drug_combination__in=list(
                        survival_per_combination.keys()
                    )
                ),
            )
        )
        return survival_per_combination

    @classmethod
    def _calculate_by_therapy_classification(
        cls, cohort: Cohort, therapyLine: str
    ) -> Dict[str, List[float]]:
        """
        Calculate progression free survival per therapy classification

        Given a cohort and a therapy line (e.g. first-line, second-line, etc.),
        this function returns a dictionary with the progression free survival
        for each therapy classification in the cohort. The therapy classification
        is a comma-separated string of therapy types (e.g. chemotherapy, immunotherapy, etc.).
        The function will split this string into its individual components, and then
        categorize the therapy lines into one of the following categories:
            - chemotherapy + immunotherapy: chemoimmunotherapy
            - radiotherapy + [any other therapy type]: radio[therapy type]
            - any other therapy type: [therapy type]
        The function will then calculate the progression free survival for each
        of the most common categories, and return a dictionary with the results.

        Parameters:
            cohort (Cohort): The cohort to calculate the progression free survival for
            therapyLine (str): The therapy line to calculate the progression free survival for

        Returns:
            dict: A dictionary with the progression free survival for each therapy classification
        """

        def _parse_category_name(value):
            def pop_from_list(list, value):
                try:
                    index = list.index(value)
                except ValueError:
                    return None
                list.remove(value)
                return value

            categories: List[str] = value.split(",")
            if "chemotherapy" in categories and "immunotherapy" in categories:
                categories.remove("chemotherapy")
                categories.remove("immunotherapy")
                categories.insert(0, "chemoimmunotherapy")
            radiotherapy = pop_from_list(categories, "radiotherapy")
            if radiotherapy and len(categories) == 1:
                return f"Radio{categories[0]}"
            else:
                return " & ".join(categories).title()

        therapy_classifications = (
            TherapyLine.objects.filter(case__in=cohort.valid_cases.all())
            .filter(label=therapyLine)
            .annotate(therapy_classification=F("therapy_classification"))
            .values_list("therapy_classification", flat=True)
        )

        most_common = [
            category[0] for category in Counter(therapy_classifications).most_common(4)
        ]
        survival_per_classification = {
            _parse_category_name(category): None for category in most_common
        }
        for classification in most_common:
            survival_per_classification[_parse_category_name(classification)] = (
                cls._get_progression_free_survival_for_therapy_line(
                    cohort,
                    label=therapyLine,
                    therapy_classification=classification,
                )
            )
        survival_per_classification["Others"] = (
            cls._get_progression_free_survival_for_therapy_line(
                cohort,
                label=therapyLine,
                exclude_filters=dict(
                    therapy_classification=list(survival_per_classification.keys())
                ),
            )
        )
        return survival_per_classification

    @classmethod
    def _get_progression_free_survival_for_therapy_line(
        cls, cohort: Cohort, exclude_filters: dict = {}, **include_filters: dict
    ) -> List[float]:
        """
        Returns the list of progression free survival values for the given therapy line
        in the given cohort, filtered by the given include and exclude filters.

        Args:
            cohort (Cohort): The cohort to filter cases from.
            exclude_filters (dict, optional): Filters to exclude cases with. Defaults to {}.
            **include_filters (dict): Filters to include cases with.

        Returns:
            List[float]: The list of progression free survival values.
        """
        return list(
            cohort.valid_cases.annotate(
                progression_free_survival=Subquery(
                    TherapyLine.objects.filter(
                        case_id=OuterRef("id"), **include_filters
                    )
                    .exclude(**exclude_filters)
                    .annotate(progression_free_survival=F("progression_free_survival"))
                    .values_list("progression_free_survival", flat=True)[:1]
                )
            )
            .filter(progression_free_survival__isnull=False)
            .values_list("progression_free_survival", flat=True)
        )


class Distribution(Schema, AnalysisMetadataMixin):

    items: List[CohortTraitCounts] = Field(
        title="Items", description="The entries in the distribution."
    )

    @classmethod
    def calculate(cls, cohort: Cohort, property: str) -> Self:
        property_info = dict(
            age={"lookup": "age", "anonymization": anonymize_age},
            ageAtDiagnosis={
                "lookup": "age_at_diagnosis",
                "anonymization": anonymize_age,
            },
            gender={"lookup": "gender__display"},
            neoplasticSites={
                "lookup": "neoplastic_entities__topography_group__display"
            },
            vitalStatus={"lookup": "vital_status"},
        ).get(property)
        return Distribution(
            items=[
                CohortTraitCounts(
                    category=category, counts=count, percentage=percentage
                )
                for category, (count, percentage) in cohort.get_cohort_trait_counts(
                    cohort.valid_cases.all(),
                    property_info["lookup"],
                    anonymization=property_info.get("anonymization"),
                ).items()
            ]
        )


class TherapyLineCasesDistribution(Distribution):

    @classmethod
    def calculate(cls, cohort: Cohort, therapyLine: str) -> Self:
        total = cohort.valid_cases.count()
        included = cohort.valid_cases.filter(therapy_lines__label=therapyLine).count()
        not_included = total - included
        return Distribution(
            items=[
                CohortTraitCounts(
                    category=f"Included in {therapyLine}",
                    counts=included,
                    percentage=round(included / total * 100.0, 4),
                ),
                CohortTraitCounts(
                    category="Not included",
                    counts=not_included,
                    percentage=round(not_included / total * 100.0, 4),
                ),
            ]
        )


class TherapyLineResponseDistribution(Distribution):

    @classmethod
    def calculate(cls, cohort: Cohort, therapyLine: str) -> Self:
        values = (
            cohort.valid_cases.filter(therapy_lines__label=therapyLine)
            .annotate(
                response=Subquery(
                    TreatmentResponse.objects.annotate(
                        therapy_line_period=Subquery(
                            TherapyLine.objects.select_properties("period")
                            .filter(case_id=OuterRef("case_id"), label=therapyLine)
                            .values_list("period", flat=True)[:1]
                        )
                    )
                    .filter(
                        case_id=OuterRef("id"),
                        therapy_line_period__contains=F("date"),
                    )
                    .order_by("-date")
                    .values_list("recist__display", flat=True)[:1]
                )
            )
            .values_list("response", flat=True)
        )
        return Distribution(
            items=[
                CohortTraitCounts(
                    category=key or "Unknown",
                    counts=count,
                    percentage=round(count / values.count() * 100.0, 4),
                )
                for key, count in Counter(values).items()
            ]
        )
