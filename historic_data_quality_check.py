from pipeline import validate_csv_quality as data_quality
import pandas as pd

# *********************************************************
# Load the historic data and save out CSVs for reuse
# *********************************************************
print('\nLoading historic data and converting to CSV')
historic_spreadsheet_file = 'data/historic/historic_data.xlsx'
output_path = 'data/yearly/'
services_output_csv = 'services.csv'
services_files_to_test = []
standards_output_csv = 'standards.csv'
standards_files_to_test = []

df_services = pd.read_excel(historic_spreadsheet_file, sheet_name='Services', encoding='utf-8', na_filter=False)
df_services['use_of_sin'] = df_services['use_of_sin'].apply(lambda x: x if x != '' else 'ND')
#df_services['info_service'] = df_services['info_service'].apply(lambda x: x if x != '' else 'ND')
#df_services['service_channels'] = df_services['service_channels'].apply(lambda x: x if x != '' else 'ND')
df_services['info_service'] = 'ND'
df_services['service_channels'] = 'ND'
for yr in df_services['fiscal_yr'].unique():
    outfile = output_path + yr + '_' + services_output_csv
    df_services[df_services['fiscal_yr'] == yr].to_csv(outfile, index=None, header=True, encoding='utf-8-sig')
    services_files_to_test.append(outfile)

df_standards = pd.read_excel(historic_spreadsheet_file, sheet_name='Standards', encoding='utf-8', na_filter=False)
df_standards['target_type'] = 'percentage'
for yr in df_standards['fiscal_yr'].unique():
    outfile = output_path + yr + '_' + standards_output_csv
    df_standards[df_standards['fiscal_yr'] == yr].to_csv(outfile, index=None, header=True, encoding='utf-8-sig')
    standards_files_to_test.append(outfile)


# *********************************************************
# Validate the services dataset with goodtables
# *********************************************************
print('\nEvaluating Services Data Quality')

services_schema_override = 'schema/service_table_schema_active.json'
#services_schema_override = services_schema_file
services_choices_override = 'schema/service_choices_active.json'
#services_choices_override = services_choices_file

for f in services_files_to_test:
    print('>> Checking {0:s}'.format(f))
    data_quality.run_data_quality_validation(f, services_schema_override, services_choices_override)

print('\nEvaluating Standards Data Quality')
standards_schema_override = 'schema/standards_table_schema_active.json'
#standards_schema_override = standards_schema_file
standards_choices_override = 'schema/standards_choices_active.json'
#standards_choices_override = standards_choices_file

for f in standards_files_to_test:
    print('>> Checking {0:s}'.format(f))
    data_quality.run_data_quality_validation(f, standards_schema_override, standards_choices_override)
