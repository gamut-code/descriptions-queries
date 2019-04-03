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

            

SELECT DISTINCT ON (merchatt."productPageDisplay", mprodvalue.value)
  array_to_string(merch.ancestor_names || merch.name,' > ') as "Merchandising Terminal Node Path"
  , mprod."merchandisingCategoryId" AS "Merchandising Terminal Node ID"
  , tprod."gtPartNumber" as "Gamut Part Number"
  , tprod."supplierSku" as "Grainger Part Number"
  , noun."primaryNoun" as "Primary Noun"
  , merchatt."filterDisplay" as "Filter Name"
  , merchatt."collectionHeaderDisplay" as "Table Name"
  , merchatt."collectionStacksDisplay" as "Stacks Name"
  , merchatt."productPageDisplay" as "PDP Name"
  , mprodvalue.value as "Attribute Value"
  , mcoll.name as "Collection Name"
  
  
FROM  merchandising_product as mprod

INNER JOIN merch
  ON merch.id = mprod."merchandisingCategoryId"
--  AND (1263 = ANY(merch.ancestors)) --OR 129 = ANY(merch.ancestors)) -- OR 7739 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***
  
INNER JOIN taxonomy_product as tprod
  ON tprod.id = mprod."taxonomyProductId"
	AND mprod.deleted = 'f'

LEFT JOIN taxonomy_product_primary_noun noun
  ON noun."supplierSku" = tprod."supplierSku"

INNER JOIN merchandising_collection_product mcollprod
  ON mprod.id = mcollprod."merchandisingProductId"

INNER JOIN merchandising_collection as mcoll
  ON mcoll.id = mcollprod."collectionId"
  
INNER JOIN  merchandising_product_value mprodvalue
  ON mprod.id = mprodvalue."merchandisingProductId"
  AND mprodvalue.deleted = 'f'
  
INNER JOIN merchandising_attribute merchatt
  ON merchatt.id = mprodvalue."merchandisingAttributeId"
  AND merchatt.deleted = 'f'

WHERE tprod.deleted = 'f'
  AND mcoll.visible = 't'
--AND mcoll.name LIKE '%Kit%'
--AND mprod."merchandisingCategoryId" IN (
--AND tprod."gtPartNumber" IN ('
--AND LOWER(merchatt.name) LIKE LOWER('%Req%')
--AND mprodvalue.value LIKE '%Reflexite%'
--AND merchatt.id IN (79961)

ORDER BY merchatt."productPageDisplay"
       , mprodvalue.value
       , merchatt.name
       , mprod."merchandisingCategoryId" 