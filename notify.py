import pandas as pd
df = pd.read_excel('public flat file.xlsx', sheet_name = ['Services', 'Standards'])
df_service = df['Services']
df_standard = df['Standards']

 #Replace blank Applied Titles with Department Name
df_service.loc[pd.isna(df_service['Applied Titled (English)']) == True, 'Consolidated Department Name (English)'] = df_service['Department Name (English)']
df_service.loc[pd.isna(df_service['Applied Titled (English)']) == False, 'Consolidated Department Name (English)'] = df_service['Applied Titled (English)']
df_standard.loc[pd.isna(df_standard['Applied Titled (English)']) == True, 'Consolidated Department Name (English)'] = df_standard['Department Name (English)']
df_standard.loc[pd.isna(df_standard['Applied Titled (English)']) == False, 'Consolidated Department Name (English)'] = df_standard['Applied Titled (English)']
df_service.loc[pd.isna(df_service['Applied Title (French)']) == True, 'Consolidated Department Name (French)'] = df_service['Department Name (French)']
df_service.loc[pd.isna(df_service['Applied Title (French)']) == False, 'Consolidated Department Name (French)'] = df_service['Applied Title (French)']
df_standard.loc[pd.isna(df_standard['Applied Title (French)']) == True, 'Consolidated Department Name (French)'] = df_standard['Department Name (French)']
df_standard.loc[pd.isna(df_standard['Applied Title (French)']) == False, 'Consolidated Department Name (French)'] = df_standard['Applied Title (French)']
    
#Transforming the contact list
contact_list = pd.read_excel('GC Service Inventory Contacts.xlsx', 
                             sheet_name = 'Contacts by department',
                             header = 2)
contact_list = contact_list[contact_list['Main Contact'] == 'Main']
contact_list = pd.merge(contact_list, df_service, 'left', left_on = 'Organization', right_on = 'Consolidated Department Name (English)').loc[:, [
    'Organization', 'Email', 'Name', 'Consolidated Department Name (French)']].drop_duplicates().rename(
    columns = {'Organization':'organization_en', 'Email':'email address', 'Name': 'name', 'Consolidated Department Name (French)': 'organization_fr'})
    
#Fill in blank application counts with 0
app_channel_volumes = ['Telephone Applications','Online Applications','In Person Applications', 'Mail Applications','Other Channel Applications']
df_service[app_channel_volumes] = df_service[app_channel_volumes].apply(pd.to_numeric, errors = 'coerce')
df_service[app_channel_volumes] = df_service.fillna(0)[app_channel_volumes]

   

#Create the dataframe that will eventually be fed to GC Notify
notify = contact_list[['organization_en', 'organization_fr', 'name', 'email address']]

#Create series that will list services that have input errors that will become columns in the notify dataframe
auth_not_enabled_en = df_service.loc[((df_service['Online Authentication'] == 'Not Enabled') | 
                                   (df_service['Online Authentication']  == 'Not Applicable')) &
                                   (df_service['Digital Identity Platforms (English)'].notnull())].groupby(
                                       'Consolidated Department Name (English)')['Service Name (English)'].apply(list).rename('auth_not_enabled_en')
            
auth_enabled_en = df_service.loc[((df_service['Online Authentication'] == 'Enabled') & 
                               (pd.isnull(df_service['Digital Identity Platforms (English)'])))].groupby(
                                   'Consolidated Department Name (English)')[
                                   'Service Name (English)'].apply(list).rename('auth_enabled_en')
           
online_app_not_enabled_en = df_service.loc[((df_service['Online Application'] == 'Not Enabled') |
                                         (df_service['Online Application']  == 'Not Applicable')) & 
                                         (df_service['Online Applications'] > 0)].groupby( 
                                             'Consolidated Department Name (English)')[
                                             'Service Name (English)'].apply(list).rename('online_app_not_enabled_en')
           
online_app_enabled_en = df_service.loc[((df_service['Online Application'] == 'Enabled') &
                                     ((df_service['Online Applications'] == 0) |
                                     (pd.isna(df_service['Online Applications']))))].groupby(
                                         'Consolidated Department Name (English)')[
                                         'Service Name (English)'].apply(list).rename('online_app_enabled_en')
                                             
auth_not_enabled_fr = df_service.loc[((df_service['Online Authentication'] == 'Not Enabled') | 
                                      (df_service['Online Authentication']  == 'Not Applicable')) &
                                      (df_service['Digital Identity Platforms (French)'].notnull())].groupby(
                                          'Consolidated Department Name (French)')['Service Name (French)'].apply(list).rename('auth_not_enabled_fr')
            
auth_enabled_fr = df_service.loc[((df_service['Online Authentication'] == 'Enabled') & 
                                                                      (pd.isnull(df_service['Digital Identity Platforms (French)'])))].groupby(
                                                                   'Consolidated Department Name (French)')[
                                                                   'Service Name (French)'].apply(list).rename('auth_enabled_fr')
           
