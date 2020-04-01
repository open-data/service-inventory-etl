import sys, json, math
from goodtables import validate
from pprint import pprint
import pandas as pd

max_rows_to_process = 2000
valid_choices = {}

def run_data_quality_validation(csv_file, schema_file, choices_file):
    try:
        #gt_report = validate(csv_file, row_limit=10000)
        gt_report = validate(csv_file, row_limit=max_rows_to_process, schema=schema_file)
        print('>> Data Quality Report\n\tStructure:\t{0}\n\tEncoding:\t{1} ({2})\n\tRow Count:\t{3}'.format(
            'Valid' if gt_report['tables'][0]['valid'] == True else 'INVALID',
            gt_report['tables'][0]['encoding'],
            'Valid' if gt_report['tables'][0]['encoding'].startswith('utf-8') else 'INVALID',
            gt_report['tables'][0]['row-count']
        ))

        if gt_report['tables'][0]['valid'] == False:
            print('\tERROR: CSV validation failed.  Printing full validation report and exiting.')
            print('\n***************************************************************************')
            #pprint(gt_report)
            sys.exit('EXIT: Data Quality checks failed (Validation returned INVALID status)')

    except:
        print('\tERROR: Unable to complete quality validation.  Exiting.')
        sys.exit('EXIT: Data Quality checks failed (Error processing request)')

    with open(choices_file) as json_file:
        valid_choices = json.load(json_file)
    
    df = pd.read_csv(csv_file, encoding='utf-8')
    df = df[list(valid_choices.keys())]

    choice_errors = []

    # Loop over the CSV rows
    for index, row in df.iterrows():
        # Loop over all of the columns and valid choices
        for col_name in list(valid_choices.keys()):
            # Skip empty values
            if type(row[col_name]) is float and math.isnan(row[col_name]):
                continue
            # Break the comma sep list into values and loop
            for v in row[col_name].split(','):
                if v in valid_choices[col_name]:
                    pass
                else:
                    error_string = 'ERROR: "{0}" is an invalid choice for column {1}'.format(v, col_name)
                    if error_string not in choice_errors:
                        print('\t' + error_string)
                        choice_errors.append(error_string)
    
    if len(choice_errors) > 0:
        print('\tERROR: Choice validation failed with {0} errors'.format(len(choice_errors)))
        print('\n***************************************************************************')
        sys.exit('EXIT: Data Quality checks failed (Invalid Choices Found)')
    else:
        print('\tChoices:\tAll Valid')

# DEBUG
"""
services_schema = 'schema/service_table_schema.json'
services_output_csv = 'data/services_registry_output.csv'
services_choices = 'schema/service_choices.json'
run_data_quality_validation(services_output_csv, services_schema, services_choices)

#standards_schema = 'standards_table_schema.json'
#data_quality.run_data_quality_validation(standards_output_csv, standards_schema)
"""

