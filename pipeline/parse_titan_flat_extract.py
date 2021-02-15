import pandas as pd
import sys, math

# Takes in a year integer and returns a year range string (2018 becomes "2018-2019")
def process_year_to_range(year):
    if year == '' or type(year) is float and math.isnan(year):
        return ''
    else:
        return str(int(year)) + '-' + str(int(year+1))


# Takes in a dictionary and an index (or list of indicies) and returns a comma separated list as a string
def process_lookup_map(val, lookup, default_value):
    if type(val) is not str or val == '':
        return default_value
    return_list = []
    for v in val.split('<>'):
        try:
            if v != '':
                return_list.append(lookup[v])
        except:
            print('\tERROR: Unable to find code in lookup for value: {0}'.format(v))
    return ','.join(return_list)

# Special condition to filter certain designations.  Could otherwise use the generic process_lookup_map() function
def process_designations(designations):
    designation_lookup = {
        'Priority Service': 'prior',
        'Essential Service': 'essent',
        'None': 'non',
        '': 'non'
    }
    designation_list = []
    for d in designations.split('<>'):
        try:
            designation_list.append(designation_lookup[d])
        except:
            if d != 'Critical Service':
                print('\tERROR: Unable to find designation code for value: {0}'.format(d))

    return_list = list(dict.fromkeys(designation_list))
    if len(return_list) == 0:
        return_list.append('non')
    return ','.join(return_list)


# Takes a list and swaps the '<>' delimiter for the ','
def process_list_restructure(bad_list):
    good_list = []
    if type(bad_list) is not str:
        return ''
    for u in bad_list.split('<>'):
        try:
            good_list.append(u)
        except:
            print('\tERROR: Problem appending value to list: {0}'.format(u))
    return ','.join(good_list)


def process_num_or_ND(count):
    if count == '' or type(count) is float and math.isnan(count):
        return 'ND'
    else:
        return count

def process_performance_calculation(total_volume, volume_meeting_target):
    try:
        return round((volume_meeting_target / total_volume)*100,2)
    except:
        return 'ND'