online_app_not_enabled_fr = df_service.loc[((df_service['Online Application'] == 'Not Enabled') |
                                                                     (df_service['Online Application']  == 'Not Applicable')) & 
                                                                     (df_service['Online Applications'] > 0)].groupby( 
                                                                   'Consolidated Department Name (French)')[
                                                                   'Service Name (French)'].apply(list).rename('online_app_not_enabled_fr')
           
online_app_enabled_fr = df_service.loc[((df_service['Online Application'] == 'Enabled') &
                                                                ((df_service['Online Applications'] == 0) |
                                                                 (pd.isna(df_service['Online Applications']))))].groupby(
                                                                   'Consolidated Department Name (French)')[
                                                                   'Service Name (French)'].apply(list).rename('online_app_enabled_fr') 
                                             
series_list_en = [auth_not_enabled_en, auth_enabled_en, online_app_not_enabled_en, online_app_enabled_en] 
series_list_fr = [auth_not_enabled_fr, auth_enabled_fr, online_app_not_enabled_fr, online_app_enabled_fr]                                                                       
#Add series to notify dataframe
for i in series_list_en:
    notify = pd.merge(notify, i, 'left', left_on = 'organization_en', right_on = 'Consolidated Department Name (English)', right_index = False)  

#Drop rows (departments) that have no input errors
notify = notify.dropna(axis = 0, how = 'all', subset = ['auth_not_enabled_en', 'auth_enabled_en', 'online_app_not_enabled_en', 'online_app_enabled_en'])
notify.reset_index(inplace = True, drop = True)
#Create body of email
notify['body_en'] = ''
for i in range(len(notify.index)):
    if isinstance(notify.auth_not_enabled_en[i], list) == True:
        notify.loc[i, 'body_en'] += ('The following services have "Online Authentication" set to "Not Enabled" but have a digital identity platform listed:' +  
                                 '\n\n') + str('\n'.join(notify.auth_not_enabled_en[i])) + '\n\n'
    if isinstance(notify.auth_enabled_en[i], list) == True:
        notify.loc[i, 'body_en'] += ('The following services have "Online Authentication" set to "Enabled" but do not have a digital identity platform listed:' +  
                                 '\n\n') + str('\n'.join(notify.auth_enabled_en[i])) + '\n\n'
    if isinstance(notify.online_app_not_enabled_en[i], list) == True:
        notify.loc[i, 'body_en'] += ('The following services have "Online Application" set to "Not Enabled" but have greater than 0 online applications:' +  
                                 '\n\n') + str('\n'.join(notify.online_app_not_enabled_en[i])) + '\n\n'
    if isinstance(notify.online_app_enabled_en[i], list) == True:
        notify.loc[i, 'body_en'] += ('The following services have "Online Application" set to "Enabled" but do not have any online applications:' +  
                                 '\n\n') + str('\n'.join(notify.online_app_enabled_en[i])) + '\n\n'
for i in series_list_fr:
    notify = pd.merge(notify, i, 'left', left_on = 'organization_fr', right_on = 'Consolidated Department Name (French)', right_index = False)  

#Drop rows (departments) that have no input errors
notify = notify.dropna(axis = 0, how = 'all', subset = ['auth_not_enabled_fr', 'auth_enabled_fr', 'online_app_not_enabled_fr', 'online_app_enabled_fr'])
notify.reset_index(inplace = True, drop = True)
#Create body of email
notify['body_fr'] = ''
for i in range(len(notify.index)):
    if isinstance(notify.auth_not_enabled_fr[i], list) == True:
        notify.loc[i, 'body_fr'] += ('Les services suivants ont l\'option "Authentification en ligne" réglée sur "Non activé" mais ont une plateforme d\'identité numérique répertoriée :' +  
                                 '\n\n') + str('\n'.join(notify.auth_not_enabled_fr[i])) + '\n\n'
    if isinstance(notify.auth_enabled_fr[i], list) == True:
        notify.loc[i, 'body_fr'] += ('Les services suivants ont l\'option "Authentification en ligne" définie sur "Activé" mais n\'ont pas de plateforme d\'identité numérique répertoriée :' +  
                                 '\n\n') + str('\n'.join(notify.auth_enabled_fr[i])) + '\n\n'
    if isinstance(notify.online_app_not_enabled_fr[i], list) == True:
        notify.loc[i, 'body_fr'] += ('Les services suivants ont l\'option "Demande en ligne" définie sur "Non activé" mais ont plus de 0 demande en ligne :' +  
                                 '\n\n') + str('\n'.join(notify.online_app_not_enabled_fr[i])) + '\n\n'
    if isinstance(notify.online_app_enabled_fr[i], list) == True:
        notify.loc[i, 'body_fr'] += ('Les services suivants ont le paramètre "Application en ligne" défini sur "Activé" mais n\'ont pas d\'application en ligne :' +  
                                 '\n\n') + str('\n'.join(notify.online_app_enabled_fr[i])) + '\n\n'      

#Write notify dataframe to excel
notify.to_excel('notify.xlsx', index = False)

