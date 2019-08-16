# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 12:40:34 2019

@author: xcxg109
"""
import pandas as pd
from gamut_query_15 import GamutQuery_15
from queries_gamut import gamut_attr_query
import gamut_file_data as gfd
import settings
from pathlib import Path


gamut = GamutQuery_15()
directory_name = "F:/CGabriel/Grainger_Shorties/OUTPUT"


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

search_level = 'tprod."categoryId"'
data_type = gfd.gamut_search_type()

if data_type == 'node':
    search_level = 'tprod."categoryId"'
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
    
search_data = gfd.gamut_data_in(data_type, settings.directory_name)


if data_type == 'node':
    for k in search_data:
        df = gamut.gamut_q15(gamut_attr_query, search_level, k)
        if df.empty == False:
            #df_stats = get_stats(df)
            #df_fill = get_fill_rate(df)
            #gfd.attr_data_out(settings.directory_name, df, df_stats, df_fill, search_level)
            outfile = Path(directory_name)/"{} TEST ATTRIBUTES.xlsx".format(k)   #set directory path and name output file
            df.to_excel (outfile, index=None, header=True, encoding='utf-8')
        else:
            print('All SKUs are R4, R9, or discontinued')
        print (k)
elif data_type == 'org':
    for k in search_data:
        if isinstance(k, int):#k.isdigit() == True:
            pass
        else:
            k = "'" + str(k) + "'"
        df = gamut.gamut_q15(gamut_attr_query, 'yellow.PROD_CLASS_ID', k)
        if df.empty == False:
            df_stats = get_stats(df)
            df_fill = get_fill_rate(df)
            gfd.attr_data_out(settings.directory_name, df, df_stats, df_fill, search_level)
        else:
            print('All SKUs are R4, R9, or discontinued')
        print (k)
elif data_type == 'sku':
        sku_str = ", ".join("'" + str(i) + "'" for i in search_data)
        df = gamut.gamut_q15(gamut_attr_query, 'item.MATERIAL_NO', sku_str)
        if df.empty == False:
            search_level = 'SKU'
            df_stats = get_stats(df)
            df_fill = get_fill_rate(df)
            gfd.attr_data_out(settings.directory_name, df, df_stats, df_fill, search_level)
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
        df = gamut.gamut_q15(gamut_attr_query, 'attr.DESCRIPTOR_NAME', k)
        if df.empty == False:
            gfd.data_out(settings.directory_name, df, search_level)
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
        df = gamut.gamut_q15(gamut_attr_query, 'item_attr.ITEM_DESC_VALUE', k)
        if df.empty == False:
            gfd.data_out(settings.directory_name, df, search_level)
        else:
            print('No results returned')
        print(k)
