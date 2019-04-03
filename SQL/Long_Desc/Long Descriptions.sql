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

SELECT
    array_to_string(merch.ancestor_names || merch.name,' > ') as "Merchandising Terminal Node Path"
  , mprod."merchandisingCategoryId" AS "Merchandising Terminal Node ID"
  , tprod."gtPartNumber"
  , copy.content AS "Long Description"
  , copy."updatedOn"

FROM  merchandising_product as mprod

INNER JOIN merch
  ON merch.id = mprod."merchandisingCategoryId"
--  AND (2110 = ANY(merch.ancestors)) --OR 8215 = ANY(merch.ancestors) OR 7739 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***

INNER JOIN entity_description entity
  ON mprod.id = entity."entityId"

INNER JOIN copy 
  ON copy.id = entity."copyId"
  AND copy.type = 5

INNER JOIN taxonomy_product tprod
  ON tprod.id = mprod."taxonomyProductId"

  
WHERE  copy.deleted = false
  AND entity.deleted = false

--  AND mprod."merchandisingCategoryId" IN (
--  AND tprod."gtPartNumber" IN ('

ORDER BY "Merchandising Terminal Node Path"