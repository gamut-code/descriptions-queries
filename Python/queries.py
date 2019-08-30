# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 21:16:11 2019

@author: xcxg109
"""

#pull short descriptions from the gamut postgres database
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
       
#pull gamut attributs by SKU to mearch with grainger_df
gamut_attr_query="""
        WITH RECURSIVE tax AS (
                SELECT  id,
            name,
            ARRAY[]::INTEGER[] AS ancestors,
            ARRAY[]::character varying[] AS ancestor_names
                FROM    taxonomy_category as category
                WHERE   "parentId" IS NULL
                AND category.deleted = false

                UNION ALL

                SELECT  category.id,
            category.name,
            tax.ancestors || tax.id,
            tax.ancestor_names || tax.name
                FROM    taxonomy_category as category
                INNER JOIN tax ON category."parentId" = tax.id
                WHERE   category.deleted = false
            )

        SELECT DISTINCT ON (tax_att.name, tprodvalue.value)
            array_to_string(tax.ancestor_names || tax.name,' > ') as "PIM Terminal Node Path"
            , tprod."categoryId" AS "PIM Terminal Node ID"
            , tprod."supplierSku" as "Grainger_SKU"
            , tprod."gtPartNumber" as "Gamut_SKU"
            , tax_att.name as "Attribute Name"
            , tax_att.description as "Attribute Definition"
            , tax_att."unitGroupId" AS "UOM ID"
            , tax_att."dataType" as "Data Type"
            , tprodvalue.value as "Original Value"
            , tprodvalue.unit as "UOM"
            , tprodvalue."valueNormalized" as "Normalized Value"
            , tprodvalue."unitNormalized" as "UOM"
  
        FROM  taxonomy_product tprod

        INNER JOIN tax
            ON tax.id = tprod."categoryId"

        LEFT JOIN  taxonomy_product_attribute_value tprodvalue
            ON tprod.id = tprodvalue."productId"

        LEFT JOIN taxonomy_attribute tax_att
            ON tax_att.id = tprodvalue."attributeId"

        WHERE tprod.deleted = 'f'
            AND {} IN ({})
        """


#get basic SKU list and hierarchy data from Grainger teradata material universe
grainger_basic_query="""
            SELECT item.MATERIAL_NO AS Grainger_SKU
            , cat.SEGMENT_ID AS L1
            , cat.SEGMENT_NAME
            , cat.FAMILY_ID AS L2
            , cat.FAMILY_NAME
            , cat.CATEGORY_ID AS L3
            , cat.CATEGORY_NAME
            , item.PM_CODE
            , item.SALES_STATUS
            , yellow.PROD_CLASS_ID AS Gcom_Yellow
            , flat.Web_Parent_Name AS Gcom_Web_Parent
            , supplier.SUPPLIER_NO AS Supplier_ID
            , supplier.SUPPLIER_NAME AS Supplier


            FROM PRD_DWH_VIEW_MTRL.CATEGORY_V AS cat
            
            RIGHT JOIN PRD_DWH_VIEW_LMT.ITEM_V AS item
            	ON cat.CATEGORY_ID = item.CATEGORY_ID
        		AND item.DELETED_FLAG = 'N'
                AND item.PRODUCT_APPROVED_US_FLAG = 'Y'
                AND item.PM_CODE NOT IN ('R9')

            FULL OUTER JOIN PRD_DWH_VIEW_LMT.Prod_Yellow_Heir_Class_View AS yellow
                ON yellow.PRODUCT_ID = item.MATERIAL_NO

            FULL OUTER JOIN PRD_DWH_VIEW_LMT.Yellow_Heir_Flattend_view AS flat
                ON yellow.PROD_CLASS_ID = flat.Heir_End_Class_Code

            INNER JOIN PRD_DWH_VIEW_LMT.material_v AS prod
                on prod.MATERIAL = item.MATERIAL_NO

            INNER JOIN PRD_DWH_VIEW_MTRL.supplier_v AS supplier
                ON prod.vendor = supplier.SUPPLIER_NO
                                
            WHERE item.SALES_STATUS NOT IN ('DG', 'DV', 'WV', 'WG')
            	AND {} IN ({})
            """

#variation of the basic query designed to include discontinued items
grainger_discontinued_query="""
            SELECT item.MATERIAL_NO AS Grainger_SKU
            , cat.SEGMENT_ID AS L1
            , cat.SEGMENT_NAME
            , cat.FAMILY_ID AS L2
            , cat.FAMILY_NAME
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

            WHERE item.SALES_STATUS NOT IN ('DG', 'DV', 'WV', 'WG')
            	AND {} IN ({})
            """

#pull attribute values from Grainger teradata material universe by L3
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
            
grainger_value_query="""
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
                AND LOWER({}) LIKE LOWER('%°%')
            """

#NOTE: This query ONLY seems to work with a return of all category values. Inefficient, but at least it works and runs quickly.
cat_definition_query="""
        SELECT cat.*

        FROM PRD_DWH_VIEW_MTRL.CATEGORY_V AS cat
        
        WHERE {} IN ({})
        """
        
        
grainger_sales_query="""
    SELECT DISTINCT
		TRIM(prod.material) AS Grainger_SKU
		, prod.zvmsta AS Sales_Status
		, COALESCE(inv.sales,0) AS Sales
		, COALESCE(inv.GP, 0) AS GP
		, cat.SEGMENT_ID AS L1
        , cat.SEGMENT_NAME
        , cat.FAMILY_ID AS L2
        , cat.FAMILY_NAME
        , cat.CATEGORY_ID AS L3
        , cat.CATEGORY_NAME
		, supplier.SUPPLIER_NO AS Supplier_ID
		, supplier.SUPPLIER_NAME AS Supplier

FROM PRD_DWH_VIEW_LMT.material_v AS prod

LEFT JOIN

  (SELECT DISTINCT si.material
    , sum(si.subtotal_2) AS Sales
    , sum(si.subtotal_2) - sum(si.source_cost) AS GP
    , cast(count(si.material) as decimal(18,4)) AS txn_lines
    , count(distinct si.sold_to) AS buying_accounts
    , sum(si.inv_qty) AS units
    
    FROM PRD_DWH_VIEW_LMT.sales_invoice_v AS si
    WHERE si.fiscper between 2018007 and 2019007 -- change data range to get last 12 months sales info 
          AND si.division = '01'
    GROUP BY si.material
    ) AS inv
  
   ON prod.material = inv.material

INNER JOIN PRD_DWH_VIEW_LMT.ITEM_V AS item
	ON prod.material = item.MATERIAL_NO

INNER JOIN PRD_DWH_VIEW_MTRL.CATEGORY_V AS cat
	ON cat.CATEGORY_ID = item.CATEGORY_ID
    	AND item.DELETED_FLAG = 'N'
        AND item.PRODUCT_APPROVED_US_FLAG = 'Y'
        AND item.PM_CODE NOT IN ('R9')
        AND item.PM_CODE NOT IN ('R4')

INNER JOIN PRD_DWH_VIEW_MTRL.supplier_v AS supplier
	ON prod.vendor = supplier.SUPPLIER_NO

INNER JOIN PRD_DWH_VIEW_LMT.Prod_Yellow_Heir_Class_View AS yellow
    ON yellow.PRODUCT_ID = item.MATERIAL_NO

WHERE prod.zvmsta IS NOT null
  AND prod.zvmsta NOT IN ('DG', 'WG','DV', 'WV')
  AND supplier.SUPPLIER_NAME NOT LIKE ('%GRAINGER GLOBAL SOURCING%')
  AND {} IN ({})
 """