# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 12:40:34 2019

@author: xcxg109
"""
import pandas as pd
from grainger_query import GraingerQuery
from queries import grainger_ONLY_discontinueds, grainger_value_query
import file_data as fd
import settings
import time

gcom = GraingerQuery()


def pull_skus(query_type, search_level, k):
    grainger_df = gcom.grainger_q(query_type, search_level, k)
    
    # remove Zoro SKUs (R9, RMC code = L15)
    dropIndex = grainger_df[(grainger_df['PM_Code'] == 'R9') & (grainger_df['RMC'] == 'L15')].index
    grainger_df.drop(dropIndex, inplace=True)

    grainger_df = grainger_df.sort_values(by=['SEGMENT_NAME', 'FAMILY_NAME', 'CATEGORY_NAME', 'Grainger_SKU'], ascending=True)

    item_df = grainger_df[grainger_df['Grainger_Attribute_Name'].str.contains('Item')]
    item_df = item_df.drop_duplicates(subset=['Grainger_SKU'])
    item_df = drop_cols(item_df)

    grainger_df[~grainger_df['Attribute_Value'].str.contains('Item', na=False)]
    grainger_df.drop(item_df.index, axis=0, inplace=True)
    grainger_df = grainger_df.drop_duplicates(subset=['Grainger_SKU'])
    grainger_df = drop_cols(grainger_df)
      
    if grainger_df.empty == False:
        fd.data_out(settings.directory_name, grainger_df, search_level, 'OTHER_ATTR_discont')
    if item_df.empty == False:
        fd.data_out(settings.directory_name, item_df, search_level, 'ITEM_discont')
    else:
        print('Node {}: no discontinued skus'.format(k))
    
    print("--- {} seconds ---".format(round(time.time() - start_time, 2)))


def drop_cols(df):
    if 'Attribute_Value' in df.columns:
        df.drop(['Attribute_Value'], axis=1, inplace=True)
    if 'Grainger_Attribute_Name' in df.columns:
        df.drop(['Grainger_Attribute_Name'], axis=1, inplace=True)

    return df

#determine SKU or node search
search_level = 'cat.CATEGORY_ID'
data_type = fd.search_type()
query_type = grainger_ONLY_discontinueds
grainger_df = pd.DataFrame()
item_df = pd.DataFrame()

if data_type == 'node':
    search_level = fd.blue_search_level()
elif data_type == 'value' or data_type == 'name':
    while True:
        try:
            val_type = input('Search Type?:\n1. Exact value \n2. Value contained in field ')
            if val_type in ['1', 'EXACT', 'exact', 'Exact']:
                val_type = 'exact'
                break
            elif val_type in ['2', '%']:
                val_type = 'approx'
                break
        except ValueError:
            print('Invalid search type')
    
search_data = fd.data_in(data_type, settings.directory_name)
quer = 'DISC'

start_time = time.time()
print('working...')

if data_type == 'node':
    for k in search_data:
        pull_skus(query_type, search_level, k)
        print(k)
    
elif data_type == 'yellow':
    search_level = 'yellow.PROD_CLASS_ID'
    for k in search_data:
        if isinstance(k, int):#k.isdigit() == True:
            pass
        else:
            k = "'" + str(k) + "'"
        temp_df = pull_skus(query_type, search_level, k)
        grainger_df = pd.concat([grainger_df, temp_df], axis=0, sort=False)

        
elif data_type == 'sku':
    search_level = 'item.MATERIAL_NO'
    query_type = grainger_attr_query
    
    sku_str = ", ".join("'" + str(i) + "'" for i in search_data)
    grainger_df = pull_skus(query_type, search_level, k)

elif data_type == 'name':
    search_level = 'attr.DESCRIPTOR_NAME'
    query_type = grainger_value_query

    for k in search_data:
        if val_type == 'exact':
            if isinstance(k, int):  #k.isdigit() == True:
                pass
            else:
                k = "'" + str(k) + "'"
        elif val_type == 'approx':
            k = "'%" + str(k) + "%'"
        temp_df = pull_skus(query_type, search_level, k)
        grainger_df = pd.concat([grainger_df, temp_df], axis=0, sort=False)

elif data_type == 'value':
    search_level = 'item_attr.ITEM_DESC_VALUE'
    query_type = grainger_value_query

    for k in search_data:
        if val_type == 'exact':
            if isinstance(k, int):  #k.isdigit() == True:
                pass
            else:
                k = "'" + str(k) + "'"
        elif val_type == 'approx':
            k = "'%" + str(k) + "%'"
        temp_df = pull_skus(query_type, search_level, k)
        grainger_df = pd.concat([grainger_df, temp_df], axis=0, sort=False)
        

