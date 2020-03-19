import sys
from goodtables import validate
from pprint import pprint

def run_data_quality_validation(csv_file, schema_file):
    #TODO: Figure out why the json schema throws an unhashable dict error
    try:
        gt_report = validate(csv_file, row_limit=10000)
        print('>> Data Quality Report\n\tStructure:\t{0}\n\tEncoding:\t{1} ({2})\n\tRow Count:\t{3}'.format(
            'Valid' if gt_report['tables'][0]['valid'] == True else 'INVALID',
            gt_report['tables'][0]['encoding'],
            'Valid' if gt_report['tables'][0]['encoding'] == 'utf-8' else 'INVALID',
            gt_report['tables'][0]['row-count']
        ))

        if gt_report['tables'][0]['valid'] == False:
            print('\tERROR: CSV validation failed.  Printing full validation report and exiting.')
            print('\n***************************************************************************')
            pprint(gt_report)
            sys.exit('EXIT: Data Quality checks failed (Validation returned INVALID status)')

    except:
        print('\tERROR: Unable to complete quality validation.  Exiting.')
        sys.exit('EXIT: Data Quality checks failed (Error processing request)')


