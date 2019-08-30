# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 16:39:52 2019

@author: xcxg109
"""

import pandas as pd
from gamut_query_15 import GamutQuery_15
from grainger_query import GraingerQuery
from queries_PIM import gamut_basic_query, grainger_attr_query, gamut_attr_query
import file_data as fd
import settings
from pathlib import Path


gcom = GraingerQuery()
gamut = GamutQuery_15()


def gamut_skus(grainger_skus):
    #get basic list of gamut SKUs to pull the related PIM nodes
    sku_list = grainger_df['Grainger_SKU'].tolist()
    gamut_skus = ", ".join("'" + str(i) + "'" for i in sku_list)
    gamut_sku_list = gamut.gamut_q15(gamut_basic_query, 'tprod."supplierSku"', gamut_skus)
    
    return gamut_sku_list


def gamut_atts(gamut_l3):
    df = pd.DataFrame()
    #cycle through the gamut_l3 list and pull attributes for each
    for node in gamut_l3:
        temp_df = gamut.gamut_q15(gamut_attr_query, 'tprod."categoryId"', node)
        df = pd.concat([df, temp_df], axis=0)
        print(node)

    return df

#determine SKU or node search
search_level = 'cat.CATEGORY_ID'
data_type = fd.search_type()

gamut_df = pd.DataFrame()
gamut_l3 = dict()


if data_type == 'node':
    search_level = fd.blue_search_level()
    
search_data = fd.data_in(data_type, settings.directory_name)

if data_type == 'node':
    for k in search_data:
        grainger_df = gcom.grainger_q(grainger_attr_query, search_level, k)
        grainger_skus = grainger_df.drop_duplicates(subset='Grainger_SKU')  #create list of unique grainger skus that feed into gamut query       
        grainger_df['Grainger Blue Path'] = grainger_df['L1']+' > '+grainger_df['L2']+' > '+grainger_df['CATEGORY_NAME'] #compile grainger path details
        if grainger_df.empty == False:
            gamut_sku_list = gamut_skus(grainger_skus)
        else:
            print('All SKUs are R4, R9, or discontinued')
        if gamut_sku_list.empty == False:
            #create a dictionary of the unique gamut nodes that corresponde to the grainger node
            gamut_l3 = gamut_sku_list['PIM Terminal Node ID'].unique()
            gamut_df = gamut_atts(gamut_l3)  #get gamut attribute values for each gamut_l3 node
        grainger_df = grainger_df.drop_duplicates(subset=['L3', 'Grainger_Attr_ID'])
        grainger_df['Grainger_Attribute_Name'] = grainger_df['Grainger_Attribute_Name'].str.lower()
        gamut_df = gamut_df.drop_duplicates(subset='Gamut_Attr_ID')
        gamut_df['Gamut_Attribute_Name'] = gamut_df['Gamut_Attribute_Name'].str.lower()
        common_df = grainger_df.merge(gamut_df, left_on=['Grainger_Attribute_Name'], right_on=['Gamut_Attribute_Name'], how='outer')
        extra_df = [(~grainger_df['Grainger_Attribute_Name'].isin(common_df['Grainger_Attribute_Name']))&
                    (~gamut_df['Gamut_Attribute_Name'].isin(common_df['Gamut_Attribute_Name']))]
     #   attribute_df = pd.concat([common_df, extra_df], axis=0)
        attribute_df = common_df
        attribute_df['Grainger-Gamut Terminal Node Mapping'] = attribute_df['CATEGORY_NAME']+' -- '+attribute_df['Gamut Node Name']
        print (k)       
        
#grainger_df = grainger_df.drop_duplicates(['L3', 'Grainger_Attr_ID',  'PIM Terminal Node ID', 'Gamut Attr ID'])

outfile = Path(settings.directory_name)/"grainger_test2.xlsx"
attribute_df.to_excel (outfile, index=None, header=True, encoding='utf-8')

