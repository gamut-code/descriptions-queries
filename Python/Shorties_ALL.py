# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 16:29:44 2019

@author: xcxg109
"""

from grainger_query import GraingerQuery
#from queries import grainger_short_query
import pandas as pd
import datetime

gcom = GraingerQuery()


#pull item and SEO descrpitions from the grainger teradata material universe
grainger_short_query="""
            SELECT item.MATERIAL_NO AS Grainger_SKU
            , cat.SEGMENT_ID AS L1
            , cat.SEGMENT_NAME
            , cat.FAMILY_ID AS L2
            , cat.FAMILY_NAME
            , cat.CATEGORY_ID AS L3
            , cat.CATEGORY_NAME
            , item.SHORT_DESCRIPTION AS Item_Description
            , item.GIS_SEO_SHORT_DESC_AUTOGEN AS SEO_Description
            , item.PM_CODE
            , yellow.PROD_CLASS_ID AS Gcom_Yellow
            , flat.Web_Parent_Name AS Gcom_Web_Parent

            FROM PRD_DWH_VIEW_LMT.ITEM_V AS item

            INNER JOIN PRD_DWH_VIEW_MTRL.CATEGORY_V AS cat
            	ON cat.CATEGORY_ID = item.CATEGORY_ID
        		AND item.DELETED_FLAG = 'N'
                AND item.PRODUCT_APPROVED_US_FLAG = 'Y'
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

            WHERE --item.GIS_SEO_SHORT_DESC_AUTOGEN IS NULL
                 item.SALES_STATUS NOT IN ('DG', 'DV', 'WV', 'WG')
            """


print('working...')
print(datetime.datetime.now())

df = gcom.grainger_q(grainger_short_query, 'yellow.PROD_CLASS_ID', 0)

print(df.info())
print(datetime.datetime.now())
df.to_excel('F:\CGabriel\Grainger_Shorties\OUTPUT\SHORTIES_all.xlsx')