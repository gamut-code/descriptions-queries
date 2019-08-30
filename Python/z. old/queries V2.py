# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 21:16:11 2019

@author: xcxg109
"""

gamut_short_query="""
        WITH RECURSIVE merch AS (
                SELECT  id,
			name,
                    ARRAY[]::INTEGER[] AS ancestors,
                    ARRAY[]::character varying[] AS ancestor_names
                FROM    merchandising_category as category
                WHERE   "parentId" IS NULL
                AND category.deleted = false
                 and category.visible = true

                UNION ALL

                SELECT  category.id,
			category.name,
                    merch.ancestors || category."parentId",
                    merch.ancestor_names || parent_category.name
                FROM    merchandising_category as category
                    JOIN merch on category."parentId" = merch.id
                    JOIN merchandising_category parent_category on category."parentId" = parent_category.id
                WHERE   category.deleted = false
			and category.visible = true		
            )

           SELECT tprod."supplierSku" AS "Grainger_SKU"
            , tprod."gtPartNumber" AS "Gamut_SKU"
            , mprod.description AS "Gamut_Description"
            , mprod."merchandisingCategoryId" AS "Gamut_Merch_Node"
            , mcoll.name as "Gamut_Collection"
            
            FROM  merchandising_product as mprod   

            INNER JOIN taxonomy_product AS tprod
                ON tprod.id = mprod."taxonomyProductId"
                AND mprod.deleted = 'f'

            INNER JOIN merchandising_collection_product mcollprod
                ON mprod.id = mcollprod."merchandisingProductId"

            INNER JOIN merchandising_collection as mcoll
                ON mcoll.id = mcollprod."collectionId"

            WHERE tprod.deleted = 'f'
                AND {} IN ({})
            """
            

grainger_basic_query="""
            SELECT item.MATERIAL_NO AS Grainger_SKU
            , cat.SEGMENT_NAME AS L1
            , cat.CATEGORY_ID AS L3
            , cat.CATEGORY_NAME
            , item.PM_CODE
            , yellow.PROD_CLASS_ID AS Gcom_Yellow
            , flat.Web_Parent_Name AS Gcom_Web_Parent
            , yellow.*
		    , flat.*
            , cat.*


            FROM PRD_DWH_VIEW_LMT.ITEM_V AS item

            INNER JOIN PRD_DWH_VIEW_MTRL.CATEGORY_V AS cat
            	ON cat.CATEGORY_ID = item.CATEGORY_ID
        		AND item.DELETED_FLAG = 'N'

            FULL OUTER JOIN PRD_DWH_VIEW_LMT.Prod_Yellow_Heir_Class_View AS yellow
                ON yellow.PRODUCT_ID = item.MATERIAL_NO

            FULL OUTER JOIN PRD_DWH_VIEW_LMT.Yellow_Heir_Flattend_view AS flat
                ON yellow.PROD_CLASS_ID = flat.Heir_End_Class_Code

            WHERE 	item.SALES_STATUS NOT IN ('DG', 'DV', 'WV', 'WG')
            	AND {} IN ({})
            """
            
    
grainger_discontinued_query="""
            SELECT item.MATERIAL_NO AS Grainger_SKU
            , cat.SEGMENT_NAME AS L1
            , cat.CATEGORY_ID AS L3
            , cat.CATEGORY_NAME
            , item.PM_CODE
            , item.SALES_STATUS
            , yellow.PROD_CLASS_ID AS Gcom_Yellow
            , flat.Web_Parent_Name AS Gcom_Web_Parent

            FROM PRD_DWH_VIEW_LMT.ITEM_V AS item

            INNER JOIN PRD_DWH_VIEW_MTRL.CATEGORY_V AS cat
            	ON cat.CATEGORY_ID = item.CATEGORY_ID
        		AND item.DELETED_FLAG = 'N'

            FULL OUTER JOIN PRD_DWH_VIEW_LMT.Prod_Yellow_Heir_Class_View AS yellow
                ON yellow.PRODUCT_ID = item.MATERIAL_NO

            FULL OUTER JOIN PRD_DWH_VIEW_LMT.Yellow_Heir_Flattend_view AS flat
                ON yellow.PROD_CLASS_ID = flat.Heir_End_Class_Code

            WHERE {} IN ({})
            """
            
            
            
grainger_short_query="""
            SELECT item.MATERIAL_NO AS Grainger_SKU
            , cat.SEGMENT_NAME AS L1
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
            	AND {} IN ({})
            """

grainger_attr_query="""
           	SELECT cat.SEGMENT_NAME AS L1
            , cat.FAMILY_NAME AS L2
            , cat.CATEGORY_NAME
            , cat.CATEGORY_ID AS L3
            , item.MATERIAL_NO AS Grainger_SKU
            , item.MFR_MODEL_NO AS Mfr_Part_No
            , attr.DESCRIPTOR_NAME AS Attribute
            , item_attr.ITEM_DESC_VALUE AS Attribute_Value
            , cat_desc.ENDECA_RANKING
            , item.PM_CODE AS PM_Code
            , yellow.PROD_CLASS_ID AS Yellow_ID


            FROM PRD_DWH_VIEW_MTRL.ITEM_DESC_V AS item_attr

            INNER JOIN PRD_DWH_VIEW_MTRL.ITEM_V AS item
                ON 	item_attr.MATERIAL_NO = item.MATERIAL_NO
                AND item.DELETED_FLAG = 'N'
                AND item_attr.DELETED_FLAG = 'N'
                AND item_attr.LANG = 'EN'
                AND item.PRODUCT_APPROVED_US_FLAG = 'Y'

            INNER JOIN PRD_DWH_VIEW_MTRL.CATEGORY_V AS cat
                ON cat.CATEGORY_ID = item_attr.CATEGORY_ID
                AND item_attr.DELETED_FLAG = 'N'
                AND item.PM_CODE NOT IN ('R9')
                AND item.PM_CODE NOT IN ('R4')

            INNER JOIN PRD_DWH_VIEW_MTRL.CAT_DESC_V AS cat_desc
                ON cat_desc.CATEGORY_ID = item_attr.CATEGORY_ID
                AND cat_desc.DESCRIPTOR_ID = item_attr.DESCRIPTOR_ID
                AND cat_desc.DELETED_FLAG='N'

            INNER JOIN PRD_DWH_VIEW_MTRL.MAT_DESCRIPTOR_V AS attr
                ON attr.DESCRIPTOR_ID = item_attr.DESCRIPTOR_ID
                AND attr.DELETED_FLAG = 'N'

            INNER JOIN PRD_DWH_VIEW_LMT.Prod_Yellow_Heir_Class_View AS yellow
                ON yellow.PRODUCT_ID = item.MATERIAL_NO

            WHERE item.SALES_STATUS NOT IN ('DG', 'DV', 'WV', 'WG')
                AND {} IN ({})
            """