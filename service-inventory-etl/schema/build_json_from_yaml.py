import yaml
import urllib.request
import pandas as pd
import json

"""
    Transform the registry YAML file into a JSON Table Schema that can be 
    fed into goodtables to validate

    {
        "type": "table name",
        "fields": [
            {
                "name": "name of field (e.g. column name)",
                "title": "A nicer human readable label or title for the field",
                "type": "A string specifying the type",
                "format": "A string specifying a format",
                "description": "A description for the field",
                "constraints": {
                    "required": True,
                    "enum": [
                        "choice_1", 
                        "choice_2", 
                        "..."
                    ]
                }
            }
        ]
    }
"""

type_lookup = {
    'text': 'string',
    '_text': 'string',
    'numeric': 'number'
}

def run_conversion(base_git_url, resource_id, yaml_file, json_schema_file, json_choices_file):
    yaml_base_path = base_git_url
    yaml_url = yaml_base_path + yaml_file

    print('>> Fetching the YAML from the provided URL')
    try:
        yaml_content = urllib.request.urlopen(yaml_url)
    except:
        print('\tERROR: Unable to load the specified URL')

    print('>> Parsing the YAML file')
    try:
        yaml_object = yaml.full_load(yaml_content)
    except:
        print('\tERROR: Unable to parse the YAML file')

    print('>> Transforming the YAML file to a JSON Schema')
    yaml_json = []
    fields_list = []
    choices_export = {}

    for f in yaml_object['resources'][resource_id]['fields']:
        constraints_list = []
        constraints_entry = {}
        valid_choices = []
        is_required = False

        if 'import_template_include' in f.keys() and f['import_template_include'] is False:
            #print('\tSKIP: {0} should not be included in the import file'.format(f['datastore_id']))
            continue

        try:
            if 'choices' in f.keys():
                valid_choices = list(f['choices'].keys())
            if 'choices_file' in f.keys():
                c = yaml.full_load(urllib.request.urlopen(yaml_base_path + f['choices_file']))
                valid_choices = list(c.keys())
            if len(valid_choices) > 1:
                choices_export[f['datastore_id']] = valid_choices
        except:
            print('\tERROR: Problem extracting supplied choices for {0}'.format(f['datastore_id']))
            pass

        try:
            if 'obligation' in f.keys():
                o = f['obligation']
            else:
                o = 'Optional'
            is_required = True if o == 'Mandatory' else False
        except:
            print('\tERROR: Problem extracting obligation for {0}'.format(f['datastore_id']))
            pass

        try:
            if is_required:
                constraints_entry = {'required': is_required}
                constraints_list.append(constraints_entry)
            """
            if is_required or len(valid_choices) > 0:
                constraints_entry = {'required': is_required}
                if len(valid_choices) > 0:
                    constraints_entry['enum'] = valid_choices
                constraints_list.append(constraints_entry)
            """
        except:
            print('\tERROR: Problem building the constraints entry for {0}'.format(f['datastore_id']))
            pass
            
        try:
            fields_entry = {
                'name': f['datastore_id'],
                'type': type_lookup[f['datastore_type']]
            }

            if len(constraints_list) > 0:
                fields_entry['constraints'] = constraints_list[0]

            fields_list.append(fields_entry)
        except:
            print('\tERROR: Problem building the fields entry for {0}'.format(f['datastore_id']))
            pass

    yaml_json = {'fields': fields_list}

    with open(json_schema_file, 'w') as outfile:
        json.dump(yaml_json, outfile)

    with open(json_choices_file, 'w') as choicefile:
        json.dump(choices_export, choicefile)

# DEBUG
"""
base_git_url = 'https://raw.githubusercontent.com/Jmikelittle/ckanext-canada/DPOR_changes2/ckanext/canada/tables/'
yaml_schema_file = 'service.yaml'
json_schema_file = 'schema/service_table_schema.json'
services_resource_id = 0 
run_conversion(base_git_url, services_resource_id, yaml_schema_file, json_schema_file)
"""