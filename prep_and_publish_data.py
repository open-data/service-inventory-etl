import pandas as pd

def convert_csv_to_json(csv_file):
    df_csvinput = pd.read_csv(csv_file, encoding='utf-8')
    return df_csvinput.to_json(orient='records')

def run_prep_and_publish(csv_file):
    dataset_resource_id = 'someguid'
    records_json = convert_csv_to_json(csv_file)

    """
    ckan = RemoteCKAN('https://registry-staging.open.canada.ca', apikey='somekey')
    publish_result = ckan.action.datastore.upsert(
        resource_id=dataset_resource_id,
        records=records_json
    )
    """

# Debug
# run_prep_and_publish('data/registry_output.csv')