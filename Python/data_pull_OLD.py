# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 16:51:41 2019

@author: xcxg109
"""
import pandas as pd


def get_old_data():
    """all previous attribute matching has been complied into a single file"""
    folder_path = 'R:\PM\Product Information and Search\Taxonomy\Master Grainger-Gamut Attribute Mapping\Attribute Mapping Project files\MATCHING ATTRIBUTES FINAL_old format.xlsx'

    df = pd.read_excel(folder_path, 
                   sheet_name=0, 
                   header=0, 
                   index_col=False, 
                   keep_default_na=True)

    df = df[['Blue-PIM L3 ID', 'Gamut PIM Node ID', 'Grainger Attribute Name',
             'Grainger Attributes by Node.attribute_id', 'Gamut Attribute Name', 'Gamut Attribute ID',
             'CA Identified Matching Gamut Attribute Name (use semi-colon to separate names)',
             'CA Identified Matching Grainger Attribute Name (use semi-colon to separate names)']]

    df = df.dropna(subset=['CA Identified Matching Gamut Attribute Name (use semi-colon to separate names)', 
                           'CA Identified Matching Grainger Attribute Name (use semi-colon to separate names)'], 
                            how='all')

    return df