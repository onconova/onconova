from fhircraft.fhir.resources.datatypes.R4.complex import (
    Reference,
    Coding,
    CodeableConcept,
)
from onconova.core.schemas import CodedConcept


def construct_fhir_codeable_concept(concept: CodedConcept | Coding) -> CodeableConcept:
    """
    Construct a FHIR CodeableConcept from a CodedConcept or Coding object.

    Args:
        concept (CodedConcept | Coding): The concept to convert. Can be either a
            CodedConcept or a Coding object.

    Returns:
        CodeableConcept: A FHIR CodeableConcept containing the provided concept
            as a coding element.

    Examples:
        >>> coded_concept = CodedConcept(...)
        >>> codeable = construct_fhir_codeable_concept(coded_concept)
        >>>
        >>> coding = Coding(...)
        >>> codeable = construct_fhir_codeable_concept(coding)
    """
    if isinstance(concept, CodedConcept):
        return CodeableConcept(coding=[Coding.model_validate(concept.model_dump())])
    elif isinstance(concept, Coding):
        return CodeableConcept(coding=[concept])


def internal_to_ucum(unit: str) -> str:
    """Convert internal unit representation to UCUM format.

    Maps internal unit strings used in measures.py to their UCUM equivalents.
    Handles both simple units and bidimensional units (e.g., mg__dl -> mg/dL).

    Args:
        unit: Internal unit string representation

    Returns:
        UCUM-formatted unit string

    Examples:
        >>> internal_to_ucum("mg__dl")
        'mg/dL'
        >>> internal_to_ucum("IU")
        '[iU]'
        >>> internal_to_ucum("square_meter")
        'm2'
    """
    if not unit or not isinstance(unit, str):
        return unit

    # Handle bidimensional units first (primary__reference format)
    if "__" in unit:
        primary, reference = unit.split("__", 1)
        # Convert both parts and combine with UCUM division
        primary_ucum = _convert_single_unit_to_ucum(primary)
        reference_ucum = _convert_single_unit_to_ucum(reference)
        return f"{primary_ucum}/{reference_ucum}"

    # Handle simple units
    return _convert_single_unit_to_ucum(unit)


def _convert_single_unit_to_ucum(unit: str) -> str:
    """Convert a single internal unit to UCUM format.

    Args:
        unit: Single internal unit string

    Returns:
        UCUM-formatted unit string
    """
    # Direct mappings from measures.py units to UCUM
    unit_mappings = {
        # International Units
        "IU": "[iU]",
        # Mass units (from Mass measure)
        "g": "g",
        "kg": "kg",
        "mg": "mg",
        "ug": "ug",
        "ng": "ng",
        "pg": "pg",
        # Volume units (from Volume measure)
        "l": "L",
        "ml": "mL",
        "dl": "dL",
        "ul": "uL",
        "cubic_meter": "m3",
        "cubic_centimeter": "cm3",
        "cubic_millimeter": "mm3",
        # Time units (from Time measure)
        "s": "s",
        "min": "min",
        "hour": "h",
        "day": "d",
        "week": "wk",
        "month": "mo",
        "year": "a",
        # Temperature units (from Temperature measure)
        "celsius": "Cel",
        "fahrenheit": "[degF]",
        "kelvin": "K",
        # Pressure units (from Pressure measure)
        "Pa": "Pa",
        "atm": "atm",
        "mmHg": "mm[Hg]",
        "psi": "[psi]",
        "bar": "bar",
        "Torr": "Torr",
        # Area units (from Area measure)
        "square_meter": "m2",
        "square_centimeter": "cm2",
        "square_millimeter": "mm2",
        "square_foot": "[sft_i]",
        "square_inch": "[sin_i]",
        # Substance units (from Substance measure)
        "mol": "mol",
        "mmol": "mmol",
        "umol": "umol",
        "nmol": "nmol",
        # Fraction units (from Fraction measure)
        "%": "%",
        "ppm": "[ppm]",
        "ppb": "[ppb]",
        "ppt": "[ppt]",
        # Radiation dose units (from RadiationDose measure)
        "Gy": "Gy",
        # Multiple of median units (from MultipleOfMedian measure)
        "multiple_of_median": "1",  # Dimensionless in UCUM
        # Distance units (from Distance measure - inherited from measurement library)
        "m": "m",
        "cm": "cm",
        "mm": "mm",
        "km": "km",
        "ft": "[ft_i]",
        "inch": "[in_i]",
        # Common lab units not directly in measures.py but used in practice
        "U": "U",  # Enzyme units
        "kU": "kU",
        "mU": "mU",
        "cells": "{cells}",  # Cell counts
        "copies": "{copies}",  # DNA/RNA copies
        # pH units
        "ph_units": "[pH]",
        # Osmolality units
        "osm": "osm",
        "mosm": "mosm",
    }

    return unit_mappings.get(unit, unit)  # Return original if no mapping found


