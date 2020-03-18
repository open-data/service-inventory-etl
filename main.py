import build_json_from_yaml as schema_convert
import parse_titan_flat_extract as data_transform
import validate_csv_quality as data_quality
import prep_and_publish_data as publish_prep
import json, sys

# *********************************************************
# Look for configuration.json in the root folder and load 
# required secrets and API keys.  Use the configuration.template.json 
# file and enter your own keys.
# *********************************************************
print('\nLoading configuration file')
environment = "local"

try:
    with open('configuration.json') as creds:    
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

# The output file name for the generated JSON file
json_schema_file = 'service_table_schema.json'

# The YAML has multiple schemas defined (zero-based) and the resource_id 
# points to the desired schema.  0 = service and 1 = standard
services_resource_id = 0 

# Build the JSON Table Schema file for goodtables
schema_convert.run_conversion(base_git_url, services_resource_id, yaml_schema_file, json_schema_file)
print('>> Finished producing services JSON schema')


# *********************************************************
# Convert Standards YAML to JSON Schema
# *********************************************************
print('\nConverting Standards YAML schema to JSON schema')

# The output file name for the generated JSON file
json_schema_file = 'standards_table_schema.json'

# The YAML has multiple schemas defined (zero-based) and the resource_id 
# points to the desired schema.  0 = service and 1 = standard
standards_resource_id = 1 

# Build the JSON Table Schema file for goodtables
schema_convert.run_conversion(base_git_url, standards_resource_id, yaml_schema_file, json_schema_file)
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

services_schema = 'service_table_schema_active.json'

data_quality.run_data_quality_validation(services_output_csv, services_schema)

print('\nEvaluating Standards Data Quality')
standards_schema = 'standards_table_schema_active.json'

data_quality.run_data_quality_validation(standards_output_csv, standards_schema)


# *********************************************************
# Transform the CSV to JSON and submit to the Registry API
# *********************************************************
print('\nPreparing Data and Publishing to the Registry')

publish_prep.run_prep_and_publish(services_output_csv)