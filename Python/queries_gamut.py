# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 12:56:37 2019

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
        , tprod."gtPartNumber" as "Gamut Part Number"
        , tprod."supplierSku" as "Grainger SKU"
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
        --  AND (4458 = ANY(tax.ancestors)) --OR 8215 = ANY(tax.ancestors) OR 7739 = ANY(tax.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***

    INNER JOIN taxonomy_attribute tax_att
        ON tax_att."categoryId" = tprod."categoryId"

    INNER JOIN  taxonomy_product_attribute_value tprodvalue
        ON tprod.id = tprodvalue."productId"
	AND tax_att.id = tprodvalue."attributeId"
        
    WHERE tprod.deleted = 'f'
        AND {} IN ({})
        """