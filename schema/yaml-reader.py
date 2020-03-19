import yaml
import urllib.request
import pandas as pd

yaml_base_path = 'https://raw.githubusercontent.com/open-data/ckanext-canada/65b4727c8ac07519530969a231f55d7adaff6e9b/ckanext/canada/tables/'
yaml_url = yaml_base_path + 'service.yaml'

yaml_content = urllib.request.urlopen(yaml_url)
yaml_object = yaml.full_load(yaml_content)

yaml_columns = []

for f in yaml_object['resources'][0]['fields']:
    if 'import_template_include' in f.keys() and f['import_template_include'] is False:
        print('SKIP: {0} should not be included in the import file'.format(f['datastore_id']))
        continue

    valid_choices = []

    try:
        if 'choices' in f.keys():
            print(f['choices'].keys())
            valid_choices = list(f['choices'].keys())
        if 'choices_file' in f.keys():
            c = yaml.full_load(urllib.request.urlopen(yaml_base_path + f['choices_file']))
            print(c.keys())
            valid_choices = list(c.keys())
    except:
        print('ERROR: Problem extracting supplied choices for {0}'.format(f['datastore_id']))
        pass

    try:
        if 'obligation' in f.keys():
            o = f['obligation']
        else:
            o = 'Optional'
        dict_entry = {
            'column_name': f['datastore_id'],
            'obligation': o,
            'data_type': f['datastore_type'],
            'valid_choices': valid_choices
        }
        yaml_columns.append(dict_entry)
    except:
        print('ERROR: Problem appending entry for {0}'.format(f['datastore_id']))
        pass

df_expected_column_definitions = pd.DataFrame(yaml_columns)

print('Column Name Unique Values:\t{0}'.format(df_expected_column_definitions['column_name'].unique()))
print('Obligation Unique Values:\t{0}'.format(df_expected_column_definitions['obligation'].unique()))
print('Data Type Unique Values:\t{0}'.format(df_expected_column_definitions['data_type'].unique()))

print(yaml_columns)

#for line in yaml_content:
#    print(line)

#with open(yaml_file, encoding='utf-8') as f:
#    print(f.read())

#yaml_object = yaml.full_load(yaml_file)

#print(yaml_object)