import os
import json
from fhircraft.fhir.resources.generator import generate_resource_model_code
from fhircraft.fhir.resources.factory import factory
import traceback
base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.abspath(os.path.join(base_dir, "../../../../../fhir/ig/output"))
output_dir = base_dir

os.makedirs(output_dir, exist_ok=True)

factory.configure_repository(files=[
    os.path.join(input_dir, filename) for filename in os.listdir(input_dir)
    if filename.endswith(".json") and "StructureDefinition-onconova" in filename 
])

files = [os.path.join(input_dir, filename) for filename in os.listdir(input_dir) 
         if filename.endswith(".json")
         and "StructureDefinition-onconova" in filename 
         and not ("onconova-ext" in filename or "onconova-vs" in filename)
]

# Load necessary FHIR packages
print(f"Importing FHIR packages ...")
factory.load_package("hl7.fhir.us.mcode", "4.0.0")
factory.load_package("hl7.fhir.uv.genomics-reporting", "2.0.0")

print(f"Found {len(files)} files in {input_dir}")
processed = 0
for input_path in files:
    filename = os.path.basename(input_path)
    print(f"\n\nProcessing {filename} ...")
    with open(input_path, "r") as f:
        structure_definition = json.load(f)

    # Create model and generate source code using Fhircraft
    try:
        model = factory.construct_resource_model(canonical_url=structure_definition['url'])
        source_code = generate_resource_model_code(model)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        traceback.print_exc()
        continue

    # Write to output file (e.g., same name but .py extension)
    output_filename = structure_definition.get('name').replace('Onconova', '') + ".py"
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w") as out_f:
        out_f.write(source_code)
    print(f"Written {output_filename} to {output_dir}")
    processed += 1

print(f"\n\nDone. {processed} files processed.")