def run_services_transformation(extract_file, output_path, output_file):
    print('>> Loading services data from {0}'.format(extract_file))
    df_services = pd.read_excel(extract_file, sheet_name='Services', encoding='utf-8', na_filter=False)
    select_columns = []
    
    print('>> Building services registry dataset')

    # These lookups get used multiple times
    generic_channel_lookup = {
        'Online':'onl',
        'Telephone':'tel',
        'In-Person':'person',
        'Email':'eml',
        'Fax':'fax',
        'Postal Mail':'post',
        'Other':'oth',
        'None':'non',
        '':'ND'
    }
    yesno_field_lookup = {
        'Yes': 'Y',
        'No': 'N',
        'Not Applicable': 'NA',
        'Enabled': 'Y',
        'Not Enabled': 'N',
        '': 'NA'
    }
    
    # Create fiscal_yr column
    df_services['fiscal_yr'] = df_services['Year'].apply(lambda x: process_year_to_range(x))
    select_columns.append('fiscal_yr')

    # Create service_id column
    df_services['service_id'] = df_services['Service ID']
    select_columns.append('service_id')

    # Create service_name_* columns
    df_services['service_name_en'] = df_services['Service Name (English)']
    select_columns.append('service_name_en')
    df_services['service_name_fr'] = df_services['Service Name (French)']
    select_columns.append('service_name_fr')

    # Create department_name_* columns
    df_services['department_name_en'] = df_services['Applied Titled (English)']
    df_services['department_name_en'] = df_services.apply(lambda x: x['department_name_en'] if x['department_name_en'] != '' else x['Department Name (English)'], axis=1)
    select_columns.append('department_name_en')
    
    df_services['department_name_fr'] = df_services['Applied Title (French)']
    df_services['department_name_fr'] = df_services.apply(lambda x: x['department_name_fr'] if x['department_name_fr'] != '' else x['Department Name (French)'], axis=1)
    select_columns.append('department_name_fr')

    # Create external_internal column
    external_internal_lookup = {
        'External Service':'extern',
        'Internal Service':'intern',
        'Internal Enterprise Service':'enterprise'
    }
    df_services['external_internal'] = df_services['Service scope (English)'].apply(lambda x: process_lookup_map(x, external_internal_lookup, ''))
    select_columns.append('external_internal')

    # Create service type column
    service_type_lookup = {
        'Acquisition Services':'acq',
        'Advisory Services':'adv',
        'Communications Services':'comm',
        'Educational, Recreational and Cultural Encounters':'ecu',
        'Financial Management Services':'fm',
        'Grants and Contributions':'gnc',
        'Human Resources Management':'hr',
        'High Volume Regulatory Transactions (HVRT)':'reg_vol',
        'Information Management Services':'im',
        'Information Technology Services':'its',
        'Legal Services':'legal',
        'Management and Oversight Services':'mgnt',
        'Material Services':'mat',
        'Regulatory Compliance and Enforcement':'reg',
        'Resources':'res',
        'Real Property Services':'prop',
        'Rule Making':'rule'
    }
    df_services['service_type'] = df_services['Service Type (English)'].apply(lambda x: process_lookup_map(x, service_type_lookup, ''))
    select_columns.append('service_type')

    # Create special designations column
    df_services['special_designations'] = df_services['Special Designations (English)'].apply(lambda x: process_designations(x))
    select_columns.append('special_designations')

    # Create service_description_* columns
    df_services['service_description_en'] = df_services['Description (English)']
    select_columns.append('service_description_en')
    df_services['service_description_fr'] = df_services['Description (French)']
    select_columns.append('service_description_fr')

    # Create service_url_* columns
    df_services['service_url_en'] = df_services['URLs (English)'].apply(lambda x: process_list_restructure(x))
    select_columns.append('service_url_en')
    df_services['service_url_fr'] = df_services['URLs (French)'].apply(lambda x: process_list_restructure(x))
    select_columns.append('service_url_fr')

    # Create program_name_* columns
    df_services['program_name_en'] = df_services['Programs (English)'].apply(lambda x: process_list_restructure(x))
    select_columns.append('program_name_en')
    df_services['program_name_fr'] = df_services['Programs (French)'].apply(lambda x: process_list_restructure(x))
    select_columns.append('program_name_fr')

    # Create last_GBA column
    df_services['last_GBA'] = df_services['Year of Last GBA+'].apply(lambda x: process_year_to_range(x))
    select_columns.append('last_GBA')

    # Create digital_id_platform column    
    ident_platform_lookup = {
        'Cyber Auth/ECM - External (Public) credential and authentication (GCKey, CBS)':'ex_auth',
        'Sign In Canada':'signin_authenti',
        'GCpass/ICAS (Internal Centralized Authentication Service)':'gcpass',
        'ICM - Internal (GC worker) credential and authentication service (myKEY)':'in_auth',
        'Provinces, Territories and Communities':'PTC',
        'Other':'oth',
        '':'ND'
    }
    df_services['ident_platform'] = df_services['Digital Identity Platforms (English)'].apply(lambda x: process_lookup_map(x, ident_platform_lookup, ''))
    select_columns.append('ident_platform')

    # Create client_target_groups column
    target_group_lookup = {
        'Persons':'person',
        'Non-Profit Institutions and Organizations':'NGO',
        'Economic Segments':'econom',
        'Foreign Entities':'for',
        'Provinces, Territories and Communities':'PTC',
        'Internal to Government':'intern_gov',
        'Environmental':'enviro',
        '':'ND'
    }
    df_services['client_target_groups'] = df_services['Clients/Target Groups (English)'].apply(lambda x: process_lookup_map(x, target_group_lookup, ''))
    select_columns.append('client_target_groups')

    #Create info_service column
    #TODO: Find out where this data point comes from
    #df_services['info_service'] = df_services['Add Titan Extract Column Name'].apply(lambda x: process_Y_N_NA(x))
    df_services['info_service'] = df_services['Information Service'].apply(lambda x: process_lookup_map(x, yesno_field_lookup, 'NA'))
    select_columns.append('info_service')

    # Create service_fee column
    df_services['service_fee'] = df_services['Collects Fees'].apply(lambda x: process_lookup_map(x, yesno_field_lookup, 'NA'))
    select_columns.append('service_fee')

    # Create cra_business_number column
    df_services['cra_business_number'] = df_services['CRA Business Number is identifier'].apply(lambda x: process_lookup_map(x, yesno_field_lookup, 'NA'))
    select_columns.append('cra_business_number')

    # Create use_of_sin column
    df_services['use_of_sin'] = df_services['SIN is identifier'].apply(lambda x: process_lookup_map(x, yesno_field_lookup, 'NA'))
    select_columns.append('use_of_sin')

    # Create service_channels column
    #TODO: Figure out where this data point comes from
    #df_services['service_channel'] = df_services['Add Titan Extract Column Name'].apply(lambda x: process_lookup_map(x, generic_channel_lookup, ''))
    df_services['service_channels'] = df_services['Channel(s) through which the service is offered (English)'].apply(lambda x: process_lookup_map(x, generic_channel_lookup, ''))
    select_columns.append('service_channels')

    # Create calls_received column
    df_services['calls_received'] = df_services['Telephone Enquiries'].apply(lambda x: process_num_or_ND(x))
    select_columns.append('calls_received')
    
    # Create web_visits_info_service column
    df_services['web_visits_info_service'] = df_services['Website Visits'].apply(lambda x: process_num_or_ND(x))
    select_columns.append('web_visits_info_service')
    
    # Create online_applications column
    df_services['online_applications'] = df_services['Online Applications'].apply(lambda x: process_num_or_ND(x))
    select_columns.append('online_applications')

    # Create telephone_applications column
    df_services['telephone_applications'] = df_services['Telephone Applications'].apply(lambda x: process_num_or_ND(x))
    select_columns.append('telephone_applications')

    # Create in_person_applications column
    df_services['in_person_applications'] = df_services['In Person Applications'].apply(lambda x: process_num_or_ND(x))
    select_columns.append('in_person_applications')

    # Create postal_mail_applications column
    df_services['postal_mail_applications'] = df_services['Mail Applications'].apply(lambda x: process_num_or_ND(x))
    select_columns.append('postal_mail_applications')

    # Create other_applications column
    df_services['other_applications'] = df_services['Other Channel Applications'].apply(lambda x: process_num_or_ND(x))
    select_columns.append('other_applications')

    # Create e_registration column
    df_services['e_registration'] = df_services['Online Account Registration and Enrolment'].apply(lambda x: process_lookup_map(x, yesno_field_lookup, 'NA'))
    select_columns.append('e_registration')

    # Create e_authentication column
    df_services['e_authentication'] = df_services['Online Authentication'].apply(lambda x: process_lookup_map(x, yesno_field_lookup, 'NA'))
    select_columns.append('e_authentication')

    # Create e_application column
    df_services['e_application'] = df_services['Online Authentication'].apply(lambda x: process_lookup_map(x, yesno_field_lookup, 'NA'))
    select_columns.append('e_application')

    # Create e_decision column
    df_services['e_decision'] = df_services['Online Decision'].apply(lambda x: process_lookup_map(x, yesno_field_lookup, 'NA'))
    select_columns.append('e_decision')

    # Create e_issuance column
    df_services['e_issuance'] = df_services['Online Issuance'].apply(lambda x: process_lookup_map(x, yesno_field_lookup, 'NA'))
    select_columns.append('e_issuance')

    # Create e_feedback column
    df_services['e_feedback'] = df_services['Online Issue Resolution'].apply(lambda x: process_lookup_map(x, yesno_field_lookup, 'NA'))
    select_columns.append('e_feedback')

    # Create client_feedback column
    df_services['client_feedback'] = df_services['Feedback Channels (English)'].apply(lambda x: process_lookup_map(x, generic_channel_lookup, ''))
    select_columns.append('client_feedback')

    # Create special_remarks_* columns
    df_services['special_remarks_en'] = df_services['Comments (English)']
    select_columns.append('special_remarks_en')
    df_services['special_remarks_fr'] = df_services['Comments (French)']
    select_columns.append('special_remarks_fr')

    if len(df_services['fiscal_yr'].unique()) > 1:
        sys.exit('More than 1 year found in the SERVICES dataset. Each file should only have a single year to process.  Searate years into multiple files and try again running one extract at a time.')
    else:
        outfile = output_path + df_services['fiscal_yr'].unique()[0] + '_' + output_file

    print('>> Writing services registry dataset to {0}'.format(output_file))
    df_services[select_columns].to_csv(outfile, index=None, header=True, encoding='utf-8-sig')

    return outfile

