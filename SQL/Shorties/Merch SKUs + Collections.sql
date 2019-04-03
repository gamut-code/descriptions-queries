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
--  , mprod.id as "Merchandising Product ID"
  , tprod."gtPartNumber" as "Gamut Part Number"
  , tprod."supplierSku" as "Grainger Part Number"
  , mcoll.name as "Collection Name"
  
  
FROM  merchandising_product as mprod

INNER JOIN merch
  ON merch.id = mprod."merchandisingCategoryId"
--  AND (6231 = ANY(merch.ancestors)) --OR 8215 = ANY(merch.ancestors) OR 7739 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***
  
INNER JOIN taxonomy_product as tprod
  ON tprod.id = mprod."taxonomyProductId"
	AND mprod.deleted = 'f'

INNER JOIN merchandising_collection_product mcollprod
  ON mprod.id = mcollprod."merchandisingProductId"

INNER JOIN merchandising_collection as mcoll
  ON mcoll.id = mcollprod."collectionId"

WHERE tprod.deleted = 'f'
--AND tprod."gtPartNumber" IN ('
--AND tprod."supplierSku" IN ('
--AND mprod."merchandisingCategoryId" IN (
--AND mcoll.id IN (
--AND mcoll.name IN ('

ORDER BY mprod."merchandisingCategoryId"
  , tprod."gtPartNumber"