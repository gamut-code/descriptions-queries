 # -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from graingerio import TeraClient

tc = TeraClient()

#def test_query(search, k):
test_q="""
        SELECT
            TRIM (PRD_DWH_VIEW_MTRL.ITEM_V.MATERIAL_NO)
        FROM
            PRD_DWH_VIEW_MTRL.CATEGORY_V RIGHT JOIN PRD_DWH_VIEW_MTRL.ITEM_V ON PRD_DWH_VIEW_MTRL.CATEGORY_V.CATEGORY_ID=PRD_DWH_VIEW_MTRL.ITEM_V.CATEGORY_ID
        WHERE
            ( PRD_DWH_VIEW_MTRL.ITEM_V.DELETED_FLAG = 'N'  )
                AND  ( PRD_DWH_VIEW_MTRL.ITEM_V.PRODUCT_APPROVED_US_FLAG = 'Y'  )
                AND  
                {term}  IN ({k})
""".format(term='PRD_DWH_VIEW_MTRL.CATEGORY_V.FAMILY_ID', k=25719)


#gcom = GraingerQuery()

grainger_df = tc.query(test_q)
#grainger_df = tc.query(test_query('PRD_DWH_VIEW_MTRL.CATEGORY_V.SEGMENT_ID', 1035)

#fd.data_out(settings.directory_name, grainger_df, 'test')

#, 'cat.SEGMENT_ID'