def run_standards_transformation(extract_file, output_path, output_file):
    print('>> Loading standards data from {0}'.format(extract_file))
    df_standards = pd.read_excel(extract_file, sheet_name='Standards', encoding='utf-8', na_filter=False)
    select_columns = []
    
    print('>> Building standards registry dataset')

    # These lookups get used multiple times
    generic_channel_lookup = {
        'Online':'onl',
        'Telephone':'tel',
        'In-Person':'person',
        'Email':'eml',
        'Fax':'fax',
        'Postal Mail':'post',
        'Other':'oth',
        'None':'non',
        '':'ND'
    }

    # Create fiscal_yr column
    df_standards['fiscal_yr'] = df_standards['Year'].apply(lambda x: process_year_to_range(x))
    select_columns.append('fiscal_yr')

    # Create service_id column
    df_standards['service_id'] = df_standards['Service ID']
    select_columns.append('service_id')

    # Create service_name_* columns
    df_standards['service_name_en'] = df_standards['Service Name (English)']
    select_columns.append('service_name_en')
    df_standards['service_name_fr'] = df_standards['Service Name (French)']
    select_columns.append('service_name_fr')

    # Create service_std_id column
    df_standards['service_std_id'] = df_standards['Standard ID']
    select_columns.append('service_std_id')

    # Create service_std_* columns
    df_standards['service_std_en'] = df_standards['Service Standards (English)']
    select_columns.append('service_std_en')
    df_standards['service_std_fr'] = df_standards['Service Standards (French)']
    select_columns.append('service_std_fr')

    # Create service_std_url_* columns
    df_standards['service_std_url_en'] = df_standards['Standard URLs (English)'].apply(lambda x: process_list_restructure(x))
    select_columns.append('service_std_url_en')
    df_standards['service_std_url_fr'] = df_standards['Standard URLs (French)'].apply(lambda x: process_list_restructure(x))
    select_columns.append('service_std_url_fr')

    # Create service_std_type column
    service_std_type_lookup = {
        'Timeliness':'time',
        'Accuracy':'accur',
        'Access':'acces',
        'Other':'oth',
        'Other (requires explanation)':'oth'
    }
    df_standards['service_std_type'] = df_standards['Standard Type (English)'].apply(lambda x: process_lookup_map(x, service_std_type_lookup, ''))
    select_columns.append('service_std_type')

    # Create target_type column
    target_type_lookup = {
        'Percentage of outcomes':'percentage',
        'Other type of target':'other_type'
    }
    df_standards['target_type'] = df_standards['Target Type'].apply(lambda x: process_lookup_map(x, target_type_lookup, ''))
    select_columns.append('target_type')

    # Create service_std_target column
    df_standards['service_std_target'] = df_standards['Target'].apply(lambda x: process_num_or_ND(x))
    select_columns.append('service_std_target')

    # Create volume_meeting_target column
    df_standards['volume_meeting_target'] = df_standards['Volume Meeting Target'].apply(lambda x: process_num_or_ND(x))
    select_columns.append('volume_meeting_target')

    # Create total_volume column
    df_standards['total_volume'] = df_standards['Total Volume'].apply(lambda x: process_num_or_ND(x))
    select_columns.append('total_volume')

    # Create performance column
    df_standards['performance'] = df_standards.apply(lambda x: process_performance_calculation(x['Total Volume'], x['Volume Meeting Target']), axis=1)
    select_columns.append('performance')

    # Create gcss_tool_fiscal_year column
    df_standards['gcss_tool_fiscal_yr'] = df_standards['Last GCSS Assessment'].apply(lambda x: process_year_to_range(x))
    select_columns.append('gcss_tool_fiscal_yr')

    # Create channel column
    df_standards['channel'] = df_standards['Channel (English)'].apply(lambda x: process_lookup_map(x, generic_channel_lookup, ''))
    select_columns.append('channel')

    # Create standard_channel_comment_* columns
    df_standards['standard_channel_comment_en'] = df_standards['Standard Type Comment (English)']
    select_columns.append('standard_channel_comment_en')
    df_standards['standard_channel_comment_fr'] = df_standards['Standard Type Comment (French)']
    select_columns.append('standard_channel_comment_fr')

    # Create standard_comment_* columns
    df_standards['standard_comment_en'] = df_standards['Comments (English)']
    select_columns.append('standard_comment_en')
    df_standards['standard_comment_fr'] = df_standards['Comments (French)']
    select_columns.append('standard_comment_fr')

    # Create realtime_result_url_* columns
    df_standards['realtime_result_url_en'] = df_standards['RTP URLs (English)'].apply(lambda x: process_list_restructure(x))
    select_columns.append('realtime_result_url_en')
    df_standards['realtime_result_url_fr'] = df_standards['RTP URLs (French)'].apply(lambda x: process_list_restructure(x))
    select_columns.append('realtime_result_url_fr')

    # Create department_name_* columns
    df_standards['department_name_en'] = df_standards['Applied Titled (English)']
    df_standards['department_name_en'] = df_standards.apply(lambda x: x['department_name_en'] if x['department_name_en'] != '' else x['Department Name (English)'], axis=1)
    select_columns.append('department_name_en')
    
    df_standards['department_name_fr'] = df_standards['Applied Title (French)']
    df_standards['department_name_fr'] = df_standards.apply(lambda x: x['department_name_fr'] if x['department_name_fr'] != '' else x['Department Name (French)'], axis=1)
    select_columns.append('department_name_fr')


    if len(df_standards['fiscal_yr'].unique()) > 1:
        sys.exit('More than 1 year found in the STANDARDS dataset. Each file should only have a single year to process.  Searate years into multiple files and try again running one extract at a time.')
    else:
        outfile = output_path + df_standards['fiscal_yr'].unique()[0] + '_' + output_file

    print('>> Writing standards registry dataset to {0}'.format(output_file))
    df_standards[select_columns].to_csv(outfile, index=None, header=True, encoding='utf-8-sig')

    return outfile
