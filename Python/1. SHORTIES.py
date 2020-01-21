# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 15:53:41 2019

@author: xcxg109
"""

from gamut_query import GamutQuery
from grainger_query import GraingerQuery
from queries import gamut_short_query, grainger_short_query
import pandas as pd
import file_data as fd
import settings


gcom = GraingerQuery()
gamut = GamutQuery()

def gamut_data(grainger_df):
       sku_list = grainger_df['Grainger_SKU'].tolist()
       gamut_skus = ", ".join("'" + str(i) + "'" for i in sku_list)
       gamut_df = gamut.gamut_q(gamut_short_query, 'tprod."supplierSku"', gamut_skus)
       return gamut_df
    
#determine SKU or node search
data_type = fd.search_type()
search_level = 'cat.CATEGORY_ID'
gamut_df = pd.DataFrame()

if data_type == 'node':
    search_level = fd.blue_search_level()

search_data = fd.data_in(data_type, settings.directory_name)

if data_type == 'node':
    for k in search_data:
        grainger_df = gcom.grainger_q(grainger_short_query, search_level, k)
        if grainger_df.empty == False:
            gamut_df = gamut_data(grainger_df)
            fd.shorties_data_out(settings.directory_name, grainger_df, gamut_df, search_level)
        else:
           print('All SKUs are R4, R9, or discontinued')
        print(k)
elif data_type == 'yellow':
    for k in search_data:
       if isinstance(k, int):#k.isdigit() == True:
           pass
       else:
           k = "'" + str(k) + "'"
       grainger_df = gcom.grainger_q(grainger_short_query, 'yellow.PROD_CLASS_ID', k)
       if grainger_df.empty == False:
           gamut_df = gamut_data(grainger_df)
           fd.shorties_data_out(settings.directory_name, grainger_df, gamut_df, search_level)
       else:
           print('All SKUs are R4, R9, or discontinued')
       print(k)
elif data_type == 'sku':
    search_level = 'SKU'
    sku_str = ", ".join("'" + str(i) + "'" for i in search_data)
    grainger_df = gcom.grainger_q(grainger_short_query, 'item.MATERIAL_NO', sku_str)
    gamut_df = gamut_data(grainger_df)
    fd.shorties_data_out(settings.directory_name, grainger_df, gamut_df, search_level)
    
