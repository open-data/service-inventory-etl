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

def parse_obligation(o):
    return True if o == 'Mandatory' else False

def run_conversion(base_git_url, resource_id, yaml_file, json_schema_file):
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

    for f in yaml_object['resources'][resource_id]['fields']:
        constraints_list = []
        constraints_entry = {}
        valid_choices = []
        is_required = False

        if 'import_template_include' in f.keys() and f['import_template_include'] is False:
            print('\tSKIP: {0} should not be included in the import file'.format(f['datastore_id']))
            continue

        try:
            if 'choices' in f.keys():
                valid_choices = list(f['choices'].keys())
            if 'choices_file' in f.keys():
                c = yaml.full_load(urllib.request.urlopen(yaml_base_path + f['choices_file']))
                valid_choices = list(c.keys())
        except:
            print('\tERROR: Problem extracting supplied choices for {0}'.format(f['datastore_id']))
            pass

        try:
            if 'obligation' in f.keys():
                o = f['obligation']
            else:
                o = 'Optional'
            is_required = parse_obligation(o)
        except:
            print('\tERROR: Problem extracting obligation for {0}'.format(f['datastore_id']))
            pass

        try:
            if is_required or len(valid_choices) > 0:
                constraints_entry = {'required': is_required}
                if len(valid_choices) > 0:
                    constraints_entry['enum'] = valid_choices
                constraints_list.append(constraints_entry)
        except:
            print('\tERROR: Problem building the constraints entry for {0}'.format(f['datastore_id']))
            pass
            
        try:
            fields_entry = {
                'name': f['datastore_id'],
                'type': f['datastore_type']
            }

            if len(constraints_list) > 0:
                fields_entry['constraints'] = constraints_list

            fields_list.append(fields_entry)
        except:
            print('\tERROR: Problem building the fields entry for {0}'.format(f['datastore_id']))
            pass

    yaml_json = {'fields': fields_list}

    with open(json_schema_file, 'w') as outfile:
        json.dump(yaml_json, outfile)
