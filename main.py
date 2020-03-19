import json, sys
from schema import build_json_from_yaml as schema_convert
from pipeline import parse_titan_flat_extract as data_transform
from pipeline import validate_csv_quality as data_quality
from pipeline import prep_and_publish_data as publish_prep

# *********************************************************
# Look for configuration.json in the root folder and load 
# required secrets and API keys.  Use the configuration.template.json 
# file and enter your own keys.
# *********************************************************
print('\nLoading configuration file')
environment = 'local'
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
base_git_url = 'https://raw.githubusercontent.com/Jmikelittle/ckanext-canada/DPOR_changes/ckanext/canada/tables/'

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
print('\nTransforming Titan extract to CSV schema')

# Define the path to the local Titan extract file
titan_flat_extract = 'data/titan_extract_flat.xlsx'

# Define the path to write the services output csv file
services_output_csv = 'data/services_registry_output.csv'

# Transform the Titan extract to the desired format and produce a services CSV
data_transform.run_services_transformation(titan_flat_extract, services_output_csv)

# Define the path to write the standard output csv file
standards_output_csv = 'data/standards_registry_output.csv'

# Transform the Titan extract to the desired format and produce a services CSV
data_transform.run_standards_transformation(titan_flat_extract, standards_output_csv)


# *********************************************************
# Validate the services dataset with goodtables
# *********************************************************
print('\nEvaluating Services Data Quality')

services_schema_override = 'schema/service_table_schema_active.json'
#services_schema_override = services_schema_file
services_choices_override = 'schema/service_choices_active.json'
#services_choices_override = services_choices_file

data_quality.run_data_quality_validation(services_output_csv, services_schema_override, services_choices_override)

print('\nEvaluating Standards Data Quality')
standards_schema_override = 'schema/standards_table_schema_active.json'
#standards_schema_override = standards_schema_file
standards_choices_override = 'schema/standards_choices_active.json'
#standards_choices_override = standards_choices_file

data_quality.run_data_quality_validation(standards_output_csv, standards_schema_override, standards_choices_override)


# *********************************************************
# Transform the CSV to JSON and submit to the Registry API
# *********************************************************
print('\nPreparing Data and Publishing to the Registry')

publish_prep.run_prep_and_publish(services_output_csv)