def ucum_to_internal(unit: str) -> str:
    """Convert UCUM unit format to internal representation.

    Maps UCUM unit strings to internal format used in measures.py.
    Handles both simple units and compound units with division.

    Args:
        unit: UCUM-formatted unit string

    Returns:
        Internal unit string representation

    Examples:
        >>> ucum_to_internal("mg/dL")
        'mg__dl'
        >>> ucum_to_internal("[iU]")
        'IU'
        >>> ucum_to_internal("m2")
        'square_meter'
    """
    if not unit or not isinstance(unit, str):
        return unit

    # Handle compound units with division
    if "/" in unit:
        parts = unit.split("/", 1)  # Split on first occurrence only
        primary_ucum = parts[0]
        reference_ucum = parts[1]

        # Convert both parts and combine with internal format
        primary_internal = _convert_single_ucum_to_internal(primary_ucum)
        reference_internal = _convert_single_ucum_to_internal(reference_ucum)
        return f"{primary_internal}__{reference_internal}"

    # Handle simple units
    return _convert_single_ucum_to_internal(unit)


def _convert_single_ucum_to_internal(unit: str) -> str:
    """Convert a single UCUM unit to internal format.

    Args:
        unit: Single UCUM unit string

    Returns:
        Internal unit string
    """
    # Reverse mappings from UCUM to internal format
    ucum_mappings = {
        # International Units
        "[iU]": "IU",
        # Mass units
        "g": "g",
        "kg": "kg",
        "mg": "mg",
        "ug": "ug",
        "ng": "ng",
        "pg": "pg",
        # Volume units
        "L": "l",
        "mL": "ml",
        "dL": "dl",
        "uL": "ul",
        "m3": "cubic_meter",
        "cm3": "cubic_centimeter",
        "mm3": "cubic_millimeter",
        # Time units
        "s": "s",
        "min": "min",
        "h": "hour",
        "d": "day",
        "wk": "week",
        "mo": "month",
        "a": "year",
        # Temperature units
        "Cel": "celsius",
        "[degF]": "fahrenheit",
        "K": "kelvin",
        # Pressure units
        "Pa": "Pa",
        "atm": "atm",
        "mm[Hg]": "mmHg",
        "[psi]": "psi",
        "bar": "bar",
        "Torr": "Torr",
        # Area units
        "m2": "square_meter",
        "cm2": "square_centimeter",
        "mm2": "square_millimeter",
        "[sft_i]": "square_foot",
        "[sin_i]": "square_inch",
        # Substance units
        "mol": "mol",
        "mmol": "mmol",
        "umol": "umol",
        "nmol": "nmol",
        # Fraction units
        "%": "%",
        "[ppm]": "ppm",
        "[ppb]": "ppb",
        "[ppt]": "ppt",
        # Radiation dose units
        "Gy": "Gy",
        # Multiple of median (dimensionless)
        "1": "multiple_of_median",
        # Distance units
        "m": "m",
        "cm": "cm",
        "mm": "mm",
        "km": "km",
        "[ft_i]": "ft",
        "[in_i]": "inch",
        # Lab units
        "U": "U",
        "kU": "kU",
        "mU": "mU",
        "{cells}": "cells",
        "{copies}": "copies",
        # pH units
        "[pH]": "ph_units",
        # Osmolality units
        "osm": "osm",
        "mosm": "mosm",
    }

    return ucum_mappings.get(unit, unit)  # Return original if no mapping found


def normalize_unit_string(unit: str) -> str:
    """Normalize a unit string by handling common variations and case issues.

    Args:
        unit: Unit string to normalize

    Returns:
        Normalized unit string
    """
    if not unit or not isinstance(unit, str):
        return unit

    # Remove extra whitespace
    normalized = unit.strip()

    # Handle common case variations
    case_normalizations = {
        "ML": "mL",
        "DL": "dL",
        "UL": "uL",
        "Ml": "mL",
        "Dl": "dL",
        "Ul": "uL",
        "iu": "[iU]",  # UCUM format
        "IU": "IU",  # Internal format
    }

    for old, new in case_normalizations.items():
        if normalized == old:
            normalized = new
            break

    return normalized


