"""
FHIR Resource Model Generator

This script generates Python model classes from FHIR StructureDefinition JSON files
using the fhircraft library. It processes Onconova-specific FHIR profiles and creates
corresponding Python model files.

Usage:
    python _generate_models.py <input_dir> [--fail-fast] [--output-dir <dir>] [--verbose]

Example:
    python _generate_models.py ./fhir_definitions --fail-fast --verbose
"""

import argparse
import json
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import List, Tuple

from fhircraft.fhir.resources.factory import FHIRModelFactory
from fhircraft.config import override_config
from fhircraft.fhir.resources.generator import generate_resource_model_code

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

factory = FHIRModelFactory(fhir_release="R4")

# Constants
FHIR_PACKAGES = [
    ("hl7.fhir.us.mcode", "4.0.0"),
    ("hl7.fhir.uv.genomics-reporting", "2.0.0"),
]
STRUCTURE_DEFINITION_PREFIX = "StructureDefinition-onconova"
EXCLUDED_PATTERNS = ["onconova-ext", "onconova-vs"]


def setup_argument_parser() -> argparse.ArgumentParser:
    """Configure and return the argument parser."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "input_dir",
        type=str,
        help="Directory containing FHIR StructureDefinition JSON files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for generated Python models (default: script directory)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop processing on first error instead of continuing",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging output"
    )
    return parser


def validate_input_directory(input_dir: Path) -> None:
    """
    Validate that the input directory exists and is accessible.

    Args:
        input_dir: Path to the input directory

    Raises:
        SystemExit: If the directory doesn't exist or is not accessible
    """
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)

    if not input_dir.is_dir():
        logger.error(f"Input path is not a directory: {input_dir}")
        sys.exit(1)

    if not os.access(input_dir, os.R_OK):
        logger.error(f"Input directory is not readable: {input_dir}")
        sys.exit(1)


def get_structure_definition_files(input_dir: Path) -> List[Path]:
    """
    Find all valid StructureDefinition JSON files in the input directory.

    Args:
        input_dir: Path to the input directory

    Returns:
        List of Paths to valid StructureDefinition files
    """
    files = [
        input_dir / filename
        for filename in os.listdir(input_dir)
        if filename.endswith(".json")
        and STRUCTURE_DEFINITION_PREFIX in filename
        and not any(pattern in filename for pattern in EXCLUDED_PATTERNS)
    ]

    logger.info(f"Found {len(files)} StructureDefinition files to process")
    return files


def configure_fhir_factory(input_dir: Path, files: List[Path]) -> None:
    """
    Configure the FHIR factory with repository files and load required packages.

    Args:
        input_dir: Path to the input directory containing StructureDefinition files
        files: List of StructureDefinition files to include in the factory
    """
    logger.info("Configuring FHIR factory repository...")

    repository_files = [
        str(input_dir / filename)
        for filename in os.listdir(input_dir)
        if filename.endswith(".json") and STRUCTURE_DEFINITION_PREFIX in filename
    ]

    with override_config(validation_mode="skip", disable_fhir_warnings=True):
        for repo_file in repository_files + files:
            logger.debug(f"Adding repository file: {repo_file}")
            with open(repo_file, "r", encoding="utf-8") as f:
                factory.register(json.load(f))

        logger.info("Loading required FHIR packages...")
        for package_name, version in FHIR_PACKAGES:
            logger.debug(f"Loading package: {package_name} v{version}")
            factory.register_package(package_name, version, skip_invalid=True)


def process_structure_definition(
    input_path: Path, output_dir: Path, fail_fast: bool
) -> Tuple[bool, str]:
    """
    Process a single StructureDefinition file and generate Python model.

    Args:
        input_path: Path to the input StructureDefinition JSON file
        output_dir: Path to the output directory
        fail_fast: Whether to exit on error

    Returns:
        Tuple of (success: bool, output_filename: str)
    """
    with override_config(validation_mode="skip", disable_fhir_warnings=True):
        filename = input_path.name
        logger.info(f"Processing {filename}...")

        try:
            # Load StructureDefinition
            with open(input_path, "r", encoding="utf-8") as f:
                structure_definition = json.load(f)

            # Validate required fields
            if "url" not in structure_definition:
                raise ValueError("StructureDefinition missing required 'url' field")
            if "name" not in structure_definition:
                raise ValueError("StructureDefinition missing required 'name' field")

            # Generate model using fhircraft
            canonical_url = structure_definition["url"]
            logger.debug(f"Constructing model for: {canonical_url}")

            model = factory.build(canonical_url=canonical_url, mode="differential")
            source_code = generate_resource_model_code(model)

            # Determine output filename
            resource_name = structure_definition["name"].replace("Onconova", "")
            output_filename = f"{resource_name}.py"
            output_path = output_dir / output_filename

            # Write generated code
            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(source_code)

            logger.info(f"✓ Generated {output_filename}")
            return True, output_filename

        except Exception as e:
            logger.error(f"✗ Failed to process {filename}: {e}")
            logger.debug(traceback.format_exc())

            if fail_fast:
                logger.error("Fail-fast mode enabled. Exiting.")
                sys.exit(1)

            return False, ""


def main() -> None:
    """Main execution function."""
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Setup paths
    script_dir = Path(__file__).parent.resolve()
    input_dir = Path(args.input_dir).resolve()
    output_dir = (
        Path(args.output_dir).resolve() if args.output_dir else (script_dir / "models")
    )

    logger.info("=" * 70)
    logger.info("FHIR Resource Model Generator")
    logger.info("=" * 70)
    logger.info(f"Input directory:  {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Fail-fast mode:   {'Enabled' if args.fail_fast else 'Disabled'}")
    logger.info("=" * 70)

    # Validate input
    validate_input_directory(input_dir)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Output directory created/verified: {output_dir}")

    # Get files to process
    files = get_structure_definition_files(input_dir)

    if not files:
        logger.warning("No StructureDefinition files found to process")
        sys.exit(0)

    # Configure FHIR factory
    try:
        configure_fhir_factory(input_dir, files)
    except Exception as e:
        logger.error(f"Failed to configure FHIR factory: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

    # Process each file
    logger.info("")
    logger.info("Processing files...")
    logger.info("-" * 70)

    processed_count = 0
    failed_count = 0

    for input_path in files:
        success, _ = process_structure_definition(
            input_path, output_dir, args.fail_fast
        )
        if success:
            processed_count += 1
        else:
            failed_count += 1

    # Summary
    logger.info("-" * 70)
    logger.info("Summary:")
    logger.info(f"  Total files:      {len(files)}")
    logger.info(f"  Successfully processed: {processed_count}")
    logger.info(f"  Failed:           {failed_count}")
    logger.info("=" * 70)

    if failed_count > 0:
        logger.warning(f"Completed with {failed_count} error(s)")
        sys.exit(1)
    else:
        logger.info("All files processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
