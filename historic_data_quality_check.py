from pipeline import validate_csv_quality as data_quality
import pandas as pd

# *********************************************************
# Load the historic data and save out CSVs for reuse
# *********************************************************
print('\nLoading historic data and converting to CSV')
spreadsheet_file = 'data/historic_data.xlsx'
services_output_csv = 'data/historic_services.csv'
standards_output_csv = 'data/historic_standards.csv'

df_services = pd.read_excel(spreadsheet_file, sheet_name='Services', encoding='utf-8', na_filter=False)
df_services['use_of_sin'] = df_services['use_of_sin'].apply(lambda x: x if x != '' else 'NA')
df_services.to_csv(services_output_csv, index=None, header=True, encoding='utf-8')

df_standards = pd.read_excel(spreadsheet_file, sheet_name='Standards', encoding='utf-8', na_filter=False)
df_standards['target_type'] = 'percentage'
df_standards.to_csv(standards_output_csv, index=None, header=True, encoding='utf-8')

print('checkpoint')

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
