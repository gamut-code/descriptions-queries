# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 12:40:34 2019

@author: xcxg109
"""
import pandas as pd
from grainger_query import GraingerQuery
from queries import grainger_attr_query, grainger_value_query
import file_data as fd
import settings

gcom = GraingerQuery()


def get_stats(df):
    """return unique values for each attribute with a count of how many times each is used in the node"""
    df['Count'] =1
    stats = pd.DataFrame(df.groupby(['Attribute', 'Attribute_Value'])['Count'].sum())
    return stats


def dict_search(dict, searchfor):
    """search the dictionary of attributes for any key containing the passed in value. Used to look for any 'Item' attributes"""
    total = [value for (key, value) in dict.items() if searchfor in key]
    if len(total) > 1:
        total = max(total)
    return total


def get_fill_rate(df):
    """create a dictionary with attribute name as key and counts as values"""
    analysis = df['Attribute'].value_counts().to_dict()
    total = dict_search(analysis, 'Item')
    df['Fill_Rate %'] = (df.groupby('Attribute')['Attribute'].transform('count')/total)*100
    fill_rate = pd.DataFrame(df.groupby(['Attribute'])['Fill_Rate %'].count()/total*100).reset_index()
    fill_rate = fill_rate.sort_values(by=['Fill_Rate %'], ascending=False)
    df = df[['Attribute', 'ENDECA_RANKING']]
    df = df.drop_duplicates(subset='Attribute')
    fill_rate = fill_rate.merge(df, how= "inner", on=['Attribute'])
 #   fill_rate = fill_rate[['Attribute',	'Fill_Rate %_x', 'ENDECA_RANKING']]
    return fill_rate


#determine SKU or node search
search_level = 'cat.CATEGORY_ID'
data_type = fd.search_type()

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


if data_type == 'node':
    for k in search_data:
        df = gcom.grainger_q(grainger_attr_query, search_level, k)
        if df.empty == False:
            df_stats = get_stats(df)
            df_fill = get_fill_rate(df)
            fd.attr_data_out(settings.directory_name, df, df_stats, df_fill, search_level)
        else:
            print('All SKUs are R4, R9, or discontinued')
        print (k)
elif data_type == 'yellow':
    for k in search_data:
        if isinstance(k, int):#k.isdigit() == True:
            pass
        else:
            k = "'" + str(k) + "'"
        df = gcom.grainger_q(grainger_attr_query, 'yellow.PROD_CLASS_ID', k)
        if df.empty == False:
            df_stats = get_stats(df)
            df_fill = get_fill_rate(df)
            fd.attr_data_out(settings.directory_name, df, df_stats, df_fill, search_level)
        else:
            print('All SKUs are R4, R9, or discontinued')
        print (k)
elif data_type == 'sku':
        sku_str = ", ".join("'" + str(i) + "'" for i in search_data)
        df = gcom.grainger_q(grainger_attr_query, 'item.MATERIAL_NO', sku_str)
        if df.empty == False:
            search_level = 'SKU'
            df_stats = get_stats(df)
            df_fill = get_fill_rate(df)
            fd.attr_data_out(settings.directory_name, df, df_stats, df_fill, search_level)
        else:
            print('All SKUs are R4, R9, or discontinued')
        print(search_data)
elif data_type == 'name':
    for k in search_data:
        if val_type == 'exact':
            if isinstance(k, int):#k.isdigit() == True:
                pass
            else:
                k = "'" + str(k) + "'"
        elif val_type == 'approx':
            k = "'%" + str(k) + "%'"
        df = gcom.grainger_q(grainger_value_query, 'attr.DESCRIPTOR_NAME', k)
        if df.empty == False:
            fd.data_out(settings.directory_name, df, search_level)
        else:
            print('No results returned')
        print(k)
elif data_type == 'value':
    for k in search_data:
        if val_type == 'approx':
            if isinstance(k, int):#k.isdigit() == True:
                pass
            else:
                k = "'" + str(k) + "'"
        elif val_type == 'approx':
            k = "'%" + str(k) + "%'"
        df = gcom.grainger_q(grainger_value_query, 'item_attr.ITEM_DESC_VALUE', k)
        if df.empty == False:
            fd.data_out(settings.directory_name, df, search_level)
        else:
            print('No results returned')
        print(k)
