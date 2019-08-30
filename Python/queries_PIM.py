# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 12:56:37 2019

@author: xcxg109
"""

            
gamut_basic_query="""
    SELECT
          tprod."gtPartNumber" as "Gamut_SKU"
        , tprod."supplierSku" as "Grainger_SKU"
        , tprod."categoryId" AS "PIM Terminal Node ID"
        
    FROM taxonomy_product tprod
    
    WHERE {} IN ({})
"""

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

    SELECT
          array_to_string(tax.ancestor_names || tax.name,' > ') as "PIM Terminal Node Path"
        , tprod."categoryId" AS "PIM Terminal Node ID"
        , tax.name as "Gamut Node Name"
        , tprod."gtPartNumber" as "Gamut_SKU"
        , tprod."supplierSku" as "Grainger_SKU"
        , tax_att.id as "Gamut_Attr_ID"
        , tax_att.name as "Gamut_Attribute_Name"
        , tax_att.description as "Gamut_Attribute_Definition"
--        , tax_att."unitGroupId" AS "Gamut UOM ID"
--        , tax_att."dataType" as "Gamut Data Type"
        , tprodvalue.value as "Original Value"
--        , tprodvalue.unit as "UOM"
        , tprodvalue."valueNormalized" as "Normalized Value"
--        , tprodvalue."unitNormalized" as "UOM"
   
    FROM  taxonomy_product tprod

    INNER JOIN tax
        ON tax.id = tprod."categoryId"
        --  AND (4458 = ANY(tax.ancestors)) --OR 8215 = ANY(tax.ancestors) OR 7739 = ANY(tax.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***

    INNER JOIN taxonomy_attribute tax_att
        ON tax_att."categoryId" = tprod."categoryId"

    INNER JOIN  taxonomy_product_attribute_value tprodvalue
        ON tprod.id = tprodvalue."productId"
	AND tax_att.id = tprodvalue."attributeId"
        
    WHERE tprod.deleted = 'f'
        AND {} IN ({})
        """
        
        
#pull attribute values from Grainger teradata material universe by L3
grainger_attr_query="""
           	SELECT cat.SEGMENT_NAME AS L1
            , cat.FAMILY_NAME AS L2
            , cat.CATEGORY_NAME
            , cat.CATEGORY_ID AS L3
            , item.MATERIAL_NO AS Grainger_SKU
            , attr.DESCRIPTOR_ID as Grainger_Attr_ID
            , attr.DESCRIPTOR_NAME AS Grainger_Attribute_Name
            , item_attr.ITEM_DESC_VALUE AS Grainger_Attribute_Value
            , attr.attribute_level_definition
            , cat_desc.cat_specific_attr_definition
            , cat_desc.ENDECA_RANKING


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
            --    AND item.PM_CODE NOT IN ('R4')


            INNER JOIN PRD_DWH_VIEW_MTRL.CAT_DESC_V AS cat_desc
                ON cat_desc.CATEGORY_ID = item_attr.CATEGORY_ID
                AND cat_desc.DESCRIPTOR_ID = item_attr.DESCRIPTOR_ID
                AND cat_desc.DELETED_FLAG='N'

            INNER JOIN PRD_DWH_VIEW_MTRL.MAT_DESCRIPTOR_V AS attr
                ON attr.DESCRIPTOR_ID = item_attr.DESCRIPTOR_ID
                AND attr.DELETED_FLAG = 'N'

            INNER JOIN PRD_DWH_VIEW_LMT.Prod_Yellow_Heir_Class_View AS yellow
                ON yellow.PRODUCT_ID = item.MATERIAL_NO

            WHERE {} IN ({})
            """