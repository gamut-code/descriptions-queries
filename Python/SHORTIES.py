# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 15:53:41 2019

@author: xcxg109
"""

from gamut_query import GamutQuery
from grainger_query import GraingerQuery
from queries import gamut_short_query, grainger_short_query
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

search_data = fd.data_in(data_type, settings.directory_name, settings.file_name)

if data_type == 'node':
    for k in search_data:
       grainger_df = gcom.grainger_q(grainger_short_query, 'cat.CATEGORY_ID', k)
       gamut_df = gamut_data(grainger_df)
       fd.shorties_data_out(grainger_df, gamut_df, k)
       print(k)
elif data_type == 'sku':
    sku_str = ", ".join("'" + str(i) + "'" for i in search_data)
    grainger_df = gcom.grainger_q(grainger_short_query, 'item.MATERIAL_NO', sku_str)
    gamut_df = gamut_data(grainger_df)
    fd.shorties_data_out(grainger_df, gamut_df, 'SKUs')
    
