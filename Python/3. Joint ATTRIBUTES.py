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
    sku_list = grainger_skus['Grainger_SKU'].tolist()
    gamut_skus = ", ".join("'" + str(i) + "'" for i in sku_list)
    gamut_sku_list = gamut.gamut_q15(gamut_basic_query, 'tprod."supplierSku"', gamut_skus)
    
    return gamut_sku_list


def gamut_atts(node):
    df = pd.DataFrame()
    #pull attributes for the next pim node in the gamut list
    df = gamut.gamut_q15(gamut_attr_query, 'tprod."categoryId"', node)
        #df = pd.concat([df, temp_df], axis=0)
    print('Gamut ', node)

    return df


def grainger_process(grainger_df, k):
    """create a list of grainger skus, run through through the gamut_skus query and pull gamut attribute data if skus are present
        concat both dataframs and join them on matching attribute names"""
    df = pd.DataFrame()
    gamut_FINAL = pd.DataFrame()
    
    grainger_skus = grainger_df.drop_duplicates(subset='Grainger_SKU')  #create list of unique grainger skus that feed into gamut query
    
    grainger_df = grainger_df.drop_duplicates(subset=['L3', 'Grainger_Attr_ID'])  #group by L3 and attribute name and keep unique
    grainger_df['Grainger Blue Path'] = grainger_df['L1']+' > '+grainger_df['L2']+' > '+grainger_df['CATEGORY_NAME'] #compile grainger path details
    grainger_df = grainger_df.drop(columns=['Grainger_SKU', 'Grainger_Attribute_Value']) #remove unneeded columns
    grainger_df['Grainger_Attribute_Name'] = grainger_df['Grainger_Attribute_Name'].str.lower()  #prep att name for merge
    
    gamut_sku_list = gamut_skus(grainger_skus) #get gamut sku list to determine pim nodes to pull

    if gamut_sku_list.empty == False:
        #create a dictionary of the unique gamut nodes that corresponde to the grainger node
        gamut_l3 = gamut_sku_list['PIM Terminal Node ID'].unique()  #create list of pim nodes to pull
        for node in gamut_l3:
            gamut_df = gamut_atts(node)  #get gamut attribute values for each gamut_l3 node
            gamut_df = gamut_df.drop_duplicates(subset='Gamut_Attr_ID')  #gamut attribute IDs are unique, so no need to group by pim node before getting unique
            gamut_df = gamut_df.drop(columns=['Gamut_SKU', 'Grainger_SKU'])
            grainger_df['PIM Terminal Node ID'] = int(node)
            gamut_df['L3'] = int(k)  #add grainger L3 column for gamut attributes
            gamut_df['Gamut_Attribute_Name'] = gamut_df['Gamut_Attribute_Name'].str.lower()  #prep att name for merge
            gamut_FINAL = pd.concat([gamut_FINAL, gamut_df], axis=0)
            #create df based on names that match exactly
            temp_df = grainger_df.merge(gamut_df, left_on=['Grainger_Attribute_Name', 'L3', 'PIM Terminal Node ID'], right_on=['Gamut_Attribute_Name', 'L3', 'PIM Terminal Node ID'], how='outer')
            df = pd.concat([df, temp_df], axis=0)

    return df, grainger_df, gamut_FINAL

    
    
#determine SKU or node search
search_level = 'cat.CATEGORY_ID'
data_type = fd.search_type()

gamut_df = pd.DataFrame()
grainger_df = pd.DataFrame()
attribute_df = pd.DataFrame()

gamut_l3 = dict()


if data_type == 'node':
    search_level = fd.blue_search_level()
    
search_data = fd.data_in(data_type, settings.directory_name)

if data_type == 'node':
    for k in search_data:
        grainger_df = gcom.grainger_q(grainger_attr_query, search_level, k)
        if grainger_df.empty == False:
            temp_df, grainger_df, gamut_df  = grainger_process(grainger_df, k)
            attribute_df = pd.concat([attribute_df, temp_df], axis=0)
        else:
            print('No attribute data')
        attribute_df['Grainger-Gamut Terminal Node Mapping'] = attribute_df['CATEGORY_NAME']+' -- '+attribute_df['Gamut Node Name']
        print ('Grainger ', k)

# DO WE NEED THIS? true/false list of whether atts are in common
#        extra_df = [(~grainger_df['Grainger_Attribute_Name'].isin(common_df['Grainger_Attribute_Name']))&
#                    (~gamut_df['Gamut_Attribute_Name'].isin(common_df['Gamut_Attribute_Name']))]
     #   attribute_df = pd.concat([common_df, extra_df], axis=0)
      #  attribute_df = attribute_df.drop(columns=[])
        
        
#grainger_df = grainger_df.drop_duplicates(['L3', 'Grainger_Attr_ID',  'PIM Terminal Node ID', 'Gamut Attr ID'])

outfile = Path(settings.directory_name)/"grainger_test2.xlsx"

outfile2 = Path(settings.directory_name)/"GRAINGER.xlsx"
outfile3 = Path(settings.directory_name)/"GAMUT.xlsx"

#TEMP DROP FOR WORKING
attribute_df = attribute_df.drop(columns=['attribute_level_definition', 'cat_specific_attr_definition', 'Gamut_Attribute_Definition'])
attribute_df.to_excel (outfile, index=None, header=True, encoding='utf-8')

grainger_df.to_excel (outfile2, index=None, header=True, encoding='utf-8')
gamut_df.to_excel (outfile3, index=None, header=True, encoding='utf-8')
