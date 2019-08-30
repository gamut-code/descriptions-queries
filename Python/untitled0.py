# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 16:51:41 2019

@author: xcxg109
"""


import pandas as pd
import numpy as np
import os,glob


folder_path = 'R:\PM\Product Information and Search\Taxonomy\Master Grainger-Gamut Attribute Mapping\Attribute Mapping Project files\MATCHING ATTRIBUTES FINAL_old format.xlsx'


#for filename in glob.glob(os.path.join(folder_path, '*.xlsx')):
#    with open(filename, 'r') as f:

df = pd.read_excel(folder_path, 
                   sheet_name=0, 
                   header=0, 
                   index_col=False, 
                   keep_default_na=True)

#df = df[np.isfinite(df['Identified_Matching_Gamut_Attribute_Name',
 #                      'Identified_Matching_Grainger_Attribute_Name'])]
 
df = df[['Blue-PIM L3 ID', 'Gamut PIM Node ID', 'Grainger Attribute Name',
        'Grainger Attributes by Node.attribute_id', 'Gamut Attribute Name', 'Gamut Attribute ID',
        'CA Identified Matching Gamut Attribute Name (use semi-colon to separate names)',
        'CA Identified Matching Grainger Attribute Name (use semi-colon to separate names)']]

df = df.dropna(subset=['CA Identified Matching Gamut Attribute Name (use semi-colon to separate names)', 
                       'CA Identified Matching Grainger Attribute Name (use semi-colon to separate names)'], 
                        how='all')
