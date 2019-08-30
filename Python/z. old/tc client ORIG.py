# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 13:15:20 2019

@author: xcxg109
"""
import pandas as pd
import os
import re
from graingerio import TeraClient

#read nodes.csv from directory
os.chdir("F:/CGabriel/Grainger_Shorties/OUTPUT")

file_data = [re.split('\s+', i.strip('\n')) for i in open('data.csv')]
node_list = [int(row[0]) for row in file_data[1:]]

node_str = ", ".join(str(i) + "" for i in node_list)

tc = TeraClient()

for k in node_list:
    q = """
      SELECT item.MATERIAL_NO AS Grainger_SKU
        , cat.SEGMENT_NAME AS L1
        , cat.CATEGORY_ID AS L3
        , cat.CATEGORY_NAME
        , item.SHORT_DESCRIPTION AS Item_Description
        , item.GIS_SEO_SHORT_DESC_AUTOGEN AS SEO_Description
        , item.PM_CODE
 		, supplier.SUPPLIER_NAME
		, brand.BRAND_NAME
		, yellow.PROD_CLASS_ID AS Yellow_ID
		, flat.Web_Parent_Name


    FROM PRD_DWH_VIEW_LMT.ITEM_V AS item

    INNER JOIN PRD_DWH_VIEW_MTRL.CATEGORY_V AS cat
    	ON cat.CATEGORY_ID = item.CATEGORY_ID
    		AND item.DELETED_FLAG = 'N'
            AND item.PM_CODE NOT IN ('R9')
            AND item.PM_CODE NOT IN ('R4')

    INNER JOIN PRD_DWH_VIEW_LMT.Prod_Yellow_Heir_Class_View AS yellow
        ON yellow.PRODUCT_ID = item.MATERIAL_NO

    INNER JOIN PRD_DWH_VIEW_LMT.Yellow_Heir_Flattend_view AS flat
         ON yellow.PROD_CLASS_ID = flat.Heir_End_Class_Code

    INNER JOIN PRD_DWH_VIEW_MTRL.BRAND_V AS brand
        ON item.BRAND_NO = brand.BRAND_NO

    INNER JOIN PRD_DWH_VIEW_MTRL.SUPPLIER_V AS supplier
    	ON supplier.SUPPLIER_NO = item.SUPPLIER_NO

    WHERE 	item.SALES_STATUS NOT IN ('DG', 'DV', 'WV', 'WG')
    	AND cat.CATEGORY_ID in {node}
""".format(node=k)
    print (k)
    df = tc.query(q)
    print (df)    
    with open('testdata{}.csv'.format(k), 'w') as output:
        output.write(df)
