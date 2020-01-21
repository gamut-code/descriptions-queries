 # -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
from graingerio import TeraClient
import time


tc = TeraClient()

#def test_query(search, k):
test_q="""
   	SELECT 
		item.MATERIAL
		, cat.CATALOG_INDEX_LEVEL1_IEN AS TDLMT2_level1
		, cat.CATALOG_INDEX_LEVEL2_IEN AS TDLMT2_Level2
		, cat.CATALOG_INDEX_LEVEL3_IEN AS TDLMT2_Level3
		, brand.CATALOG_INDEX_LEVEL1_IEN AS Brand_INDEX_LEVEL1
		, brand.CATALOG_INDEX_LEVEL2_IEN AS Brand_INDEX_LEVEL2
        , cat2.CATALOG_INDEX_LEVEL1_IEN AS TDLMT_level1
        , cat2.CATALOG_INDEX_LEVEL2_IEN AS TDLMT_level2
        , cat2.CATALOG_INDEX_LEVEL3_IEN AS TDLMT_level3
		, page.CATALOG_2020_PAGE AS Catalog_128
        , category.*

FROM PRD_DWH_VIEW_LMT.AGI_CATALOG_INDEX_V AS cat

INNER JOIN PRD_DWH_VIEW_LMT.AGI_Item_V AS item
	ON 	cat.MATERIAL = item.MATERIAL

LEFT OUTER JOIN PRD_DWH_VIEW_LMT.AGI_ITEM_CATALOG_PAGE_V AS page
	ON page.MATERIAL = cat.MATERIAL
	
LEFT OUTER JOIN PRD_DWH_VIEW_LMT.AGI_CAT_BRAND_INDEX_V AS brand
	ON brand.MATERIAL = page.MATERIAL

LEFT OUTER JOIN PRD_DWH_VIEW_MTRL.AGI_CATALOG_INDEX_V AS cat2
    ON cat2.MATERIAL = cat.MATERIAL

LEFT OUTER JOIN PRD_DWH_VIEW_MTRL.CATEGORY_V AS category
    ON category.CATEGORY_ID = item.CATEGORY_ID
WHERE item.MATERIAL in ('AOSC271')
"""

start_time = time.time()
print('working...')

grainger_df = tc.query(test_q)

grainger_df.to_csv ('F:/CGabriel/Grainger_Shorties/OUTPUT/TEST OUTPUT.csv')

print("--- {} seconds ---".format(round(time.time() - start_time, 2)))

