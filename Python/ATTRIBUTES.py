# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 12:40:34 2019

@author: xcxg109
"""
import pandas as pd
from grainger_query import GraingerQuery
from queries import grainger_attr_query
import file_data as fd
import settings

gcom = GraingerQuery()


def get_stats(df):
    """return unique values for each attribute with a count of how many times each is used in the node"""
    df['Count'] =1
    stats = pd.DataFrame(df.groupby(['Attribute', 'Attribute_Value'])['Count'].sum())
    return stats


def get_fill_rate(df):
    analysis = df['Attribute'].value_counts().to_dict()
    total = analysis['Item']
    df['Fill_Rate %'] = (df.groupby('Attribute')['Attribute'].transform('count')/total)*100
    fill_rate = pd.DataFrame(df.groupby(['Attribute'])['Fill_Rate %'].count()/total*100)
    fill_rate = fill_rate.sort_values(by=['Fill_Rate %'], ascending=False)
#    fill_rate = pd.DataFrame(att.size().reset_index(drop=True))
    return fill_rate

    
#determine SKU or node search
data_type = fd.search_type()

search_data = fd.data_in(data_type, settings.directory_name, settings.file_name)

if data_type == 'node':
    for k in search_data:
        df = gcom.grainger_q(grainger_attr_query, 'cat.CATEGORY_ID', k)
        if df.empty == False:
            df_stats = get_stats(df)
            df_fill = get_fill_rate(df)
            fd.attr_data_out(df, df_stats, df_fill, k)
        else:
            print('All SKUs are R4, R9, or discontinued')
        print (k) 