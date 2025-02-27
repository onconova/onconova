


from ninja import Schema, Field
from typing import List

class KapplerMeierCurve(Schema):
    months: List[float]
    probabilities: List[float]
    lowerConfidenceBand: List[float]
    upperConfidenceBand: List[float]