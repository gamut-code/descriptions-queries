# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 11:03:25 2019

@author: xcxg109
"""
from grainger_query import GraingerQuery
from queries import cat_definition_query
import pandas as pd
import file_data as fd
import settings


def generate_data():
    gcom = GraingerQuery()

    #request the type of data to pull: blue or yellow, SKUs or node, single entry or read from file
    data_type = fd.search_type()
    search_level = 'cat.CATEGORY_ID'
    #if Blue is chosen, determine the level to pull L1 (segment), L2 (family), or L1 (category)
    if data_type == 'node':
        search_level = fd.blue_search_level()

    #ask user for node number/SKU or pull from file if desired    
    search_data = fd.data_in(data_type, settings.directory_name)

    grainger_df = pd.DataFrame()

    if data_type == 'node':
        for k in search_data:
            temp_df = gcom.grainger_q(cat_definition_query, search_level, k)
            grainger_df = pd.concat([grainger_df, temp_df], axis=0)
            print(k)
    return [grainger_df, search_level]


grainger_df, search_level = generate_data()


fd.data_out(settings.directory_name, grainger_df, search_level)