def validate_bidirectional_conversion(internal_unit: str) -> bool:
    """Validate that a unit conversion works bidirectionally.

    Args:\n        internal_unit: Internal format unit to test

    Returns:\n        True if conversion is bidirectional, False otherwise
    """
    try:
        # Test internal -> UCUM -> internal roundtrip
        ucum_unit = internal_to_ucum(internal_unit)
        back_to_internal = ucum_to_internal(ucum_unit)
        return back_to_internal == internal_unit
    except Exception:
        return False


def get_unit_type_category(unit: str) -> str:
    """Categorize a unit by type for better organization.

    Args:
        unit: Unit string (internal or UCUM format)

    Returns:
        Unit category string
    """
    if not unit or not isinstance(unit, str):
        return "unknown"

    unit_lower = unit.lower()

    # Categorize based on common patterns and measure types
    if any(
        x in unit_lower
        for x in ["g/", "mg/", "ug/", "ng/", "pg/", "g__", "mg__", "ug__"]
    ):
        return "mass_concentration"
    elif any(
        x in unit_lower for x in ["mol/", "mmol/", "umol/", "nmol/", "mol__", "mmol__"]
    ):
        return "substance_concentration"
    elif any(x in unit_lower for x in ["iu/", "[iu]/", "u/", "iu__", "u__"]):
        return "activity_concentration"
    elif any(x in unit_lower for x in ["cells/", "{cells}/", "cells__"]):
        return "cell_count"
    elif any(x in unit_lower for x in ["%", "ppm", "ppb", "ppt"]):
        return "fraction"
    elif any(
        x in unit_lower for x in ["cel", "degf", "fahrenheit", "celsius", "kelvin"]
    ):
        return "temperature"
    elif any(
        x in unit_lower for x in ["mmhg", "mm[hg]", "pa", "atm", "bar", "psi", "torr"]
    ):
        return "pressure"
    elif any(x in unit_lower for x in ["m2", "m3", "cm2", "cm3", "square", "cubic"]):
        return "area_volume"
    elif any(
        x in unit_lower for x in ["s", "min", "hour", "day", "week", "month", "year"]
    ):
        return "time"
    elif any(x in unit_lower for x in ["gy", "gray"]):
        return "radiation_dose"
    elif any(x in unit_lower for x in ["ph]", "ph_units"]):
        return "ph_scale"
    elif any(x in unit_lower for x in ["osm", "mosm"]):
        return "osmolality"
    else:
        return "other"


# Common unit mappings for quick reference and validation
COMMON_CLINICAL_UNITS = {
    # Mass concentration - common lab values
    "mg__dl": "mg/dL",  # Glucose, cholesterol, etc.
    "g__l": "g/L",  # Protein, albumin
    "mg__l": "mg/L",  # Various drugs
    "ug__ml": "ug/mL",  # Vitamins, hormones
    "ng__ml": "ng/mL",  # Hormones, tumor markers
    "pg__ml": "pg/mL",  # Very low concentration hormones
    # Substance concentration - chemistry
    "mmol__l": "mmol/L",  # Electrolytes, glucose
    "umol__l": "umol/L",  # Creatinine, bilirubin
    "mol__l": "mol/L",  # Osmolality calculations
    # Activity concentration - enzymes
    "IU__l": "[iU]/L",  # ALT, AST, ALP
    "U__l": "U/L",  # Enzyme activity
    "mU__l": "mU/L",  # Thyroid hormones
    # Cell counts
    "cells__ul": "{cells}/uL",  # CBC, differential
    "10_9__l": "10*9/L",  # WBC, RBC (scientific notation)
    "10_6__ul": "10*6/uL",  # Platelet count
    # Time-based rates
    "per_min": "/min",  # Heart rate, breathing rate
    "per_hour": "/h",  # Clearance rates
    "per_day": "/d",  # Daily outputs
    # Area-based measurements
    "mg__square_meter": "mg/m2",  # Chemotherapy dosing
    "g__square_meter": "g/m2",  # Body surface area calculations
}


def get_common_ucum_equivalent(internal_unit: str) -> str:
    """Get UCUM equivalent for common clinical units.

    Args:
        internal_unit: Internal unit format

    Returns:
        UCUM equivalent or original if not found
    """
    return COMMON_CLINICAL_UNITS.get(internal_unit, internal_to_ucum(internal_unit))
