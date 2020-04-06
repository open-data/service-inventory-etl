import pandas as pd
from ckanapi import RemoteCKAN, NotAuthorized
import os, glob

def run_prep_and_publish(csv_file, endpoint, api_key, dataset_id, resource_id, dataset_title):
    print('>>Publishing {0:s}'.format(dataset_title))

    ua = 'prep_and_publish_data.py/1.0 (+{0:s})'.format(endpoint)
    reg = RemoteCKAN(endpoint, apikey=api_key, user_agent=ua)
    resource_name = os.path.basename(csv_file)
    
    try:
        with open(csv_file, encoding='utf-8-sig') as f:
            pkg = reg.action.resource_patch(
                id=resource_id,
                upload=(resource_name, f)
            )
    except:
        print('\tERROR: Publish failed.')

def run_merge_years(yearly_file_path, search_string, publish_file):
    file_list = glob.glob(yearly_file_path + search_string)
    combined_files = pd.concat([pd.read_csv(f, encoding='utf-8-sig', na_filter=False) for f in file_list])
    combined_files.to_csv(publish_file, index=False, encoding='utf-8-sig')
    print('>> Merging {0:s} data into a single file for years {1}'.format(search_string, combined_files['fiscal_yr'].unique()))
