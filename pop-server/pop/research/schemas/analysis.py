from typing import List, Optional, Dict
from ninja import Schema, Field
from pydantic import RootModel, AliasChoices

class KapplerMeierCurve(Schema):
    """
    Schema for Kaplan-Meier survival curve results.
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
    
    
class OncoplotVariants(Schema):
    gene: str
    caseId: str = Field(
        alias='pseudoidentifier',
        validation_alias=AliasChoices('caseId','pseudoidentifier')
    )
    hgvsExpression: str =  Field(
        alias='is_pathogenic',
        validation_alias=AliasChoices('hgvsExpression','hgvs_expression')
    )
    isPathogenic: Optional[bool] = Field(
        alias='is_pathogenic',
        validation_alias=AliasChoices('isPathogenic','is_pathogenic')
    )
    
class OncoplotDataset(Schema):
    genes: List[str] = Field(
        title='Genes',
        description='List of most frequently encountered genes'
    )
    cases: List[str] = Field(
        title='Cases',
        description='List of patient cases'
    )
    variants: List[OncoplotVariants] = Field(
        title='Variants',
        description='Variants included in the Oncoplot'
    )
    
class CategorySurvivals(RootModel):
    root: Dict[str, List[float]]