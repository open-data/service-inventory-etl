import json, sys
from schema import build_json_from_yaml as schema_convert
from pipeline import parse_titan_flat_extract as data_transform
from pipeline import validate_csv_quality as data_quality
from pipeline import prep_and_publish_data as publish_prep
import argparse

# *********************************************************
# Parse the command-line arguments to define how the script will run
#       --p, --publish:     Enable publishing on this run
#               default: False
#       --e, --environment: Specify the environment to publish to
#               choices: {staging, production}
#               default: staging
# *********************************************************
parser = argparse.ArgumentParser(description='Service Inventory ETL from Titan to the OpenData Portal')
parser.add_argument("--publish", "--p", action="store_true", help="enable automatic publishing to the OpenData portal")
parser.add_argument("--environment", "--e", choices=["staging", "production"], default="staging", type=str, help="specify the environment to publish to")
args = parser.parse_args()

try:
    publish_to_portal = args.publish # default = False
except:
    publish_to_portal = False

try:
    environment = args.environment # default = staging
except:
    environment = 'staging'

# Publish from VS Code
#publish_to_portal = True
#environment = 'staging'


# *********************************************************
# Look for configuration.json in the config folder and load 
# required secrets and API keys.  Use the configuration.template.json 
# file and enter your own keys.
# *********************************************************
print('\nLoading configuration file')
config_file = 'config/configuration.json'

try:
    with open(config_file) as creds:    
        credentials = json.load(creds)[environment]
    print('>> Credentials file found.  Environment set to "{0}"'.format(environment))
except:
    print('\nERROR: Cannot find configuration file.  Unable to continue.')
    sys.exit('EXIT: No credentials.json found in the project root directory.')


# *********************************************************
# Convert Services YAML to JSON Schema
# *********************************************************
print('\nConverting Services YAML schema to JSON schema')

# The tables folder for the target branch
base_git_url = 'https://raw.githubusercontent.com/Jmikelittle/ckanext-canada/DPOR_changes2/ckanext/canada/tables/'

# The filename for the target YAML
yaml_schema_file = 'service.yaml'

# The output file name for the generated JSON file and the choices file
services_schema_file = 'schema/service_table_schema.json'
services_choices_file = 'schema/service_choices.json'

# The YAML has multiple schemas defined (zero-based) and the resource_id 
# points to the desired schema.  0 = service and 1 = standard
services_resource_id = 0 

# Build the JSON Table Schema file for goodtables
schema_convert.run_conversion(base_git_url, services_resource_id, yaml_schema_file, services_schema_file, services_choices_file)
print('>> Finished producing services JSON schema')


# *********************************************************
# Convert Standards YAML to JSON Schema
# *********************************************************
print('\nConverting Standards YAML schema to JSON schema')

# The output file name for the generated JSON file
standards_schema_file = 'schema/standards_table_schema.json'
standards_choices_file = 'schema/standards_choices.json'

# The YAML has multiple schemas defined (zero-based) and the resource_id 
# points to the desired schema.  0 = service and 1 = standard
standards_resource_id = 1 

# Build the JSON Table Schema file for goodtables
schema_convert.run_conversion(base_git_url, standards_resource_id, yaml_schema_file, standards_schema_file, standards_choices_file)
print('>> Finished producing standards JSON schema')


# *********************************************************
# Load and process the Titan flat extract
# *********************************************************
print('\nTransforming extract to CSV schema')

# Define the path to the local Titan extract file
titan_flat_extract = 'data/latest_annual_extract.xlsx'

output_path = 'data/yearly/'

# Define the path to write the services output csv file
services_output_csv = 'services.csv'

# Transform the Titan extract to the desired format and produce a services CSV
new_services_file = data_transform.run_services_transformation(titan_flat_extract, output_path, services_output_csv)

# Define the path to write the standard output csv file
standards_output_csv = 'standards.csv'

# Transform the Titan extract to the desired format and produce a services CSV
new_standards_file = data_transform.run_standards_transformation(titan_flat_extract, output_path, standards_output_csv)


# *********************************************************
# Validate the services dataset with goodtables
# *********************************************************
print('\nEvaluating New Services Data Quality')

services_schema_override = 'schema/service_table_schema_active.json'
#services_schema_override = services_schema_file
services_choices_override = 'schema/service_choices_active.json'
#services_choices_override = services_choices_file

data_quality.run_data_quality_validation(new_services_file, services_schema_override, services_choices_override)

print('\nEvaluating New Standards Data Quality')
standards_schema_override = 'schema/standards_table_schema_active.json'
#standards_schema_override = standards_schema_file
standards_choices_override = 'schema/standards_choices_active.json'
#standards_choices_override = standards_choices_file

data_quality.run_data_quality_validation(new_standards_file, standards_schema_override, standards_choices_override)

# *********************************************************
# Merge all years together
# *********************************************************
print('\nMerging annual files and performing final validation')

publish_services_file = 'data/publish/service_inventory.csv'
publish_prep.run_merge_years('data/yearly/', '*_services.csv', publish_services_file)
publish_standards_file = 'data/publish/service_standards.csv'
publish_prep.run_merge_years('data/yearly/', '*_standards.csv', publish_standards_file)

print('\nEvaluating Combined Services Data Quality')
data_quality.run_data_quality_validation(publish_services_file, services_schema_override, services_choices_override)

print('\nEvaluating Combined Standards Data Quality')
data_quality.run_data_quality_validation(publish_standards_file, standards_schema_override, standards_choices_override)


# *********************************************************
# Publish the updated files to the portal
# *********************************************************
if publish_to_portal:
    print('\nPreparing Services Data and Publishing to the Registry')

    services_dataset_title = 'Service Identification Information & Metrics'
    publish_prep.run_prep_and_publish(publish_services_file, credentials['registry_endpoint'], credentials['registry_api_key'], credentials['dataset_id'], credentials['services_resource_id'], services_dataset_title)

    print('\nPreparing Standards Data and Publishing to the Registry')

    standards_dataset_title = 'Service Standards & Performance Results'
    publish_prep.run_prep_and_publish(publish_standards_file, credentials['registry_endpoint'], credentials['registry_api_key'], credentials['dataset_id'], credentials['standards_resource_id'], standards_dataset_title)

    print('\nPublishing complete')
else:
    print('\nPublishing set to False - skipping publishing step.  Set publish_to_portal to True to push data to the portal.')

print('\nScript finished.')
