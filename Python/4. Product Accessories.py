# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 12:03:35 2019

@author: xcxg109
"""

import file_data as fd
import settings
import time
import pandas as pd
from grainger_query import GraingerQuery
from queries import grainger_product_accessories

gcom = GraingerQuery()

grainger_df = pd.DataFrame()

quer = 'PROD_ACCESSORIES'
search_level = 'PRD_DWH_VIEW_MTRL.ITEM_V.CATEGORY_ID'

data_type = fd.search_type()

if data_type == 'node':
    search_level = fd.blue_search_level()

if search_level == 'cat.SEGMENT_ID':
    search_level = 'PRD_DWH_VIEW_MTRL.CATEGORY_V.SEGMENT_ID'
elif search_level == 'cat.FAMILY_ID':
    search_level = 'PRD_DWH_VIEW_MTRL.CATEGORY_V.FAMILY_ID'    
elif search_level == 'cat.CATEGORY_ID':
    search_level = 'PRD_DWH_VIEW_MTRL.ITEM_V.CATEGORY_ID'

search_data = fd.data_in(data_type, settings.directory_name)

start_time = time.time()
print('working...')


if data_type == 'node':
    if search_level == 'cat.CATEGORY_ID':
        for k in search_data:
            temp_df = gcom.grainger_q(grainger_product_accessories, search_level, k)
            grainger_df = pd.concat([grainger_df, temp_df], axis=0)

            if temp_df.empty == True:
                print('{} No accessories  in node'.format(k))
            print(k)

            grainger_df = grainger_df.sort_values(['SEGMENT_NAME', 'CATEGORY_NAME', 'Grainger_SKU', 'Accessory_Status'], ascending=[True, True, True, True])
            fd.data_out(settings.directory_name, grainger_df, search_level, quer)

            print("--- {} seconds ---".format(round(time.time() - start_time, 2)))
    else:
        for k in search_data:
            grainger_df = gcom.grainger_q(grainger_product_accessories, search_level, k)

            if grainger_df.empty == True:
                print('{} No accessories in node'.format(k))

            grainger_df = grainger_df.sort_values(['SEGMENT_NAME', 'CATEGORY_NAME', 'Grainger_SKU', 'Accessory_Status'], ascending=[True, True, True, True])
            fd.data_out(settings.directory_name, grainger_df, search_level, quer)
            print(k)
            print("--- {} seconds ---".format(round(time.time() - start_time, 2)))
            
elif data_type == 'sku':
    search_level = 'SKU'
    sku_str = ", ".join("'" + str(i) + "'" for i in search_data)
    grainger_df = gcom.grainger_q(grainger_product_accessories, 'PRD_DWH_VIEW_MTRL.ITEM_V.MATERIAL_NO', sku_str)
    if grainger_df.empty == False:
        fd.data_out(settings.directory_name, grainger_df, search_level, quer)
    else:
        print('No SKU data for ', sku_str)