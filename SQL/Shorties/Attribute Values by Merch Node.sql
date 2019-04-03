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

            

SELECT --DISTINCT ON (merchatt.name, mprodvalue.value)
  array_to_string(merch.ancestor_names || merch.name,' > ') as "Merchandising Terminal Node Path"
  , mprod."merchandisingCategoryId" AS "Merchandising Terminal Node ID"
  , mprod.id as "Merchandising Product ID"
  , tprod."gtPartNumber" as "Gamut Part Number"
  , merchatt.name as "Attribute Name"
  , merchatt."dataType" as "Data Type"
  , mprodvalue.value as "Attribute Value"
  , mcoll.name as "Collection Name"
  
  
FROM  merchandising_product as mprod

INNER JOIN merch
  ON merch.id = mprod."merchandisingCategoryId"
--  AND (6231 = ANY(merch.ancestors)) --OR 8215 = ANY(merch.ancestors) OR 7739 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***
  
INNER JOIN taxonomy_product as tprod
  ON tprod.id = mprod."taxonomyProductId"
	AND mprod.deleted = 'f'

INNER JOIN merchandising_attribute merchatt --I moved this first and attached it to the categoryID
  ON merchatt."merchandisingCategoryId" = mprod."merchandisingCategoryId"

LEFT JOIN  public.merchandising_product_value mprodvalue --I joined this on BOTH mprod and merchatt, and put the left join here.
  ON mprod.id = mprodvalue."merchandisingProductId"
  AND merchatt.id = mprodvalue."merchandisingAttributeId"

INNER JOIN merchandising_collection_product mcollprod
  ON mprod.id = mcollprod."merchandisingProductId"

INNER JOIN merchandising_collection as mcoll
  ON mcoll.id = mcollprod."collectionId"

WHERE tprod.deleted = 'f'
--AND tprod."gtPartNumber" IN ('
--AND LOWER(mprodvalue.value) LIKE LOWER('%
--AND merchatt.id IN (
--AND mprod."merchandisingCategoryId" IN (
--AND mcoll.id IN (
--AND mcoll.name IN ('

ORDER BY merchatt.name
       , mprodvalue.value
       , mprod."merchandisingCategoryId" 