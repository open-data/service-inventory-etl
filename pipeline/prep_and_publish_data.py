import pandas as pd

def convert_csv_to_json(csv_file):
    df_csvinput = pd.read_csv(csv_file, encoding='utf-8')
    return df_csvinput.to_json(orient='records')

def run_prep_and_publish(csv_file, endpoint, apikey, dataset_id, resource_id):
    print('checkpoint')

    """
    ckan = RemoteCKAN('https://registry-staging.open.canada.ca', apikey='somekey')
    publish_result = ckan.action.datastore.upsert(
        resource_id=dataset_resource_id,
        records=records_json
    )
    """

# Debug
# run_prep_and_publish('data/registry_output.csv')
#https://registry.open.canada.ca/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c