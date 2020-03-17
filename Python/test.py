 # -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from graingerio import TeraClient
import time


tc = TeraClient()

#def test_query(search, k):
test_q="""
    SELECT cat.SEGMENT_ID AS Segment_ID
      , cat.SEGMENT_NAME AS Segment_Name
      , cat.FAMILY_ID AS Family_ID
      , cat.FAMILY_NAME AS Family_Name
      , cat.CATEGORY_ID AS Category_ID
      , cat.CATEGORY_NAME AS Category_Name
      , yellow.*

            
FROM PRD_DWH_VIEW_MTRL.ITEM_DESC_V AS item_attr

INNER JOIN PRD_DWH_VIEW_MTRL.ITEM_V AS item
    ON 	item_attr.MATERIAL_NO = item.MATERIAL_NO
    AND item.DELETED_FLAG = 'N'
    AND item_attr.DELETED_FLAG = 'N'
    AND item_attr.LANG = 'EN'
    AND item.PRODUCT_APPROVED_US_FLAG = 'Y'

LEFT OUTER JOIN PRD_DWH_VIEW_LMT.Prod_Yellow_Heir_Class_view AS yellow
    ON item.PRODUCT_APPROVED_US_FLAG = 'Y'
    AND item.MATERIAL_NO = yellow.PRODUCT_ID

INNER JOIN PRD_DWH_VIEW_MTRL.CATEGORY_V AS cat
    ON cat.CATEGORY_ID = item_attr.CATEGORY_ID
    AND item_attr.DELETED_FLAG = 'N'
    AND item.PM_CODE NOT IN ('R9')

WHERE {term} IN ({k})
""".format(term='cat.CATEGORY_ID', k=8353)

start_time = time.time()
print('working...')

grainger_df = tc.query(test_q)

grainger_df.to_csv ('F:/CGabriel/Grainger_Shorties/OUTPUT/TEST OUTPUT.csv')

print("--- {} seconds ---".format(round(time.time() - start_time, 2)))

