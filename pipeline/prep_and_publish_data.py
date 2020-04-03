import pandas as pd
from ckanapi import RemoteCKAN, NotAuthorized
import os

def run_prep_and_publish(csv_file, endpoint, api_key, dataset_id, resource_id, dataset_title):
    print('>>Publishing {0:s}'.format(dataset_title))

    ua = 'prep_and_publish_data.py/1.0 (+{0:s})'.format(endpoint)

    reg = RemoteCKAN(endpoint, apikey=api_key, user_agent=ua)

    resource_name = os.path.basename(csv_file)
    with open(csv_file, encoding='utf-8-sig') as f:
        pkg = reg.action.resource_patch(
            id=resource_id,
            upload=(resource_name, f)
        )